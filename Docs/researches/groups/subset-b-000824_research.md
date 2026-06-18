# Research: subset-b-000824

Grouped research for `subset-b-000824`. Each section preserves the source path in its title and is delimited so the reconciliation lane can split the report into the mapped source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/uvdevice.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/uvdevice.h

## Purpose
Defines the user ABI for the s390 Ultravisor character device `/dev/uv`. It describes the common ioctl control block, attestation argument layout, device capability query result, ioctl numbers, supported-call bit definitions, and intentionally generous maximum buffer sizes for attestation and secret-management requests.

## Important APIs, Types, And Functions
The central ABI type is `struct uvio_ioctl_cb`, an `_IOWR` wrapper carrying flags, returned Ultravisor rc/rrc values, a userspace argument pointer, and argument length. `struct uvio_attest` describes attestation input and output buffers. `struct uvio_uvdev_info` returns the device and Ultravisor support masks. `UVIO_IOCTL_*` macros encode the ioctl commands, while `UVIO_SUPP_*` exposes bit positions for capability reporting.

## Control Flow
This header has no executable control flow. Userspace issues one of the `UVIO_IOCTL_*` commands with a `uvio_ioctl_cb`; the kernel uvdevice driver validates the wrapper, copies the command-specific argument from `argument_addr`, executes the matching UV call when supported, and reports UV return information in `uv_rc` and `uv_rrc`.

## State And Persistence
No state is stored in the header. Runtime state lives in the uvdevice driver and firmware. The ABI is persistent because field sizes, ioctl numbers, and bit positions are user-visible and must remain stable.

## Dependencies And Integration Points
Depends on Linux UAPI integer types and ioctl encoding. It integrates userspace confidential-computing tools with the s390 Ultravisor, especially attestation and protected-secret workflows.

## Risks And Edge Cases
`UVIO_SUPP_UDEV_INFO` uses `UVIO_IOCTL_UDEV_INFO_NR`, while the enum spells `UVIO_IOCTL_UVDEV_INFO_NR`; this is a typo-like ABI risk unless hidden by another definition. Buffer limit changes are ABI-sensitive. User pointers are 64-bit integer fields, so compat handling and zeroed reserved bytes matter.

## Test Signals
Useful signals are UAPI compile tests, ioctl number stability checks, uvdevice selftests for unsupported commands, reserved-field rejection, oversized buffers, UV rc/rrc propagation, and attestation/secret commands on supported hardware or firmware simulators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/uvdevice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/virtio-ccw.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/virtio-ccw.h

## Purpose
Provides the small s390 virtio-ccw UAPI shared by KVM, guest kernels, and userspace tooling. It fixes the virtqueue ring alignment and the diagnose 0x500 subcode used to notify virtio-ccw devices.

## Important APIs, Types, And Functions
The exported constants are `KVM_VIRTIO_CCW_RING_ALIGN`, set to 4096 bytes, and `KVM_S390_VIRTIO_CCW_NOTIFY`, set to subcode 3. There are no functions or structs.

## Control Flow
There is no control flow. Guest or userspace virtio setup code allocates vrings with the required alignment and uses the notify subcode when issuing the s390 virtio diagnose hypercall.

## State And Persistence
No runtime state is owned here. The constants are persistent ABI and must not change without breaking existing guests or hypervisors.

## Dependencies And Integration Points
Integrates the virtio-ccw transport with KVM s390 diagnose 0x500 handling and vring layout assumptions. The permissive dual license supports both Linux and non-Linux consumers.

## Risks And Edge Cases
Changing alignment or subcode values would break device notification and shared-memory layout. Tests should also catch accidental include-guard or license regressions because this header is consumed outside the kernel tree.

## Test Signals
Signals include virtio-ccw guest boot, KVM unit tests for diagnose 0x500 notify, vring alignment assertions, and UAPI header install/build checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/virtio-ccw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/vmcp.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/vmcp.h

## Purpose
Defines the userspace ioctl ABI for the s390 z/VM CP command character device. The device lets userspace submit CP commands via diagnose code 8 and retrieve CP responses.

## Important APIs, Types, And Functions
The header exposes `VMCP_GETCODE`, `VMCP_SETBUF`, and `VMCP_GETSIZE`. These use ioctl type `0x10` and an `int` payload to get the CP response code, configure the response buffer size, and query the current response buffer size.

## Control Flow
This header has no executable logic. Userspace writes CP commands to the vmcp device, then uses these ioctls to control or inspect command response handling in the vmcp driver.

## State And Persistence
The header persists only ioctl numbers. Runtime state such as the last CP response code and buffer size belongs to the vmcp device instance.

## Dependencies And Integration Points
Depends on `<linux/ioctl.h>`. It integrates z/VM management tools with the kernel vmcp driver and the lower-level `cpcmd` diagnose 8 implementation.

## Risks And Edge Cases
The ABI is old and compact, so ioctl number reuse is the main risk. `int` payload sizing must remain compat-safe. Driver tests need to cover invalid buffer sizes and CP commands that return large or no responses.

## Test Signals
Signals include UAPI header compile checks, vmcp ioctl smoke tests under z/VM, response-code propagation, buffer resize behavior, and compat 32-bit userspace ioctl tests where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/vmcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/vtoc.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/vtoc.h

## Purpose
Defines packed user-visible layouts for s390 DASD volume labels and VTOC data set control blocks. These structures let DASD tooling and filesystems parse CKD/FBA labels, extents, free-space descriptors, and CMS labels exactly as stored on disk.

## Important APIs, Types, And Functions
Core address types are `vtoc_ttr`, `vtoc_cchhb`, and `vtoc_cchh`. Label structures include `vtoc_volume_label_cdl`, `vtoc_volume_label_ldl`, and `vtoc_cms_label`. VTOC DSCB layouts include `vtoc_format1_label`, `vtoc_format4_label`, `vtoc_format5_label`, and `vtoc_format7_label`, plus extent helper structs such as `vtoc_extent`, `vtoc_ds5ext`, and `vtoc_ds7ext`.

## Control Flow
No code executes here. DASD code reads raw label sectors or records, overlays these packed structures, and interprets fields such as volume IDs, VTOC addresses, data set extents, device constants, free extents, and CMS allocation metadata.

## State And Persistence
The structures mirror persistent on-disk state. Packing is critical because padding would corrupt interpretation. Many fields are EBCDIC strings or hardware-specific binary values rather than native Linux text.

## Dependencies And Integration Points
Depends on Linux UAPI integer types. Integrates with s390 DASD block drivers, partition parsing, label utilities, and any userspace code reading VTOC records through kernel-exported headers.

## Risks And Edge Cases
Risks are ABI layout drift, endian assumptions, EBCDIC text handling, and confusing CDL, LDL, and CMS label variants. The one-byte year fields and packed multi-byte device geometry values require careful parsing. Structure changes can break disk tools.

## Test Signals
Useful tests parse known DASD label images, verify `sizeof` and `offsetof` for every exported struct, run partition discovery on CDL/LDL/CMS examples, and check userspace header compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/vtoc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/zcrypt.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/zcrypt.h

## Purpose
Defines the s390 zcrypt userspace ABI for AP crypto adapters. It covers legacy ICA RSA requests, CCA CPRB passthrough, EP11 request blocks, device status matrices, autoselect constants, supported ioctl numbers, and deprecated compatibility commands.

## Important APIs, Types, And Functions
Important request structs are `ica_rsa_modexpo`, `ica_rsa_modexpo_crt`, `CPRBX`, `ica_xcRB`, `ep11_cprb`, `ep11_target_dev`, and `ep11_urb`. Device inventory uses `zcrypt_device_status_ext` and `zcrypt_device_matrix_ext`; deprecated variants remain for old callers. Ioctls include `ICARSAMODEXPO`, `ICARSACRT`, `ZSECSENDCPRB`, `ZSENDEP11CPRB`, `ZCRYPT_DEVICE_STATUS`, `ZCRYPT_STATUS_MASK`, `ZCRYPT_QDEPTH_MASK`, and `ZCRYPT_PERDEV_REQCNT`.

## Control Flow
The header defines the payloads passed to the zcrypt misc device. Userspace fills request structs with user pointers and lengths; the kernel zcrypt layer validates, copies, routes to AP queues/domains or autoselects targets, waits for adapter completion, then copies reply data and status back.

## State And Persistence
No code state is held here, but the ABI persists. Some request fields represent big-endian hardware control blocks, 16-byte padded pointer slots, or per-device counters exposed since adapter discovery.

## Dependencies And Integration Points
Depends on ioctl, compiler, and integer UAPI headers. Integrates libica, EP11/CCA userspace, AP bus drivers, zcrypt device nodes, sysfs status, and compatibility paths for old z90stat-style applications.

## Risks And Edge Cases
The highest risks are ABI layout and bitfield packing, user pointer validation, 32/64-bit compat behavior, AP/domain autoselect semantics, and preserving deprecated ioctl numbers. CPRB comments note big-endian shorts/ints and pointer padding, which are common sources of bad requests.

## Test Signals
Signals include UAPI `sizeof`/`offsetof` tests, libica/zcrypt ioctl selftests, AP queue emulation, CCA and EP11 passthrough tests, deprecated ioctl compatibility checks, large status matrix reads, and error-path tests for invalid user buffers and unsupported adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/zcrypt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/Makefile

## Purpose
Defines the Kbuild object selection and per-file compiler instrumentation policy for the s390 kernel directory. It wires core boot, entry, interrupt, diagnostic, tracing, crash, crypto, topology, kexec, and VDSO support into the architecture build.

## Important APIs, Types, And Functions
This file exports no C API. Important build variables are `obj-y`, `obj-$(CONFIG_*)`, `CFLAGS_REMOVE_*`, sanitizer/profiling toggles, `always-$(KBUILD_BUILTIN)`, and `CFLAGS_*` overrides.

## Control Flow
At build time, Kbuild evaluates s390 configuration symbols and appends the corresponding objects. Core objects such as `head.o`, `entry.o`, `debug.o`, `diag/`, `fpu.o`, and `abs_lowcore.o` are always linked. Optional objects are added for audit, early printk, kprobes, ftrace, crash dump, kexec, cert store, perf, BPF, and tracepoints.

## State And Persistence
No runtime state. It persists build policy: early code is excluded from ftrace, gcov, kcov, and UBSAN where instrumentation would be unsafe; stack tracing paths disable sibling-call optimization.

## Dependencies And Integration Points
Integrates s390 architecture code with Kconfig, Kbuild instrumentation, VDSO, perf, BPF, tracing, and the `diag/` subdirectory.

## Risks And Edge Cases
Wrong object selection can cause missing entry points or duplicate instrumentation in fragile boot paths. Ftrace or sanitizer instrumentation on early/entry code can break boot. Tail-call optimization on stack walkers can corrupt backtraces.

## Test Signals
Signals are broad s390 defconfig and randconfig builds, boot tests with tracing and sanitizers toggled, link map checks for `vmlinux.lds`, and feature-specific builds for kexec, crash dump, BPF, perf, and cert store.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/abs_lowcore.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/abs_lowcore.c

## Purpose
Maps and unmaps per-CPU lowcore pages into the absolute lowcore virtual area used by s390 control-register save and low-address access paths.

## Important APIs, Types, And Functions
`abs_lowcore_map(int cpu, struct lowcore *lc, bool alloc)` maps `LC_PAGES` of a CPU lowcore to `__abs_lowcore + cpu * sizeof(struct lowcore)`. `abs_lowcore_unmap(int cpu)` removes those mappings. The preserved boot datum `__abs_lowcore` provides the virtual base.

## Control Flow
Mapping iterates page by page, converting `lc` to physical addresses and calling `__vmem_map_4k_page`. If a map fails and allocation was allowed, already mapped pages are unwound. Unmap mirrors the same page loop with `vmem_unmap_4k_page`.

## State And Persistence
The persistent state is page-table mapping state for absolute lowcore aliases. The source lowcore memory belongs to per-CPU setup; this file only creates and removes virtual mappings.

## Dependencies And Integration Points
Depends on pgtable helpers, `struct lowcore`, `LC_PAGES`, `__pa`, and boot-preserved section data. It is used by control-register and lowcore access code that needs an absolute lowcore view.

## Risks And Edge Cases
The unwind path intentionally avoids unmapping when `alloc` is false because the caller may be in atomic context and unmap could sleep. CPU index arithmetic and lowcore size alignment must stay consistent with architecture layout.

## Test Signals
Signals include CPU hotplug tests, boot with multiple CPUs, failure injection for page-table allocation, lockdep sleep checks around atomic callers, and lowcore alias access validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/abs_lowcore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/alternative.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/alternative.c

## Purpose
Applies s390 runtime instruction alternatives based on CPU facilities, machine features, and speculation-control state. It patches kernel text after feature discovery so generic instruction sites can use faster or safer variants.

## Important APIs, Types, And Functions
`__apply_alternatives(struct alt_instr *start, struct alt_instr *end, unsigned int ctx)` is the main entry. `struct alt_debug` stores boot-preserved masks controlling debug dumps. `alternative_dump()` formats old and replacement bytes when debug bits are set.

## Control Flow
The function scans an `alt_instr` table in order, filters by context, decides whether replacement is active for `ALT_TYPE_FACILITY`, `ALT_TYPE_FEATURE`, or `ALT_TYPE_SPEC`, computes old and replacement instruction addresses from table-relative offsets, optionally logs the patch, and writes replacement bytes with `s390_kernel_write`.

## State And Persistence
Patching mutates live kernel text. Boot-preserved `machine_features` and `alt_debug` keep feature/debug state across early phases.

## Dependencies And Integration Points
Depends on alternative metadata, facility and machine-feature probes, no-spec branch state, text patching, absolute lowcore helpers, and boot sections. Entry assembly uses these alternatives heavily.

## Risks And Edge Cases
Scan order matters because later alternatives can overwrite earlier replacements. Incorrect instruction length, context masks, or feature tests can patch partial instructions. Text patching must synchronize with instruction fetch and respect early-boot address translation.

## Test Signals
Signals include boot tests across facility combinations, `debug-alternative` byte dumps, objtool/build checks of alternative records, runtime tests for no-spec toggles, and crash-free execution of entry paths using alternative macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/alternative.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/asm-offsets.c

## Purpose
Generates constants consumed by s390 assembly files. It emits offsets and sizes for `task_struct`, `thread_struct`, `pt_regs`, stack frames, lowcore, KVM SIE blocks, kexec metadata, boot parameter areas, ftrace registers, and per-CPU flags.

## Important APIs, Types, And Functions
The only function is `main()`, which uses Kbuild `OFFSET`, `DEFINE`, and `BLANK` macros. Important generated names include `__PT_*`, `__SF_*`, `__LC_*`, `__SIE_*`, `STACK_FRAME_OVERHEAD`, `__PARMAREA_SIZE`, and `__FTRACE_REGS_SIZE`.

## Control Flow
Kbuild compiles and runs this helper during the architecture build. Its output is post-processed into an assembly include file. The emitted constants track the C layout used by entry assembly and low-level boot code.

## State And Persistence
No runtime state. The generated offset header is a build artifact and must match the compiled kernel's structure layout exactly.

## Dependencies And Integration Points
Depends on scheduler, purgatory, page table, ftrace, KVM, stacktrace, ptrace, lowcore, and boot parameter definitions. It is tightly integrated with `entry.S`, `head.S`, kexec, ftrace, and crash dump code.

## Risks And Edge Cases
Missing an offset after a C layout change can silently break assembly. Conditional offsets, such as stack protector fields, must match Kconfig. Lowcore offsets are ABI-like for hardware and dump tooling.

## Test Signals
Signals include successful s390 builds, assembler failures when names are missing, boot tests, KVM SIE entry tests, ftrace tests, and static assertions around generated sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/audit.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/audit.c

## Purpose
Provides s390 syscall classification tables for Linux audit. It maps selected syscall numbers to audit classes and registers generic audit class arrays for read, write, directory-write, attribute-change, and signal operations.

## Important APIs, Types, And Functions
`audit_classify_arch()` returns 0 for architecture classification. `audit_classify_syscall(int abi, unsigned syscall)` maps `open`, `openat`, `socketcall`, `execve`, and `openat2` to special audit classes and returns `AUDITSC_NATIVE` otherwise. `audit_classes_init()` registers class arrays included from asm-generic headers.

## Control Flow
At initcall time, the class arrays are registered. During audit processing, the generic audit layer calls the classify functions for syscall events and uses the registered bitmaps to decide rule matching.

## State And Persistence
The registered class arrays become audit subsystem state for the lifetime of the kernel. There is no file persistence.

## Dependencies And Integration Points
Depends on Linux audit core, s390 syscall numbers, and asm-generic audit class include files. It integrates syscall entry reporting with architecture-neutral audit filtering.

## Risks And Edge Cases
New s390 syscall numbers may need class updates. `audit_classify_arch()` is trivial, so ABI distinctions must be handled elsewhere if they matter. `socketcall` exists for compatibility paths and must remain correctly classified.

## Test Signals
Signals include audit syscall filter tests for open/openat/openat2/execve/socketcall, build checks after syscall table changes, and audit rule matching on s390 systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/bpf.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/bpf.c

## Purpose
Exposes an s390 BPF kfunc that lets BPF programs obtain the current CPU's lowcore pointer.

## Important APIs, Types, And Functions
`bpf_get_lowcore()` is declared with `__bpf_kfunc` and returns `struct lowcore *` by calling `get_lowcore()`. The definitions are wrapped in `__bpf_kfunc_start_defs()` and `__bpf_kfunc_end_defs()`.

## Control Flow
When a verifier-approved BPF program calls this kfunc, the BPF runtime invokes the helper and receives the lowcore address for the executing CPU.

## State And Persistence
No state is stored here. The returned pointer exposes live per-CPU lowcore state, so verifier and BTF typing are the safety boundary.

## Dependencies And Integration Points
Depends on BTF kfunc registration infrastructure and the s390 lowcore API. It integrates BPF observability with architecture-specific CPU state.

## Risks And Edge Cases
The main risk is exposing sensitive or unstable lowcore fields to BPF programs. Correct BTF typing, verifier restrictions, and privilege policy are critical. CPU migration semantics should be considered by BPF callers.

## Test Signals
Signals include BPF selftests that load a program using `bpf_get_lowcore`, verifier rejection for unsafe field access, BTF availability checks, and runtime validation on SMP systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/cache.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/cache.c

## Purpose
Extracts s390 cache topology and attributes through ECAG and exposes them through generic Linux cacheinfo/sysfs and `/proc/cpuinfo` style output.

## Important APIs, Types, And Functions
`show_cacheinfo()` prints cache leaves. `init_cache_level()` determines level and leaf count. `populate_cache_leaves()` fills `struct cacheinfo` entries. Internal helpers include `get_cache_type()`, `ecag()`, and `ci_leaf_init()`. `union cache_topology` decodes per-level scope/type fields.

## Control Flow
Initialization reads ECAG topology once per CPU, counts cache levels until no valid cache appears, then populates each leaf with line size, associativity, size, set count, type, level, and shared/private state. Separate instruction/data cache levels produce two leaves.

## State And Persistence
State is stored in generic per-CPU `cpu_cacheinfo` structures. No persistent storage is used. Shared caches are marked with `disable_sysfs`, reflecting limited per-CPU ownership.

## Dependencies And Integration Points
Depends on `linux/cacheinfo.h`, CPU masks, seq files, and s390 facility ECAG. It integrates with generic cache sysfs and CPU reporting.

## Risks And Edge Cases
ECAG values must be nonzero and internally consistent or set-count division can misbehave. Cache levels above `CACHE_MAX_LEVEL` are ignored. Private/shared mapping affects sysfs visibility.

## Test Signals
Signals include cacheinfo sysfs inspection on multiple machine generations, CPU hotplug cache population, ECAG emulation tests, and sanity checks for line size, associativity, and number of sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/cert_store.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/cert_store.c

## Purpose
Implements s390 DIAG 0x320 certificate-store support. It queries firmware-provided verification certificates, validates them, imports valid certificates into a kernel keyring, and exposes refresh/status controls under `/sys/firmware/cert_store`.

## Important APIs, Types, And Functions
Firmware block layouts are `vcssb`, `vcb_header`, `vcb`, `vce_header`, and `vce`. `fill_cs_keyring()` orchestrates refresh. `query_diag320_subcodes()`, `get_vcssb()`, `get_sevcb()`, and `create_key_from_sevcb()` perform diagnose queries. `check_certificate_valid()` and `check_certificate_hash()` validate entries. Keyring helpers include `create_cs_keyring()`, `cleanup_cs_keys()`, and `create_key_from_vce()`. Sysfs handlers are `cs_status_show()` and `refresh_store()`.

## Control Flow
Device init registers debug features, creates the firmware sysfs directory, and registers the `cert_store_key` key type. A sysfs refresh locks `cs_refresh_lock`, retries `fill_cs_keyring()` on `-EAGAIN`, queries supported DIAG 320 subcodes, reads storage size metadata, creates a fresh `cert_store` keyring, iterates certificate indices, fetches one VCB per certificate, extracts and validates the VCE, then links the certificate payload as a restricted key.

## State And Persistence
Persistent runtime state is the keyring and its keys, `cs_status_val`, debug feature buffers, and firmware certificate-store token. Refresh first cleans old keys and keyring state. Certificates live as kernel keys until invalidated or refreshed.

## Dependencies And Integration Points
Depends on s390 DIAG 320, SCLP feature bits, EBCDIC conversion, SHA256, keyrings, sysfs firmware kobjects, vmalloc, and s390 debug feature. It integrates firmware certificate material with Linux key consumers.

## Risks And Edge Cases
Risks include firmware token mismatch, insufficient VCB buffer size, invalid hashes, EBCDIC descriptions, key type unregister on cleanup failure, and user-visible keyring cleanup races. Some debug hexdumps intentionally expose certificate bytes to s390dbf.

## Test Signals
Signals include DIAG 320 feature probing, sysfs refresh/status tests, keyring contents after refresh, invalid certificate/hash rejection, token mismatch retry, no-certificate behavior, and cleanup on repeated refreshes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/cert_store.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/cpacf.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/cpacf.c

## Purpose
Exposes raw s390 CP Assist for Cryptographic Function query masks and query-authentication-information blocks through CPU sysfs binary attributes.

## Important APIs, Types, And Functions
Macros `CPACF_QUERY()` and `CPACF_QAI()` generate read handlers and `BIN_ATTR_RO` objects for KM, KMC, KIMD, KLMD, KMAC, PCKMO, KMF, KMCTR, KMO, PCC, PRNO, KMA, and KDSA. `cpacf_init()` creates the `cpacf` binary attribute group under the CPU subsystem root.

## Control Flow
At device init, the CPU root kobject is looked up and a sysfs group is created. Each binary read executes the corresponding CPACF query or QAI instruction helper; unsupported instructions return `-EOPNOTSUPP`, supported ones copy the raw fixed-size result through `memory_read_from_buffer`.

## State And Persistence
No persistent state is owned. Data is queried on read, so sysfs output tracks current hardware/firmware capabilities.

## Dependencies And Integration Points
Depends on Linux sysfs, CPU subsystem devices, and `asm/cpacf.h`. It integrates hardware crypto capability discovery with userspace tools.

## Risks And Edge Cases
The raw binary ABI exposes instruction-specific masks, so size and naming are ABI-like. Unsupported facilities must fail cleanly. CPU root lookup failure silently skips group creation.

## Test Signals
Signals include sysfs presence under `/sys/devices/system/cpu/cpacf`, binary read length checks, unsupported instruction behavior, and comparison with CPACF facility bits on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/cpacf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/cpcmd.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/cpcmd.c

## Purpose
Implements in-kernel z/VM CP command execution through diagnose code 8. It converts commands and responses between ASCII and EBCDIC and serializes access to the shared low-address command buffer.

## Important APIs, Types, And Functions
`cpcmd()` is the exported SMP-safe API. `__cpcmd()` is exported but explicitly unlocked. Internal helpers are `diag8_noresponse()` and `diag8_response()`. Static state includes `cpcmd_lock` and `cpcmd_buf[241]`.

## Control Flow
`cpcmd()` optionally allocates a low buffer for vmalloc/module response destinations, takes the spinlock, and calls `__cpcmd()`. `__cpcmd()` validates command length with `BUG_ON`, copies and ASCII-to-EBCDIC converts the command, increments the DIAG 0x008 counter, issues diagnose 8 with or without a response buffer, converts response bytes back to ASCII, and returns response length while optionally storing the CP response code.

## State And Persistence
The shared static command buffer is transient protected state. No durable persistence is used, but CP commands can mutate z/VM control-program state outside Linux.

## Dependencies And Integration Points
Depends on diagnose accounting, physical address conversion, EBCDIC helpers, and low-level asm condition-code handling. It backs vmcp and other z/VM-aware kernel code.

## Risks And Edge Cases
Command length above 240 triggers `BUG_ON`, so callers must validate. The unlocked API is not SMP-safe. Response handling differs by condition code and must handle vmalloc destinations with bounce buffers.

## Test Signals
Signals include z/VM CP command smoke tests, no-response and response paths, EBCDIC round trips, vmalloc response buffer tests, and concurrency tests around `cpcmd_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/cpcmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/cpufeature.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/cpufeature.c

## Purpose
Implements s390's `cpu_have_feature()` predicate for module initialization and feature-gated code. It maps abstract Linux CPU feature IDs to ELF hwcap bits, facility bits, or machine-feature bits.

## Important APIs, Types, And Functions
`struct s390_cpu_feature` stores a feature type and number. `s390_cpu_features[]` maps `S390_CPU_FEATURE_MSA`, `VXRS`, `UV`, and `D288`. `cpu_have_feature(unsigned int num)` validates the index and dispatches to `elf_hwcap`, `test_facility()`, or `test_machine_feature()`.

## Control Flow
Callers pass a feature enum. The function warns on out-of-range IDs, then selects a backend based on the table entry type and returns a boolean capability result.

## State And Persistence
The static feature table is read-only runtime state. Actual capability state lives in global hwcap, facility, and machine-feature discovery data.

## Dependencies And Integration Points
Depends on cpufeature core, s390 ELF hwcap numbering, facility probing, and machine feature probing. It provides a generic feature API for loadable modules.

## Risks And Edge Cases
Table entries must be kept in sync with `MAX_CPU_FEATURES` and feature enum definitions. Unknown type values warn and return false. HWCAP and facility numbering mistakes silently misgate code.

## Test Signals
Signals include module tests for each feature, boot logs for WARN_ON paths under fault injection, and cross-checks against `/proc/cpuinfo` or facility data on systems with and without UV/VX/MSA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/cpufeature.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/crash_dump.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/crash_dump.c

## Purpose
Implements s390 crash dump support for kdump and zfcp/nvme dump environments. It copies old memory, remaps `/proc/vmcore`, builds ELF core headers, and records CPU register save areas.

## Important APIs, Types, And Functions
Save-area APIs are `save_area_alloc()`, `save_area_boot_cpu()`, `save_area_add_regs()`, and `save_area_add_vxrs()`. Old-memory APIs include `copy_oldmem_page()`, `copy_oldmem_kernel()`, and `remap_oldmem_pfn_range()`. ELF header APIs include `elfcorehdr_alloc()`, `elfcorehdr_free()`, `elfcorehdr_read()`, `elfcorehdr_read_notes()`, and optional `elfcorehdr_fill_device_ram_ptload_elf64()`.

## Control Flow
During crash kernel setup, CPU lowcore register state is copied into linked save areas. Old memory reads choose HSA copying for dump IPL or real-memory copying with kdump address swapping. `elfcorehdr_alloc()` validates dump mode, initializes oldmem ranges, counts memory/text headers, allocates an ELF buffer, emits `PT_NOTE` notes for process info, CPU regs, timers, control regs, prefix, vector regs, and vmcoreinfo, then emits `PT_LOAD` program headers for memory and optional old kernel text.

## State And Persistence
State includes `oldmem_region`, `oldmem_type`, `dump_save_areas`, and the allocated ELF header passed to vmcore. It represents previous-kernel memory and CPU state until freed.

## Dependencies And Integration Points
Depends on crash dump core, memblock, ELF, SCLP HSA access, old OS info, IPL type detection, lowcore layout, vector/FPU support, and `/proc/vmcore`.

## Risks And Edge Cases
Address swapping for crashkernel memory is subtle. zfcp/nvme HSA below `sclp.hsa_size` cannot be remapped and must be copied. ELF note sizing must match emitted data. Missing header allocation panics intentionally to allow alternate dump mechanisms.

## Test Signals
Signals include kdump boot, zfcp/nvme dump IPL, `/proc/vmcore` read and mmap tests, crash utility parsing, vector-register note presence when VX is available, and memory range correctness with KASLR old OS info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/crash_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/ctlreg.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/ctlreg.c

## Purpose
Coordinates system-wide s390 control-register updates and maintains a global save copy in absolute lowcore once initialized.

## Important APIs, Types, And Functions
Exports `system_ctlreg_lock()`, `system_ctlreg_unlock()`, and `system_ctlreg_modify()`. `system_ctlreg_init_save_area()` initializes control-register save areas. Internal `ctlreg_callback()` applies modifications on a CPU, and `system_ctlreg_update()` dispatches locally during early boot or with `on_each_cpu()` later.

## Control Flow
Callers request set-bit, clear-bit, or load operations. `system_ctlreg_modify()` builds `ctlreg_parms`, updates the absolute-lowcore saved register copy under `system_ctl_lock` if initialized, then applies the change on all CPUs. During early boot, interrupts are disabled and only the local CPU is updated.

## State And Persistence
Global state includes `system_ctl_lock`, `system_ctlreg_area_init`, and saved control-register values in absolute lowcore. Hardware control registers on every CPU are modified.

## Dependencies And Integration Points
Depends on lowcore, absolute lowcore mapping, local control-register load/store helpers, SMP callbacks, and irq state. Entry and early setup rely on these helpers for low-address protection and other control bits.

## Risks And Edge Cases
All-CPU synchronization is critical. Updating saved lowcore state without matching hardware registers can break restart and dump paths. Early-boot behavior must avoid unavailable SMP infrastructure.

## Test Signals
Signals include boot tests, CPU hotplug/control register consistency checks, low-address protection behavior, lockdep coverage, and fault injection around absolute lowcore mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/ctlreg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/debug.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/debug.c

## Purpose
Implements the s390 debug feature (s390dbf), a per-component ring-buffer logging facility exposed through debugfs views. It supports raw hex/ascii, sprintf formatting, level and page controls, flushing, snapshots, and critical/oops behavior.

## Important APIs, Types, And Functions
Public APIs include `debug_register_mode()`, `debug_register()`, `debug_register_static()`, `debug_unregister()`, `debug_register_view()`, `debug_unregister_view()`, `debug_set_level()`, `debug_stop_all()`, `debug_set_critical()`, `debug_event_common()`, `debug_exception_common()`, `__debug_sprintf_event()`, `__debug_sprintf_exception()`, `debug_dump()`, `debug_dflt_header_fn()`, and `debug_sprintf_format_fn()`. Key state is `debug_info_t`, `debug_view`, and per-open `file_private_info_t`.

## Control Flow
Postcore init creates `/sys/kernel/debug/s390dbf` and registers sysctls. Components register debug areas, which allocate multi-area page rings and create debugfs files for default and custom views. Writes append event or exception records under raw spinlock; exception records advance to the next area. Opens create snapshots so reads are consistent. Control views parse writes to change level, page count, or flush areas.

## State And Persistence
State is in memory ring buffers, debugfs dentries, sysctl flags, linked debug-area list, refcounts, and per-open snapshots. There is no durable persistence, but static debug info can preserve early events until dynamic registration copies them.

## Dependencies And Integration Points
Depends on debugfs, sysctl, raw spinlocks, refcounts, TOD clock, SMP CPU IDs, copy_to/from_user, and s390 debug headers. Many s390 drivers and firmware paths use this for diagnostics.

## Risks And Edge Cases
Buffer resizing copies existing events and must not race writers. Critical mode uses trylock to avoid deadlocks after CPU-stop scenarios. `sprintf` view stores format pointers and long arguments, so callers must use stable format strings and compatible argument widths.

## Test Signals
Signals include debugfs read/write tests for all default views, concurrent logging and resize, static debug registration, oops path `debug_stop_all()`, critical mode behavior, and component users such as cert_store debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/diag/Makefile -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/diag/Makefile

## Purpose
Selects the object files for the s390 diagnose support subdirectory.

## Important APIs, Types, And Functions
No C API is defined. The single Kbuild assignment links `diag_misc.o`, `diag324.o`, `diag.o`, and `diag310.o` into the parent `diag/` object list.

## Control Flow
At build time, Kbuild compiles the listed objects in order. This pulls in the `/dev/diag` misc device, DIAG 324 power-information ioctls, generic diagnose wrappers/statistics, and DIAG 310 memory-topology ioctls.

## State And Persistence
No runtime state is owned by the Makefile. Runtime state is in the selected C objects.

## Dependencies And Integration Points
Integrates the subdirectory with `arch/s390/kernel/Makefile`, which includes `obj-y += diag/`.

## Risks And Edge Cases
Removing an object breaks exported diagnose helpers or ioctl dispatch. Order changes are low risk but can affect link diagnostics and initcall placement visibility.

## Test Signals
Signals include s390 build/link success, `/dev/diag` registration, and feature-specific DIAG 310/324 tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/diag/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/diag/diag.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/diag/diag.c

## Purpose
Provides common s390 diagnose instruction wrappers, per-CPU diagnose usage statistics, tracepoint integration, and AMODE31 operation pointers.

## Important APIs, Types, And Functions
Exports `diag_stat_inc()`, `diag_stat_inc_norecursion()`, `diag0c()`, `diag14()`, `diag204()`, and `diag210()`. `diag_map[]` maps statistic IDs to diagnose codes and names. `diag_amode31_ops` holds AMODE31 callable implementations. Debugfs `diag_stat` exposes per-CPU counters.

## Control Flow
Device init creates a read-only debugfs sequence file. Diagnose wrappers increment stats and tracepoints before issuing architecture-specific diagnose calls. `diag14()` translates virtual buffer addresses for subcodes that require it. `diag204()` validates vmalloc/page alignment, translates STIB4 addresses to physical page frame addresses, issues DIAG 204, and maps busy/unsupported return codes to errno. `diag210()` serializes access to a temporary AMODE31 buffer.

## State And Persistence
State includes per-CPU `diag_stat` counters and static AMODE31 temporary buffers for DIAG 210/8C paths. No persistent storage is used.

## Dependencies And Integration Points
Depends on debugfs, seq_file, tracepoints, AMODE31 sections, exception tables, vmalloc address helpers, and diagnose asm. It is shared by cpcmd, cert_store, diag310, diag324, and virtualization support.

## Risks And Edge Cases
Some diagnose calls require real/physical addresses, page alignment, or AMODE31 buffers. Incorrect translation can corrupt memory or fail silently. Statistic increments must avoid recursion in trace-sensitive contexts.

## Test Signals
Signals include debugfs `diag_stat` output, tracepoint events, DIAG 204 busy/unsupported tests, DIAG 210 serialization, and z/VM or LPAR feature smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/diag/diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/diag/diag310.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/diag/diag310.c

## Purpose
Implements `/dev/diag` ioctl support for DIAG 0x310 memory topology information. It queries supported subcodes, stride length, topology map sizes by nesting level, and copies topology maps to userspace.

## Important APIs, Types, And Functions
Externally used ioctl handlers are `diag310_memtop_stride()`, `diag310_memtop_len()`, and `diag310_memtop_buf()`. Internal helpers include `diag310()`, `diag310_get_subcode_mask()`, `diag310_get_memtop_stride()`, `diag310_get_memtop_size()`, `diag310_store_topology_map()`, `diag310_check_features()`, `memtop_get_stride_len()`, and `memtop_get_page_count()`.

## Control Flow
Each ioctl checks SCLP/DIAG 310 feature availability and required subcodes. Stride and page counts are lazily cached. `diag310_memtop_len()` receives a nesting level through the same userspace word it later overwrites with byte length. `diag310_memtop_buf()` reads level and target userspace address, allocates page-aligned vmalloc memory, requests subcode 5 to fill the topology map, then copies the buffer to userspace.

## State And Persistence
Static caches store feature availability, stride, and page counts per level. They persist until reboot. No filesystem persistence is used.

## Dependencies And Integration Points
Depends on SCLP capability bits, DIAG 310 return-code format, vmalloc, UAPI `struct diag310_memtop`, and `/dev/diag` dispatch in `diag_misc.c`.

## Risks And Edge Cases
Level bounds are 1 through 6. Cached sizes may become stale if firmware topology characteristics change after boot. Large page-count responses can create large allocations. User address is carried as a `u64`, requiring careful compat behavior.

## Test Signals
Signals include `/dev/diag` ioctl tests for stride, length, and buffer reads, unsupported subcode paths, invalid level handling, `-ENODATA` and `-EOVERFLOW` paths, and topology-map format validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/diag/diag310.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/diag/diag324.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/diag/diag324.c

## Purpose
Implements `/dev/diag` ioctl support for DIAG 0x324 power information blocks. It discovers PIB availability and length, periodically refreshes readings, caches the last block, and copies it to userspace with a sequence number.

## Important APIs, Types, And Functions
Public ioctl handlers are `diag324_piblen()` and `diag324_pibbuf()`. Internal state is `struct pibdata` containing a PIB pointer, expiry time, sequence, length, and last rc. Helpers include `diag324()`, `pib_update()`, `pibwork_handler()`, and `diag324_init()`.

## Control Flow
Init checks SCLP support, queries installed subcodes, verifies subcodes 1 and 2, and records PIB length. `diag324_pibbuf()` allocates a cached PIB if needed, refreshes it on first use or after expiry, updates sequence/expiry from the firmware interval, schedules delayed cleanup, then copies the PIB and sequence to userspace. A delayed work item frees the cached PIB after it remains expired for an additional delay.

## State And Persistence
State is protected by `pibmutex` and stored in global `pibdata`. The PIB cache is volatile and freed when idle. Sequence increments on refresh.

## Dependencies And Integration Points
Depends on SCLP feature bits, DIAG 324 response formats, vmalloc, delayed work, TOD-to-ns conversion, UAPI `diag324_pib`, and `/dev/diag`.

## Risks And Edge Cases
PIB length is a 16-bit firmware value stored as bytes; invalid or zero length disables support. `-EBUSY` still allows copying the previous PIB. Copy length uses `data->pib->len`, so firmware-filled length must be sane within allocated size.

## Test Signals
Signals include ioctl tests for unsupported systems, PIB length, buffer copy, sequence increments, busy return handling, delayed cache cleanup, and firmware interval expiry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/diag/diag324.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/diag/diag_ioctl.h -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/diag/diag_ioctl.h

## Purpose
Declares internal ioctl handler prototypes shared by the s390 `/dev/diag` dispatcher and its DIAG 310/324 implementation files.

## Important APIs, Types, And Functions
The header declares `diag324_pibbuf()`, `diag324_piblen()`, `diag310_memtop_stride()`, `diag310_memtop_len()`, and `diag310_memtop_buf()`.

## Control Flow
No control flow exists. `diag_misc.c` includes this header and calls the declared functions from its ioctl switch.

## State And Persistence
No state is defined. Runtime state is owned by `diag310.c` and `diag324.c`.

## Dependencies And Integration Points
Depends only on Linux integer types. It integrates the private diag subdirectory modules without exposing these functions as public UAPI.

## Risks And Edge Cases
Prototype drift between dispatcher and implementation would cause build failures or, if types changed incorrectly, ioctl argument handling bugs. The use of `unsigned long arg` matches ioctl dispatch conventions.

## Test Signals
Signals are compile/link success and `/dev/diag` ioctl dispatch tests covering every declared handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/diag/diag_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/diag/diag_misc.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/diag/diag_misc.c

## Purpose
Registers the s390 `/dev/diag` misc device and dispatches supported diagnose-related ioctls to DIAG 310 and DIAG 324 handlers.

## Important APIs, Types, And Functions
`diag_ioctl()` switches on `DIAG324_GET_PIBLEN`, `DIAG324_GET_PIBBUF`, `DIAG310_GET_STRIDE`, `DIAG310_GET_MEMTOPLEN`, and `DIAG310_GET_MEMTOPBUF`. `diag_init()` registers `diagdev`, a read-only mode misc device with `nonseekable_open` and `.unlocked_ioctl`.

## Control Flow
At device init, the misc device is registered with a dynamic minor. Userspace opens `/dev/diag` and issues ioctls. Unknown commands return `-ENOIOCTLCMD`; known commands forward the raw unsigned long argument to the implementation handler.

## State And Persistence
This file owns only the miscdevice registration state. Per-feature state is in the DIAG 310/324 files.

## Dependencies And Integration Points
Depends on miscdevice, ioctl UAPI definitions from `<uapi/asm/diag.h>`, and internal handler prototypes. It is the user-visible entry point for diagnose information.

## Risks And Edge Cases
The device mode is `0444`, but ioctl operations still copy data to userspace, so access policy depends on device node permissions and ioctl validation. Missing compat handling may matter for 32-bit userspace if structures carry 64-bit address fields.

## Test Signals
Signals include `/dev/diag` node creation, open/nonseekable behavior, valid and invalid ioctl results, permission checks, and compat ioctl coverage where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/diag/diag_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/dis.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/dis.c

## Purpose
Provides an in-kernel s390 instruction disassembler used for fault dumps, register dumps, and printing function code. It decodes opcodes, instruction formats, operands, and PC-relative targets.

## Important APIs, Types, And Functions
Public functions are `find_insn()`, `show_code()`, and `print_fn_code()`. Internal data includes `struct s390_operand`, `struct s390_insn`, opcode tables generated by `OPCODE_TABLE_INITIALIZER`, format tables, and `opcode_offset[]`. Helpers include `extract_operand()`, `print_insn()`, and `copy_from_regs()`.

## Control Flow
`find_insn()` uses the first opcode byte to locate an offset table entry, extracts an opcode fragment, and searches matching instruction records. `show_code()` snapshots bytes around the PSW address from user or kernel memory, finds a plausible instruction boundary, then prints up to eight disassembled instructions with markers around the faulting instruction. `print_fn_code()` linearly decodes a supplied kernel function byte range.

## State And Persistence
Opcode and format tables are static read-mostly state. No mutable persistent state is held.

## Dependencies And Integration Points
Depends on s390 opcode tables from asm headers, ptrace regs, uaccess/no-fault copying, kallsyms formatting, and dumpstack paths. It integrates with `show_registers()` and oops diagnostics.

## Risks And Edge Cases
Instruction boundary recovery is heuristic. Bad PSW addresses, inaccessible user memory, vector register extension bits, long displacement encodings, and sign extension are fragile. Unknown opcodes print as unknown rather than faulting.

## Test Signals
Signals include disassembly tests for representative instruction formats, oops output inspection, user-mode fault dumps, vector instruction decoding, PC-relative target printing, and unknown/truncated instruction handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/dis.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/dumpstack.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/dumpstack.c

## Purpose
Implements s390 stack identification, call-trace printing, register dumping, and fatal oops handling.

## Important APIs, Types, And Functions
Exports `stack_type_name()`, `get_stack_info()`, `show_stack()`, `show_registers()`, `show_regs()`, and `die()`. Internal helpers classify task, irq, nodat, mcck, and restart stacks and print the last breaking-event address.

## Control Flow
Stack classification validates alignment, checks task stack first, then current CPU special stacks, and uses a visit mask to prevent recursive stack walking. Register dumping prints PSW bits, GPRs, disassembled code, optional stack trace, and last breaking-event address. `die()` enters oops handling, stops debug logging, serializes output, notifies die notifiers, prints modules and regs, taints the kernel, and either panics or kills the task.

## State And Persistence
State includes `die_lock` and a static `die_counter`. It reads per-CPU lowcore stack pointers and task stack state. No durable persistence exists.

## Dependencies And Integration Points
Depends on unwind, debug feature, lowcore, disassembler, IPL logging, lockdep, notifier die chain, module printing, and scheduler task death.

## Risks And Edge Cases
Incorrect stack classification can produce misleading traces or loops. Oops path locking must avoid deadlocks. PSW rewind/forward handling must match exception state. Fatal interrupt oops and `panic_on_oops` change termination path.

## Test Signals
Signals include induced kernel oops output, stack unwinder reliability flags, special-stack exception tests, lockdep held-lock output, and panic-on-oops behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/dumpstack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/early.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/early.c

## Purpose
Performs early s390 architecture initialization before the generic kernel start. It handles decompressor-consumed command-line parameters, early KASAN, storage keys, lowcore setup, hardware description, topology probing, SCLP detection, and early exception handling.

## Important APIs, Types, And Functions
`startup_init()` is the main entry from `head.S`. `__do_early_pgm_check()` handles early program checks. Other helpers include `kasan_early_init()`, `init_kernel_storage_key()`, `setup_arch_string()`, `setup_topology()`, `setup_lowcore_early()`, `save_vector_registers()`, `setup_low_address_protection()`, `setup_access_registers()`, `setup_boot_command_line()`, and `sort_amode31_extable()`.

## Control Flow
Early params already processed by the decompressor are registered as ignored. `startup_init()` initializes KASAN/time/storage keys, disables lockdep, sorts AMODE31 exception tables, sets early lowcore PSWs and return-LPSWE instructions, derives machine/hypervisor strings from STSI, copies the boot command line, saves vector registers for crash dump, probes topology, detects SCLP features, enables low-address protection, initializes access registers, and re-enables lockdep.

## State And Persistence
State includes `early_command_line`, `arch_hw_string`, lowcore early PSWs, topology maximum nesting, storage keys, and boot CPU vector save area for crash dump.

## Dependencies And Integration Points
Depends on STSI, SCLP, lowcore, control registers, boot data, extable sorting, KASAN, FPU/vector helpers, and `entry.h` early handler symbols.

## Risks And Edge Cases
This code runs before normal kernel services are fully available. Early exceptions must use early console and disabled wait. Instrumentation is disabled in the Makefile because tracing/sanitizers here can break boot.

## Test Signals
Signals include early boot on LPAR/z/VM/KVM, earlyprintk panic diagnostics, storage-key configurations, topology reporting, decompressor param handling, and crash dump vector-save validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/early.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/early_printk.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/early_printk.c

## Purpose
Registers an early SCLP console for s390 boot diagnostics before the normal console stack is available.

## Important APIs, Types, And Functions
`register_early_console()` installs `sclp_early_console` if SCLP line-mode or VT220 output is available. `setup_early_printk()` handles the `earlyprintk` early parameter. `sclp_early_write()` forwards console writes to `__sclp_early_printk()`.

## Control Flow
The early parameter accepts bare `earlyprintk` or `earlyprintk=sclp`. Registration is skipped if an early console already exists or if SCLP output facilities are absent. Once registered, console writes are routed to SCLP early output.

## State And Persistence
Uses the global `early_console` pointer. The boot console is temporary and marked `CON_BOOT`; normal console registration later replaces it.

## Dependencies And Integration Points
Depends on console core, s390 setup globals, and SCLP early print support. It is used by early exception handling in `early.c`.

## Risks And Edge Cases
Registration before SCLP feature detection will fail if flags are not available yet. Non-sclp parameter values are ignored. Early console output must avoid dependencies on normal memory allocation.

## Test Signals
Signals include boot with `earlyprintk`, early exception output, SCLP line-mode and VT220 environments, and absence of duplicate early consoles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/early_printk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/ebcdic.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/ebcdic.c

## Purpose
Provides exported lookup tables for ASCII/EBCDIC conversion and EBCDIC case folding on s390. These tables support firmware, z/VM, DASD, and certificate-store paths that exchange EBCDIC text.

## Important APIs, Types, And Functions
Exports `_ascebc`, `_ebcasc`, `_ascebc_500`, `_ebcasc_500`, `_ebc_tolower`, and `_ebc_toupper`. The first pair maps ASCII IBM PC 437 to/from EBCDIC 037; the second pair maps to/from EBCDIC 500. Case tables map EBCDIC upper/lower bytes.

## Control Flow
No functions execute in this file. Inline/macros from `asm/ebcdic.h` index these arrays to convert buffers in place or byte by byte.

## State And Persistence
The conversion tables are global exported data and read-only by convention. No runtime state changes.

## Dependencies And Integration Points
Depends on Linux integer/export support and `asm/ebcdic.h`. Used by cpcmd, early machine strings, cert_store, DASD label tools, and other s390 firmware interfaces.

## Risks And Edge Cases
The tables encode codepage-specific behavior. Unsupported high ASCII bytes often map to `0x3f`, losing information. Case folding only makes sense for EBCDIC bytes and should not be applied to ASCII text.

## Test Signals
Signals include round-trip conversion tests for known strings, CP 037 vs CP 500 punctuation differences, cpcmd response conversion, certificate-name display, and exported symbol availability for modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/ebcdic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/entry.S -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/entry.S

## Purpose
Implements core s390 low-level entry and exit paths: context switch assembly, KVM SIE entry/exit, syscall entry, program checks, external and I/O interrupts, machine checks, restart interrupts, early program checks, invalid-stack panic setup, and branch-prediction isolation toggles.

## Important APIs, Types, And Functions
Global symbols include `__switch_to_asm`, `__WARN_trap`, `__sie64a`, `sie_exit`, `system_call`, `ret_from_fork`, `pgm_check_handler`, `ext_int_handler`, `io_int_handler`, `mcck_int_handler`, `restart_int_handler`, `early_pgm_check_handler`, and `stack_invalid`. Macros include `STBEAR`, `LBEAR`, `LPSWEY`, `MBEAR`, `CHECK_VMAP_STACK`, `TSTMSK`, `BPOFF`, `BPON`, `BPENTER`, `BPEXIT`, and `SIEEXIT`.

## Control Flow
Entry paths save volatile state into lowcore or stack frames, switch to the correct task or per-CPU stack, sanitize user-controlled registers for speculation safety, build `pt_regs`, call C handlers, restore PSWs/registers, and exit through lowcore LPSWE sequences. KVM SIE saves host state, loads guest registers/asce, enters SIE, handles exits and machine-check races, then restores host state. Machine-check handling validates available state, may stop all CPUs on severe damage, or calls `s390_do_machine_check`.

## State And Persistence
Mutates lowcore save areas, current task pointers, stack frames, SIE flags, per-CPU control flags, branch-prediction state, and machine-check stop-lock data. No filesystem persistence.

## Dependencies And Integration Points
Depends on generated asm offsets, lowcore layout, alternative patching, nospec branch support, KVM SIE block layout, stack protector, irq/trap C handlers, restart infrastructure, and ftrace/kprobes section placement.

## Risks And Edge Cases
This is one of the highest-risk files. Stack selection, PSW bits, SIE race windows, machine-check validity masks, branch-prediction isolation, VMAP stack validation, and speculation register clearing must be exact. A wrong offset or alternative patch can prevent boot.

## Test Signals
Signals include boot, syscall stress, signal return, interrupts, KVM guest tests, machine-check injection, restart IPI paths, ftrace/kprobe interactions, VMAP stack fault tests, and objdump/ORC-style inspection of generated entry code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/entry.h -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/entry.h

## Purpose
Declares internal s390 entry, trap, syscall, interrupt, restart, AMODE31, stack, and architecture syscall interfaces shared between assembly and C files.

## Important APIs, Types, And Functions
Declares assembly symbols such as `system_call`, interrupt handlers, `early_pgm_check_handler`, and `__switch_to_asm`; C handlers such as `__do_pgm_check`, `__do_syscall`, `do_ext_irq`, `do_io_irq`, and `die`; architecture syscalls such as `sys_s390_guarded_storage`, `sys_s390_runtime_instr`, and PCI MMIO helpers; stack allocation helpers; and AMODE31 section symbols. It defines `__amode31_data` and `__amode31_ref`.

## Control Flow
No executable flow. It provides prototypes so entry assembly and C code agree on call targets and calling conventions.

## State And Persistence
No state is owned. It declares external symbols that refer to runtime stacks, AMODE31 ranges, and entry points.

## Dependencies And Integration Points
Depends on percpu, signal, ptrace, idle, extable, and s390 type headers. It connects `entry.S`, trap handling, guarded storage, signal handling, AMODE31 diagnose code, and syscall implementations.

## Risks And Edge Cases
Prototype drift can create subtle ABI bugs between assembly and C. AMODE31 section annotations must remain correct so references are placed in the expected sections.

## Test Signals
Signals include full s390 build with warnings enabled, boot of entry paths, syscall tests, AMODE31 diagnose users, and link-time symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/entry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/facility.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/facility.c

## Purpose
Provides a cached helper for determining how many facility-list doublewords the current machine reports through STFL(E).

## Important APIs, Types, And Functions
`stfle_size()` calls `__stfle_asm(&dummy, 1) + 1` on first use, stores the result in a static `size`, and exports the function.

## Control Flow
Callers read the cached size with `READ_ONCE`. If zero, the function executes the STFL(E) helper with a dummy one-doubleword buffer, converts the returned last-doubleword index to a count, writes it with `WRITE_ONCE`, and returns it.

## State And Persistence
The static `size` cache persists for the boot lifetime. There is no external persistence.

## Dependencies And Integration Points
Depends on `asm/facility.h` and export infrastructure. Used by code sizing facility masks or presenting facility information.

## Risks And Edge Cases
Concurrent first calls can repeat the same query, which is benign. The helper assumes facility-list size is stable after boot. The dummy buffer is only for the query return convention.

## Test Signals
Signals include facility-list reporting on different machine generations, module calls to `stfle_size()`, and comparison with actual facility bits exposed elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/facility.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/fpu.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/fpu.c

## Purpose
Implements s390 in-kernel FPU/vector save and restore helpers. It lets kernel code temporarily use floating point or vector registers while preserving task state according to requested register masks.

## Important APIs, Types, And Functions
Exports `__kernel_fpu_begin()`, `__kernel_fpu_end()`, and `save_fpu_state()`. Also provides `load_fpu_state()`. These operate on `struct kernel_fpu` or `struct fpu` and flags such as `KERNEL_FPC`, `KERNEL_VXR`, `KERNEL_VXR_LOW`, `KERNEL_VXR_HIGH`, and subranges like `KERNEL_VXR_V0V7`.

## Control Flow
Begin/save paths mask requested flags by state mask, save FPC when requested, then choose legacy FP save/load helpers on systems without vector facility or vector load/store multiple instructions for full, mid, low, high, and subrange register sets. End/load paths mirror the same mask decisions to restore saved state.

## State And Persistence
State is copied between hardware FPC/vector registers and caller-provided memory. No global state is owned.

## Dependencies And Integration Points
Depends on CPU vector facility detection and low-level FPU instruction wrappers. Used by crypto, checksum, and other kernel code that uses vector registers.

## Risks And Edge Cases
Incorrect masks can clobber user or kernel FPU state. Legacy non-VX machines only preserve low FP-compatible registers. FPC safe loading is used for task state to avoid invalid-control faults.

## Test Signals
Signals include kernel vector selftests, crypto tests using kernel FPU regions, context-switch stress with user vector workloads, non-VX build/runtime coverage, and invalid FPC restore tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/ftrace.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/ftrace.c

## Purpose
Implements the s390 dynamic ftrace backend. It patches compiler-generated function-entry instructions, manages hotpatch trampolines on machines without sequential-instruction support, updates the active ftrace function, supports graph tracing, and integrates kprobes-on-ftrace.

## Important APIs, Types, And Functions
Important functions include `ftrace_need_init_nop()`, `ftrace_init_nop()`, `ftrace_modify_call()`, `ftrace_make_nop()`, `ftrace_make_call()`, `ftrace_update_ftrace_func()`, `arch_ftrace_update_code()`, `ftrace_arch_code_modify_post_process()`, optional `ftrace_graph_func()`, `kprobe_ftrace_handler()`, and `arch_prepare_kprobe_ftrace()`. State includes global `ftrace_func` and hotpatch trampoline ranges from `ftrace.h`.

## Control Flow
For CPUs with sequential instruction support, calls/nops are patched by replacing a six-byte branch instruction at the recorded function IP. Without it, `ftrace_init_nop()` allocates a per-site trampoline, writes a shared trampoline branch and target metadata, then changes only the branch displacement or mask. Code modification verifies expected old bytes before patching and synchronizes instruction fetch after updates. Graph tracing rewrites the saved return address to `return_to_handler`. Kprobe ftrace handler emulates probe pre/post handlers using ftrace regs.

## State And Persistence
Patches live kernel/module text and trampoline slots. `ftrace_func` is read-mostly global state. Module architecture data tracks trampoline allocation.

## Dependencies And Integration Points
Depends on ftrace core, module metadata, text patching, cache synchronization, nospec expoline state, kprobes, KMSAN unpoisoning, and generated ftrace register offsets.

## Risks And Edge Cases
Instruction alignment, expected-byte verification, displacement range, trampoline exhaustion, module lifetime, expoline selection, and concurrent text patching are all sensitive. Wrong return-address handling breaks graph tracing.

## Test Signals
Signals include ftrace selftests, function graph tracer tests, kprobes-on-ftrace tests, module tracing, CPUs with and without seq-insn support, expoline toggles, and text patch failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/ftrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/ftrace.h -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/ftrace.h

## Purpose
Defines the s390 ftrace hotpatch trampoline layout and linker-provided trampoline symbols used by `ftrace.c`.

## Important APIs, Types, And Functions
`struct ftrace_hotpatch_trampoline` contains a `brasl` opcode/disp pair, padding, the address of the rest of the intercepted function, and the interceptor address. Externs identify vmlinux trampoline ranges and shared branch/exrl trampoline code ranges.

## Control Flow
No code executes. `ftrace.c` writes instances of this packed structure and branches through the shared trampoline code to reach the selected ftrace interceptor.

## State And Persistence
Trampoline memory becomes live executable patch state. The packed layout must match linker script and assembly expectations.

## Dependencies And Integration Points
Depends on s390 integer types and ftrace linker symbols. Integrates with module architecture trampoline allocation and `asm/ftrace.lds.h` size checks.

## Risks And Edge Cases
Any layout change must update size constants and generated code. Branch displacement calculations assume field offsets and instruction sizes. Packed alignment is part of the runtime ABI between C and assembly.

## Test Signals
Signals include `BUILD_BUG_ON` size checks, ftrace initialization, module ftrace tests, and disassembly of generated trampolines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/ftrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/guarded_storage.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/guarded_storage.c

## Purpose
Implements the s390 guarded-storage syscall, per-task guarded-storage control block management, and broadcast loading of guarded-storage control blocks across threads.

## Important APIs, Types, And Functions
Exports `guarded_storage_release()` and `gs_load_bc_cb()`. The syscall is `sys_s390_guarded_storage(command, struct gs_cb __user *)`. Internal commands are handled by `gs_enable()`, `gs_disable()`, `gs_set_bc_cb()`, `gs_clear_bc_cb()`, and `gs_broadcast()`.

## Control Flow
The syscall first checks `cpu_has_gs()`, then dispatches command IDs. Enabling allocates a zeroed control block, sets default `gsd`, disables preemption, sets CR2 guarded-storage bit, loads the control block, and stores it in the current thread. Broadcast control blocks are copied from userspace into `thread.gs_bc_cb`. `gs_broadcast()` scans sibling threads, sets `TIF_GUARDED_STORAGE`, and kicks them. On return-to-user handling, `gs_load_bc_cb()` swaps the pending broadcast block into active state and loads it.

## State And Persistence
Per-task state lives in `thread.gs_cb` and `thread.gs_bc_cb`; CR2 guarded-storage bit is per-CPU hardware state while active. Release frees both blocks.

## Dependencies And Integration Points
Depends on guarded-storage instruction helpers, syscall dispatch, tasklist locking, thread flags, signal/return-to-user path, and control-register helpers.

## Risks And Edge Cases
Preemption is disabled around hardware state changes to bind control-register and load operations to the current CPU. Broadcast races with thread exit and repeated pending blocks require careful freeing. User copy failures leave allocated pending blocks intact.

## Test Signals
Signals include guarded-storage syscall tests for every command, unsupported CPU behavior, multithread broadcast delivery, context-switch preservation, thread exit cleanup, and invalid userspace pointer handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/guarded_storage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/head.S -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/head.S

## Purpose
Provides the post-decompressor s390 kernel entry continuation. It sets up the initial task and kernel stack in lowcore, enables early SCLP address adjustment, runs s390 early initialization, and enters the generic kernel.

## Important APIs, Types, And Functions
Defines `startup_continue` in the `__HEAD` section and local data `dw_psw`, a disabled-wait PSW used if `start_kernel()` ever returns.

## Control Flow
`startup_continue` obtains lowcore, stores `init_task` as current, stores the initial stack pointer from `init_thread_union + STACK_INIT_OFFSET`, calls `sclp_early_adjust_va`, calls `startup_init`, then calls `start_kernel`. If control returns, it loads `dw_psw` to enter disabled wait.

## State And Persistence
Initializes lowcore `current_task` and `kernel_stack` fields. No file persistence. The disabled-wait PSW is static boot data.

## Dependencies And Integration Points
Depends on lowcore offsets, init task symbols, SCLP early setup, `startup_init()` from `early.c`, and generic `start_kernel()`. It is the bridge from architecture boot code to common kernel init.

## Risks And Edge Cases
Wrong lowcore offsets or stack pointer setup prevents boot immediately. Returning from `start_kernel()` is treated as fatal. This code must remain free of unsafe instrumentation.

## Test Signals
Signals include successful early boot, initial stack/current task correctness, early SCLP output availability, and disabled-wait behavior only on catastrophic return from `start_kernel()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/head.S -->
