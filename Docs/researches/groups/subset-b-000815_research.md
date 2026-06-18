# subset-b-000815 research

Grouped research for the RISC-V kernel files in `sources/distributed-fs/ceph-client/arch/riscv/kernel`. Each source file has a delimited section for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/cacheinfo.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/cacheinfo.c

Purpose: Provides RISC-V cacheinfo population and private cache attribute plumbing for Linux sysfs cache descriptions.

Important APIs/types/functions: `riscv_set_cacheinfo_ops()`, `cache_get_priv_group()`, `get_cache_size()`, `get_cache_geometry()`, `init_cache_level()`, `populate_cache_leaves()`, and the optional `struct riscv_cacheinfo_ops` provider.

Control flow: Boot or CPU bringup calls generic cacheinfo setup, then `populate_cache_leaves()` fills leaves from ACPI cache descriptors or walks DT CPU/cache nodes. Runtime helpers look up the current CPU cache leaf by level/type and return size or encoded geometry. Private sysfs groups are delegated to registered RISC-V cache ops.

State and persistence: Persistent state is the global `rv_cache_ops` pointer and per-CPU `cpu_cacheinfo` leaves owned by generic cacheinfo. No storage is written to disk.

Dependencies and integration points: Depends on ACPI cache info, OF cache nodes, Linux cacheinfo, and RISC-V vendor/platform code that may register private cache attributes.

Risks and test signals: The current-CPU lookup assumes homogeneous cache topology for the UABI. Bad DT cache-level ordering, missing ACPI split-level data, or stale private ops can expose wrong sysfs cache data. Test with DT and ACPI RISC-V boots, `lscpu`/sysfs cache inspection, hotplug cacheinfo initialization, and vendor cache private attribute coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/cacheinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/cfi.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/cfi.c

Purpose: Decodes and reports Clang kernel CFI trap failures on RISC-V so indirect-call type violations produce useful diagnostics.

Important APIs/types/functions: `handle_cfi_failure()` is the public trap hook. `decode_cfi_insn()` inspects the compiler-generated `beq` and following `jalr` or compressed `c.jalr` sequence, using RISC-V instruction helpers and `pt_regs`.

Control flow: A breakpoint trap first checks `is_cfi_trap(regs->epc)`. If it is not a CFI trap, the handler returns none. If it is, the code reads nearby kernel instructions with `get_kernel_nofault()`, extracts the expected type from the `beq` source register and the indirect target from the `jalr` source register, then calls the generic CFI reporter.

State and persistence: No persistent state is maintained. It consumes register state from the trap frame and nearby text.

Dependencies and integration points: Integrated with generic `linux/cfi.h`, RISC-V instruction decoders in `asm/insn.h`, breakpoint/trap handling, and bug reporting.

Risks and test signals: The decoder is tightly coupled to the compiler CFI sequence and register extraction layout; compiler codegen changes can degrade reports to no-address failures. Test with Clang CFI enabled, injected bad indirect calls, compressed and normal `jalr` sequences, and fault-injection around invalid text reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/cfi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_signal.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_signal.c

Purpose: Implements 32-bit compat signal frame setup and return for 64-bit RISC-V kernels running compat tasks.

Important APIs/types/functions: Defines `compat_sigcontext`, `compat_ucontext`, `compat_rt_sigframe`, and implements compat register save/restore, floating-point state movement, `compat_setup_rt_frame()`, and `compat_sys_rt_sigreturn()`.

Control flow: Signal delivery builds a compat rt frame on the user signal stack, copies siginfo/ucontext, saves integer and FP state, installs the handler PC, stack pointer, return address, and VDSO `rt_sigreturn` trampoline. `compat_sys_rt_sigreturn()` validates and copies the frame back, restores signal mask, register state, FP state, and returns through the normal syscall restart path.

State and persistence: State exists in the user-space signal frame and transient kernel `pt_regs`. Signal masks and alternate stack metadata persist in task signal state according to generic signal rules.

Dependencies and integration points: Depends on compat ABI structs, `asm/signal32.h`, RISC-V `pt_regs`, VDSO trampoline offsets, user access helpers, and generic Linux signal delivery.

Risks and test signals: ABI layout is user visible. Incorrect padding, stack alignment, FP restore, or trampoline address selection breaks 32-bit processes. Test with compat signal delivery, nested signals, alternate stacks, FP-heavy handlers, `sigreturn` fuzzing, and 32-bit userspace on RV64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_syscall_table.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_syscall_table.c

Purpose: Builds the compat syscall dispatch table for 32-bit user ABI tasks on a 64-bit RISC-V kernel.

Important APIs/types/functions: Defines `__SYSCALL()` table entries through generated syscall headers and exports `compat_sys_call_table[]` as an aligned array of compat syscall entry pointers.

Control flow: The syscall entry path indexes this table for compat tasks after syscall number validation. Most control flow is generated by included syscall definitions rather than handwritten logic in this file.

State and persistence: The table is read-only kernel data after initialization and has no dynamic state.

Dependencies and integration points: Depends on generated `asm/syscall_table_32.h`, generic compat syscall implementations, and RISC-V syscall entry code.

Risks and test signals: Table ordering and size are ABI critical. Generated header drift, missing compat wrappers, or wrong alignment can dispatch the wrong syscall. Test with 32-bit syscall ABI smoke tests, syscall number boundary tests, and build coverage after syscall table regeneration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_syscall_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/Makefile

Purpose: Describes how the 32-bit compat VDSO image is assembled, linked, stripped, and converted into kernel objects.

Important APIs/types/functions: Defines compat VDSO object lists, linker script preprocessing, `compat_vdso.so.dbg`, generated `compat_vdso.so`, offset header generation with `gen_compat_vdso_offsets.sh`, and flags such as `-mabi=ilp32`, `-march=rv32g`, no relaxation, no stack protector, and hidden visibility.

Control flow: Kbuild compiles the compat VDSO assembly/C objects, links them with `compat_vdso.lds`, strips debug-only output into a deployable image, embeds the image through `compat_vdso.S`, and generates offsets for kernel mapping code.

State and persistence: Build artifacts persist in the object tree; runtime state is the mapped compat VDSO image in each process.

Dependencies and integration points: Integrates RISC-V VDSO sources, generated offsets, objcopy, linker support for rv32 ABI, and compat signal/syscall code that references VDSO symbols.

Risks and test signals: Toolchain flags are fragile: relaxation, wrong ABI, or wrong link script can make the image unmappable or ABI-incompatible. Test with rv64 kernels enabling compat, VDSO symbol inspection, `gettimeofday`/`getcpu`/`rt_sigreturn` compat tests, and build coverage across GCC/Clang.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/compat_vdso.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/compat_vdso.S

Purpose: Embeds the built compat VDSO shared object bytes into the kernel image.

Important APIs/types/functions: Defines linker-visible symbols around the included `compat_vdso.so` binary blob, normally consumed by VDSO mapping code.

Control flow: There is no runtime branching in this wrapper. The assembler emits a section containing the binary image; later kernel code maps those bytes into compat user processes.

State and persistence: The VDSO image is persistent read-only kernel data after boot and is mapped into user address spaces on demand.

Dependencies and integration points: Depends on the compat VDSO Makefile producing the binary, linker script symbols, and RISC-V VDSO loader code.

Risks and test signals: A missing or stale embedded blob breaks compat VDSO mappings. Test by checking exported blob symbols, VDSO ELF headers in compat processes, and fallback behavior when user code calls VDSO helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/compat_vdso.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/compat_vdso.lds.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/compat_vdso.lds.S

Purpose: Provides the compat VDSO linker script by selecting the 32-bit VDSO symbol namespace and reusing the common RISC-V VDSO linker layout.

Important APIs/types/functions: Defines `VDSO_32BIT` and includes the generic `vdso/vdso.lds.S`.

Control flow: The linker script controls ELF sections, dynamic symbols, versioning, and exported VDSO entry placement at build time; there is no runtime control flow.

State and persistence: Produces immutable layout metadata and sections inside `compat_vdso.so`.

Dependencies and integration points: Depends on common RISC-V VDSO linker script logic and the compat VDSO build.

Risks and test signals: Layout mistakes affect symbol versioning and user ABI. Test with `readelf` on `compat_vdso.so.dbg`, symbol version checks, and compat VDSO runtime calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/compat_vdso.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/flush_icache.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/flush_icache.S

Purpose: Builds the compat VDSO `flush_icache` entry by reusing the common RISC-V VDSO implementation in 32-bit mode.

Important APIs/types/functions: Defines `VDSO_32BIT` and includes `../vdso/flush_icache.S`.

Control flow: Runtime behavior is inherited from the common VDSO assembly: user code enters the VDSO symbol and issues the appropriate syscall or helper sequence for instruction-cache synchronization.

State and persistence: No private state; it is part of the mapped compat VDSO image.

Dependencies and integration points: Depends on common VDSO assembly, compat VDSO linking, and user-space cache flush ABI.

Risks and test signals: ABI register width and syscall number handling must match compat expectations. Test with compat JIT/self-modifying code paths that call `__riscv_flush_icache`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/flush_icache.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/gen_compat_vdso_offsets.sh -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/gen_compat_vdso_offsets.sh

Purpose: Generates C preprocessor definitions for compat VDSO symbol offsets from the linked debug VDSO image.

Important APIs/types/functions: Invokes the common `vdso/gen_vdso_offsets.sh` script with a `compat_` prefix.

Control flow: During the build, Kbuild runs this shell script against `compat_vdso.so.dbg`; the common script extracts selected symbols and emits offset definitions used by kernel C code.

State and persistence: The generated header persists in the build tree and tracks the linked VDSO image layout.

Dependencies and integration points: Depends on shell, the common VDSO offset generator, objdump/readelf tooling used by that generator, and compat VDSO mapping code.

Risks and test signals: Prefix or symbol extraction errors cause kernel code to reference wrong offsets. Test by rebuilding after VDSO symbol changes and comparing generated offsets against `readelf -s`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/gen_compat_vdso_offsets.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/getcpu.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/getcpu.S

Purpose: Provides the compat VDSO `getcpu` entry by compiling the common RISC-V VDSO implementation for the 32-bit ABI.

Important APIs/types/functions: Defines `VDSO_32BIT` and includes `../vdso/getcpu.S`.

Control flow: Runtime control flow is inherited from the common VDSO implementation and returns CPU/NUMA information according to the compat calling convention.

State and persistence: Uses VDSO/VVAR data mapped into the process; this wrapper has no independent mutable state.

Dependencies and integration points: Depends on common VDSO `getcpu`, compat VDSO layout, and generic scheduler/VVAR data provisioning.

Risks and test signals: Register size, pointer width, and VVAR layout must be compat-correct. Test with 32-bit `getcpu()` loops under migration and CPU hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/getcpu.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/note.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/note.S

Purpose: Emits the compat VDSO ELF note section by reusing the common RISC-V VDSO note source.

Important APIs/types/functions: Defines `VDSO_32BIT` and includes `../vdso/note.S`.

Control flow: This is build-time data emission only. Runtime consumers inspect ELF notes for metadata such as Linux/VDSO identity.

State and persistence: The note section persists inside the compat VDSO ELF image.

Dependencies and integration points: Depends on common VDSO note definitions and ELF tooling.

Risks and test signals: Incorrect notes can confuse debuggers, loaders, or diagnostics. Test with `readelf -n` on the compat VDSO image and mapped process VDSO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/note.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/rt_sigreturn.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/rt_sigreturn.S

Purpose: Provides the compat VDSO `rt_sigreturn` trampoline by compiling the common RISC-V VDSO signal-return source for the 32-bit ABI.

Important APIs/types/functions: Defines `VDSO_32BIT` and includes `../vdso/rt_sigreturn.S`.

Control flow: Signal setup points the user return address at this VDSO entry. When user handlers return, the entry issues the compat `rt_sigreturn` syscall, which is handled by compat signal restoration code.

State and persistence: No private state; it is executable code mapped in compat tasks.

Dependencies and integration points: Integrates with `compat_signal.c`, compat syscall numbers, and VDSO mapping.

Risks and test signals: Wrong syscall number or ABI mode prevents all compat signal handlers from returning correctly. Test with signal delivery, nested signals, alternate signal stacks, and seccomp/audit visibility of `rt_sigreturn`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/rt_sigreturn.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/copy-unaligned.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/copy-unaligned.S

Purpose: Implements scalar RISC-V helpers for unaligned copy operations used by misaligned access handling and copy benchmarks.

Important APIs/types/functions: Defines `__riscv_copy_words_unaligned` and `__riscv_copy_bytes_unaligned`.

Control flow: The word helper copies full machine words in a loop using unaligned load/store sequences, then falls through to byte copying for the tail. The byte helper copies remaining bytes one at a time until the requested count is consumed.

State and persistence: No persistent state. It mutates only caller-provided source/destination memory and clobbers scratch registers per the assembly ABI.

Dependencies and integration points: Depends on RISC-V assembler macros and is declared by `copy-unaligned.h`; it may be selected against vector copy alternatives by unaligned access code.

Risks and test signals: Overlap semantics, count handling, and tail copying must match callers. Test with randomized unaligned source/destination offsets, small sizes, word-boundary tails, KASAN/KMSAN, and platforms with strict misaligned access traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/copy-unaligned.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/copy-unaligned.h -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/copy-unaligned.h

Purpose: Declares the RISC-V scalar and optional vector unaligned copy assembly entry points.

Important APIs/types/functions: Declares `__riscv_copy_words_unaligned`, `__riscv_copy_bytes_unaligned`, and, under vector support, `__riscv_copy_vec_words_unaligned` and `__riscv_copy_vec_bytes_unaligned`.

Control flow: This header has no runtime control flow. It supplies prototypes used by C code to select scalar or vector copy helpers.

State and persistence: No state is stored here.

Dependencies and integration points: Integrates `copy-unaligned.S`, vector copy assembly, and RISC-V unaligned access performance/handling code.

Risks and test signals: Prototype mismatches with assembly calling conventions can corrupt copies or registers. Test through the unaligned copy users with scalar-only and vector-enabled configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/copy-unaligned.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/cpu-hotplug.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/cpu-hotplug.c

Purpose: Supplies RISC-V CPU hotplug callbacks for bringing harts down and parking them safely.

Important APIs/types/functions: Implements `arch_cpu_idle_dead()`, `__cpu_disable()`, `cpu_die()`, and related stop/park paths using SBI HSM or platform CPU operations.

Control flow: CPU-down preparation disables interrupts, marks the CPU offline, migrates per-CPU work through generic hotplug, and asks firmware or spinwait code to stop the hart. The dying CPU enters an idle-dead path and does not return unless a platform cannot truly power it off.

State and persistence: Updates CPU online/offline masks and relies on per-hart firmware state. No persistent storage beyond kernel CPU state.

Dependencies and integration points: Depends on generic CPU hotplug, RISC-V SMP, `cpu_ops`, SBI HSM when available, IRQ state, and scheduler CPU teardown.

Risks and test signals: Hotplug races can leave interrupts targeted at offline CPUs or park a CPU with stale stack/task pointers. Test repeated online/offline cycles, CPU0 restrictions, SBI and spinwait boot modes, lockdep, and interrupt affinity after hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/cpu-hotplug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/cpu.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/cpu.c

Purpose: Reports RISC-V CPU identity, ISA, MMU, vendor, and cache information through cpuinfo and procfs-style interfaces.

Important APIs/types/functions: Handles CPU feature string formatting, `cpuinfo` population, `show_cpuinfo()`, ISA extension printing, vendor/arch/implementation IDs, and cache block size reporting.

Control flow: During boot, architecture code records per-hart ISA and identity data. When userspace reads `/proc/cpuinfo`, this file iterates online CPUs, formats base ISA and extension strings, prints vendor and MMU information, and exposes cache block parameters when available.

State and persistence: Reads persistent in-kernel per-CPU identity state, global ISA bitmaps, hardware probe data, and DT/ACPI-derived properties. It does not own long-lived mutable state itself.

Dependencies and integration points: Depends on `cpufeature.c`, DT/ACPI CPU descriptions, SBI/CSR identity reads, cache block globals, seq_file, and procfs CPU reporting.

Risks and test signals: Output is userspace-visible and relied on by diagnostics. Heterogeneous harts, vendor extensions, and deprecated ISA strings can produce misleading output. Test `/proc/cpuinfo` on DT and ACPI systems, heterogeneous simulated harts, vendor extension builds, and compat userspace parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/cpu_ops.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/cpu_ops.c

Purpose: Selects the CPU bringup operations implementation used for secondary harts.

Important APIs/types/functions: Provides `cpu_ops[]`/selection logic around available `struct cpu_operations` implementations such as SBI HSM and spinwait.

Control flow: Early SMP setup chooses a CPU operations backend based on firmware/device-tree compatibility and build configuration. Later CPU start/stop calls go through the selected backend.

State and persistence: Stores selected CPU operation pointers used for the lifetime of the booted kernel.

Dependencies and integration points: Integrates with `cpu_ops_sbi.c`, `cpu_ops_spinwait.c`, SMP boot, hotplug, device tree CPU enable methods, and SBI availability.

Risks and test signals: Wrong backend selection can prevent secondary CPUs from starting or stopping. Test boot on SBI HSM systems, legacy spinwait systems, bad enable-method DT nodes, and CPU hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/cpu_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/cpu_ops_sbi.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/cpu_ops_sbi.c

Purpose: Implements CPU start/stop operations using the SBI Hart State Management extension.

Important APIs/types/functions: Defines `cpu_ops_sbi`, SBI start/stop helpers, boot-data setup for stack/task pointers, and hart status checks.

Control flow: For CPU start, the kernel fills secondary boot data, translates the start address to a physical address as required, and calls `sbi_hsm_hart_start()`. For stop, the dying CPU invokes `sbi_hsm_hart_stop()` and parks if firmware returns unexpectedly.

State and persistence: Uses per-hart boot data shared with early assembly and persistent firmware hart state managed by SBI.

Dependencies and integration points: Depends on SBI HSM, SMP secondary entry in `head.S`, CPU hotplug, physical address helpers, and boot CPU/hart ID mapping.

Risks and test signals: Firmware status handling, physical address conversion, and boot-data lifetime are critical. Test with OpenSBI HSM, hotplug loops, failed hart-start injection, non-linear CPU-to-hart mappings, and suspend/resume interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/cpu_ops_sbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/cpu_ops_spinwait.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/cpu_ops_spinwait.c

Purpose: Implements legacy spinwait secondary CPU boot for systems without SBI HSM.

Important APIs/types/functions: Defines `cpu_ops_spinwait`, `__cpu_spinwait_stack_pointer[]`, `__cpu_spinwait_task_pointer[]`, and `spinwait_cpu_start()`.

Control flow: Boot CPU writes the idle task and stack pointer into per-CPU arrays, then the secondary hart spinning in `head.S` observes nonzero values, fences, and enters the common secondary start path.

State and persistence: Persistent boot arrays in `.data` coordinate one-time secondary bringup and later hotplug-like starts where supported.

Dependencies and integration points: Tied to `CONFIG_RISCV_BOOT_SPINWAIT`, `head.S` spinwait loops, SMP setup, and CPU hotplug expectations.

Risks and test signals: Missing ordering or stale pointers can boot a hart on the wrong stack or task. Test legacy DT boot paths, high hart IDs, multiple secondary starts, and memory-ordering stress under emulators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/cpu_ops_spinwait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/cpufeature.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/cpufeature.c

Purpose: Central RISC-V ISA discovery, validation, feature bitmap construction, ELF HWCAP exposure, user ISA enablement, vendor extension aggregation, and alternative patch application.

Important APIs/types/functions: Exports `riscv_isa_extension_base()`, `__riscv_isa_extension_available()`, `riscv_fill_hwcap()`, `riscv_get_elf_hwcap()`, `riscv_user_isa_enable()`, `riscv_cpufeature_patch_func()`, global `elf_hwcap`, `riscv_isa`, `hart_isa[]`, and `riscv_isa_ext[]` with validation callbacks for F/D, vector, crypto, CFI, cache-block, compressed, and supervisor extensions.

Control flow: Boot parses either DT `riscv,isa-extensions`, deprecated `riscv,isa`, or ACPI RHCT ISA strings. It resolves dependencies iteratively, disables unsupported extensions by kernel config or missing properties, intersects per-hart bitmaps into host-wide capabilities, applies vendor extension aggregation, runs T-Head vector/ghostwrite handling, initializes vector size, then prints base ISA and ELF HWCAPs. Later alternative patching scans `alt_entry` records and patches text when a standard or vendor extension is available.

State and persistence: Maintains global and per-hart ISA bitmaps, `elf_hwcap`, cache-block availability flags, `thead_vlenb_of`, and command-line fallback state. `riscv_user_isa_enable()` writes current thread `envcfg` bits for cache-block user access.

Dependencies and integration points: Integrates with DT, ACPI RHCT, SBI/CSR identity, vector setup, vendor extension lists, alternative patching, text patching, user CFI command-line policy, hwprobe, `/proc/cpuinfo`, and ELF aux vector HWCAP.

Risks and test signals: This file is boot- and ABI-critical. Dependency resolution, heterogeneous harts, deprecated ISA fallback, duplicate or malformed extension entries, and alternative patching can expose unsupported instructions or hide real features. Test DT and ACPI boots, extension dependency matrices, F-without-D, vector/no-vector configs, CFI disable flags, cache block size validation, vendor extension alternatives, and ELF HWCAP regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/cpufeature.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/crash_dump.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/crash_dump.c

Purpose: Provides old-memory page copying for RISC-V crash dump kernels.

Important APIs/types/functions: Implements `copy_oldmem_page()` using `memremap()`, `copy_to_iter()`, and `memunmap()`.

Control flow: Kdump readers request a physical page frame, offset, and byte count. The function maps the old kernel page as write-back memory, copies the requested range into an iterator, unmaps, and returns copied bytes or an error.

State and persistence: No persistent state; it transiently maps old physical memory.

Dependencies and integration points: Integrated with generic crash dump/proc vmcore code, `iov_iter`, and memory remapping.

Risks and test signals: Incorrect bounds or remap attributes can read wrong crash memory or fail vmcore extraction. Test kdump boot, `/proc/vmcore` reads at page offsets, zero-length reads, and invalid PFN error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/crash_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/crash_save_regs.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/crash_save_regs.S

Purpose: Saves RISC-V register state into a `pt_regs`-layout buffer during crash handling.

Important APIs/types/functions: Defines `riscv_crash_save_regs`.

Control flow: The assembly stores all integer registers and selected CSRs (`status`, `tval`, `cause`) into offsets from `a0`; it synthesizes `epc` from the current PC using `auipc`.

State and persistence: Writes a crash-time `pt_regs` snapshot consumed by kdump/vmcore tooling.

Dependencies and integration points: Depends on `asm-offsets.h` register offsets, CSR definitions, and crash/kexec paths.

Risks and test signals: The function overwrites the saved `a0` field after using `a0` as the destination base, so offset correctness and calling convention are critical. Test kdump register notes, crash-triggered vmcore analysis, and 32/64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/crash_save_regs.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/efi-header.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/efi-header.S

Purpose: Emits the PE/COFF header needed for booting the RISC-V kernel as a UEFI application.

Important APIs/types/functions: Defines the `__EFI_PE_HEADER` macro, COFF header fields, optional header fields, `.text` and `.data` section table entries, and RISC-V machine type selection.

Control flow: Build-time assembly only; `head.S` includes the macro when `CONFIG_EFI` is enabled so firmware recognizes the image and jumps to the EFI stub entry.

State and persistence: Produces immutable image header bytes at the start of the kernel image.

Dependencies and integration points: Depends on PE constants, EFI stub symbols, linker-provided section bounds, and RISC-V image header layout.

Risks and test signals: Header size, alignment, section virtual/raw sizes, or entry point mistakes can make firmware reject the kernel. Test UEFI boot on RV32/RV64, Clang/GCC data size paths, PE inspection, and secure-boot tooling compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/efi-header.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/efi.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/efi.c

Purpose: Creates and protects RISC-V EFI runtime service mappings with architecture-specific page attributes.

Important APIs/types/functions: Implements `efimem_to_pgprot_map()`, `efi_create_mapping()`, and `efi_set_mapping_permissions()`.

Control flow: EFI memory descriptors are translated into RISC-V page protections, runtime mappings are installed page by page with global-bit clearing, and later permission updates walk PTEs to apply RO/XN policy from EFI attributes.

State and persistence: Mutates EFI runtime page tables for the life of the kernel. No file-local persistent state.

Dependencies and integration points: Depends on generic EFI runtime services, RISC-V page-table helpers, memory descriptor attributes, and early boot EFI setup.

Risks and test signals: Incorrect executable/read-only handling can break runtime services or weaken W+X protections. Test EFI variable/runtime calls, mixed RO/XP descriptors, MMIO descriptors, page table attribute inspection, and boot under UEFI firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/efi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/entry.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/entry.S

Purpose: Implements the RISC-V trap/interrupt entry and return path, fork return assembly, IRQ stack switch, context switch, and exception vector table.

Important APIs/types/functions: Defines `handle_exception`, `ret_from_exception`, optional `handle_kernel_stack_overflow`, `ret_from_fork_kernel_asm`, `ret_from_fork_user_asm`, `call_on_irq_stack`, `__switch_to`, `excp_vect_table`, and no-MMU `__user_rt_sigreturn`.

Control flow: Trap entry swaps `tp` with scratch to distinguish user/kernel origin, handles new vmalloc retry/fence checks on kernel page faults, saves all registers and CSRs into `pt_regs`, disables SUM/FP/vector/ELP state, saves user shadow stack state when CFI is enabled, then dispatches interrupts to `do_irq` or exceptions through `excp_vect_table`. Return restores state, handles user work via C code before reentry when applicable, clears load reservations with an SC, restores CSRs/registers, and executes `sret` or `mret`.

State and persistence: Maintains per-task kernel/user stack pointers, scratch CSR, shadow call stack pointers, optional user SSP, per-CPU IRQ stack, and callee-saved thread context.

Dependencies and integration points: Tied to `pt_regs` offsets, trap C handlers, scheduler `__switch_to`, VMAP stack overflow handling, vector preemption hooks, shadow call stack, user CFI, alternatives, and syscall/signal paths.

Risks and test signals: Any register, CSR, stack, or alternate patch bug corrupts execution globally. Test syscall/interrupt/trap stress, page faults after vmalloc, VMAP stack overflow, FP/vector illegal-use detection, context switch torture, IRQ stacks, KASAN/stackleak, and user CFI shadow stack transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/fpu.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/fpu.S

Purpose: Saves/restores RISC-V floating-point state and provides debugger/register access helpers for FP registers.

Important APIs/types/functions: Defines `__fstate_save`, `__fstate_restore`, `put_f32_reg`, `get_f32_reg`, `put_f64_reg`, `get_f64_reg`, plus access prologue/epilogue macros.

Control flow: Save/restore routines enable FP access as needed, move all FP registers and `fcsr` to or from task storage, then restore status bits. Get/put helpers temporarily enable FP state and move one register between memory and hardware.

State and persistence: Persists user FP state in task `__riscv_d_ext_state` storage and manipulates `sstatus.FS`/`fcsr`.

Dependencies and integration points: Used by switch-to, signal, ptrace, KGDB, and kernel FP wrappers; depends on F/D extension availability and `asm-offsets`.

Risks and test signals: Lazy FP state, fcsr preservation, and register width handling are ABI-visible. Test FP context switching, signal save/restore, ptrace register reads/writes, preemption around kernel FP use, and RV32/RV64 builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/fpu.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/ftrace.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/ftrace.c

Purpose: Implements RISC-V dynamic ftrace text patching, call-site management, direct-call ops encoding, and function graph return setup.

Important APIs/types/functions: Provides `ftrace_arch_code_modify_prepare/post_process`, `ftrace_call_adjust`, `arch_ftrace_get_symaddr`, `arch_ftrace_update_code`, `ftrace_make_call`, `ftrace_make_nop`, `ftrace_init_nop`, `ftrace_update_ftrace_func`, `ftrace_modify_call`, `prepare_ftrace_return`, and `ftrace_graph_func`.

Control flow: Ftrace transitions patch `auipc/jalr` call pairs or NOPs under text modification guards. Runtime ftrace caller assembly dispatches through the selected function pointer, and graph tracing rewrites return addresses through `prepare_ftrace_return()`.

State and persistence: Persistent state lives in ftrace records, patched kernel/module text, and optional encoded ops stored at call sites for direct-call support.

Dependencies and integration points: Depends on RISC-V instruction encoding helpers, `patch_text`, ftrace core, module text, graph tracer, and `mcount*.S`.

Risks and test signals: Text patching must be atomic enough for live CPUs and must preserve call-site reachability. Test dynamic ftrace enable/disable, function graph tracing, module tracing, direct ftrace ops, concurrent tracing toggles, and instruction decode validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/ftrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/head.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/head.S

Purpose: Contains the RISC-V kernel image header, primary boot entry, MMU relocation, secondary CPU entry, M-mode setup, and register sanitization.

Important APIs/types/functions: Defines `_start`, `_start_kernel`, `relocate_enable_mmu`, `secondary_start_sbi`, spinwait secondary path, `.Lsetup_trap_vector`, `.Lsecondary_park`, and M-mode `reset_regs`.

Control flow: Firmware enters `_start`, whose image header advertises load offset, size, flags, magic, and optional EFI PE header. `_start_kernel` masks interrupts, configures M-mode PMP or S-mode counters, clears BSS, records boot hart, sets initial stack/task, calls `setup_vm`, enables MMU with trampoline and final page tables, installs trap vector, enables user CFI firmware feature if available, initializes early sanitizer hooks, and tails into `start_kernel`. Secondary harts enter through SBI or spinwait, load boot stack/task, enable MMU, install trap vector, and call `smp_callin`.

State and persistence: Sets boot CPU hart ID, initial thread stack/task state, SATP, TVEC, PMP, counter enable CSRs, scratch CSR, shadow call stack state, and spinwait boot arrays.

Dependencies and integration points: Depends on linker image symbols, `efi-header.S`, page-table setup, `head.h` helper prototypes, SBI firmware, SMP, user CFI FWFT, SCS, KASAN, and RISC-V boot protocol.

Risks and test signals: Boot header ABI, SATP relocation, BSS clearing, hart lottery, and firmware feature locking are early-fatal if wrong. Test U-Boot/EFI/OpenSBI boot, M-mode and S-mode configs, no-MMU/MMU variants, SMP spinwait and SBI paths, KASLR page-table setup, and early trap park diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/head.h -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/head.h

Purpose: Declares early RISC-V boot helpers shared between boot assembly and C setup.

Important APIs/types/functions: Declares `setup_vm()`, `setup_vm_final()`, and early page-table or relocation symbols used by `head.S` and MM setup.

Control flow: No runtime logic is in the header. It establishes call contracts for early assembly to invoke C VM initialization.

State and persistence: No direct state; it names boot-time page table setup interfaces that mutate global MMU state.

Dependencies and integration points: Integrates `head.S`, early MM code, KASLR/FDT boot logic, and final kernel page-table installation.

Risks and test signals: Prototype drift between assembly calls and C definitions can fail at link time or boot. Test all RISC-V MMU build modes and early boot under QEMU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/head.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/hibernate-asm.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/hibernate-asm.S

Purpose: Provides low-level RISC-V hibernation resume and image-restore assembly.

Important APIs/types/functions: Defines `__hibernate_cpu_resume`, `hibernate_restore_image`, and `hibernate_core_restore_code`.

Control flow: Resume assembly restores saved CPU context, switches to resume page tables, jumps into relocated restore code, and copies saved image pages back to original locations before returning to restored kernel execution.

State and persistence: Consumes `suspend_context`, relocated restore code address, SATP/page-table state, and memory copy lists prepared by `hibernate.c`.

Dependencies and integration points: Tied to hibernation C code, suspend context layout, `asm-offsets`, cache/TLB ordering, and MMU page table setup.

Risks and test signals: Running while overwriting the old kernel image is extremely sensitive to relocation, register preservation, and executable mapping. Test hibernate/resume with KASLR, high memory pressure, multiple CPUs disabled, and post-resume register/state validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/hibernate-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/hibernate.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/hibernate.c

Purpose: Implements architecture hibernation save/resume support for RISC-V.

Important APIs/types/functions: Defines hibernation header structures, `pfn_is_nosave()`, `save_processor_state()`, `restore_processor_state()`, `arch_hibernation_header_save()`, `arch_hibernation_header_restore()`, `swsusp_arch_suspend()`, `swsusp_arch_resume()`, temporary page-table mapping helpers, `relocate_restore_code()`, `hibernate_resume_nonboot_cpu_disable()`, and `riscv_hibernate_init()`.

Control flow: Suspend saves invariants and CPU context, records the sleeping CPU, and returns through generic swsusp. Resume validates kernel version, SATP mode, and restore metadata, disables nonboot CPUs, allocates a temporary resume page directory, maps the restore code and saved image ranges, copies restore code to safe executable memory, switches to the resume path, and runs assembly restore code.

State and persistence: Maintains `sleep_cpu`, `resume_pg_dir`, `hibernate_cpu_context`, `relocated_restore_code`, and the architecture hibernation header embedded in the image. It mutates temporary page tables and page permissions.

Dependencies and integration points: Integrates with generic hibernation, memblock nosave ranges, RISC-V page table allocation, suspend assembly, cacheflush/TLB barriers, SMP CPU disable, and kernel version checks.

Risks and test signals: Header validation, page-table permissions, executable restore code, and CPU identity must be exact or resume corrupts memory. Test hibernate/resume across KASLR, SATP modes, SMP, module-loaded kernels, nosave PFNs, and failure cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/hibernate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/image-vars.h -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/image-vars.h

Purpose: Exposes selected kernel image symbols to decompressor/PI or EFI image-link contexts without duplicating definitions.

Important APIs/types/functions: Uses `KERNEL_MAP`/symbol alias declarations for image boundaries, EFI stub symbols, and other linker-provided addresses needed outside the normal kernel link.

Control flow: Header-only build/link metadata; no runtime control flow.

State and persistence: No mutable state. It describes persistent linker symbols.

Dependencies and integration points: Used by RISC-V image build, EFI stub, position-independent early code, and linker scripts.

Risks and test signals: Alias mistakes cause link failures or wrong runtime addresses. Test EFI and non-EFI builds, PIE/PI paths, and symbol inspection with `nm`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/image-vars.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/irq.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/irq.c

Purpose: Initializes RISC-V interrupt handling, optional IRQ stacks, shadow call stacks for IRQs, and softirq stack switching.

Important APIs/types/functions: Implements `init_IRQ()`, `do_softirq_own_stack()`, `arch_show_interrupts()`, IRQ stack initialization, SCS stack initialization, and per-CPU `irq_stack_ptr`.

Control flow: Boot initializes IRQ domains through irqchip probing and prepares per-CPU IRQ/SCS stacks where configured. Hard interrupt entry can call handlers on an IRQ stack through assembly, and softirq processing can be redirected to the IRQ stack.

State and persistence: Per-CPU IRQ stack arrays, stack pointers, and optional SCS stacks persist for each CPU.

Dependencies and integration points: Depends on irqchip, generic IRQ/softirq core, `entry.S` `call_on_irq_stack`, SCS, VMAP/IRQ stack config, and seq_file interrupt reporting.

Risks and test signals: Stack switching bugs corrupt task stacks or shadow call stacks. Test interrupt storms, softirq-heavy networking/storage, CPU hotplug with IRQ stacks, lockdep, and `/proc/interrupts`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/jump_label.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/jump_label.c

Purpose: Implements RISC-V static key/jump label patching.

Important APIs/types/functions: Provides `arch_jump_label_transform()` and architecture helpers to patch branch/NOP instruction sequences for static keys.

Control flow: Static key core requests enable/disable transformations. The RISC-V implementation encodes either a jump to the target or a NOP at the patch site and writes it using text patching, with early boot or runtime synchronization as required.

State and persistence: Persistent state is patched kernel text and static key metadata owned by generic jump label code.

Dependencies and integration points: Depends on RISC-V instruction encoding, `patch_text`, alternatives/text mutex, and Linux jump label core.

Risks and test signals: Offset range, instruction length, and synchronization mistakes can produce bad text. Test static key toggling, tracepoints, scheduler/static branch sites, modules, and concurrent CPU execution during patching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/jump_label.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/kernel_mode_fpu.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/kernel_mode_fpu.c

Purpose: Provides guarded kernel-mode floating-point access helpers for RISC-V.

Important APIs/types/functions: Implements `kernel_fpu_begin()` and `kernel_fpu_end()` or equivalent wrappers around preemption and FP status management.

Control flow: Callers enter a short critical section, save/disable preemption as required, enable FP state for kernel use, perform FP operations, then restore status and preemption state.

State and persistence: Temporarily mutates CPU status FS bits and per-task FP ownership state; no file-local persistent state.

Dependencies and integration points: Depends on FPU assembly save/restore, `switch_to`, preemption control, and cryptographic or math code that uses kernel FP.

Risks and test signals: Kernel FP use across preemption or interrupt boundaries can corrupt user FP state. Test with preemptible kernels, FP-heavy user workloads, kernel FP callers, and lockdep/preempt debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/kernel_mode_fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/kernel_mode_vector.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/kernel_mode_vector.c

Purpose: Provides guarded kernel-mode vector access for RISC-V vector instructions.

Important APIs/types/functions: Implements vector begin/end helpers, vector nesting/ownership handling, preemption hooks, and state save/restore interactions for kernel vector users.

Control flow: A kernel vector user enters a protected section that disables preemption or records nesting, saves any live user vector state as needed, enables VS state, runs vector code, then restores status and nesting state on exit. Optional preemptive vector support coordinates with trap entry/exit.

State and persistence: Temporarily mutates VS bits, per-task vector flags, CPU vector context, and nesting counters. User vector state persists in task structures.

Dependencies and integration points: Depends on RISC-V vector support, `entry.S` vector nesting hooks, scheduler context switching, signal/ptrace vector state, and kernel vector consumers.

Risks and test signals: Incorrect nesting or preemption handling corrupts vector registers across tasks. Test vector user tasks concurrent with kernel vector users, preemption stress, signal delivery with vector state, and configs with/without `CONFIG_RISCV_ISA_V_PREEMPTIVE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/kernel_mode_vector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/kexec_elf.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/kexec_elf.c

Purpose: Loads ELF-format RISC-V kernels for the `kexec_file_load` syscall.

Important APIs/types/functions: Defines `riscv_kexec_elf_load()`, `elf_find_pbase()`, `elf_kexec_load()`, and `elf_kexec_ops`.

Control flow: The loader parses ELF headers, finds the lowest physical and virtual load addresses, locates a suitably aligned memory hole, computes the new entry address, adds each PT_LOAD segment to the kexec image, and appends DTB/initrd/cmdline extra segments.

State and persistence: Mutates `struct kimage` segment list and `image->start`. ELF info is transient and freed after loading.

Dependencies and integration points: Depends on generic kexec ELF parsing, memblock/kexec buffer placement, RISC-V boot alignment, and `load_extra_segments()` in machine kexec file code.

Risks and test signals: Wrong base translation or alignment makes the second kernel unbootable. Test ELF vmlinux kexec, large segment layouts, initrd/cmdline handling, crash kernels, and invalid ELF rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/kexec_elf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/kexec_image.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/kexec_image.c

Purpose: Loads raw RISC-V `Image` kernels for `kexec_file_load`.

Important APIs/types/functions: Defines `image_probe()`, `image_load()`, and `image_kexec_ops`.

Control flow: The probe validates the RISC-V image header and magic. Load checks image size and endianness flags, places the kernel image with alignment from `text_offset`, sets `image->start`, then adds extra DTB/initrd/cmdline segments.

State and persistence: Populates `struct kimage` buffers and start address; no file-local persistent state.

Dependencies and integration points: Depends on RISC-V boot image header definitions, kexec buffer placement, endian config, and machine kexec extra segment setup.

Risks and test signals: Header parsing is boot ABI critical; wrong alignment or endian acceptance can boot garbage. Test raw Image kexec, BE/LE mismatch rejection, malformed image sizes, and initrd/cmdline propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/kexec_image.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/kexec_relocate.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/kexec_relocate.S

Purpose: Provides low-level relocation and final jump code for RISC-V kexec.

Important APIs/types/functions: Defines `riscv_kexec_relocate`, `riscv_kexec_norelocate`, and `riscv_kexec_relocate_size`.

Control flow: The relocation path runs from a safe copied buffer, processes kexec indirection pages, copies source pages to destination pages, handles destination/source/control/page flags, flushes caches/TLBs as needed, passes hart ID and FDT pointer, and jumps to the new kernel entry. The no-relocate path disables translation/state and jumps directly when relocation is unnecessary.

State and persistence: Consumes kexec control pages and mutates physical memory into the next kernel layout. It changes SATP/status/interrupt state before transfer.

Dependencies and integration points: Called by `machine_kexec.c`, depends on RISC-V page size, CSR macros, kexec page flags, and boot protocol register conventions.

Risks and test signals: This code executes while replacing the running kernel, so address translation, cache ordering, and flag decoding are high risk. Test normal kexec, crash kexec, large memory maps, relocation across overlapping ranges, and SMP shutdown before jump.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/kexec_relocate.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/kgdb.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/kgdb.c

Purpose: Implements RISC-V KGDB register access, breakpoint handling, and software single-step emulation.

Important APIs/types/functions: Defines register metadata `dbg_reg_def`, `dbg_get_reg()`, `dbg_set_reg()`, `kgdb_arch_set_pc()`, `kgdb_arch_handle_exception()`, `kgdb_arch_init()`, `kgdb_arch_exit()`, `arch_kgdb_ops`, and helpers to decode branch/jump targets and install temporary breakpoints.

Control flow: On KGDB exceptions, command handling can read/write registers, continue, single-step by planting a breakpoint at the computed next PC, or recover the original opcode. A notifier catches break instructions and routes KGDB breakpoints into the debugger.

State and persistence: Maintains `stepped_address` and `stepped_opcode` for temporary single-step breakpoints, plus notifier registration and KGDB architecture ops.

Dependencies and integration points: Depends on KGDB core, RISC-V instruction decoding, text patching/breakpoint helpers, `pt_regs`, and trap notifiers.

Risks and test signals: Branch target decode and temporary breakpoint restoration must be exact or debugging changes program behavior. Test KGDB break/continue/single-step over compressed and normal control-flow instructions, register read/write, SMP breakpoints, and module text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/kgdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/machine_kexec.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/machine_kexec.c

Purpose: Implements architecture-level kexec preparation, shutdown, cleanup, and final machine transition for RISC-V.

Important APIs/types/functions: Provides `machine_kexec_prepare()`, `machine_kexec_cleanup()`, `machine_shutdown()`, `machine_crash_shutdown()`, and `machine_kexec()`.

Control flow: Prepare validates and records kexec image state. Shutdown stops secondary CPUs and masks interrupts. Crash shutdown preserves crash state. `machine_kexec()` copies relocation code to a control page, flushes it, prepares hart/FDT/entry arguments, and jumps into `riscv_kexec_relocate` or no-relocate code.

State and persistence: Mutates `struct kimage`, per-CPU shutdown state, crash registers, and physical control pages. No file-local long-lived data beyond setup.

Dependencies and integration points: Depends on kexec core, SMP stop, crash dump, MMU/cache flushing, `kexec_relocate.S`, and RISC-V boot protocol.

Risks and test signals: Secondary CPU shutdown and control-code relocation are critical. Test normal kexec, panic kdump, CPU hotplug before kexec, no-MMU or MMU variants, and repeated kexec cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/machine_kexec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/machine_kexec_file.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/machine_kexec_file.c

Purpose: Supplies RISC-V `kexec_file_load` support for crash extras, purgatory relocations, and DTB/initrd/cmdline segments.

Important APIs/types/functions: Defines `kexec_file_loaders[]`, `arch_kimage_file_post_load_cleanup()`, `prepare_elf_headers()`, `setup_kdump_cmdline()`, `arch_kexec_apply_relocations_add()`, and `load_extra_segments()`.

Control flow: For crash kernels it counts RAM ranges, builds ELF core headers, rewrites crashkernel command-line arguments, applies purgatory relocations for RISC-V relocation types, and places extra segments. Relocation handling encodes branch, JAL, PC-relative high/low, compressed branch/jump, ADD/SUB, and 64-bit relocations while ignoring relax/alignment where appropriate.

State and persistence: Populates `struct kimage` with elfcorehdr, FDT, initrd, command line, and purgatory relocation results. Temporary crash memory arrays and FDT buffers are freed during cleanup.

Dependencies and integration points: Depends on kexec file core, libfdt, crash memory iteration, RISC-V relocation encoders, ELF constants, and both ELF/raw image loaders.

Risks and test signals: Purgatory relocation bugs cause silent boot failure; FDT/cmdline edits affect crash dump usability. Test signed `kexec_file_load`, crash kernel with elfcorehdr, relocation type coverage, FDT validation, and command-line crashkernel stripping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/machine_kexec_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/mcount-dyn.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/mcount-dyn.S

Purpose: Provides the dynamic ftrace caller trampoline for RISC-V.

Important APIs/types/functions: Defines `ftrace_caller`, inner labels `ftrace_call` and `ftrace_caller_direct`, and `ftrace_stub_direct_tramp`.

Control flow: Instrumented function calls enter the trampoline, which saves live argument/return state, computes the traced function and parent caller, optionally resolves per-callsite direct ops, calls the active ftrace function, then restores state and returns to the instrumented function.

State and persistence: Uses patched call targets and optional per-record ops state managed by ftrace core; no standalone persistent data beyond trampoline text.

Dependencies and integration points: Integrated with `ftrace.c`, dynamic patching, function graph tracing, direct ftrace, and RISC-V calling convention.

Risks and test signals: Register save masks and stack layout must preserve all call ABI expectations. Test dynamic ftrace, direct ftrace, graph tracing, nested tracers, and module call sites under heavy tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/mcount-dyn.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/mcount.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/mcount.S

Purpose: Implements classic RISC-V mcount/ftrace entry stubs and graph return handler.

Important APIs/types/functions: Defines `ftrace_stub`, `ftrace_stub_graph`, `return_to_handler`, and `_mcount`.

Control flow: Compiler-instrumented functions call `_mcount`, which saves registers, invokes ftrace and optional graph tracer hooks, then restores execution. `return_to_handler` redirects function returns through graph tracing and resumes at the original return address.

State and persistence: Uses ftrace core global function pointers and per-task graph return state. Assembly text is persistent.

Dependencies and integration points: Works with `ftrace.c`, function graph tracer, compiler `-pg` instrumentation, and RISC-V ABI.

Risks and test signals: Incorrect frame layout or return address handling corrupts call chains. Test function tracer and graph tracer in static and dynamic ftrace modes, recursion handling, and interrupt-context tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/mcount.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/module-sections.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/module-sections.c

Purpose: Prepares module GOT and PLT sections needed when RISC-V module relocations cannot directly reach their targets.

Important APIs/types/functions: Implements `module_emit_got_entry()`, `module_emit_plt_entry()`, relocation sorting/dedup helpers, `rela_needs_plt_got_entry()`, and `module_frob_arch_sections()`.

Control flow: Before final relocation, module sections are scanned and sorted to count unique GOT/PLT needs. The module loader reserves architecture section storage, then relocation handlers emit or reuse GOT/PLT entries for out-of-range calls or GOT references.

State and persistence: Mutates module architecture metadata and allocated GOT/PLT sections that persist with the loaded module.

Dependencies and integration points: Used by `module.c` relocation handlers under `CONFIG_MODULE_SECTIONS`, depends on ELF Rela entries, module loader section allocation, and RISC-V relocation semantics.

Risks and test signals: Dedup or size-count errors can overflow reserved sections or duplicate entries. Test modules with far calls, GOT references, many relocations, duplicate relocations, and module unload/reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/module-sections.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/module.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/module.c

Purpose: Applies RISC-V ELF relocations for loadable kernel modules and finalizes module alternatives.

Important APIs/types/functions: Defines relocation apply handlers for absolute, branch, JAL, compressed branch/jump, PC-relative HI20/LO12, GOT, CALL/CALL_PLT, ADD/SUB/SET, ULEB128, unsupported dynamic/TLS relocations, relocation accumulation structures, `apply_relocate_add()`, and `module_finalize()`.

Control flow: `apply_relocate_add()` iterates relocation entries, resolves symbols and addends, finds matching HI20 relocations for LO12 entries, dispatches direct relocation handlers, or accumulates ADD/SUB/SET/ULEB128 chains by address before writing final values with overflow checks. Out-of-range calls may route through module PLT entries when module sections are enabled. Finalization applies module alternatives from the `.alternative` section.

State and persistence: Mutates loaded module text/data, module GOT/PLT sections, and temporary hash/list storage for accumulated relocations. Patched module alternatives persist until unload.

Dependencies and integration points: Depends on ELF psABI relocation constants, module loader, `module-sections.c`, alternative patching, endian helpers, and RISC-V instruction encoding.

Risks and test signals: Relocation math is high risk: range checks, PC-relative LO12 pairing, accumulation overflow, ULEB128 length, and GOT/PLT emission can break modules. Test module selftests, RISC-V module relocation test suite, far-call modules, weak unresolved symbols, compressed relocations, alternatives in modules, and error cleanup on allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/paravirt.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/paravirt.c

Purpose: Implements RISC-V paravirtual steal-time support using the SBI STA extension.

Important APIs/types/functions: Defines `pv_time_init()`, `pv_time_cpu_online()`, `pv_time_cpu_down_prepare()`, `pv_time_steal_clock()`, `sbi_sta_steal_time_set_shmem()`, per-CPU `steal_time`, and the `no-steal-acc` early parameter.

Control flow: Boot checks for SBI STA availability, registers paravirt steal-clock operations, and installs CPU hotplug callbacks. On CPU online it shares a per-CPU steal-time memory region with firmware; on down it disables the shared memory. Runtime clock reads return accumulated stolen time.

State and persistence: Per-CPU aligned `struct sbi_sta_struct` buffers persist while CPUs are online. The `steal_acc` command-line flag controls accumulated mode.

Dependencies and integration points: Depends on SBI STA, paravirt time accounting, CPU hotplug states, and scheduler steal-time reporting.

Risks and test signals: Physical address sharing and hotplug cleanup must match firmware expectations or steal time is wrong. Test under KVM/SBI STA hosts, CPU hotplug, `no-steal-acc`, scheduler accounting, and migration if the hypervisor supports it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/paravirt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/patch.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/patch.c

Purpose: Provides safe RISC-V kernel text patching primitives for alternatives, ftrace, jump labels, kprobes, and module code.

Important APIs/types/functions: Defines `patch_text_set_nosync()`, `patch_insn_write()`, `patch_text_nosync()`, `patch_text()`, fixmap mapping helpers, and `riscv_patch_in_stop_machine`.

Control flow: Runtime patching maps target text writable through fixmap when strict kernel RWX is active, writes bytes or instructions, flushes instruction cache, and optionally synchronizes all CPUs with `stop_machine()` for fully synchronized patching.

State and persistence: Mutates executable kernel or module text. Uses fixmap slots and global patching state during operations.

Dependencies and integration points: Depends on `text_mutex`, fixmap, set_memory permissions, cacheflush, stop_machine, alternatives, ftrace, kprobes, and jump labels.

Risks and test signals: Partial instruction writes, missing icache flushes, or patching freed text can crash live CPUs. Test alternatives at boot/module load, kprobe arm/disarm, ftrace toggling, jump label stress, strict RWX, and SMP patching races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/patch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/perf_callchain.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/perf_callchain.c

Purpose: Implements RISC-V perf callchain collection for kernel and user stack samples.

Important APIs/types/functions: Provides perf callchain walkers that collect return addresses from `pt_regs`, frame pointers, and user stack frames.

Control flow: Perf sampling starts from the interrupted PC and frame pointer, records kernel frames while valid, then optionally walks user frames using safe user access until bounds or errors stop the walk.

State and persistence: No persistent file-local state; samples are appended to perf callchain contexts.

Dependencies and integration points: Depends on perf core, RISC-V stacktrace/frame-pointer conventions, user access helpers, and `pt_regs`.

Risks and test signals: Invalid frame pointers, no-frame-pointer builds, and user memory faults can truncate or corrupt callchains. Test perf record/report for kernel/user workloads, signal stacks, compat tasks, and frame-pointer config changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/perf_callchain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/perf_regs.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/perf_regs.c

Purpose: Maps perf register sampling ABI numbers to RISC-V `pt_regs` fields.

Important APIs/types/functions: Implements `perf_reg_value()` and register mask validation helpers for the RISC-V perf ABI.

Control flow: Perf asks for selected registers in a sample. The implementation validates the register id and returns the corresponding general register, PC, or status value from the trap frame.

State and persistence: No persistent state; it reads sample-time `pt_regs`.

Dependencies and integration points: Depends on perf event core, `pt_regs`, and RISC-V userspace perf register ABI.

Risks and test signals: ABI numbering errors break profiler register dumps. Test `perf record --intr-regs`, invalid masks, user/kernel samples, and 32/64-bit register width expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/perf_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/pi/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/pi/Makefile

Purpose: Builds early position-independent RISC-V code used before the main kernel relocation environment is fully available.

Important APIs/types/functions: Lists PI objects such as early FDT parsing, command-line parsing, and early random/KASLR seed support, with flags suitable for freestanding early execution.

Control flow: Kbuild compiles these objects for early boot use and links them into the kernel image so assembly boot code can call them before normal subsystems initialize.

State and persistence: Produces build artifacts only; runtime state is owned by the individual PI C files.

Dependencies and integration points: Integrates with `head.S`, early FDT, KASLR, SATP mode selection, and architecture build flags.

Risks and test signals: Incorrect flags can introduce relocations or instrumentation unsafe for early boot. Test early boot with KASLR, no-MMU/MMU modes, and objdump checks for unsupported relocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/pi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/pi/archrandom_early.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/pi/archrandom_early.c

Purpose: Provides an early RISC-V architectural random seed path for KASLR before normal drivers initialize.

Important APIs/types/functions: Implements `get_kaslr_seed_zkr()` and uses the Zkr entropy CSR path when available.

Control flow: Early boot checks whether the CPU/FDT indicates the Zkr extension and then samples architectural random values to contribute a KASLR seed.

State and persistence: No long-lived state; returns seed material to early KASLR logic.

Dependencies and integration points: Depends on early ISA extension detection, CSR access, and `fdt_early.c` KASLR seed selection.

Risks and test signals: Early CSR access must only occur when supported, and weak entropy should not be over-trusted. Test Zkr-present and absent systems, traps on unsupported CSR access, and KASLR seed variation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/pi/archrandom_early.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/pi/cmdline_early.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/pi/cmdline_early.c

Purpose: Parses early boot command-line options before normal command-line setup.

Important APIs/types/functions: Defines `early_cmdline`, `get_early_cmdline()`, `set_satp_mode_from_cmdline()`, `set_nokaslr_from_cmdline()`, and matching helpers for `no4lvl`, `no5lvl`, and `nokaslr`.

Control flow: Early code obtains `/chosen/bootargs` from the FDT, copies it into a static buffer, searches for paging mode suppressors or `nokaslr`, and returns SATP mode or KASLR policy decisions to boot setup.

State and persistence: `early_cmdline` is static early storage; decisions persist by influencing page-table mode and KASLR enablement.

Dependencies and integration points: Depends on libfdt-safe early parsing, `pi.h`, FDT physical address from boot, and `head.S`/MM SATP setup.

Risks and test signals: Buffer truncation or parser false positives can select wrong paging mode. Test command lines with `nokaslr`, `no4lvl`, `no5lvl`, long bootargs, missing `/chosen`, and malformed FDTs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/pi/cmdline_early.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/pi/fdt_early.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/pi/fdt_early.c

Purpose: Performs early FDT parsing for KASLR seed discovery, ISA extension matching, and SATP mode selection.

Important APIs/types/functions: Implements `get_kaslr_seed()`, `fdt_early_match_extension_isa()`, `set_satp_mode_from_fdt()`, and helpers for node availability, node-name checks, and ISA-string extension matching.

Control flow: Early boot reads `/chosen/kaslr-seed`, checks CPU nodes for availability and requested ISA extensions, parses memory/MMU-related properties, and chooses supported page-table mode before normal OF code is available.

State and persistence: No file-local persistent state; returns seed and SATP decisions to early boot. Consumes immutable FDT data.

Dependencies and integration points: Depends on libfdt, early command-line parsing, KASLR, page table mode setup, and ISA extension naming conventions.

Risks and test signals: Early parsing must be robust against malformed FDTs and heterogeneous CPU nodes. Test missing seed, Zkr fallback, disabled CPU nodes, ISA extension string variants, and page-mode restrictions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/pi/fdt_early.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/pi/pi.h -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/pi/pi.h

Purpose: Declares interfaces shared by RISC-V position-independent early boot helpers.

Important APIs/types/functions: Declares early FDT, command-line, SATP mode, KASLR seed, and architectural random helper functions.

Control flow: Header-only; no runtime logic.

State and persistence: No direct state, but the declared helpers influence persistent boot choices such as KASLR and page-table mode.

Dependencies and integration points: Used by `archrandom_early.c`, `cmdline_early.c`, `fdt_early.c`, and early boot/MM setup.

Risks and test signals: Prototype drift can break early boot or link. Test all PI helper build configs and early boot with and without KASLR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/pi/pi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/Makefile

Purpose: Builds RISC-V kprobes, instruction decode, simulation, rethook, and uprobe support objects.

Important APIs/types/functions: Lists objects for `kprobes.o`, `decode-insn.o`, `simulate-insn.o`, `rethook.o`, `rethook_trampoline.o`, and optional uprobes.

Control flow: Kbuild selects objects based on probe-related Kconfig options; runtime behavior is in the compiled C/assembly files.

State and persistence: Build metadata only.

Dependencies and integration points: Integrates with Linux kprobes/uprobes/rethook frameworks and RISC-V trap/text patching code.

Risks and test signals: Missing object selection can silently disable probe features. Test builds with kprobes, kretprobes, uprobes, and combinations with modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/decode-insn.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/decode-insn.c

Purpose: Classifies RISC-V instructions for kprobe single-step or simulation handling.

Important APIs/types/functions: Implements `riscv_probe_decode_insn()` returning `enum probe_insn` values.

Control flow: Kprobe preparation passes an instruction and address to the decoder. The decoder rejects unsupported or unsafe instructions, marks simulatable control-flow forms for software simulation, and allows normal single-step slot preparation for other probeable instructions.

State and persistence: No persistent state; classification is per instruction.

Dependencies and integration points: Used by `kprobes.c`, instruction simulation helpers, RISC-V instruction predicates, and probe blacklists.

Risks and test signals: Misclassification can probe unsafe instructions or single-step instructions that cannot be executed out of line. Test kprobe placement on compressed/normal branches, jumps, breakpoints, illegal instructions, and exception-generating instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/decode-insn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/decode-insn.h -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/decode-insn.h

Purpose: Declares RISC-V kprobe instruction decode results and the decoder entry point.

Important APIs/types/functions: Defines `enum probe_insn` classification values and declares `riscv_probe_decode_insn()`.

Control flow: Header-only; it establishes the contract between decode, kprobe preparation, and instruction simulation.

State and persistence: No state.

Dependencies and integration points: Used by kprobes and simulator code in the same directory.

Risks and test signals: Enum meaning must stay synchronized with kprobe control flow. Test build coverage and kprobe decode paths for every enum case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/decode-insn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/kprobes.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/kprobes.c

Purpose: Implements RISC-V kprobe arming, trap handling, single-step/simulation, reentry, fault recovery, and blacklist setup.

Important APIs/types/functions: Defines per-CPU `current_kprobe` and `kprobe_ctlblk`, `arch_prepare_kprobe()`, `arch_arm_kprobe()`, `arch_disarm_kprobe()`, `arch_remove_kprobe()`, `kprobe_breakpoint_handler()`, `kprobe_single_step_handler()`, `kprobe_fault_handler()`, `arch_populate_kprobe_blacklist()`, `arch_trampoline_kprobe()`, and `arch_init_kprobes()`.

Control flow: Preparation validates addresses, decodes instruction length/type, and either builds an out-of-line single-step slot or marks the instruction for simulation. Arming patches a breakpoint into text. Breakpoint traps find the kprobe, run pre-handlers, set up single-step or simulation, and later post-handlers restore state. Fault handling rewinds PC or restores nested probe state, while reentry logic tracks missed probes and nested status.

State and persistence: Per-CPU current probe and control block track active/reentered probes, saved IRQ flags, previous probes, and status. Probe slots and patched text persist while probes are armed.

Dependencies and integration points: Depends on text patching, extable, RISC-V break instruction encoding, instruction decoder/simulator, trap handling, irqentry blacklist symbols, and generic kprobes/rethook.

Risks and test signals: Probe reentry, compressed instruction length, PC restoration, and IRQ flag restoration are delicate. Test kprobes on kernel text and modules, kretprobes, nested probes, probes in exception paths rejection, faulting probed instructions, and concurrent arm/disarm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/kprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/rethook.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/rethook.c

Purpose: Provides RISC-V architecture glue for generic rethook/kretprobe return interception.

Important APIs/types/functions: Implements `arch_rethook_trampoline_callback()` and `arch_rethook_prepare()`.

Control flow: Kretprobe setup calls `arch_rethook_prepare()` to save the original return address and replace it with `arch_rethook_trampoline`. When the function returns, the trampoline builds a register frame and calls `arch_rethook_trampoline_callback()`, which runs generic rethook handlers and returns the real target address.

State and persistence: Per-call rethook nodes store original return addresses; `pt_regs` is transient during trampoline handling.

Dependencies and integration points: Depends on generic rethook, kprobes/kretprobes, `rethook_trampoline.S`, and RISC-V return address conventions.

Risks and test signals: Return address replacement must preserve normal call ABI and handle mcount/ftrace interactions. Test kretprobes on normal and traced functions, nested returns, faulting handlers, and module functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/rethook.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/rethook.h -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/rethook.h

Purpose: Declares the RISC-V rethook trampoline symbol used by kretprobe/rethook setup.

Important APIs/types/functions: Declares `arch_rethook_trampoline`.

Control flow: Header-only; C code writes this symbol address into saved return-address slots so execution enters assembly trampoline on function return.

State and persistence: No state.

Dependencies and integration points: Connects `rethook.c` with `rethook_trampoline.S` and generic rethook infrastructure.

Risks and test signals: Declaration/linkage drift breaks kretprobe builds or return redirection. Test kretprobe build/runtime with modules and ftrace enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/rethook.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/rethook_trampoline.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/rethook_trampoline.S

Purpose: Implements the RISC-V assembly trampoline entered when a probed function returns through rethook.

Important APIs/types/functions: Defines `arch_rethook_trampoline`.

Control flow: The trampoline saves a full register frame compatible with `pt_regs`, calls `arch_rethook_trampoline_callback()`, receives the real return address, restores registers, and jumps to the original caller.

State and persistence: Uses stack-resident saved registers only. Persistent per-return state is held by generic rethook nodes.

Dependencies and integration points: Depends on `pt_regs` offsets, RISC-V ABI, `rethook.c`, and generic kretprobe/rethook handling.

Risks and test signals: Register save/restore omissions or stack alignment bugs corrupt returning functions. Test kretprobes on functions with many live registers, nested returns, interrupt-disabled contexts, and ftrace/mcount combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/rethook_trampoline.S -->
