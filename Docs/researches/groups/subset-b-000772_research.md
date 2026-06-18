# subset-b-000772 research

Grouped research for the requested PowerPC vDSO, architecture, UAPI, interrupt, cache, early display, and CPU setup files. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/gettimeofday.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/gettimeofday.h

Purpose: PowerPC vDSO time entry support, wiring generic vDSO gettimeofday/clock_gettime code to the PowerPC timebase and to architecture-specific syscall fallbacks.

Important APIs/types/functions: `VDSO_HAS_CLOCK_GETRES`, `VDSO_HAS_TIME`, `VDSO_DELTA_NOMASK`, `do_syscall_2()`, `gettimeofday_fallback()`, clock gettime/getres fallback variants, `__arch_get_hw_counter()`, `vdso_clocksource_ok()`, 32-bit `vdso_shift_ns()`, and exported C vDSO entry prototypes such as `__c_kernel_clock_gettime` and `__c_kernel_gettimeofday`.

Control flow: Fast paths read the timebase through `get_tb()` and let generic vDSO code compute times; fallback paths load PowerPC syscall arguments into r0/r3/r4, execute `sc`, normalize negative error returns, and select time64 syscalls for 32-bit vDSO clock_gettime/getres.

State and persistence: No persistent software state is owned here. The header consumes read-only vDSO data and the CPU timebase; it assumes PowerPC vDSO clocksources use a full 64-bit mask.

Dependencies and integration points: Depends on `asm/vdso/timebase.h`, syscall numbers, barrier semantics, UAPI time types, and generic vDSO data structures. Integrated by PowerPC vDSO builds and libc callers mapped to the vDSO page.

Risks: Inline assembly register constraints and clobbers are ABI-sensitive. Wrong syscall number selection breaks 32-bit time64 behavior. The `VDSO_DELTA_NOMASK` assumption must remain aligned with available PowerPC clocksources.

Test signals: Build 32-bit and 64-bit vDSO, run `clock_gettime`, `clock_getres`, `gettimeofday`, and `time` tests with forced fallback paths, and compare monotonic/realtime behavior against syscalls.

Source read size: 149 lines, 4132 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/gettimeofday.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/processor.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/processor.h

Purpose: Provides vDSO-safe processor relaxation and hardware multithreading priority helpers for PowerPC.

Important APIs/types/functions: `HMT_very_low()` through `HMT_high()` priority nops on PPC64 and `cpu_relax()` with feature patching for pre-POWER10 versus POWER10 `wait 2,0` pause behavior.

Control flow: Spin loops call `cpu_relax()`, which either emits low/medium priority nops or a patched short wait depending on `CPU_FTR_ARCH_31`; non-PPC64 builds degrade to a compiler barrier.

State and persistence: No persistent state is stored. The only state effect is transient thread priority/pause behavior on SMT hardware.

Dependencies and integration points: Includes CPU feature and feature-fixup headers; integrated by vDSO and low-level polling code that cannot rely on full kernel facilities.

Risks: Instruction choice is CPU-generation-sensitive. Incorrect feature patching can hurt spin performance or use unsupported wait instructions in user-visible vDSO code.

Test signals: PPC64 and PPC32 compile coverage, objdump of patched alternatives, and spin-loop latency/scheduler smoke tests on POWER9 and POWER10 class machines.

Source read size: 41 lines, 1258 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/timebase.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/timebase.h

Purpose: Defines PowerPC timebase read/write helpers used by vDSO and low-level timekeeping.

Important APIs/types/functions: `mftb()`, `mftbu()`, `mttbl()`, `mttbu()`, `get_tb()`, and `set_tb()` with special cases for Cell, e500, and 8xx.

Control flow: 64-bit vDSO reads the lower timebase directly; 32-bit-compatible code loops high-low-high until stable. Cell bug handling retries a zero lower timebase when the CPU feature is set. `set_tb()` writes upper/lower timebase registers in the required order.

State and persistence: Interacts directly with CPU timebase special-purpose registers. `get_tb()` is read-only; `set_tb()` mutates global processor timebase state and is only appropriate for kernel-side setup.

Dependencies and integration points: Depends on `asm/reg.h` for SPR numbers and feature macros. Integrated by vDSO clocks, kernel time setup, and architecture code that needs stable TB values.

Risks: A non-atomic 32-bit read without the retry loop can produce backwards time. Wrong SPR access or Cell workaround gating can break timekeeping on older platforms.

Test signals: Timebase monotonicity tests, vDSO time tests on 32-bit compat and 64-bit kernels, and platform boot coverage for Cell/e500/8xx configurations.

Source read size: 73 lines, 1933 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/timebase.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/vsyscall.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/vsyscall.h

Purpose: Connects PowerPC vDSO datapage definitions to the generic vDSO vsyscall implementation.

Important APIs/types/functions: Includes `asm/vdso_datapage.h` before `asm-generic/vdso/vsyscall.h`; it defines no standalone functions.

Control flow: Generic vDSO code is compiled after architecture datapage definitions are visible, allowing generic helpers to use PowerPC-specific layout/macros.

State and persistence: No runtime state is owned; it is an include-order integration header.

Dependencies and integration points: Depends on `asm/vdso_datapage.h` and generic vDSO vsyscall code. Used during PowerPC vDSO object builds.

Risks: Include order matters. Moving generic inclusion before the architecture datapage can create missing or mismatched definitions.

Test signals: PowerPC vDSO compile coverage and runtime vDSO syscall/time smoke tests.

Source read size: 14 lines, 358 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/vsyscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso_datapage.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso_datapage.h

Purpose: Defines PowerPC access to the vDSO datapage for C and assembly users.

Important APIs/types/functions: Includes generic `vdso/datapage.h` for C and defines assembler macro `get_datapage ptr symbol` to compute a position-independent datapage address via link-register relative addressing.

Control flow: Assembly callers branch-and-link to a local label, read LR with `mflr`, then add high/low relocations from the local label to the requested symbol.

State and persistence: No storage is allocated here; it exposes access to the kernel-populated vDSO data page.

Dependencies and integration points: Kernel-only header depending on generic vDSO datapage layout and PowerPC assembler relocation syntax. Integrated by vDSO assembly and syscall veneers.

Risks: The macro is relocation- and instruction-sequence-sensitive. Incorrect symbol math breaks position-independent vDSO access.

Test signals: vDSO assembly build, objdump relocation inspection, and runtime validation of vDSO time/syscall data reads.

Source read size: 29 lines, 586 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso_datapage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vermagic.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vermagic.h

Purpose: Adds PowerPC architecture feature strings to module vermagic so modules are tied to compatible kernel instrumentation/relocation settings.

Important APIs/types/functions: `MODULE_ARCH_VERMAGIC_FTRACE`, `MODULE_ARCH_VERMAGIC_RELOCATABLE`, and combined `MODULE_ARCH_VERMAGIC`.

Control flow: Preprocessor selects strings for patchable-function-entry, mprofile-kernel, relocatable kernels, or empty alternatives; module build embeds the concatenated string.

State and persistence: No runtime state. The resulting module metadata persists in built `.ko` files and participates in module loading compatibility checks.

Dependencies and integration points: Driven by `CONFIG_ARCH_USING_PATCHABLE_FUNCTION_ENTRY`, `CONFIG_MPROFILE_KERNEL`, and `CONFIG_RELOCATABLE`; consumed by Linux module infrastructure.

Risks: Missing a configuration bit can allow incompatible modules to load or reject compatible modules unnecessarily.

Test signals: Build modules under each tracing/relocation configuration and verify `modinfo vermagic` plus module load/reject behavior.

Source read size: 22 lines, 612 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vermagic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vga.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vga.h

Purpose: Provides PowerPC VGA/MDA text-mode video memory access helpers with correct little-endian cell handling.

Important APIs/types/functions: `scr_writew()`, `scr_readw()`, `scr_memsetw()`, `VGA_MAP_MEM()`, `vga_readb()`, and `vga_writeb()`.

Control flow: When VGA or MDA console is enabled, console code reads/writes 16-bit screen cells through endian-converting helpers; PPC64 maps physical VGA memory through `ioremap`, while 32-bit keeps the passed address.

State and persistence: State is external VGA text memory. The header owns no buffers but writes directly to mapped framebuffer cells.

Dependencies and integration points: Depends on `asm/io.h`, endian conversion helpers, and vt buffer integration. Used by VGA/MDA console code.

Risks: VGA text cells are little-endian regardless of CPU endian mode. Missing conversion corrupts characters/attributes; wrong mapping on PPC64 can access physical memory incorrectly.

Test signals: VGA/MDA console build and boot tests, text rendering checks on big-endian and little-endian PowerPC, and sparse/compile coverage for non-console configs.

Source read size: 55 lines, 1159 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vga.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/video.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/video.h

Purpose: Supplies PowerPC framebuffer page-protection selection before falling back to generic video helpers.

Important APIs/types/functions: `pgprot_framebuffer()` and `#define pgprot_framebuffer pgprot_framebuffer`.

Control flow: Framebuffer mmap code calls `pgprot_framebuffer()`, which delegates to `__phys_mem_access_prot()` using the physical PFN and mapping length.

State and persistence: No persistent state. It computes page protections for user mappings of framebuffer memory.

Dependencies and integration points: Depends on `asm/page.h` and generic video header; integrated by framebuffer and DRM mmap paths.

Risks: Incorrect cacheability/guarded attributes can produce stale display contents or unsafe MMIO caching.

Test signals: Framebuffer mmap tests, display driver smoke tests, and build coverage across PowerPC memory-management configurations.

Source read size: 17 lines, 431 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vio.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vio.h

Purpose: Declares IBM PowerPC Virtual I/O bus objects, driver registration, CMO accounting, and PFO hypercall plumbing.

Important APIs/types/functions: VIO attribute names, `h_vio_signal()`, IRQ mode constants, `struct vio_pfo_op`, `enum vio_dev_family`, `struct vio_dev`, `struct vio_driver`, `vio_register_driver()`, device/driver unregister functions, CMO helpers, `vio_h_cop_sync()`, `vio_register_device_node()`, `vio_get_attribute()`, and pSeries interrupt helpers.

Control flow: VIO drivers register a `vio_driver`, match OF-backed `vio_dev` instances, request DMA entitlement through `get_desired_dma`, and use hcalls or bus helpers for PFO operations and interrupt enable/disable.

State and persistence: Persistent state lives in each `vio_dev`: identity, unit/resource IDs, IRQ, DMA entitlement/allocated counters, failure count, family, and embedded device object.

Dependencies and integration points: Depends on Linux driver core, DMA/scatterlist APIs, module device tables, and PowerPC hcalls. Integrated by pSeries virtual Ethernet, SCSI, crypto, and platform-facility drivers.

Risks: CMO accounting must match DMA usage or allocation can fail under constrained memory. Hypercall parameters are logical real addresses, so bad translation or length signs can corrupt firmware operations.

Test signals: pSeries VIO device probe/remove, DMA entitlement update tests, virtual Ethernet/storage I/O, PFO hcall error-path testing, and non-pSeries compile stubs.

Source read size: 163 lines, 4649 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vmalloc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vmalloc.h

Purpose: Controls whether huge vmalloc mappings are supported on PowerPC.

Important APIs/types/functions: `arch_vmap_pud_supported()` and `arch_vmap_pmd_supported()` when `CONFIG_HAVE_ARCH_HUGE_VMAP` is enabled.

Control flow: vmalloc code asks these helpers before creating huge PUD/PMD mappings; both return true only under radix MMU because hash page table mode cannot handle large pages in vmalloc space.

State and persistence: No owned state; behavior depends on current MMU mode from `radix_enabled()`.

Dependencies and integration points: Depends on `asm/mmu.h`, `asm/page.h`, and generic vmalloc huge-vmap machinery.

Risks: Allowing huge vmalloc mappings under HPT can break address translation; disabling them under radix costs performance but is safe.

Test signals: Build huge-vmap configs, boot radix and HPT kernels, run vmalloc/ioremap stress and module loading tests.

Source read size: 24 lines, 554 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vphn.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vphn.h

Purpose: Defines virtual processor home-node associativity buffer sizing and hcall entry point for pSeries NUMA placement updates.

Important APIs/types/functions: `VPHN_REGISTER_COUNT`, `VPHN_ASSOC_BUFSIZE`, `VPHN_FLAG_VCPU`, `VPHN_FLAG_PCPU`, and `hcall_vphn()`.

Control flow: NUMA/topology code calls `hcall_vphn(cpu, flags, associativity)` to fill an associativity array, with flags choosing guest vCPU or host CPU associativity.

State and persistence: No state is owned; output is a caller-provided big-endian associativity buffer derived from hypervisor state.

Dependencies and integration points: Integrates with PowerPC hcall implementation and pSeries topology/NUMA update code.

Risks: Buffer sizing includes an initial length cell; off-by-one handling can truncate topology information. Endianness and flag selection must match PAPR.

Test signals: pSeries NUMA boot and hotplug tests, dynamic LPAR topology updates, and hcall failure-path coverage.

Source read size: 24 lines, 802 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vphn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/word-at-a-time.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/word-at-a-time.h

Purpose: Implements PowerPC optimized word-at-a-time zero-byte detection and safe unaligned zero-padded loads used by string routines.

Important APIs/types/functions: Endian-specific `struct word_at_a_time`, `WORD_AT_A_TIME_CONSTANTS`, `has_zero()`, `prep_zero_mask()`, `create_zero_mask()`, `find_zero()`, `zero_bytemask()`, and `load_unaligned_zeropad()`.

Control flow: String scanning loads machine words, computes masks for zero bytes using big-endian arithmetic, little-endian `cmpb` on 64-bit, or generic 32-bit LE arithmetic, then converts masks to byte offsets. Faulting unaligned loads branch through an exception-table fixup that reloads an aligned word and shifts away bytes before the address.

State and persistence: No persistent state. The exception table metadata persists in the object file so fault handling can redirect load faults.

Dependencies and integration points: Depends on bit operations, wordpart helpers, asm compatibility macros, exception-table macros, and PowerPC load/shift instructions. Used by optimized `strlen`, `strnlen`, and related routines/selftests.

Risks: Endian and word-size branches are easy to regress. `load_unaligned_zeropad()` is exception-table-sensitive and must preserve fault safety near page boundaries.

Test signals: lib/string and word-at-a-time selftests, fault-near-page-boundary tests, big/little-endian PPC32/PPC64 builds, and objtool/exception-table inspection.

Source read size: 206 lines, 4905 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/word-at-a-time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xics.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xics.h

Purpose: Declares common XICS interrupt-controller constants, ICP/ICS backend hooks, CPPR stack helpers, and public XICS lifecycle APIs.

Important APIs/types/functions: `XICS_IPI`, priority constants, backend init stubs, `struct icp_ops`, `struct ics`, global server/domain variables, `struct xics_cppr`, `xics_push_cppr()`, `xics_pop_cppr()`, `xics_set_base_cppr()`, `xics_cppr_top()`, per-CPU `xics_ipi_message`, and XICS setup/migration/IRQ APIs.

Control flow: Initialization selects native, hypervisor, OPAL, RTAS, or other backends; interrupt handling uses `icp_ops`, pushes CPPR priority around nested interrupts/IPIs, dispatches via an irq domain, and migrates or tears down interrupts during CPU hotplug/kexec.

State and persistence: State includes global default interrupt servers, `xics_host`, registered ICS instances, per-CPU CPPR stacks, and per-CPU IPI messages.

Dependencies and integration points: Depends on Linux interrupt/irq-domain APIs, OF nodes, SMP cpumasks, and platform-specific ICP/ICS implementations. Used by pSeries and PowerNV interrupt setup and KVM-adjacent code.

Risks: CPPR stack overflow/underflow changes interrupt priority masking. Wrong server selection can strand interrupts during hotplug or migration.

Test signals: XICS boot on pSeries/PowerNV, IPI stress, CPU hotplug, kexec teardown, IRQ affinity changes, and backend init fallback coverage.

Source read size: 177 lines, 4446 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xive-regs.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xive-regs.h

Purpose: Defines XIVE ESB and TIMA MMIO offsets, bit fields, and side-effect operation codes.

Important APIs/types/functions: ESB offsets such as `XIVE_ESB_STORE_EOI`, `XIVE_ESB_GET`, `XIVE_ESB_SET_PQ_*`, ordering offset `XIVE_ESB_LD_ST_MO`, PQ values, TIMA quadrants `TM_QW*`, byte/word offsets, QW word-2 bit masks, special TM operation offsets, and NSR field masks.

Control flow: XIVE code manipulates interrupt source P/Q state via 8-byte MMIO loads/stores and uses TIMA byte/word operations to acknowledge, pull/push contexts, and manage OS/HV/user interrupt state.

State and persistence: All state is hardware MMIO state: ESB P/Q pending bits, queue context validity, CPPR/IPB/NSR bytes, and TIMA context registers.

Dependencies and integration points: Depends on PowerPC bit macros and XIVE hardware/firmware programming models. Integrated by native, spapr, KVM, and xmon XIVE code.

Risks: Many offsets have side effects and require exact access sizes. Missing load-after-store ordering can break StoreEOI. Misusing QW permissions can corrupt interrupt context.

Test signals: XIVE interrupt delivery, EOI/retrigger tests, StoreEOI ordering checks, KVM XIVE tests, and hardware boot on POWER9/POWER10.

Source read size: 134 lines, 5083 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xive-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xive.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xive.h

Purpose: Declares the main PowerPC XIVE interrupt-controller software interface and KVM/native queue APIs.

Important APIs/types/functions: `xive_tima`, `xive_tima_os`, `xive_tima_offset`, `struct xive_irq_data`, XIVE IRQ flags, `struct xive_q`, `xive_enabled()`, init/SMP/teardown helpers, xmon dump helpers, and native VP/IRQ/queue configuration and state APIs.

Control flow: Platform init enables native or spapr XIVE, per-CPU setup maps TIMA and event queues, per-IRQ data caches ESB trigger/EOI pages, and KVM/native APIs allocate VPs, configure queues, sync sources/queues, and expose queue state.

State and persistence: Persistent state includes global enable/TIMA mapping, per-IRQ ESB data and saved/stale P flags, per-CPU queue indexes/toggles/counters, guest queue fields, and firmware-backed VP/IRQ allocations.

Dependencies and integration points: Depends on OPAL API, irq chips, atomic counters, MMIO mapping, SMP setup, and KVM. Stubbed out when `CONFIG_PPC_XIVE` is disabled.

Risks: EOI/trigger page handling is concurrency-sensitive. Saved/stale P bookkeeping must match queue state or interrupts can be lost or duplicated. KVM escalation interrupts may skip normal EOI.

Test signals: Native/spapr XIVE boot, IRQ affinity and hotplug, KVM guest interrupt tests, queue state save/restore, xmon dumps, and disabled-config compile coverage.

Source read size: 168 lines, 5147 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xive.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xmon.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xmon.h

Purpose: Declares hooks for the PowerPC xmon kernel debugger and its printk-style output function.

Important APIs/types/functions: `xmon_setup()`, `xmon(struct pt_regs *)`, `xmon_irq()`, SMP `cpus_are_in_xmon()`, and always-declared `xmon_printf()`.

Control flow: When `CONFIG_XMON` is enabled, exception/IRQ paths can enter xmon and setup registers debugger hooks; otherwise setup is a no-op while `xmon_printf` remains available to linked code.

State and persistence: Debugger state is implemented elsewhere; this header only exposes entry points.

Dependencies and integration points: Depends on irq return types and `pt_regs`. Integrated with trap, IRQ, SMP, and debug code.

Risks: Entry points run in fragile exception contexts. Incorrect stubbing can break builds with xmon disabled.

Test signals: CONFIG_XMON on/off builds, debugger entry via keyboard/sysrq/NMI paths, SMP rendezvous tests, and xmon output smoke tests.

Source read size: 29 lines, 611 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xmon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/Kbuild

Purpose: Lists generated PowerPC UAPI syscall-number headers for export.

Important APIs/types/functions: `generated-y += unistd_32.h` and `generated-y += unistd_64.h`.

Control flow: During headers generation, Kbuild emits both 32-bit and 64-bit syscall tables for UAPI installation.

State and persistence: No runtime state; generated header presence persists in the exported headers tree.

Dependencies and integration points: Depends on the kernel UAPI header generation pipeline and syscall table generation.

Risks: Omitting either generated header breaks userspace builds for that ABI.

Test signals: Run `make headers_install` and compile trivial programs including `<asm/unistd.h>` for ppc32 and ppc64.

Source read size: 3 lines, 89 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/auxvec.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/auxvec.h

Purpose: Defines PowerPC auxiliary vector entries exposed to ELF userspace.

Important APIs/types/functions: Cache block-size entries `AT_DCACHEBSIZE`, `AT_ICACHEBSIZE`, `AT_UCACHEBSIZE`, `AT_IGNOREPPC`, `AT_SYSINFO_EHDR`, detailed cache size/geometry entries, `AT_MINSIGSTKSZ`, and `AT_VECTOR_SIZE_ARCH`.

Control flow: ELF loader/kernel setup fills these keys in auxv; libc and applications read them for vDSO location, cache instruction safety, cache geometry, and signal stack sizing.

State and persistence: Auxv values are per-process ABI state copied at exec time.

Dependencies and integration points: Integrated with ELF binfmt, vdso setup, glibc expectations, and cache topology code.

Risks: Numeric values are ABI-stable; changing them breaks libc. Cache block versus line semantics must remain distinct.

Test signals: Inspect `/proc/self/auxv`, glibc startup/vDSO tests, cache geometry validation, and signal-stack sizing tests.

Source read size: 55 lines, 1846 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/auxvec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/bitsperlong.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/bitsperlong.h

Purpose: Selects PowerPC userspace word size for generic type headers.

Important APIs/types/functions: Defines `__BITS_PER_LONG` as 64 for `__powerpc64__` and 32 otherwise, then includes the generic header.

Control flow: Preprocessor selection occurs when userspace includes UAPI type headers.

State and persistence: No runtime state; affects compile-time ABI layout.

Dependencies and integration points: Depends on compiler-defined `__powerpc64__` and `asm-generic/bitsperlong.h`.

Risks: Wrong word size breaks ioctl, stat, signal, and syscall ABI structures.

Test signals: Headers-install compile tests for ppc32 and ppc64 ABIs and sizeof checks for long-based structs.

Source read size: 13 lines, 312 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/bitsperlong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/bootx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/bootx.h

Purpose: Documents the legacy BootX-to-Linux boot information structure used by old Macintosh PowerPC systems.

Important APIs/types/functions: Boot magic/register contract, `BOOT_INFO_VERSION`, architecture flags, `MAX_MEM_MAP_SIZE`, `boot_info_map_entry_t`, and `boot_infos_t` with framebuffer, device tree, ramdisk, command line, memory map, and total parameter fields.

Control flow: BootX enters the kernel with r3 magic and r4 pointing to `boot_infos`; early boot parses appended device tree/arguments/ramdisk and may use framebuffer fields for early text.

State and persistence: The structure is persistent boot-time handoff state supplied by firmware/loader and consumed before normal device discovery.

Dependencies and integration points: Depends on Linux integer types and optional MacOS headers. Integrated by old PowerMac boot and early display code.

Risks: Layout and alignment are ABI-sensitive. Offsets are relative to the structure and invalid values can mislocate the device tree or ramdisk.

Test signals: Old PowerMac/BootX boot tests, structure layout checks, and early framebuffer/device-tree parsing smoke tests.

Source read size: 133 lines, 4416 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/bootx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/byteorder.h

Purpose: Selects PowerPC userspace byteorder helpers for little- or big-endian builds.

Important APIs/types/functions: Includes `linux/byteorder/little_endian.h` when `__LITTLE_ENDIAN__` is set, otherwise big-endian helpers.

Control flow: Compile-time include selection provides conversion macros to userspace/kernel UAPI consumers.

State and persistence: No runtime state; affects compile-time endian conversions.

Dependencies and integration points: Depends on compiler/endian defines and Linux byteorder headers.

Risks: Wrong include corrupts multibyte UAPI field interpretation on cross-endian builds.

Test signals: Headers compile for powerpc64le and big-endian powerpc plus byte-swap macro unit checks.

Source read size: 17 lines, 550 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/cputable.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/cputable.h

Purpose: Defines PowerPC hardware capability bits reported through `AT_HWCAP` and `AT_HWCAP2`.

Important APIs/types/functions: `PPC_FEATURE_*` bits for 32/64-bit, FPU, Altivec, MMU, SPE, architecture generations, endian features, and `PPC_FEATURE2_*` bits for ISA 2.07 through 3.1, HTM, DSCR, EBB, vector crypto, DARN, SCV, MMA, and related features.

Control flow: Kernel CPU probing builds HWCAP masks; ELF exec exposes them in auxv; libc and applications branch on bits for optimized or required instruction use.

State and persistence: Per-process auxv state mirrors CPU/platform feature state.

Dependencies and integration points: Integrated with CPU feature discovery, OPAL/skiboot device-tree bindings, ELF auxvec setup, glibc, JITs, and optimized libraries.

Risks: Bit values are ABI-stable and coordinated with firmware bindings. Reusing reserved bits or misreporting features can cause illegal instruction faults.

Test signals: Auxv HWCAP inspection across CPU generations, userspace instruction dispatch tests, and CPU feature table build coverage.

Source read size: 63 lines, 2399 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/cputable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/eeh.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/eeh.h

Purpose: Defines user-visible PowerPC EEH PCI error state and error injection classifications.

Important APIs/types/functions: PE state constants `EEH_PE_STATE_*`, error type constants, and error function constants for load/store/config/DMA address/data/master/target events.

Control flow: EEH user interfaces and tooling pass these numeric constants to query or inject PCI error conditions.

State and persistence: No state owned; values describe PCI PE state maintained by EEH core/firmware.

Dependencies and integration points: Integrated with EEH kernel code, debugfs/sysfs/ioctl-like users, and platform firmware error handling.

Risks: Numeric ABI changes break diagnostic tooling. Function ranges must match kernel validation.

Test signals: EEH recovery and error injection tests on pSeries/PowerNV PCI, plus userspace tooling compile checks.

Source read size: 44 lines, 1580 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/eeh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/elf.h

Purpose: Defines PowerPC ELF relocation numbers, register-set types, core-dump register counts, ELF class/data selection, and vector register layouts.

Important APIs/types/functions: `R_PPC_*`, TLS relocations, `R_PPC64_*`, `ELF_N*` register counts, `elf_gregset_t32/64`, `elf_fpregset_t`, `elf_vrregset_t`, `ELF_ARCH`, `ELF_CLASS`, and `ELF_DATA`.

Control flow: Linkers/loaders use relocation numbers; kernel core dump and ptrace paths use register-set typedefs; userspace debuggers interpret note layouts from these ABI definitions.

State and persistence: No runtime state, but it fixes persistent ELF object and core-file ABI formats.

Dependencies and integration points: Depends on Linux types, PowerPC ptrace/cputable/auxvec headers, and `__vector128`. Integrated by binfmt_elf, core dumping, ptrace, GDB, loaders, and toolchains.

Risks: Relocation values and register layouts are immutable ABI. VMX/VSX layout must stay compatible with ptrace and signal contexts.

Test signals: Toolchain relocation tests, ELF loader smoke tests, core dump register-note validation, ptrace tests, and ppc32/ppc64 endian variants.

Source read size: 298 lines, 13415 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/epapr_hcalls.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/epapr_hcalls.h

Purpose: Defines the ePAPR hypercall token and return-code ABI for PowerPC guests.

Important APIs/types/functions: `EV_*` hypercall numbers, vendor IDs, `EV_BYTE_CHANNEL_MAX_BYTES`, `_EV_HCALL_TOKEN()`, `EV_HCALL_TOKEN()`, and ePAPR return codes `EV_SUCCESS` through `EV_BUFFER_OVERFLOW`.

Control flow: Guests compose hypercall tokens from vendor ID and call number, issue the hypercall through architecture code, and interpret numeric return codes.

State and persistence: No state owned; constants describe hypervisor interface state and error outcomes.

Dependencies and integration points: Used by KVM paravirtual code, ePAPR guests, byte channels, interrupt-controller calls, and idle/doorbell paths.

Risks: Token encoding and return codes are ABI. Incorrect vendor IDs collide with private hypercalls.

Test signals: KVM/ePAPR guest boot, byte-channel tests, interrupt hcall tests, and headers compile under GPL/BSD consumers.

Source read size: 99 lines, 4274 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/epapr_hcalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/errno.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/errno.h

Purpose: Overrides the generic `EDEADLOCK` value for PowerPC userspace ABI compatibility.

Important APIs/types/functions: Includes generic errno then redefines `EDEADLOCK` to 58.

Control flow: UAPI inclusion first clears any existing value, imports generic errno, and then applies the PowerPC-specific value.

State and persistence: No runtime state; numeric errno ABI persists in userspace programs.

Dependencies and integration points: Depends on `asm-generic/errno.h` and libc errno integration.

Risks: Changing the value breaks old binaries and source compatibility.

Test signals: Headers compile and errno numeric conformance checks for PowerPC libc.

Source read size: 11 lines, 278 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/fcntl.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/fcntl.h

Purpose: Defines PowerPC-specific open flag numeric values before importing generic fcntl definitions.

Important APIs/types/functions: `O_DIRECTORY`, `O_NOFOLLOW`, `O_LARGEFILE`, and `O_DIRECT` values.

Control flow: Userspace includes fcntl definitions; these architecture values override/precede generic handling used by syscalls.

State and persistence: No state; constants define syscall ABI bits.

Dependencies and integration points: Integrated with VFS syscall flag decoding and libc headers through `asm-generic/fcntl.h`.

Risks: Flag values are ABI-stable. Collisions with generic flags or wrong octal values alter open behavior.

Test signals: Headers compile and syscall tests for directory/no-follow/largefile/direct-open behavior on PowerPC.

Source read size: 12 lines, 367 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/fcntl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ioctl.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ioctl.h

Purpose: Defines PowerPC ioctl command bitfield layout.

Important APIs/types/functions: `_IOC_SIZEBITS`, `_IOC_DIRBITS`, `_IOC_NONE`, `_IOC_READ`, `_IOC_WRITE`, followed by generic ioctl macros.

Control flow: The generic `_IOC` macros use these widths and direction values to encode/decode ioctl numbers.

State and persistence: No runtime state; ioctl numbers persist as userspace/kernel ABI.

Dependencies and integration points: Used by all PowerPC UAPI ioctl headers and libc ioctl definitions.

Risks: Changing size/dir widths or direction bits changes every encoded ioctl number.

Test signals: Compile-time ioctl number checks and runtime tests for termios, framebuffer, PAPR, and other PowerPC ioctls.

Source read size: 14 lines, 302 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ioctls.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ioctls.h

Purpose: Defines PowerPC terminal, file, pseudo-terminal, serial, and console ioctl numbers.

Important APIs/types/functions: `FIOC*`, `TIOC*`, `TCGETS/TCSETS*`, modem bits `TIOCM_*`, packet mode bits `TIOCPKT_*`, serial ioctls, PTY helpers, and ISO7816 ioctls.

Control flow: TTY/VFS drivers decode these command numbers from userspace `ioctl()` calls and read/write the associated structures.

State and persistence: No state owned; constants address driver-maintained tty/file state.

Dependencies and integration points: Depends on PowerPC ioctl encoding, termios structure declarations, and generic tty/serial drivers.

Risks: Numbers are ABI-stable and include legacy BSD/System V compatibility. Incorrect structure direction/size breaks 32-bit and 64-bit userspace.

Test signals: TTY ioctl regression tests, pty tests, serial control-line tests, and ioctl-number comparison with libc expectations.

Source read size: 123 lines, 4359 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ioctls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ipcbuf.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ipcbuf.h

Purpose: Defines PowerPC `ipc64_perm` layout for SysV IPC user ABI.

Important APIs/types/functions: `struct ipc64_perm` with key, uid/gid/cuid/cgid, mode, sequence, padding, and unused 64-bit slots.

Control flow: SysV IPC syscalls copy this structure between kernel and userspace for permission metadata.

State and persistence: Represents persistent IPC object permission state, with padding reserved for ABI growth/alignment.

Dependencies and integration points: Depends on Linux UAPI types and is embedded by msg/sem/shm buffer headers.

Risks: Field order, sizes, and padding are ABI-sensitive, especially across 32-bit and 64-bit tasks.

Test signals: SysV IPC permission tests, compat syscall tests, and structure layout checks against libc.

Source read size: 35 lines, 1057 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ipcbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/kvm.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/kvm.h

Purpose: Defines the extensive PowerPC KVM userspace ABI for vCPU registers, special registers, debug controls, TCE/RMA/RTAS/MMU setup, one-reg IDs, interrupt controllers, XIVE, and PPC-specific VM capabilities.

Important APIs/types/functions: Feature selectors `__KVM_HAVE_*`, `struct kvm_regs`, `struct kvm_sregs`, FPU/debug structs, interrupt constants, CPU type IDs, SPAPR TCE/RMA/RTAS structs, BookE TLB structs, HTAB/MMU/radix/CPU-character structs, hundreds of `KVM_REG_PPC_*` one-reg IDs, XICS/XIVE device groups, `struct kvm_ppc_xive_eq`, PV info, SMMU info, and HPT resize structures.

Control flow: Userspace VMMs issue KVM ioctls using these structs and register IDs to create devices, save/restore vCPU state, configure MMU/TCE/interrupts, inject interrupts, expose paravirtual info, and migrate machines.

State and persistence: Defines persistent VM/vCPU ABI state: GPRs, SPRs, MMU state, debug breakpoints, interrupt-controller state, event queues, page-size geometry, and migration streams.

Dependencies and integration points: Depends on Linux types and generic KVM ioctls. Integrated by QEMU, kvmtool, KVM Book3S/BookE implementations, XICS/XIVE device models, and migration tooling.

Risks: This is a migration and virtualization ABI; field padding, feature bits, one-reg sizes, and update semantics must not change incompatibly. Reserved fields must be preserved by userspace.

Test signals: KVM selftests for PPC, QEMU boot/migration across Book3S/BookE, one-reg get/set round trips, XICS/XIVE interrupt tests, TCE/MMU setup tests, and ABI structure size checks.

Source read size: 769 lines, 25469 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/kvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/kvm_para.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/kvm_para.h

Purpose: Defines PowerPC KVM paravirtual shared-page ABI and KVM hypercall token helpers.

Important APIs/types/functions: `struct kvm_vcpu_arch_shared`, magic `KVM_SC_MAGIC_R0`, `KVM_HCALL_TOKEN()`, `KVM_FEATURE_MAGIC_PAGE`, `KVM_MAGIC_FEAT_*`, and `MAGIC_PAGE_FLAG_NOT_MAPPED_NX`.

Control flow: Guest and host share selected vCPU state in a magic page; guest code uses advertised feature bits and KVM vendor hypercall tokens for paravirtual operations.

State and persistence: Shared page fields persist per vCPU and mirror scratch registers, exception state, segment registers, MAS registers, PIR, and high SPRGs.

Dependencies and integration points: Depends on ePAPR hcall definitions and KVM guest/host code. Documented by PowerPC KVM paravirtual docs.

Risks: Struct fields may only be appended; alignment and feature advertisement protect old guests. Inconsistent SPRG sharing can expose stale state to guest userspace.

Test signals: KVM guest boot with magic page enabled, paravirt feature probing, shared-register consistency tests, and migration compatibility checks.

Source read size: 85 lines, 2140 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/kvm_para.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/mman.h

Purpose: Defines PowerPC memory mapping and protection flags.

Important APIs/types/functions: `PROT_SAO`, PowerPC `MAP_*` values, `MCL_*` values, and pkey execute-disable override with `PKEY_ACCESS_MASK`.

Control flow: mmap/mprotect/mlock/pkey syscalls decode these bits from userspace and apply PowerPC memory-management semantics.

State and persistence: Bits contribute to VMA protection and locking state maintained by mm core.

Dependencies and integration points: Depends on generic mman-common and PowerPC pkey support.

Risks: Flag collisions break syscall ABI. `PROT_SAO` and pkey execute-disable must match architecture behavior.

Test signals: mmap/mprotect/mlock tests, pkey permission tests including execute disable, and compat ABI checks.

Source read size: 35 lines, 1294 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/msgbuf.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/msgbuf.h

Purpose: Defines PowerPC SysV message queue status layout.

Important APIs/types/functions: `struct msqid64_ds` with `ipc64_perm`, timestamp fields split on 32-bit, byte/message limits, last sender/receiver PIDs, and padding.

Control flow: `msgctl` copies this layout to/from userspace depending on 32-bit or 64-bit ABI.

State and persistence: Represents persistent message queue metadata state.

Dependencies and integration points: Depends on `ipcbuf.h` and kernel pid/time UAPI types.

Risks: Timestamp split/high fields and padding are ABI-sensitive for compat tasks.

Test signals: SysV message queue tests on ppc32/ppc64, Y2038-oriented compat layout tests, and libc structure checks.

Source read size: 36 lines, 1159 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/msgbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/nvram.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/nvram.h

Purpose: Defines PowerPC NVRAM partition signatures, PowerMac XPRAM identifiers, location structure, and `/dev/nvram` ioctls.

Important APIs/types/functions: `NVRAM_SIG_*`, `pmac_nvram_*` enum values, XPRAM offsets, `struct pmac_machine_location`, obsolete and current NVRAM ioctl numbers.

Control flow: Userspace tools identify partitions and issue ioctls to discover partition offsets or request NVRAM sync.

State and persistence: NVRAM contents persist across reboots; structures describe firmware/PowerMac state.

Dependencies and integration points: Depends on PowerPC ioctl encoding and nvram driver implementation.

Risks: Partition signatures and ioctl numbers are ABI. Writing wrong offsets can corrupt firmware environment or panic logs.

Test signals: NVRAM tool compile tests, ioctl smoke tests on PowerMac/PowerNV where available, and partition parsing validation.

Source read size: 63 lines, 2077 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/nvram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/opal-prd.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/opal-prd.h

Purpose: Defines the userspace ABI for OPAL runtime diagnostics daemon access on PowerNV systems.

Important APIs/types/functions: `OPAL_PRD_KERNEL_VERSION`, ioctls `OPAL_PRD_GET_INFO`, `OPAL_PRD_SCOM_READ`, `OPAL_PRD_SCOM_WRITE`, `struct opal_prd_info`, and `struct opal_prd_scom`.

Control flow: The PRD daemon opens `/dev/opal-prd`, queries interface info, and requests SCOM reads/writes with chip/address/data fields and firmware return code.

State and persistence: The kernel mediates firmware diagnostic state; SCOM accesses target persistent hardware registers.

Dependencies and integration points: Depends on OPAL firmware, PowerNV PRD driver, ioctl encoding, and userspace opal-prd daemon.

Risks: SCOM access is privileged and hardware-sensitive. ABI versioning must remain backward compatible.

Test signals: opal-prd daemon startup, GET_INFO ioctl, SCOM read/write error-path tests on PowerNV, and headers compile tests.

Source read size: 59 lines, 1784 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/opal-prd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-hvpipe.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-hvpipe.h

Purpose: Defines `/dev/papr-hvpipe` header format and handle-creation ioctl for PAPR hypervisor pipe payload exchange.

Important APIs/types/functions: `struct papr_hvpipe_hdr`, `PAPR_HVPIPE_IOC_CREATE_HANDLE`, `HVPIPE_MSG_AVAILABLE`, and `HVPIPE_LOST_CONNECTION`.

Control flow: Userspace creates a handle, reads messages prefixed by the header, and checks flags for payload availability or closed/unavailable pipe state.

State and persistence: Per-handle pipe connection state lives in the driver/hypervisor; the header serializes message status.

Dependencies and integration points: Depends on PAPR miscdev ioctl ID, PowerPC ioctl encoding, and Linux types.

Risks: Header reserved bytes and version must remain compatible. Lost-connection handling must not be confused with empty payload.

Test signals: PAPR hvpipe userspace read/ioctl tests, connection loss simulations, and structure size checks.

Source read size: 33 lines, 816 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-hvpipe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-indices.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-indices.h

Purpose: Defines PAPR sensor/indicator index and dynamic state ioctl blocks.

Important APIs/types/functions: `LOC_CODE_SIZE`, `RTAS_GET_INDICES_BUF_SIZE`, `struct papr_indices_io_block`, `PAPR_INDICES_IOC_GET`, `PAPR_DYNAMIC_SENSOR_IOC_GET`, and `PAPR_DYNAMIC_INDICATOR_IOC_SET`.

Control flow: Userspace requests index handles or gets/sets dynamic sensor/indicator state by passing either type selectors or token/state/location-code parameters.

State and persistence: Driver and firmware own sensor/indicator state; the union is the serialized ioctl work block.

Dependencies and integration points: Depends on PAPR miscdev ioctl ID, RTAS/PAPR firmware interfaces, and `SZ_4K` sizing from Linux types context.

Risks: Union interpretation depends on ioctl command. Location codes must fit 79 chars plus NUL. Buffer-size assumptions tie to RTAS response limits.

Test signals: PAPR indices userspace ioctl tests, sensor get/set on pSeries, invalid token/location tests, and ABI size checks.

Source read size: 41 lines, 1294 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-indices.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-miscdev.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-miscdev.h

Purpose: Provides the common ioctl type ID for PAPR misc character devices.

Important APIs/types/functions: Enum value `PAPR_MISCDEV_IOC_ID = 0xb2`.

Control flow: PAPR UAPI headers use this ID when constructing ioctl numbers for their misc devices.

State and persistence: No runtime state; it reserves an ioctl namespace.

Dependencies and integration points: Included by PAPR sysparm, VPD, indices, dump, attestation, and hvpipe headers.

Risks: Changing the ID renumbers every PAPR miscdev ioctl.

Test signals: Compile-time ioctl-number checks across PAPR headers and userspace tool compatibility tests.

Source read size: 9 lines, 199 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-miscdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-physical-attestation.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-physical-attestation.h

Purpose: Defines the PAPR physical attestation command ioctl payload.

Important APIs/types/functions: `PAPR_PHYATTEST_MAX_INPUT`, `struct papr_phy_attest_io_block`, and `PAPR_PHY_ATTEST_IOC_HANDLE`.

Control flow: Userspace passes a versioned attestation command, TCG version, big-endian length/correlator, and payload; ioctl returns a handle for the attestation exchange.

State and persistence: Attestation state is firmware/driver-managed; the block carries command input and correlator state.

Dependencies and integration points: Depends on PAPR miscdev ioctl ID, PowerPC ioctl encoding, Linux types, and PAPR 2.13 attestation structures.

Risks: Maximum input is sized to 4K minus header; length endianness and bounds must be validated. Payload format is security-sensitive.

Test signals: Attestation ioctl size/bounds tests, firmware error mapping tests, and userspace structure layout checks.

Source read size: 31 lines, 854 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-physical-attestation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-platform-dump.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-platform-dump.h

Purpose: Defines ioctls for PAPR platform dump handle creation and invalidation.

Important APIs/types/functions: `PAPR_PLATFORM_DUMP_IOC_CREATE_HANDLE` and `PAPR_PLATFORM_DUMP_IOC_INVALIDATE`, both keyed by dump tag.

Control flow: Userspace creates a file descriptor for a platform dump tag, reads dump data through the handle, and can invalidate the firmware dump record.

State and persistence: Platform dump content persists in firmware/driver storage until invalidated.

Dependencies and integration points: Depends on PAPR miscdev ioctl ID and platform dump driver.

Risks: Invalidating the wrong tag can discard diagnostic data. Ioctl numbers are ABI.

Test signals: Platform dump discovery/read/invalidate tests on pSeries and error-path tests for missing tags.

Source read size: 16 lines, 528 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-platform-dump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-sysparm.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-sysparm.h

Purpose: Defines PAPR system-parameter get/set ioctl payload and limits.

Important APIs/types/functions: `PAPR_SYSPARM_MAX_INPUT`, `PAPR_SYSPARM_MAX_OUTPUT`, `struct papr_sysparm_io_block`, `PAPR_SYSPARM_IOC_GET`, and `PAPR_SYSPARM_IOC_SET`.

Control flow: Userspace supplies parameter ID, length, and optional data. GET may use input data for special parameters and returns output length/data; SET sends the supplied data to firmware.

State and persistence: System parameters persist in platform firmware or partition configuration; the ioctl block is transient.

Dependencies and integration points: Depends on PAPR miscdev ioctl ID and RTAS `ibm,get-system-parameter`/set equivalents.

Risks: GET uses `_IOWR` because input data can matter. On errors data is indeterminate, so callers must not reuse stale values. Bounds and firmware errno mapping are important.

Test signals: GET/SET ioctl tests for supported/unsupported parameters, bad lengths/formats, permission failures, and ABI size checks.

Source read size: 58 lines, 2072 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-sysparm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-vpd.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-vpd.h

Purpose: Defines PAPR VPD location-code ioctl ABI.

Important APIs/types/functions: `struct papr_location_code` with 80-byte string and `PAPR_VPD_IOC_CREATE_HANDLE`.

Control flow: Userspace passes a location code and receives a handle file descriptor to read matching VPD data.

State and persistence: VPD data is platform firmware state; the location-code block is ioctl input.

Dependencies and integration points: Depends on PAPR miscdev ioctl ID and VPD driver/firmware interfaces.

Risks: Location code length is fixed by PAPR. Missing NUL or overlong strings must be rejected safely.

Test signals: VPD handle creation/read tests, invalid location-code tests, and structure layout checks.

Source read size: 22 lines, 553 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-vpd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/perf_event.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/perf_event.h

Purpose: Defines the PowerPC perf event configuration bit used to request Event Based Branching.

Important APIs/types/functions: `PERF_EVENT_CONFIG_EBB_SHIFT` as bit 63 of `perf_event_attr.config`.

Control flow: Userspace sets bit 63 in perf config; PowerPC perf code interprets it as an EBB request during event creation.

State and persistence: No state here; it controls per-event perf configuration state.

Dependencies and integration points: Integrated with perf_event ABI and PowerPC PMU/EBB implementation.

Risks: The high bit must not collide with raw PMU event encoding. Misinterpretation can enable wrong event delivery mode.

Test signals: perf EBB selftests, event creation validation, and perf tool compile tests.

Source read size: 19 lines, 565 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/perf_regs.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/perf_regs.h

Purpose: Enumerates PowerPC register IDs and masks for perf sample register capture.

Important APIs/types/functions: `enum perf_event_powerpc_regs`, `PERF_REG_PMU_MASK`, `PERF_REG_PMU_MASK_300`, and `PERF_REG_PMU_MASK_31`.

Control flow: Userspace perf requests sample_regs masks; kernel validates and captures GPRs, special registers, and PMU SPRs depending on CPU generation.

State and persistence: No state owned; masks describe per-sample register payload state.

Dependencies and integration points: Integrated with perf core, PowerPC PMU code, perf tools, and CPU feature gating for ISA 3.0/3.1.

Risks: Enum order is ABI. Masks must match actually readable registers or perf samples become invalid or fault-prone.

Test signals: perf sample_regs tests, POWER9/POWER10 PMU register capture, and perf tool decoding checks.

Source read size: 95 lines, 2763 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/posix_types.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/posix_types.h

Purpose: Defines PowerPC-specific POSIX base type overrides before generic POSIX types.

Important APIs/types/functions: On ppc64 `__kernel_old_dev_t` is unsigned long; on ppc32 `__kernel_ipc_pid_t` is short.

Control flow: Compile-time ABI type selection occurs before including generic posix types.

State and persistence: No runtime state; affects structure layout and syscall ABI.

Dependencies and integration points: Used by generic POSIX UAPI headers and libc.

Risks: Type width changes break stat, IPC, and legacy device-number ABI.

Test signals: Headers compile for ppc32/ppc64 and libc layout conformance checks.

Source read size: 21 lines, 594 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/posix_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ps3fb.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ps3fb.h

Purpose: Defines PlayStation 3 framebuffer ioctl ABI.

Important APIs/types/functions: `PS3FB_IOCTL_*`, fallback `FBIO_WAITFORVSYNC`, and `struct ps3fb_ioctl_res`.

Control flow: Userspace framebuffer tools issue ioctls to set/get mode, get screen info, enable/disable special operation, request flip, and wait for vsync.

State and persistence: Framebuffer mode and flip state live in the ps3fb driver/hardware; the struct reports resolution, offset, and frame count.

Dependencies and integration points: Depends on Linux ioctl/types and the PS3 framebuffer driver.

Risks: Ioctl numbers and struct layout are ABI. Mode changes can disrupt console/display users.

Test signals: ps3fb ioctl smoke tests, mode set/get tests, vsync wait, and headers compile checks.

Source read size: 33 lines, 1110 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ps3fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ptrace.h

Purpose: Defines PowerPC ptrace register frame layout, offsets, ptrace request numbers, and hardware breakpoint ABI.

Important APIs/types/functions: `struct pt_regs`/`user_pt_regs`, `PT_*` offsets, FP/VMX/VSX register offsets, ptrace requests for VR/EVR/VSR, syscall emulation and 32-on-64 access, `struct ppc_debug_info`, `struct ppc_hw_breakpoint`, and breakpoint feature/mode/condition flags.

Control flow: Kernel entry saves volatile registers in this layout; ptrace and core code use offsets to copy registers; debuggers issue requests to get/set register sets or configure hardware breakpoints/watchpoints.

State and persistence: Represents per-thread register and debug state visible to tracers and core dumps.

Dependencies and integration points: Depends on Linux types and architecture trap/ptrace/debug register code. Integrated by GDB, strace, perf, and signal/core paths.

Risks: Offsets are binary ABI and correspond to kernel stack layouts. Hardware breakpoint flags must match DAWR/IABR/DABR capabilities and alignment limits.

Test signals: ptrace register get/set tests, GDB single-step/syscall emulation, hardware breakpoint/watchpoint tests, core dump validation, and compat 32/64 tracing tests.

Source read size: 272 lines, 7793 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/sembuf.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/sembuf.h

Purpose: Defines PowerPC SysV semaphore status layout.

Important APIs/types/functions: `struct semid64_ds` with permission, timestamp fields split for 32-bit, semaphore count, and padding.

Control flow: `semctl` copies this structure for IPC status and updates.

State and persistence: Represents persistent semaphore set metadata.

Dependencies and integration points: Depends on `ipcbuf.h` and SysV IPC kernel code.

Risks: Timestamp split fields and padding are ABI-sensitive.

Test signals: SysV semaphore tests on ppc32/ppc64, compat layout checks, and libc conformance.

Source read size: 39 lines, 1144 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/sembuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/setup.h

Purpose: Defines the maximum PowerPC kernel command-line size visible to userspace tools.

Important APIs/types/functions: `COMMAND_LINE_SIZE` set to 2048.

Control flow: Boot and proc interfaces use this size when handling kernel command-line buffers.

State and persistence: No state owned; bounds boot-time command-line storage.

Dependencies and integration points: Integrated by setup code and tools including kexec or bootloaders that include UAPI headers.

Risks: Changing the value can truncate or alter assumptions in boot tooling.

Test signals: Boot with long command lines and headers compile checks.

Source read size: 7 lines, 203 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/shmbuf.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/shmbuf.h

Purpose: Defines PowerPC SysV shared-memory status and limits structures.

Important APIs/types/functions: `struct shmid64_ds` and `struct shminfo64` with 32-bit timestamp splits, segment size, PIDs, attach count, and padding.

Control flow: `shmctl` copies these layouts for shared-memory metadata and limit queries.

State and persistence: Represents persistent shared-memory segment metadata and system limits.

Dependencies and integration points: Depends on IPC and POSIX type headers and SysV SHM kernel code.

Risks: Field order, timestamp handling, and padding are ABI-sensitive.

Test signals: SysV shared-memory tests, compat layout checks, and libc structure comparisons.

Source read size: 60 lines, 1723 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/shmbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/sigcontext.h

Purpose: Defines PowerPC signal context layout, including 64-bit register, FP, VMX, and VSX save areas.

Important APIs/types/functions: `struct sigcontext` with signal metadata, handler, old mask, regs pointer, 64-bit `gp_regs`, `fp_regs`, vector-register pointer, and `vmx_reserve` backing storage.

Control flow: Signal delivery fills this context in the user signal frame; `sigreturn` reads it back to restore interrupted CPU state. On ppc64 VMX/VSX data is aligned through the `v_regs` pointer into reserved storage.

State and persistence: The user signal frame is persistent until handler return and serializes register state.

Dependencies and integration points: Depends on ptrace and ELF register definitions. Integrated by signal delivery, ptrace-compatible register layouts, and libc signal trampolines.

Risks: Signal frame layout is strict ABI. Vector/VSX reserve sizing and alignment must remain compatible with old userspace.

Test signals: Signal delivery/sigreturn tests with FP/VMX/VSX, altstack tests, GDB signal-frame unwinding, and ppc64 layout checks.

Source read size: 92 lines, 4444 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/signal.h

Purpose: Defines PowerPC signal numbers, signal-set layout, signal action structs, altstack type, stack sizes, and 32-bit debug-sigreturn operations.

Important APIs/types/functions: `_NSIG`, `_NSIG_BPW`, `sigset_t`, signal numbers, `SA_RESTORER`, `MINSIGSTKSZ`, `SIGSTKSZ`, userspace `old_sigaction`, `sigaction`, `stack_t`, 32-bit `struct sig_dbg_op`, and `SIG_DBG_*` constants.

Control flow: Kernel and libc use these constants and structures for signal install, delivery, alternate stacks, and 32-bit debug signal return behavior.

State and persistence: Signal masks/actions and altstack settings persist per task in kernel state; structures define the userspace ABI view.

Dependencies and integration points: Depends on Linux types and generic signal definitions. Integrated by signal syscalls, libc, debuggers, and signal frame code.

Risks: Signal numbers, stack sizes, and structure layout are ABI. ppc64 has larger minimum stack due to larger context state.

Test signals: Signal syscall tests, realtime signal mask tests, altstack sizing tests, 32-bit debug signal return tests, and libc ABI checks.

Source read size: 119 lines, 2595 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/socket.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/socket.h

Purpose: Defines PowerPC-specific socket option numbers that differ before importing generic socket options.

Important APIs/types/functions: `SO_RCVLOWAT`, `SO_SNDLOWAT`, old timeout options, `SO_PASSCRED`, and `SO_PEERCRED`.

Control flow: Socket syscalls decode these option numbers for getsockopt/setsockopt, then generic options fill the rest.

State and persistence: Options correspond to per-socket state in networking core.

Dependencies and integration points: Depends on `asm-generic/socket.h` and socket syscall implementation.

Risks: Option numbers are ABI; mismatches break libc/network applications.

Test signals: Socket option regression tests and cross-checks with PowerPC libc headers.

Source read size: 21 lines, 600 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/spu_info.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/spu_info.h

Purpose: Defines Cell SPU DMA and proxy-DMA information structures exposed to userspace tooling.

Important APIs/types/functions: Userspace `struct mfc_cq_sr`, `struct spu_dma_info`, and `struct spu_proxydma_info`.

Control flow: SPU filesystem/debug interfaces fill these structures with DMA queue status and command data for userspace inspection.

State and persistence: Structures serialize SPU DMA engine state and command queue contents.

Dependencies and integration points: Depends on Linux types and Cell SPU support.

Risks: Struct layouts are ABI for Cell debugging tools. The `mfc_cq_sr` userspace guard avoids duplicate kernel declarations.

Test signals: Cell/SPU tooling compile tests, SPU DMA info reads, and structure layout checks.

Source read size: 40 lines, 832 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/spu_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/stat.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/stat.h

Purpose: Defines PowerPC legacy and current stat structure layouts.

Important APIs/types/functions: `STAT_HAVE_NSEC`, 32-bit `struct __old_kernel_stat`, `struct stat`, and 32-bit `struct stat64` matching glibc 2.1 layout.

Control flow: stat-family syscalls copy file metadata into these ABI-specific layouts, with ppc64 and ppc32 field ordering differences.

State and persistence: Structures serialize VFS inode metadata and timestamps to userspace.

Dependencies and integration points: Depends on Linux UAPI types, VFS stat conversion, and libc.

Risks: Field sizes/order and nanosecond fields are ABI-sensitive. 32-bit `stat64` must match old glibc expectations.

Test signals: stat/lstat/fstat tests on ppc32/ppc64, large inode/device tests, timestamp nanosecond checks, and libc structure comparisons.

Source read size: 82 lines, 2362 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/swab.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/swab.h

Purpose: Selects PowerPC byte-swap implementation details for UAPI consumers.

Important APIs/types/functions: Defines `__SWAB_64_THRU_32__` for GCC on non-ppc64, then relies on generic swab handling.

Control flow: Compile-time macro choice tells generic swab code to implement 64-bit byte swaps through 32-bit operations on PPC32.

State and persistence: No runtime state.

Dependencies and integration points: Depends on Linux types/compiler headers and generic swab machinery.

Risks: Incorrect macro selection can produce inefficient or wrong 64-bit byte swaps on 32-bit builds.

Test signals: Headers compile and byte-swap unit checks for ppc32/ppc64 with GCC-compatible compilers.

Source read size: 24 lines, 602 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/swab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/termbits.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/termbits.h

Purpose: Defines PowerPC termios/ktermios layout, control-character indexes, baud constants, and terminal flag bits.

Important APIs/types/functions: `tcflag_t`, `NCCS`, `struct termios`, `struct ktermios`, `V*` character indexes, input/output/control/local mode bits, baud values, and `TCSANOW/TCSADRAIN/TCSAFLUSH`.

Control flow: TTY ioctls copy termios structures between userspace and kernel; line disciplines and drivers interpret the flag bits.

State and persistence: Termios settings persist per tty in kernel state and are serialized through this layout.

Dependencies and integration points: Depends on generic termbits common definitions and tty core.

Risks: The layout is libc-visible and differs by architecture. Reordering `c_cc` or changing flag values breaks terminal applications.

Test signals: termios ioctl tests, baud-rate tests, pty regression tests, and libc header conformance.

Source read size: 157 lines, 4104 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/termbits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/termios.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/termios.h

Purpose: Defines legacy PowerPC terminal helper structures layered on termbits/ioctls.

Important APIs/types/functions: `struct sgttyb`, `struct tchars`, `struct ltchars`, `struct winsize`, `NCC`, `struct termio`, and legacy `_V*` control-character indexes.

Control flow: Legacy tty ioctls and compatibility code copy these structures for old terminal APIs, while modern code uses `struct termios` from termbits.

State and persistence: Represents per-tty line discipline, window size, and legacy character settings.

Dependencies and integration points: Depends on PowerPC ioctls and termbits. Integrated with tty compatibility handlers and libc.

Risks: Legacy structure layout remains ABI for old programs.

Test signals: TTY legacy ioctl tests, window-size ioctls, pty tests, and libc structure checks.

Source read size: 77 lines, 1712 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/termios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/tm.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/tm.h

Purpose: Defines PowerPC transactional memory abort cause codes used by kernel and virtualization.

Important APIs/types/functions: `TM_CAUSE_PERSISTENT`, KVM/PAPR causes, and kernel causes for reschedule, TLB invalidation, facility unavailable, syscall, misc, signal, alignment, and emulation aborts.

Control flow: When the kernel aborts a transaction, it records an encoded cause that can be reflected into transactional state such as TEXASR conventions.

State and persistence: No state owned; constants describe abort state persisted in TM registers/signal context.

Dependencies and integration points: Integrated by transactional memory exception, signal, and KVM code.

Risks: Cause values are ABI/diagnostic-visible and overlap PAPR-reserved ranges intentionally.

Test signals: TM selftests for abort causes, signal context validation, and KVM TM tests where supported.

Source read size: 21 lines, 734 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/tm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/types.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/types.h

Purpose: Selects PowerPC integer type model and defines aligned 128-bit vector storage for UAPI.

Important APIs/types/functions: Conditional include of `int-l64.h` for legacy ppc64 userspace unless `__SANE_USERSPACE_TYPES__`, otherwise `int-ll64.h`; `__vector128` as four `__u32` aligned to 16 bytes.

Control flow: Compile-time selection preserves old ppc64 long-based 64-bit type ABI for userspace while allowing sane ll64 opt-in.

State and persistence: No runtime state; controls ABI type sizes and vector register storage layout.

Dependencies and integration points: Depends on generic integer type headers and compiler alignment support.

Risks: Changing type model breaks userspace structures; vector alignment is required for VMX/VSX register sets.

Test signals: Headers compile with/without `__SANE_USERSPACE_TYPES__`, ppc64 type-size checks, and vector alignment tests.

Source read size: 41 lines, 1321 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ucontext.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ucontext.h

Purpose: Defines PowerPC user context structures for signal handling and context APIs.

Important APIs/types/functions: 32-bit `struct mcontext` and cross-ABI `struct ucontext` with flags, link, stack, signal mask growth padding, and machine context.

Control flow: Signal delivery and `getcontext`/`setcontext`-style libc code use this structure to save and restore execution context.

State and persistence: User context persists in signal frames or userspace-managed context objects.

Dependencies and integration points: Depends on sigcontext/elf and signal headers. Integrated by signal code, libc, and debuggers.

Risks: ppc64 and ppc32 layouts differ and are ABI-sensitive. Signal mask expansion padding is intentional for glibc compatibility.

Test signals: ucontext/signal tests, FP/VMX context preservation, altstack tests, and libc ABI checks.

Source read size: 41 lines, 975 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ucontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/unistd.h

Purpose: Selects generated PowerPC syscall number header for 32-bit or 64-bit userspace.

Important APIs/types/functions: Includes `asm/unistd_32.h` unless `__powerpc64__`, otherwise `asm/unistd_64.h`.

Control flow: Userspace/kernel UAPI inclusion resolves syscall numbers at compile time for the target ABI.

State and persistence: No runtime state; syscall numbers are ABI constants.

Dependencies and integration points: Depends on generated headers declared in UAPI Kbuild.

Risks: Wrong ABI selection gives callers invalid syscall numbers.

Test signals: Headers-install tests and syscall-number compile checks for ppc32 and ppc64.

Source read size: 19 lines, 577 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/vas-api.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/vas-api.h

Purpose: Defines userspace ioctl ABI for opening PowerPC VAS transmit windows.

Important APIs/types/functions: `VAS_MAGIC`, `VAS_TX_WIN_OPEN`, `VAS_TX_WIN_FLAG_QOS_CREDIT`, and `struct vas_tx_win_open_attr` with version, VAS ID, flags, and reserved fields.

Control flow: Userspace passes open attributes to the VAS misc device; kernel allocates a transmit window, optionally with QoS credit.

State and persistence: VAS window allocation state is maintained by the driver/hardware; the struct is input ABI with reserved extension space.

Dependencies and integration points: Depends on ioctl encoding, Linux types, and VAS driver support on POWER systems.

Risks: Reserved fields must remain zero/compatible. VAS ID `-1` means default and must be validated.

Test signals: VAS ioctl open tests, QoS flag tests, invalid version/ID tests, and ABI size checks.

Source read size: 28 lines, 664 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/vas-api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/85xx_entry_mapping.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/85xx_entry_mapping.S

Purpose: Low-level BookE/85xx assembly routine for replacing firmware/boot TLB state with controlled kernel or kexec entry mappings.

Important APIs/types/functions: Assembler flow guarded by `ENTRY_MAPPING_BOOT_SETUP` or `ENTRY_MAPPING_KEXEC_SETUP`; uses MAS0-MAS7, PID0-2, MAS6, TLB search/write/invalidate instructions, temporary TLB1 mapping, and final `rfi` transfers.

Control flow: The code finds the TLB entry currently executing, protects it, invalidates other entries, creates a temporary mapping in the alternate address space, switches via SRR0/SRR1, clears PIDs/search state, invalidates the original mapping, installs either a 64MiB kernel virtual mapping or eight 256MiB identity mappings for kexec, jumps into the final mapping, and clears the temporary entry.

State and persistence: Mutates processor TLBs, PID registers, MAS registers, and MSR address-space bits. The changes persist as the initial translation environment for subsequent kernel execution.

Dependencies and integration points: Depends on BookE MMU SPR definitions, `TLBSYNC`, `MSR_KERNEL`, `KERNELBASE`, and caller-provided registers such as `r20`/current address context. Included by 85xx head/kexec setup paths.

Risks: This runs with fragile early boot constraints. A wrong ESEL, PID, TSIZE, or address-space bit can strand execution without translation. Kexec identity mapping only covers the first 2GiB.

Test signals: PPC_85xx boot tests, kexec/kdump on e500/85xx, early TLB dump inspection, and build coverage for both boot and kexec setup macros.

Source read size: 230 lines, 5509 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/85xx_entry_mapping.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/Makefile

Purpose: Build orchestration for the PowerPC kernel core, selecting objects, instrumentation exclusions, flags, generated linker scripts, and vDSO wrapper dependencies.

Important APIs/types/functions: Object lists `obj-y`, config-gated `obj-*`/`obj64-*`, CFLAGS/KASAN/KCSAN/KCOV/GCOV/UBSAN controls, prom init check rule, vDSO wrapper prerequisites, and clean/subdir declarations.

Control flow: Kbuild evaluates architecture configs, removes tracing/sanitizer instrumentation from early or translation-off code, builds core objects and optional platform/feature modules, runs `prom_init_check`, forces vDSO wrapper dependencies, and includes vdso as a subdir.

State and persistence: No runtime state; it controls build artifacts and object inclusion. Built objects persist in the kernel image/modules.

Dependencies and integration points: Depends on Kbuild variables, PowerPC config symbols, compiler option helpers, `prom_init_check.sh`, vdso outputs, and generated `vmlinux.lds`.

Risks: Instrumentation in early boot or real-mode code can make kernels unbootable. Missing config-gated objects break feature paths such as KVM, RTAS, XIVE, EEH, or CPU setup.

Test signals: PowerPC defconfig/allmodconfig builds across PPC32/PPC64, sanitizer-enabled builds, vdso dependency rebuilds, and prom_init check execution.

Source read size: 220 lines, 7388 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/align.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/align.c

Purpose: Handles PowerPC alignment exceptions by emulating selected unaligned user accesses, SPE loads/stores, and DCBZ where safe.

Important APIs/types/functions: `struct aligninfo`, SPE decode table, `emulate_spe()` under `CONFIG_SPE`, and exported `fix_alignment(struct pt_regs *regs)`.

Control flow: `fix_alignment()` fetches the faulting instruction from kernel or user memory, swaps it for old little-endian modes if needed, special-cases SPE opcodes, rejects copy/paste and atomic LARX/STCX cases, analyzes the instruction, emulates DCBZ or load/store, and returns success, fault, or SIGBUS-driving errors.

State and persistence: Mutates the interrupted task register state, SPE EVR state, and/or user memory when emulation succeeds. Uses current thread SPE state after flushing live registers.

Dependencies and integration points: Depends on instruction analysis/emulation helpers, user access primitives, CPU feature checks, SPE support, emulated operation warnings, and `pt_regs` fault fields.

Risks: User access fault handling must be exact. Emulating unsupported atomic or copy/paste instructions would violate architecture semantics. Endian handling and SPE register pairing are subtle.

Test signals: Alignment exception selftests for loads/stores/DCBZ, SPE unaligned access tests, bad-address `-EFAULT` paths, copy/paste SIGBUS behavior, and kernel/user instruction-fetch cases.

Source read size: 355 lines, 8473 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/align.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/asm-offsets.c

Purpose: Generates assembler-visible offsets and constants for PowerPC low-level assembly from C structure layouts.

Important APIs/types/functions: `STACK_PT_REGS_OFFSET()` and many `OFFSET()`/`DEFINE()` emissions for task/thread, PACA, lppaca, pt_regs, CPU specs, vDSO data, KVM, TM, RTAS, TLB CAM, debug, ftrace, and platform constants.

Control flow: The file is compiled to assembly; kbuild extracts emitted `#define`-style records so assembly files can address C structs safely without hardcoded stale offsets.

State and persistence: No runtime state. Generated offsets persist as build artifacts consumed by assembler.

Dependencies and integration points: Depends on the full set of PowerPC kernel structs and config symbols. Integrated by entry code, KVM handlers, vDSO assembly, suspend/resume, ftrace, and exception paths.

Risks: Missing offsets break assembly builds or, worse, runtime register saves/restores. Config guards must match the assembly consumers.

Test signals: Full architecture builds for PPC32/PPC64, Book3S/BookE, KVM, TM, XMON, ftrace, and suspend configs; inspect generated `asm-offsets.h` when changing structs.

Source read size: 688 lines, 24576 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/audit_32.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/audit_32.h

Purpose: Declares the 32-bit PowerPC audit syscall classifier.

Important APIs/types/functions: `ppc32_classify_syscall(unsigned)`.

Control flow: Audit code can call the classifier to map a 32-bit syscall number into an audit class.

State and persistence: No state owned; classification derives from syscall number tables elsewhere.

Dependencies and integration points: Integrated by PowerPC audit implementation for compat/32-bit syscall auditing.

Risks: A missing or mismatched prototype breaks audit builds; wrong classifier behavior can mislabel audited syscalls.

Test signals: CONFIG_AUDIT PPC32/compat builds and audit syscall classification tests.

Source read size: 7 lines, 136 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/audit_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/btext.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/btext.c

Purpose: Implements early boot framebuffer text output for PowerPC BootX/Open Firmware displays and hooks it into udbg.

Important APIs/types/functions: Display globals, `btext_prepare_BAT()`, `btext_setup_display()`, `btext_unmap()`, `btext_map()`, `btext_find_display()`, `btext_update_display()`, clear/flush helpers, character drawing routines, `btext_drawchar/string/text/hex()`, and `udbg_init_btext()`.

Control flow: Early boot discovers display properties from OF/BootX, maps the framebuffer, tracks an 8x16 text cursor, draws glyphs into 8/16/32-bit framebuffers, wraps or clears lines, flushes cache lines, and exposes `btext_drawchar` as `udbg_putc`.

State and persistence: Persistent early-boot state includes framebuffer physical/logical base, row bytes, depth, rectangle, cursor coordinates, maximum text cells, BAT mapping values, and mapped flag.

Dependencies and integration points: Depends on OF device nodes, memblock/pgtable/io mapping, font data, BootX setup, RMCI helpers on PPC64 early debug, and udbg.

Risks: Runs before normal console and memory mapping are stable. Wrong pitch/depth/address can write arbitrary memory; mapping/unmapping must match early MMU state.

Test signals: CONFIG_BOOTX_TEXT builds, old PowerMac/OF boot display smoke tests, early printk/udbg output, framebuffer mode update tests, and cache flush validation.

Source read size: 585 lines, 13701 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/btext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cacheinfo.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cacheinfo.c

Purpose: Builds PowerPC cache topology objects and exposes per-CPU cache information through sysfs.

Important APIs/types/functions: `struct cache_dir`, `struct cache_index_dir`, `struct cache_type_info`, `struct cache`, cache property readers, cache chain creation/linking helpers, sysfs attribute show methods, `cacheinfo_cpu_online()`, `cacheinfo_cpu_offline()`, `cacheinfo_teardown()`, and `cacheinfo_rebuild()`.

Control flow: On CPU online, code finds the CPU OF node, creates or reuses L1 split/unified cache objects, walks `next-cache` nodes for higher levels, marks shared CPU maps, creates `/sys/devices/system/cpu/cpuN/cache/index*`, and conditionally adds size/line/sets/associativity attributes. Offline removes sysfs first, clears CPU bits, and frees cache objects with empty masks.

State and persistence: Global `cache_list`, per-CPU `cache_dir_pcpu`, cache object refcounts/OF refs, shared CPU masks, and sysfs kobjects persist while CPUs are online.

Dependencies and integration points: Depends on OF cache properties, CPU devices, cpumasks, thread-group topology maps, hotplug locking, kobjects/sysfs, and `cacheinfo.h` hooks from sysfs code.

Risks: Cache sharing and thread-group group IDs must be correct or sysfs topology is misleading. Kobject lifetime and OF node refs must be balanced during hotplug/suspend rebuild.

Test signals: CPU online/offline stress, sysfs cache attribute validation against device tree, suspend/resume rebuild on pSeries, memory-leak/refcount checks, and big-core/thread-group topology tests.

Source read size: 953 lines, 24117 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cacheinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cacheinfo.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cacheinfo.h

Purpose: Declares cacheinfo lifecycle hooks used by PowerPC sysfs and hotplug code.

Important APIs/types/functions: `cacheinfo_cpu_online()`, `cacheinfo_cpu_offline()`, `cacheinfo_teardown()`, and `cacheinfo_rebuild()`.

Control flow: External code calls online/offline hooks around CPU hotplug and teardown/rebuild around migration or suspend scenarios.

State and persistence: State is implemented in `cacheinfo.c`; this header exposes the interface.

Dependencies and integration points: Integrated with PowerPC CPU sysfs and hotplug paths.

Risks: Prototype mismatches break build or hotplug integration.

Test signals: PowerPC cacheinfo build and CPU hotplug/suspend sysfs tests.

Source read size: 13 lines, 425 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cacheinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_44x.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_44x.S

Purpose: Provides low-level setup routines and errata workarounds for 44x-class PowerPC CPUs.

Important APIs/types/functions: `__setup_cpu_440ep`, `__setup_cpu_440epx`, `__setup_cpu_440grx`, `__setup_cpu_460ex/gt/sx`, `__setup_cpu_apm821xx`, `__setup_cpu_440x5/440gx/440spe`, `__init_fpu_44x()`, and `__plb_disable_wrp()`.

Control flow: CPU-specific setup branches call FPU APU enablement, PLB write-pipelining disablement, and 440A machine-check fixup helpers as required, preserving LR around multi-call sequences.

State and persistence: Mutates CCR0 to enable FPU access and PLB DCR `DCRN_PLB4A0_ACR` to disable write pipelining. Other machine-check fixup state is handled externally.

Dependencies and integration points: Depends on 44x SPR/DCR definitions, CPU spec setup dispatch, and external `__fixup_440A_mcheck`.

Risks: These routines run during early CPU initialization. Incorrect DCR/CCR writes can break memory writes or FPU access; errata workarounds are CPU-revision-specific.

Test signals: 44x/460/APM821xx boot tests, FPU availability tests, memory stress for PLB write erratum, and config build coverage.

Source read size: 69 lines, 1459 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_44x.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_6xx.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_6xx.S

Purpose: Provides low-level setup, cache/HID tuning, FPU initialization, and save/restore routines for 6xx/7xx/74xx Book3S 32-bit PowerPC CPUs.

Important APIs/types/functions: Setup entry points for 603, 604, 750 variants, 7400/7410/745x; helpers `setup_common_caches`, `setup_604_hid0`, `setup_g2_le_hid2`, workaround helpers, `setup_750_7400_hid0`, `setup_745x_specifics`, `__init_fpu_registers`, `__save_cpu_setup`, and `__restore_cpu_setup`.

Control flow: Setup routines preserve LR, initialize FPU when needed, enable/invalidate caches, set HID0/HID2/MSSCR/L2 prefetch and errata bits, adjust CPU feature flags such as NAP, and return. Save/restore stores selected SPRs into `cpu_state_storage` for sleep/resume and restores them with sync/isync ordering.

State and persistence: Mutates HID0/HID1/HID2, MSSCR0/MSSSR0, ICTC, L2CR2, L3/NAP-related feature flags, FPU register contents, and static `cpu_state_storage`.

Dependencies and integration points: Depends on CPU feature fixups, SPR definitions, cache constants, CPU spec layout offsets, and power-management callers.

Risks: SPR programming order and barriers are hardware-sensitive. Errata checks are revision-specific; wrong feature flag mutation can disable idle modes or leave caches misconfigured.

Test signals: PPC_BOOK3S_32 boot across 603/604/750/74xx, suspend/resume, cache/FPU smoke tests, NAP behavior tests, and assembly build coverage.

Source read size: 516 lines, 12010 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_6xx.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_e500.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_e500.S

Purpose: Provides cache setup, idle-state setup, IVOR initialization wrappers, restore paths, and CPU-down cache flushing for e500/e500mc/e5500/e6500 BookE CPUs.

Important APIs/types/functions: `__e500_icache_setup`, `__e500_dcache_setup`, `setup_pw20_idle`, `setup_altivec_idle`, setup/restore entry points for e500v1/v2/e500mc/e5500/e6500, `flush_dcache_L1`, `has_L2_cache`, `flush_backside_L2_cache`, and `cpu_down_flush_*` routines.

Control flow: Setup enables/invalidate L1 caches, programs IVORs according to CPU/HV capability, enables idle controls, conditionally clears embedded-HV CPU feature bits if hardware lacks LPID support, and restores similar state after resume. CPU-down paths flush L1 and, where present, backside L2 before offlining.

State and persistence: Mutates L1CSR0/1, PWRMGTCR0, IVORs via external helpers, CPU feature flags, HID0 DCFA, L2CSR0, interrupt enable state, and cache contents.

Dependencies and integration points: Depends on BookE/e500 SPRs, nohash MMU definitions, MPC85xx SVR values, IVOR setup helpers, CPU spec offsets, and hotplug/power-management paths.

Risks: Cache flush loops depend on L1CFG geometry and known block sizes. Touching E.HV IVORs on unsupported CPUs is avoided by MMUCFG checks; breaking that can fault early.

Test signals: e500/e500mc/e5500/e6500 boot and CPU hotplug, cache coherency tests after offline, L2 skip on P2040, IVOR exception delivery, and suspend/restore coverage.

Source read size: 337 lines, 7107 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_e500.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_pa6t.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_pa6t.S

Purpose: Performs minimal PA6T setup/restore for hypervisor-capable operation.

Important APIs/types/functions: `__setup_cpu_pa6t` and `__restore_cpu_pa6t` share one implementation.

Control flow: The routine checks MSR HV mode and returns if not privileged enough; otherwise it sets selected HID5 bits and LPCR bits before returning.

State and persistence: Mutates PA6T HID5 and LPCR special-purpose registers when running in HV mode.

Dependencies and integration points: Depends on PA6T SPR definitions and CPU setup dispatch for Book3S 64-bit PA Semi systems.

Risks: Only safe in HV mode. Incorrect HID5/LPCR bits can alter interrupt or partition behavior.

Test signals: PA6T boot/restore build coverage, HV-mode detection tests where hardware is available, and suspend/resume smoke tests.

Source read size: 31 lines, 609 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_pa6t.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_power.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_power.c

Purpose: C implementation of low-level setup/restore for POWER7, POWER8, POWER9, and POWER10 Book3S 64-bit CPUs.

Important APIs/types/functions: Helpers `init_hvmode_206`, `init_LPCR_ISA300`, `init_LPCR_ISA206`, `init_FSCR*`, `init_HFSCR`, `init_PMU*`, `init_DEXCR`, and setup/restore entry points `__setup_cpu_power7/8/9/10` plus matching restore functions.

Control flow: Setup initializes user-visible facility control, PMU registers, DEXCR/hash key state for POWER10, then if HV mode is available resets LPID/PID/AMOR/PCR/PSSCR as appropriate, programs LPCR for the ISA generation, enables HFSCR facilities, and resets HV PMU controls. Non-HV setup clears HV-related CPU feature bits.

State and persistence: Mutates FSCR, HFSCR, LPCR, LPID, PID, AMOR, PCR, PSSCR, MMCR/MMCRA/MMCRS/MMCRH/MMCRC/MMCR3, DEXCR, HASHKEYR, and CPU feature flags.

Dependencies and integration points: Depends on SPR definitions, sync helpers, CPU spec feature flags, Book3S HV mode, PMU/TM/DEXCR architecture features, and CPU setup dispatch from cputable.

Risks: Feature exposure and SPR initialization must match CPU generation. Running HV-only programming outside HV mode is avoided; mistakes can break guests, PMU, TM, or security controls.

Test signals: POWER7-POWER10 boot and secondary CPU bring-up, KVM HV guest tests, PMU/perf tests, facility availability tests for SCV/prefix/DEXCR, and suspend/restore smoke tests.

Source read size: 288 lines, 5551 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_power.c -->
