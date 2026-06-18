# Research: subset-b-000883

Grouped research for x86 microcode loading, Hyper-V platform discovery, CPU capability-name generation, and MTRR setup/control. Each section is keyed by exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/amd.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/amd.c

Purpose: implements AMD x86 microcode loading for family 0x10 and newer CPUs. It supports early BSP/AP loading from built-in firmware or initrd containers, late loading through the generic microcode core, resume reload, per-family firmware files, Zen patch matching, SHA256 validation for affected signed-patch generations, and an in-memory patch cache that survives initrd teardown.

Important APIs/types/functions: main private types are `ucode_patch`, `equiv_cpu_entry`, `microcode_header_amd`, `microcode_amd`, `equiv_cpu_table`, `zen_patch_rev`, `cpuid_1_eax`, `cont_desc`, and `patch_digest`. Public integration functions are `load_ucode_amd_bsp()`, `load_ucode_amd_ap()`, `reload_ucode_amd()`, `init_amd_microcode()`, and `exit_amd_microcode()`. The `microcode_amd_ops` vector supplies `request_microcode_amd()`, `collect_cpu_info_amd()`, `apply_microcode_amd()`, `microcode_fini_cpu_amd()`, and `finalize_late_load_amd()` to `core.c`. Important helpers include `verify_container()`, `verify_equivalence_table()`, `verify_patch()`, `scan_containers()`, `__apply_microcode_amd()`, `find_patch()`, `update_cache()`, and `load_microcode_amd()`.

Control flow: early BSP load records `bsp_cpuid_1_eax`, reads the current patch level, locates AMD container blobs, scans glued containers, selects the matching patch, rejects older patches, and writes `MSR_AMD64_PATCH_LOADER`. Early AP and resume paths reuse the cached matching patch. Runtime firmware load reads `amd-ucode/microcode_amd.bin` or a family-specific `amd-ucode/microcode_amd_famXXh.bin`, validates the container and equivalence table, caches newer patches, then returns `UCODE_NEW` if any node's representative CPU can advance. Late apply is invoked on the target CPU by `core.c`, finds the cached patch, applies it when the current revision is not newer, and updates `cpu_data()` plus `boot_cpu_data` on the BSP.

State and persistence: runtime state is process-local kernel memory: `microcode_cache`, `equiv_table`, `bsp_cpuid_1_eax`, `sha_check`, and each CPU's `ucode_cpu_info[].mc`. The file reads firmware from built-in blobs, initrd cpio data, or `request_firmware_direct()`, but does not persist firmware to disk. Applied microcode is CPU state and must be reloaded after reset or resume.

Dependencies and integration points: depends on AMD microcode container format, `MSR_AMD64_PATCH_LEVEL`, `MSR_AMD64_PATCH_LOADER`, CPUID family/model/stepping encoding, initrd cpio lookup from `core.c`, firmware loader APIs, `crypto/sha2.h`, `amd_shas.c`, node CPU masks, and generic late-load synchronization in `core.c`. It also honors `microcode.amd_sha_check=off`, `force_minrev`, and hypervisor debug simulation state.

Risks: wrong parsing of glued containers can select a patch for the wrong CPU or skip a valid newer patch. SHA digest tables must stay sorted and complete for the patch IDs protected by `need_sha_check()`. The Zen patch revision format embeds CPU identity, so comparison logic must not treat different steppings as interchangeable except where explicitly intended for cache replacement. Late-load failure cleanup frees the cache, so stale `uci->mc` pointers must be cleared. MSR writes are hardware-critical and must be run on the target CPU.

Test signals: boot with early AMD microcode in initrd and built-in firmware, AP bringup after BSP early load, `echo 1 > /sys/devices/system/cpu/microcode/reload`, resume reload, family 0x10-0x16 equivalence-table matching, Zen and newer patch-ID matching, SHA mismatch rejection, `microcode.amd_sha_check=off` taint behavior, missing firmware returning `UCODE_NFOUND`, and per-CPU `/sys/devices/system/cpu/cpu*/microcode/version`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/amd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/amd_shas.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/amd_shas.c

Purpose: provides the static SHA256 digest allowlist used by the AMD microcode loader to authenticate selected Zen-family microcode patch payloads whose signing algorithm requires an additional kernel-side digest check.

Important APIs/types/functions: this file defines only `static const struct patch_digest phashes[]`, consumed by `amd.c`. Each entry maps a `patch_id` to a 32-byte SHA256 digest. It relies on `struct patch_digest` and `SHA256_DIGEST_SIZE` being defined before inclusion, because `amd.c` includes this C fragment directly rather than compiling it as a separate translation unit.

Control flow: there is no executable control flow in this file. `amd.c` calls `bsearch()` over `phashes` from `verify_sha256_digest()`, using `cmp_id()` and the patch ID from the AMD microcode header. If a matching digest exists, `amd.c` hashes the patch data and compares it against the stored digest before writing the patch loader MSR.

State and persistence: state is immutable `.rodata` compiled into the kernel image. There is no allocation, I/O, runtime mutation, or persistence beyond the kernel binary.

Dependencies and integration points: tightly coupled to `amd.c`; the comment requires entries to remain sorted because binary search is used. It indirectly participates in AMD early and late microcode loading, and its coverage must match the cutoff revisions in `get_cutoff_revision()`.

Risks: an unsorted entry silently breaks binary search for some patch IDs. Missing, stale, or mistyped digests cause legitimate patches to be rejected, while an incorrect digest would weaken the mitigation this table is meant to provide. Since this is included C data, duplicate symbol or type changes in `amd.c` can break compilation.

Test signals: build coverage for `CONFIG_CPU_SUP_AMD`, binary-search lookup for first/middle/last patch IDs, rejection of intentionally corrupted patch data, successful load for every listed patch ID, and validation that the generated object contains `phashes` only as private data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/amd_shas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/core.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/core.c

Purpose: provides the vendor-neutral x86 microcode driver core. It parses boot controls, disables unsafe contexts, dispatches early BSP/AP loading to Intel or AMD code, exposes sysfs state and late reload, synchronizes late updates across CPUs and SMT siblings, handles resume reload, and registers CPU hotplug callbacks.

Important APIs/types/functions: global state includes `microcode_ops`, `dis_ucode_ldr`, `force_minrev`, `base_rev`, `microcode_rev[]`, `hypervisor_present`, `ucode_cpu_info[]`, and `early_data`. Public functions include `microcode_loader_disabled()`, `load_ucode_bsp()`, `load_ucode_ap()`, `find_microcode_in_initrd()`, `microcode_bsp_resume()`, and `microcode_nmi_handler()`. Late-loading types include `sibling_ctrl` and `microcode_ctrl`; key helpers are `wait_for_cpus()`, `wait_for_ctrl()`, `load_secondary()`, `load_primary()`, `load_late_stop_cpus()`, `setup_cpus()`, and `load_late_locked()`.

Control flow: early boot parses `microcode=` and compatibility `dis_ucode_ldr`, rejects unsupported vendors/families, then invokes vendor BSP/AP loaders. Init selects Intel or AMD ops, creates the faux firmware device, creates CPU-root and per-CPU `microcode` sysfs groups, registers syscore resume, and installs CPU hotplug callbacks. Late reload writes to the `reload` attribute, loads firmware through vendor ops, optionally stages the patch, snapshots CPU capabilities, then uses `stop_machine_cpuslocked()` and optionally NMI rendezvous to update all online and eligible offline SMT siblings. Results are counted, finalized by vendor ops, tainted on unsafe/incomplete updates, and checked for changed CPU features.

State and persistence: per-CPU `ucode_cpu_info` tracks signatures, revisions, and vendor patch pointers; sysfs exposes revision and processor flags. Early state records old/new revisions for boot messages. No disk persistence is performed; firmware is requested through normal firmware APIs, and CPU microcode must be applied again after reset.

Dependencies and integration points: depends on `microcode_ops` from `amd.c` or `intel.c`, CPU hotplug, stop-machine, APIC/NMI delivery, topology sibling masks, syscore suspend/resume, firmware faux devices, sysfs CPU devices, `find_cpio_data()`, command-line parsing, `microcode_check()`, and `store_cpu_caps()`.

Risks: late loading is synchronization-sensitive; secondary SMT siblings can execute unsafe code while a primary updates microcode unless rendezvous and offline sibling handling are correct. Timeout paths can panic for nonrecoverable primary hangs. Loader disable logic intentionally rejects hypervisors unless debug is enabled. Capability changes after late update can surprise running code, so the post-update check and tainting are important. CPU hotplug must not race with updates; all non-hotplug users take `cpus_read_lock()`.

Test signals: early Intel and AMD loading, `microcode=dis_ucode_ldr`, `microcode=force_minrev`, late reload success and failure, systems with offline SMT siblings, NMI and non-NMI rendezvous paths, resume from suspend/hibernate, CPU hotplug creating/removing sysfs groups, hypervisor-present loader disablement, and post-update capability change logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/intel-ucode-defs.h -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/intel-ucode-defs.h

Purpose: contains a generated-style inventory of Intel CPU signature/platform/minimum-revision metadata used by Intel microcode tooling or validation code. The file is data, not a normal self-contained header with declarations.

Important APIs/types/functions: the content is a sequence of `struct x86_cpu_id`-style initializers using fields such as `.flags`, `.vendor`, `.family`, `.model`, `.steppings`, `.platform_mask`, and `.driver_data`. `X86_CPU_ID_FLAG_ENTRY_VALID` marks valid rows, `X86_VENDOR_INTEL` scopes them to Intel, and `driver_data` carries the revision-like payload associated with a CPU/platform combination.

Control flow: no functions execute here. Any consumer includes or incorporates the table into a larger array, then matches CPUID family/model/stepping and platform mask against the running CPU.

State and persistence: immutable build-time table data only. It has no runtime allocation, I/O, or persistent storage behavior.

Dependencies and integration points: depends on the `x86_cpu_id` field layout and CPU match semantics from x86 CPU device ID infrastructure. It integrates with Intel microcode support by describing which CPU/platform combinations have known revision metadata.

Risks: the file is ABI-adjacent hardware data. Incorrect family/model/stepping masks can match the wrong CPU or fail to match a supported one. Because entries are plain initializers, structural changes in the consumer type can silently break build expectations. Duplicates or ordering assumptions in downstream lookup code need explicit validation.

Test signals: compile the including consumer, match representative CPUID/platform combinations, verify no malformed stepping masks, compare revisions against Intel microcode release metadata, and ensure unsupported CPUs do not match valid entries accidentally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/intel-ucode-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/intel.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/intel.c

Purpose: implements Intel x86 microcode loading. It validates Intel microcode blobs, matches primary and extended signatures, supports early BSP/AP loading from built-in firmware or initrd, late firmware reload, optional package-level staging through the Intel MCU staging mailbox, resume reload, and vendor ops registration for the generic microcode core.

Important APIs/types/functions: exported helpers are `intel_get_platform_id()`, `intel_collect_cpu_info()`, `intel_find_matching_signature()`, and `intel_microcode_sanity_check()`. Internal types include `extended_signature`, `extended_sigtable`, and `staging_state`. Key functions include `scan_microcode()`, `save_microcode_patch()`, `stage_microcode()`, `do_stage()`, `__apply_microcode()`, `load_ucode_intel_bsp()`, `load_ucode_intel_ap()`, `reload_ucode_intel()`, `parse_microcode_blobs()`, `request_microcode_fw()`, `finalize_late_load()`, `staging_available()`, and `init_intel_microcode()`.

Control flow: early loading collects CPU signature/revision/platform flags, locates `intel-ucode/ff-mm-ss` built-in firmware or `kernel/x86/microcode/GenuineIntel.bin` in initrd, scans for the newest matching patch, and writes `MSR_IA32_UCODE_WRITE`. If the BSP loaded a patch before memory allocation was available, `save_builtin_microcode()` later saves the exact patch into heap memory for AP/resume reuse. Late loading requests the per-CPU firmware file, iterates all concatenated blobs with an `iov_iter`, sanity-checks checksums and extended signatures, chooses the newest matching revision, enforces `min_req_ver` when configured, optionally stages the image through the mailbox, and lets `core.c` apply it on each CPU.

State and persistence: `ucode_patch_va` holds the saved current patch for early AP and resume paths; `ucode_patch_late` holds the candidate late patch until finalization; `llc_size_per_core` supports a Broadwell-X blacklist. There is no disk persistence. The hardware update is CPU state and the saved heap copy exists only for the running kernel.

Dependencies and integration points: depends on Intel microcode header layout, extended signature checksums, `MSR_IA32_PLATFORM_ID`, `MSR_IA32_UCODE_WRITE`, `MSR_IA32_MCU_ENUMERATION`, `MSR_IA32_MCU_STAGING_MBOX_ADDR`, architectural capability bits, firmware APIs, initrd cpio lookup, topology package/primary-thread masks, MMIO accessors, and the generic late-load rendezvous in `core.c`.

Risks: checksum and size validation protects against malformed firmware; mistakes here can read past firmware buffers or accept corrupt patches. Late loading can be unsafe without `min_req_ver`; `force_minrev` changes behavior. Staging mailbox offsets, retry limits, and response parsing must match hardware or late load silently falls back or fails. The Broadwell-X blacklist prevents known hangs. `ucode_patch_va` sentinel handling is subtle during early-to-heap transition.

Test signals: early initrd and built-in loading, AP reuse of BSP patch, resume reload, late reload with safe and unsafe headers, `force_minrev`, malformed checksum and extended table rejection, Broadwell-X blacklist, staging-capable hardware mailbox success/failure/timeout paths, sysfs revision updates, and CPU capability delta reporting after update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/intel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/internal.h -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/internal.h

Purpose: defines the private interface shared by x86 microcode core and vendor implementations. It centralizes update result states, vendor callback shape, early-load revision reporting, CPUID vendor helpers that work before `boot_cpu_data` is ready, and build-time stubs for disabled Intel or AMD support.

Important APIs/types/functions: defines `enum ucode_state`, `struct microcode_ops`, `struct early_load_data`, `MAX_UCODE_COUNT`, CPUID vendor constants, `CPUID_IS()`, `x86_cpuid_vendor()`, and `x86_cpuid_family()`. It declares `early_data`, `ucode_cpu_info[]`, `microcode_rev[]`, `base_rev`, `hypervisor_present`, `force_minrev`, `find_microcode_in_initrd()`, AMD entry points, and Intel entry points. `ucode_dbg()` gates debug prints through `CONFIG_MICROCODE_DBG`.

Control flow: the inline CPUID helpers directly execute CPUID leaf 0 or 1 and return vendor/family before normal CPU structures are initialized. The rest is callback wiring: `core.c` calls `microcode_ops` methods and vendor-specific entry points through these declarations.

State and persistence: no state is owned here, but it declares shared runtime globals. It has no I/O or persistence behavior.

Dependencies and integration points: depends on `asm/cpu.h`, `asm/microcode.h`, early cpio/initrd definitions, `NR_CPUS`, and config symbols `CONFIG_CPU_SUP_AMD`, `CONFIG_CPU_SUP_INTEL`, and `CONFIG_MICROCODE_DBG`. It is the contract between `core.c`, `amd.c`, and `intel.c`.

Risks: `microcode_ops` semantics are synchronization-sensitive: core guarantees target-CPU execution for collection/apply/stage callbacks, and vendor code depends on that for MSR writes. Adding enum values or callback flags must keep `core.c` result handling in sync. CPUID vendor constants are byte-order-specific and must remain correct.

Test signals: builds with AMD-only, Intel-only, both, and neither vendor support; early boot before `boot_cpu_data`; debug and non-debug builds; and static analysis that every enabled vendor fills required callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mkcapflags.sh -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mkcapflags.sh

Purpose: generates C string arrays for x86 CPU feature, bug, and optional VMX feature names from preprocessor definitions in header files. The output is used by CPU information reporting paths so feature bits can be rendered as stable lowercase names.

Important APIs/types/functions: shell function `dump_array ARRAY SIZE PFX POSTFIX IN` emits a `const char * const` array. It parses `#define` lines for prefixes such as `X86_FEATURE_`, `X86_BUG_`, and `VMX_FEATURE_`, extracts quoted comments as user-facing names, lowercases them, and prints designated initializers. The script writes to positional output `$1` using input headers `$2` and `$3`.

Control flow: `set -e` aborts on errors. A trap removes the output file on failure. The script emits `cpufeatures.h`, calls `dump_array` for `x86_cap_flags`, calls it again for `x86_bug_flags` using `NCAPINTS*32` as an index offset postfix, then conditionally emits VMX feature names behind `CONFIG_X86_VMX_FEATURE_NAMES`.

State and persistence: writes exactly one generated output file passed as `$1`. It reads the feature definition headers and has no other persistent state.

Dependencies and integration points: depends on POSIX shell utilities `sed`, `tr`, `wc`, `printf`, and arithmetic expansion. It integrates with the kernel build system as a generator for architecture CPU flag name arrays and relies on quoted comments in `cpufeatures.h` and `vmxfeatures.h`.

Risks: parsing is format-sensitive; feature defines without quoted comments are skipped. Spacing and tab calculations affect readability but not semantics. Missing arguments can cause confusing shell failures. Since values are lowercased blindly, comments must already encode the desired public token.

Test signals: run the generator against representative cpufeatures/vmxfeatures headers, compile the generated C, verify indexes for normal features and bug offsets, check skipped unquoted comments, and compare `/proc/cpuinfo` flag names against expected strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mkcapflags.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mshyperv.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mshyperv.c

Purpose: detects and initializes Microsoft Hyper-V support on x86. It reads Hyper-V CPUID leaves, records feature/hint/isolation state, sets hypervisor-specific platform hooks, manages synthetic interrupt handlers and SynIC MSR access, configures clocks/APIC/SMP behavior, and installs crash/kexec/shutdown integration.

Important APIs/types/functions: global exports include `hv_nested`, `ms_hyperv`, `hv_get_non_nested_msr()`, `hv_set_non_nested_msr()`, `hv_para_set_sint_proxy()`, `hv_para_get_synic_register()`, `hv_para_set_synic_register()`, `hv_get_msr()`, `hv_set_msr()`, handler setup/removal functions for mshv/vmbus/stimer0/kexec/crash, and `hv_get_hypervisor_version()`. Core init functions are `ms_hyperv_platform()`, `ms_hyperv_init_platform()`, `hv_reserve_irq_vectors()`, `hv_smp_prepare_cpus()`, `reduced_hw_init()`, `ms_hyperv_x2apic_available()`, and `ms_hyperv_msi_ext_dest_id()`.

Control flow: detection first checks the hypervisor CPUID bit, verifies the `"Microsoft Hv"` signature and required hypercall/VP-index MSRs, then returns the Hyper-V CPUID base. Platform init fills `ms_hyperv` fields from CPUID leaves, identifies partition/isolation/nested features, adjusts TSC and APIC calibration hooks, enables SNP/TDX static branches and hypercall implementations, reserves vectors for root partitions, installs IDT system vectors for callback/reenlightenment/stimer, overrides SMP preparation where required, initializes Hyper-V clocks/MMU/VTL support, and marks TSC unstable for guests without invariant TSC.

State and persistence: persistent runtime state is in `ms_hyperv`, `hv_nested`, callback function pointers, suspend reference-counter offset, and platform operation hooks. No filesystem persistence exists. Hyper-V MSRs, static calls, static branches, system vectors, and `machine_ops` are modified for the lifetime of the booted kernel.

Dependencies and integration points: depends on Hyper-V CPUID leaves/MSRs, `asm/mshyperv.h`, paravisor/isolated VM helpers, APIC and IDT system vectors, clocksource Hyper-V timer code, kexec/crash/shutdown machine ops, SMP boot hooks, NUMA logical processor creation hypercalls, SEV-SNP/TDX confidential computing attributes, EFI reduced-hardware handling, and NMI infrastructure.

Risks: feature-bit interpretation controls low-level boot paths; wrong isolation handling can select an invalid hypercall ABI or clocksource. SynIC MSR redirection must distinguish nested, non-nested, and paravisor cases. Handler pointers are global and not protected by per-registration lifetime beyond simple assignment. Reserved vectors are fatal if already used. Crash/kexec cleanup must disable Hyper-V state before the next kernel observes stale VP assist pages.

Test signals: boot as normal Hyper-V guest, root partition, nested guest, SNP isolated guest, TDX guest, and VBS/paravisor guest; verify VMBus callback and stimer interrupts; kexec and crash dump paths; suspend/hibernate clock continuity; x2APIC/MSI destination behavior; invariant TSC exposure; SynIC nested MSR remapping; and unknown NMI behavior under Debug-VM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mshyperv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/Makefile

Purpose: selects the x86 MTRR implementation objects built into the kernel.

Important APIs/types/functions: builds `mtrr.o`, `if.o`, `generic.o`, and `cleanup.o` unconditionally for this directory. Adds `amd.o`, `cyrix.o`, `centaur.o`, and `legacy.o` only when `CONFIG_X86_32` is enabled.

Control flow: no runtime control flow. Kbuild evaluates `obj-y` and `obj-$(CONFIG_X86_32)` to decide which objects are linked.

State and persistence: no runtime state. The only persistent effect is build output selection.

Dependencies and integration points: integrates with Kbuild and the MTRR source files in the same directory. The 32-bit-only objects implement legacy CPU-specific MTRR-like interfaces and suspend/resume handling for non-generic CPUs.

Risks: moving an object between unconditional and `CONFIG_X86_32` changes symbol availability. Generic MTRR code must remain available for 64-bit, while legacy AMD K6/Cyrix/Centaur code must not be linked where its CPU access mechanisms are invalid.

Test signals: build 32-bit and 64-bit x86 configurations, with and without generic MTRR support, and confirm expected object inclusion through build logs or `nm`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/amd.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/amd.c

Purpose: implements the legacy AMD K6-style MTRR operations for 32-bit systems using the `MSR_K6_UWCCR` register pair rather than generic Intel-style MTRRs.

Important APIs/types/functions: provides `amd_mtrr_ops` with `var_regs = 2`, `amd_set_mtrr()`, `amd_get_mtrr()`, `generic_get_free_region()`, `amd_validate_add_page()`, and `positive_have_wrcomb()`.

Control flow: `amd_get_mtrr()` reads `MSR_K6_UWCCR`, selects lower or upper dword for register 0 or 1, decodes base, type bits, and inverted 128K-granularity size mask. `amd_set_mtrr()` reads both dwords, clears the selected slot for size zero or encodes base/type/negative size mask, flushes cache with `wbinvd()`, then writes the combined MSR. Validation rejects unsupported types, blocks below 128K, non-power-of-two sizes, and misaligned bases.

State and persistence: hardware state lives in `MSR_K6_UWCCR`; no separate heap state is owned. Changes persist only until CPU reset or later MTRR reprogramming.

Dependencies and integration points: selected by `legacy.c` when the boot CPU reports `X86_FEATURE_K6_MTRR`. It plugs into common MTRR APIs through `struct mtrr_ops` and uses generic free-region allocation.

Risks: only two regions exist and size encoding is unusual, so off-by-one mask mistakes can create wrong cacheability over physical memory. The code assumes legacy 32-bit address behavior. Cache flush ordering around MSR writes is required for safe memory type changes.

Test signals: 32-bit AMD K6 feature detection, add/delete WC and UC regions, reject invalid alignment/sizes/types, read back encoded ranges through `/proc/mtrr`, and suspend/resume if legacy syscore support is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/amd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/centaur.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/centaur.c

Purpose: implements legacy Centaur/VIA WinChip memory control register operations for 32-bit systems that expose `X86_FEATURE_CENTAUR_MCR`.

Important APIs/types/functions: defines `centaur_mcr[8]`, `centaur_mcr_reserved`, `centaur_mcr_type`, and `centaur_mtrr_ops`. Operation callbacks are `centaur_get_free_region()`, `centaur_get_mcr()`, `centaur_set_mcr()`, `centaur_validate_add_page()`, and `positive_have_wrcomb()`.

Control flow: free-region search skips reserved MCR slots and returns empty slots from `mtrr_if->get()`. `centaur_get_mcr()` decodes cached high/low register values into base, negative-mask size, and a type that differs between WinChip and WinChip2. `centaur_set_mcr()` encodes disable or base/size/type values, updates the shadow array, and writes `MSR_IDT_MCR0 + reg`. Validation allows only write-combining on WinChip and write-combining or uncacheable on WinChip2.

State and persistence: maintains a software shadow of eight MCRs in `centaur_mcr[]` and writes hardware MSRs. No disk persistence exists.

Dependencies and integration points: selected by `legacy.c` on Centaur CPUs with MCR support. It implements the `mtrr_ops` contract used by `mtrr.c` and `/proc/mtrr`.

Risks: the file relies on `centaur_mcr_type` and reserved-mask initialization from surrounding CPU setup; if those are wrong, type encoding and allocation are wrong. The shadow array must stay synchronized with MSR writes. Legacy hardware supports fewer memory types than generic MTRRs.

Test signals: boot on WinChip/WinChip2 or emulator with MCR feature, add/read/delete WC and UC entries as appropriate, verify reserved registers are skipped, and confirm `/proc/mtrr` displays expected decoded types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/centaur.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/cleanup.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/cleanup.c

Purpose: sanitizes problematic BIOS MTRR layouts during early boot and trims RAM that is not covered by write-back MTRRs. With `CONFIG_MTRR_SANITIZER`, it can search for a better variable-MTRR layout that covers RAM with fewer or cleaner WB/UC ranges.

Important APIs/types/functions: key types are `var_mtrr_range_state`, `var_mtrr_state`, and `mtrr_cleanup_result`. Exported/init functions are `mtrr_cleanup()`, `amd_special_default_mtrr()`, and `mtrr_trim_uncached_memory()`. Helpers include `x86_get_mtrr_mem_range()`, `range_to_mtrr()`, `range_to_mtrr_with_hole()`, `x86_setup_var_mtrrs()`, `mtrr_need_cleanup()`, `mtrr_calc_range_state()`, `mtrr_search_optimal_index()`, `real_trim_memory()`, and early-parameter parsers for cleanup, chunk/granularity, spare registers, and trim disablement.

Control flow: cleanup snapshots current variable MTRRs, checks for a default UC setup with only WB and UC ranges, derives RAM ranges from WB entries minus UC/WP holes and AMD TOM2 removal, then either applies user-specified chunk/granularity or searches combinations from 64K up to 2G. The best zero-loss setting with enough spare registers is converted into `mtrr_state.var_ranges` via `fill_mtrr_var_range()`. Trimming separately computes covered WB ranges and reserves uncovered RAM in the E820 table.

State and persistence: uses `__initdata` arrays `range[]`, `range_state[]`, `result[]`, `min_loss_pfn[]`, and boot parameters. It mutates global `mtrr_state.var_ranges` and can update the E820 memory map by converting RAM to reserved. No filesystem state is written.

Dependencies and integration points: called from `mtrr_bp_init()` after generic MTRR state is read. Depends on common MTRR ops, `e820__range_update()`, range manipulation helpers, AMD `MSR_AMD64_SYSCFG` and `MSR_K8_TOP_MEM2`, early params, and `changed_by_mtrr_cleanup` in `mtrr.c`.

Risks: incorrect cleanup can mark usable RAM uncached or expose MMIO as write-back. The search space is bounded and may fail on complex layouts. Low-memory fixed MTRR precedence is special-cased; mistakes below 1MB can break legacy mappings. E820 trimming permanently removes RAM for this boot and warns loudly. Virtualized systems with blank MTRRs are intentionally skipped.

Test signals: BIOS layouts with UC default plus WB/UC variable entries, command-line `enable_mtrr_cleanup`, `disable_mtrr_cleanup`, `mtrr_chunk_size=`, `mtrr_gran_size=`, `mtrr_spare_reg_nr=`, `disable_mtrr_trim`, AMD TOM2 systems, virtualized blank MTRRs, E820 update logs, and debug output with `mtrr=debug`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/cleanup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/cyrix.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/cyrix.c

Purpose: implements legacy Cyrix Address Range Register operations for 32-bit CPUs with `X86_FEATURE_CYRIX_ARR`.

Important APIs/types/functions: provides `cyrix_mtrr_ops` with `cyrix_set_arr()`, `cyrix_get_arr()`, `cyrix_get_free_region()`, `generic_validate_add_page()`, and `positive_have_wrcomb()`. Internal helpers `prepare_set()` and `post_set()` manage cache/TLB-safe ARR programming.

Control flow: reads use MAPEN in `CX86_CCR3` to access ARR base bytes and RCR type registers, then decode size and type with special ARR7 semantics. Free-region search prefers ARR7 for ranges over 32MB, otherwise scans ARR0-ARR6 and uses ARR7 only for ranges at least 256K. Writes disable PGE if present, disable caches, flush with `wbinvd()`, enable MAPEN, program ARR base/size/type registers, restore CCR3, reenable caches, and restore CR4.

State and persistence: static globals `cr4` and `ccr3` save transient control-register state while programming. Persistent hardware state is in Cyrix ARR/RCR registers until reset or reprogramming.

Dependencies and integration points: selected by `legacy.c` for Cyrix ARR CPUs. Depends on `processor-cyrix.h` accessors, CR0/CR4 cache controls, generic MTRR validation, and common MTRR APIs.

Risks: ARR7 has different enable/type/size encoding from ARR0-ARR6. Programming requires cache-disabled critical sections; missed restore paths can leave caches or PGE misconfigured. The code manipulates legacy CPU-specific configuration registers that are not safe on other vendors.

Test signals: boot on Cyrix ARR hardware or emulator, add/read/delete ranges below and above 32MB, ARR7 minimum-size behavior, write-combining/write-through/write-back/uncacheable type decoding, and suspend/resume through legacy syscore registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/cyrix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/generic.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/generic.c

Purpose: implements generic Intel-style MTRR state reading, writing, and lookup. It builds an effective cache-type map from fixed ranges, variable ranges, default type, and AMD TOP_MEM2, supports guest-forced read-only MTRR state, and provides the `generic_mtrr_ops` backend.

Important APIs/types/functions: key types are `fixed_range_block` and `cache_map`. Globals include `mtrr_debug`, `mtrr_tom2`, `mtrr_state`, `phys_hi_rsvd`, cache-map state, and `mtrr_state_set`. Public functions include `mtrr_build_map()`, `mtrr_copy_map()`, `guest_force_mtrr_state()`, `mtrr_type_lookup()`, `fill_mtrr_var_range()`, `mtrr_save_fixed_ranges()`, `get_mtrr_state()`, `mtrr_state_warn()`, `mtrr_wrmsr()`, `mtrr_disable()`, `mtrr_enable()`, `mtrr_generic_set_state()`, `generic_get_free_region()`, `generic_validate_add_page()`, `positive_have_wrcomb()`, and `generic_mtrr_ops`.

Control flow: boot reads `MSR_MTRRcap`, variable ranges, fixed ranges, `MSR_MTRRdefType`, and AMD TOM2, then builds an ordered cache map. Fixed entries are inserted first and marked as fixed; variable ranges are overlaid with effective type merging rules. Runtime MTRR changes rebuild variable portions of the map. `mtrr_type_lookup()` walks the map and default type to return the effective memory type and whether it is uniform. Generic writes disable caches through caller sequencing, write base/mask MSRs, and update `mtrr_state`.

State and persistence: owns the effective cache-map array, initially in `__initdata` and later copied to heap by `mtrr_copy_map()`. It stores global hardware snapshot state in `mtrr_state`; actual persistence is CPU MSR state only.

Dependencies and integration points: used by `mtrr.c` during boot and runtime changes, by PAT/memtype code through `mtrr_type_lookup()`, by virtualized platforms through `guest_force_mtrr_state()`, and by cleanup through `fill_mtrr_var_range()`. Depends on MTRR MSRs, cache disable/enable helpers, SEV-SNP/TDX/Hyper-V/Xen guest detection, and AMD SYSCFG/TOM2 handling.

Risks: effective type resolution is security- and correctness-critical for memory mappings. Cache-map exhaustion disables MTRRs. Guest-forced state clears `X86_FEATURE_MTRR` to prevent later mutation and must only be accepted for vetted virtualization cases. Reserved high bits must be masked using physical address width. Fixed MTRR precedence over variable ranges must be preserved.

Test signals: `mtrr=debug` map output, fixed and variable overlap cases, UC/WB/WT effective type combinations, AMD TOM2 handling, guest-forced MTRR state under Hyper-V/Xen/SNP/TDX, runtime add/delete rebuilding, `mtrr_type_lookup()` uniform/non-uniform ranges, and BIOS inconsistent-MTRR warnings on SMP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/if.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/if.c

Purpose: exposes the legacy `/proc/mtrr` user interface for inspecting and modifying MTRR regions through text writes and ioctls, including compat ioctl support.

Important APIs/types/functions: provides `mtrr_attrib_to_str()` globally and, under `CONFIG_PROC_FS`, defines `mtrr_write()`, `mtrr_ioctl()`, `mtrr_open()`, `mtrr_close()`, `mtrr_seq_show()`, `mtrr_file_add()`, `mtrr_file_del()`, `mtrr_proc_ops`, and `mtrr_if_init()`. It uses `mtrr_sentry`, `mtrr_gentry`, compat variants, and `FILE_FCOUNT()` per-open reference counts.

Control flow: opening `/proc/mtrr` requires MTRR support, a get callback, and `CAP_SYS_ADMIN`. Reads iterate variable ranges and display non-empty entries with base, size, count, and type. Text writes accept `disable=N` or `base=... size=... type=...`, validate alignment, and call `mtrr_add_page()` or `mtrr_del_page()`. Ioctls copy user entries, dispatch add/set/delete/kill/get operations in byte or page units, hide entries that cannot fit in legacy field widths, and copy results back. Closing a file removes entries added through that open based on per-file counts.

State and persistence: allocates a per-open `fcount` array stored in `seq_file.private`; this controls cleanup on close. It also updates global `mtrr_usage_table[]` indirectly via core MTRR add/delete calls. No disk persistence exists.

Dependencies and integration points: depends on common MTRR APIs in `mtrr.c`, `mtrr_if`, `num_var_ranges`, procfs, seq_file, capabilities, user-copy helpers, and compat ioctl definitions. It registers at `arch_initcall`.

Risks: this is a privileged legacy ABI, so parsing and ioctl field width behavior must remain compatible. Per-file cleanup can fail if counts desynchronize. Text parsing uses simple conversion helpers and fixed `LINE_SIZE`. Incorrect overflow hiding can expose invalid legacy data for ranges above representable sizes.

Test signals: `/proc/mtrr` read formatting, text add/delete/disable, all ioctl and compat ioctl commands, close-time cleanup of incremented entries, permission failure without `CAP_SYS_ADMIN`, invalid alignment/type parsing, and systems without MTRR returning open errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/legacy.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/legacy.c

Purpose: selects 32-bit legacy non-generic MTRR backends and registers syscore suspend/resume save/restore for those CPUs.

Important APIs/types/functions: exports `mtrr_set_if()` and `mtrr_register_syscore()`. Internal type `mtrr_value` stores one range's type, base, and size. Helpers `mtrr_save()` and `mtrr_restore()` implement syscore callbacks through `mtrr_syscore_ops`.

Control flow: `mtrr_set_if()` switches on `boot_cpu_data.x86_vendor` and feature bits, selecting `amd_mtrr_ops` for AMD K6, `centaur_mtrr_ops` for Centaur MCR, or `cyrix_mtrr_ops` for Cyrix ARR. `mtrr_register_syscore()` allocates a `num_var_ranges` save array and registers syscore callbacks. Suspend saves each backend range through `mtrr_if->get()`; resume restores non-empty ranges through `mtrr_if->set()`.

State and persistence: `mtrr_value` is heap state retained for suspend/resume. Hardware MTRR-like state is restored after resume; nothing is written to disk by this code.

Dependencies and integration points: built only for `CONFIG_X86_32`. Called from `mtrr_bp_init()` and `mtrr_init_finalize()` in `mtrr.c`. Depends on legacy backend ops and syscore infrastructure.

Risks: only legacy CPUs without generic MTRRs use this path, but allocation failure leaves save unable to proceed. Restore only writes ranges with nonzero size, so disabled slots remain whatever firmware/resume left unless backend reset behavior is acceptable. Backend selection must match CPU feature bits exactly.

Test signals: 32-bit AMD K6, Cyrix, and Centaur boot selection; suspend/resume preserving MTRR-like ranges; allocation failure handling; and builds where `CONFIG_X86_32` is disabled ensuring stubs from `mtrr.h` satisfy references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/mtrr.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/mtrr.c

Purpose: implements the common x86 MTRR management API. It initializes the active backend, tracks usage counts, synchronizes MTRR changes across CPUs, exposes driver-facing add/delete and write-combining helpers, and finalizes boot-time MTRR state.

Important APIs/types/functions: global state includes `num_var_ranges`, `mtrr_usage_table[]`, `mtrr_mutex`, `mtrr_if`, and `changed_by_mtrr_cleanup`. Public functions are `mtrr_add_page()`, `mtrr_add()`, `mtrr_del_page()`, `mtrr_del()`, `arch_phys_wc_add()`, `arch_phys_wc_del()`, `arch_phys_wc_index()`, `mtrr_bp_init()`, `mtrr_save_state()`, and initcall `mtrr_init_finalize()`. Helpers include `have_wrcomb()`, `init_table()`, `mtrr_rendezvous_handler()`, `types_compatible()`, and `set_mtrr()`.

Control flow: boot initializes reserved high physical bits, selects generic or legacy backend, reads variable range count, initializes usage counts, reads generic MTRR state, optionally runs cleanup, and builds the lookup map. Runtime add validates type/alignment/width, checks WC support, locks CPU hotplug and `mtrr_mutex`, reuses compatible overlapping regions or finds a free register, then updates all online CPUs through `stop_machine_cpuslocked()`. Delete decrements usage and disables the register at zero. Finalization copies the map to heap, emits inconsistent-state warnings, or registers legacy syscore restore.

State and persistence: usage counts are in `mtrr_usage_table[]`; backend hardware state is CPU MSRs or legacy registers; the effective map is owned by `generic.c`. MTRR changes persist only for the running boot. `arch_phys_wc_add()` returns offset handles to distinguish real MTRR indexes from no-op/PAT cases.

Dependencies and integration points: used by drivers and architecture memory-type code through exported MTRR and WC APIs. Depends on backend `mtrr_ops`, stop-machine, CPU hotplug locks, PCI chipset checks for WC errata, PAT state, E820 cleanup interactions, and syscore.

Risks: MTRR changes must be synchronized across CPUs with caches/TLBs handled by backend code. Overlap compatibility rules are subtle and can reject valid requests or allow harmful mixed types. Usage-count bugs can leak scarce registers or disable active mappings. PAT-enabled systems return success without MTRR changes, so callers must treat handles opaquely.

Test signals: boot with generic MTRRs enabled/disabled by BIOS, cleanup changed vs unchanged, driver `arch_phys_wc_add/del`, overlapping compatible and incompatible add requests, replacement of same-type enclosed regions, register exhaustion, CPU hotplug during add/delete, and `/proc/mtrr` count behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/mtrr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/mtrr.h -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/mtrr.h

Purpose: defines the private MTRR subsystem interface shared by generic, common, procfs, cleanup, and legacy backend files.

Important APIs/types/functions: defines change-mask bits `MTRR_CHANGE_MASK_FIXED`, `MTRR_CHANGE_MASK_VARIABLE`, and `MTRR_CHANGE_MASK_DEFTYPE`; debug macro `Dprintk`; `struct mtrr_ops`; and `struct set_mtrr_context`. Declares shared globals such as `mtrr_debug`, `mtrr_usage_table[]`, `mtrr_if`, `mtrr_mutex`, `num_var_ranges`, `mtrr_tom2`, `mtrr_state`, `phys_hi_rsvd`, and `changed_by_mtrr_cleanup`. Declares common helpers including `generic_get_free_region()`, `generic_validate_add_page()`, `fill_mtrr_var_range()`, `get_mtrr_state()`, `mtrr_state_warn()`, `mtrr_attrib_to_str()`, `mtrr_wrmsr()`, `mtrr_build_map()`, `mtrr_copy_map()`, `mtrr_cleanup()`, `generic_rebuild_map()`, and legacy backend ops.

Control flow: no runtime control flow beyond the inline `mtrr_enabled()`, which reports whether an active backend has been selected.

State and persistence: no state is owned here; it declares cross-file runtime state. No I/O or persistence behavior.

Dependencies and integration points: depends on `linux/types.h`, `linux/stddef.h`, MTRR constants from public asm headers, and `CONFIG_X86_32` for legacy backend declarations versus stubs. It is the local contract for every file in `arch/x86/kernel/cpu/mtrr/`.

Risks: changes to `struct mtrr_ops` affect all backends and common call sites. `mtrr_enabled()` only checks `mtrr_if`, so callers must still verify operation callbacks where needed. Conditional stubs must match the real function signatures to keep 64-bit builds correct.

Test signals: compile all x86 configurations, static analysis for all `mtrr_ops` initializers, 32-bit legacy backend symbol availability, and 64-bit stub coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/mtrr.h -->
