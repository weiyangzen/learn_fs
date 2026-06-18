# subset-b-000876 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/uv_mmrs.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/uv_mmrs.h

Purpose: Generated-style HPE SGI UV hub MMR definition header. It gives x86 UV platform code symbolic offsets, bit shifts, masks, and packed register views for UV2, UV3, UV4, UV4A, and UV5 hub hardware. The file is declarative: it does not perform MMIO reads or writes itself, but it defines the register contract consumed by UV platform setup, interrupt routing, TLB shootdown, RTC, address-map, and scratch-register code.

Important APIs/types/functions: `UV2`, `UV3`, `UV4`, `UV4A`, `UV5`, `UVX`, `UVY`, and `UV_ANY` identify hub generations/classes. `UV_MMR_ENABLE` is the common top-bit enable flag. Hub part-number constants identify supported ASICs. `uv_undefined(char *str)` is an external error path for generation-specific registers that should not be used on the current hub. Each register family exposes an address macro, field `_SHFT` and `_MASK` macros, and a union with raw `unsigned long v` plus common and generation-specific bitfield structs. Notable families include `UVH_EVENT_OCCURRED0/1/2` and aliases, `UVH_EXTIO_INT0_BROADCAST`, GR TLB interrupt config registers, `UVH_INT_CMPB`, `UVH_IPI_INT`, `UVH_NODE_ID`, node-present registers/tables, UV5 `RH10_GAM_*` address/overlay/redirect registers, UVX `RH_GAM_*` overlay and redirect registers, `UVH_RTC`, `UVH_RTC1_INT_CONFIG`, and `UVH_SCRATCH5` aliases.

Control flow: There is no runtime function body. The only dynamic behavior is in macros that use nested `is_uv(UV*) ? value : ...` selection to return the correct offset, depth, shift, or mask for the running hub class. Unsupported runtime selections either return `0`, `-1`, or call `uv_undefined()`, depending on whether the generated table treats the register as absent or as a programming error.

State and persistence: The header models persistent hardware state in UV MMRs, including event latch bits, interrupt routing fields, node presence, global address map overlays, MMIOH/GRU redirect tables, RTC counter state, and scratch registers. It does not allocate memory or persist kernel software state. Bitfield comments distinguish RW, RO, and undefined fields, and consumers must preserve reserved bits when doing read-modify-write cycles.

Dependencies and integration points: This file depends on the broader UV platform environment for `is_uv()` and MMR accessors. It integrates with x86 UV hub discovery, address map setup, interrupt setup, NMI/RTC handling, TLB shootdown support, and hardware error handling. The generated `UVH_*` common names intentionally hide per-generation offsets and field layout differences so call sites can be mostly generation-neutral.

Risks: Bitfield layout and masks are hardware ABI. A wrong offset, shift, mask, or generation selector can corrupt interrupt routing, memory decode, or error-latch handling. The unions use C bitfields over `unsigned long`, so they are suitable only for the kernel's supported x86 ABI assumptions. Runtime macros that return `0` for unsupported registers can be dangerous if a caller treats zero as a valid MMR offset. Generated duplication also makes drift hard to review manually.

Test signals: Build coverage on UV-enabled x86 configs is the first signal. Useful runtime signals are UV boot logs, hub part-number detection, successful MMR mapping, correct node-present enumeration, interrupt delivery from external I/O and RTC, TLB interrupt operation, and absence of `uv_undefined()` paths on supported systems. Hardware or simulator tests are needed for generation-specific address-map and interrupt-register fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/uv_mmrs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso.h

Purpose: Declares the x86 kernel-side vDSO image metadata and mapping/fault-repair entry points. It is the architecture contract between vDSO image generation, process memory setup, signal-return trampolines, and exception fixup.

Important APIs/types/functions: `struct vdso_image` contains the image data pointer, page-rounded size, alternative-instruction metadata, exception-table metadata, and symbol offsets for `__kernel_sigreturn`, `__kernel_rt_sigreturn`, `__kernel_vsyscall`, `int80_landing_pad`, and compat sigreturn landing pads. `vdso64_image`, `vdsox32_image`, and `vdso32_image` are the architecture image instances. `init_vdso_image()` validates/prepares an image during init, `map_vdso_once()` maps an image at a requested user address, and `fixup_vdso_exception()` resolves faults against the vDSO exception table.

Control flow: The header only declares data and functions. Runtime flow is: init code calls `init_vdso_image()`, process setup maps the selected image with `map_vdso_once()`, user code executes vDSO symbols, and kernel exception handling can call `fixup_vdso_exception()` when a vDSO access faults.

State and persistence: `struct vdso_image` instances are read-mostly kernel metadata around embedded ELF/image bytes. Mappings are per-mm user virtual memory state; no file-backed persistence is involved.

Dependencies and integration points: Includes page types, linkage/init annotations, and `linux/mm_types.h` for `pt_regs` consumers. It integrates with x86 signal delivery, compat ABI support, alternative patching, exception-table fixups, ELF/vDSO mapping, and syscall fallback paths.

Risks: Incorrect symbol offsets or exception-table bounds can break signal return, compat entry paths, or fault recovery. Mapping size must remain page-aligned. 32-bit, x32, and 64-bit images have different ABI expectations and must not be mixed.

Test signals: Boot-time vDSO init, `clock_gettime`/`gettimeofday`/`getcpu` vDSO use from user space, signal return tests across 32-bit/x32/64-bit ABIs, and fault-injection or selftests that exercise vDSO exception fixups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/clocksource.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/clocksource.h

Purpose: Advertises x86 vDSO-supported clock modes to the generic vDSO time code.

Important APIs/types/functions: `VDSO_ARCH_CLOCKMODES` lists `VDSO_CLOCKMODE_TSC`, `VDSO_CLOCKMODE_PVCLOCK`, and `VDSO_CLOCKMODE_HVCLOCK`. `HAVE_VDSO_CLOCKMODE_HVCLOCK` signals that Hyper-V clock support exists in the architecture implementation.

Control flow: No code executes here. The macros feed generic vDSO declarations and switch logic elsewhere.

State and persistence: No state is stored. The selected clock mode lives in vDSO datapage state maintained by timekeeping code.

Dependencies and integration points: Consumed by generic `vdso/` time headers and paired with x86 `gettimeofday.h`, paravirtual clock support, and Hyper-V timer support.

Risks: The list must match actual x86 implementations. Advertising a mode without a valid reader can make user-space time calls fail or fall back incorrectly.

Test signals: Build tests for TSC, KVM pvclock, and Hyper-V configs; runtime `clock_gettime()` vDSO behavior on bare metal and hypervisors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/clocksource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/getrandom.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/getrandom.h

Purpose: Provides the x86 vDSO inline syscall fallback for `getrandom()`.

Important APIs/types/functions: `getrandom_syscall(void *buffer, size_t len, unsigned int flags)` issues `__NR_getrandom` with the x86-64 `syscall` instruction, passing args in `rdi`, `rsi`, and `rdx`, returning either bytes written or a negative error value.

Control flow: The vDSO getrandom implementation calls this helper when it cannot satisfy a request from vDSO-managed state. Inline assembly loads the syscall number in `rax`, executes `syscall`, and returns `rax`.

State and persistence: No local state. It writes random bytes to the caller-provided user buffer through the kernel syscall path.

Dependencies and integration points: Includes `asm/unistd.h` for `__NR_getrandom`. Integrates with the generic vDSO getrandom code and the kernel random subsystem.

Risks: Register constraints and clobbers are ABI-critical. The helper is x86-64 specific as written; incorrect use from non-64-bit vDSO code would be unsafe. The memory clobber is needed so buffer accesses are not reordered across the syscall.

Test signals: vDSO getrandom selftests, syscall fallback tests for flags and partial/error returns, and architecture build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/getrandom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/gettimeofday.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/gettimeofday.h

Purpose: Implements x86 architecture hooks for generic vDSO time functions: fast hardware counter reads, syscall fallbacks, cycle validation, and nanosecond conversion rules.

Important APIs/types/functions: `VDSO_HAS_TIME` and `VDSO_HAS_CLOCK_GETRES` enable generic vDSO exports. `clock_gettime_fallback()`, `gettimeofday_fallback()`, `clock_getres_fallback()`, and 32-bit variants use `VDSO_SYSCALL*` macros. `vread_pvclock()` reads KVM/Xen pvclock when `CONFIG_PARAVIRT_CLOCK` is enabled. `vread_hvclock()` reads Hyper-V reference TSC page when `CONFIG_HYPERV_TIMER` is enabled. `__arch_get_hw_counter()` dispatches TSC, pvclock, or Hyper-V clock reads. `arch_vdso_clocksource_ok()` currently accepts all provided clocksources. `arch_vdso_cycles_ok()` rejects negative/sentinel cycle values. `vdso_calc_ns()` performs x86-specific delta validation and ns conversion.

Control flow: Generic vDSO time code reads the vDSO datapage clock mode and calls `__arch_get_hw_counter()`. TSC uses `rdtsc_ordered()`. Paravirtual and Hyper-V modes are guarded by compiler barriers before touching mapped clock pages, because those pages can fault if the mode is disabled. Returned cycles are validated, then `vdso_calc_ns()` compares against `cycle_last`, clamps negative motion to base time, handles overflow with `mul_u64_u32_add_u64_shr()`, and otherwise applies `delta * mult + base`.

State and persistence: Reads shared, kernel-updated vDSO time data and optional hypervisor pages `pvclock_page` and `hvclock_page`. It stores no state locally. The code treats `U64_MAX` and sign-bit-set values as invalid counter reads.

Dependencies and integration points: Depends on x86 MSR/TSC helpers, pvclock, Hyper-V timer definitions, `asm/vgtod.h`, generic vDSO datapage structures, and `asm/vdso/sys_call.h`. It is central to user-space `clock_gettime`, `gettimeofday`, and `time` performance.

Risks: Barrier placement is critical; speculative or compiler-hoisted loads from disabled clock pages can segfault. TSC skew across sockets requires the custom delta clamp. Hypervisor clock invalidation must be treated as fallback-worthy. 32-bit syscall suffix selection must remain aligned with syscall numbering.

Test signals: vDSO time selftests, monotonicity tests under CPU migration, KVM/Xen/Hyper-V guest tests, fallback syscall tracing, and build coverage for 32-bit and 64-bit configs with and without paravirtual clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/gettimeofday.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/processor.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/processor.h

Purpose: Supplies tiny x86 processor helpers used from vDSO code.

Important APIs/types/functions: `native_pause()` emits the `pause` instruction with a memory clobber. `cpu_relax()` wraps `native_pause()`. `__vdso_getcpu(unsigned *cpu, unsigned *node, void *unused)` is declared as a notrace vDSO symbol.

Control flow: Busy-wait loops in vDSO/generic helpers call `cpu_relax()`, which executes `pause`. User-space callers can call the vDSO getcpu export, implemented elsewhere.

State and persistence: No persistent state. `__vdso_getcpu()` reports CPU/node information via caller pointers.

Dependencies and integration points: Integrates with generic vDSO processor abstraction and x86 getcpu implementation.

Risks: `pause` must remain available and correctly constrained for user-mode vDSO execution. The `notrace` declaration avoids instrumentation that would be invalid in vDSO context.

Test signals: vDSO getcpu selftests, disassembly checks for `pause`, and build coverage for vDSO compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/sys_call.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/sys_call.h

Purpose: Defines inline syscall macros for x86 vDSO fallback paths, abstracting 64-bit `syscall` and 32-bit fast-vsyscall/int80 selection.

Important APIs/types/functions: Internal macros define instruction, clobbers, syscall-number suffixing, and argument registers. `_VDSO_SYSCALL(name,suf32,...)` is the common inline asm body. `VDSO_SYSCALL0` through `VDSO_SYSCALL5` bind arguments to ABI registers and return the syscall result.

Control flow: vDSO fallback wrappers expand these macros. On x86-64, `syscall` is emitted with `rax` as both syscall number and return value and `rdi/rsi/rdx/r10/r8` for args. On 32-bit, an `ALTERNATIVE()` sequence chooses between padded `int $0x80` and `call __kernel_vsyscall` when `X86_FEATURE_SYSFAST32` is available.

State and persistence: No state. The macros cross into the kernel syscall path and return kernel results directly.

Dependencies and integration points: Uses `linux/compiler.h`, x86 CPU feature definitions, alternatives, syscall number macros, and vDSO time fallbacks.

Risks: Register binding is fragile, especially for 32-bit frame-pointer use; the header intentionally omits a 6-argument macro because `%ebp` needs special handling. Incorrect suffix use can call the wrong compat syscall.

Test signals: vDSO fallback tests for clock syscalls, 32-bit compat runs with and without SYSFAST32, objtool/build checks, and syscall ABI tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/sys_call.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/vsyscall.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/vsyscall.h

Purpose: Provides x86 vDSO/vsyscall layout constants and includes the generic vDSO-vsyscall interface after the architecture page layout is defined.

Important APIs/types/functions: `__VDSO_PAGES` is 6. `VDSO_NR_VCLOCK_PAGES` is 2. `VDSO_VCLOCK_PAGES_START(base)` computes where clock pages begin inside the vDSO mapping. `VDSO_PAGE_PVCLOCK_OFFSET` and `VDSO_PAGE_HVCLOCK_OFFSET` index the paravirtual and Hyper-V clock pages.

Control flow: No runtime code here. Generic vDSO code uses the constants to locate architecture vclock pages.

State and persistence: Describes per-mm vDSO mapping layout. The vclock pages are shared kernel/hypervisor-updated pages mapped with the vDSO.

Dependencies and integration points: Includes `vdso/datapage.h`, `asm/vgtod.h`, and then `asm-generic/vdso/vsyscall.h`. It pairs with x86 vDSO mapping code and `gettimeofday.h`.

Risks: Page count and offset mismatches break vDSO image layout or cause time code to read the wrong page. The include order matters because generic code expects architecture constants to be defined first.

Test signals: vDSO mapping layout tests, clock mode tests for pvclock and Hyper-V, and build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/vsyscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vermagic.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/vermagic.h

Purpose: Supplies x86 architecture-specific module vermagic text, mainly for 32-bit processor-family compatibility.

Important APIs/types/functions: `MODULE_PROC_FAMILY` is selected from `CONFIG_M586`, `CONFIG_M686`, Pentium, K6/K7, Transmeta, Winchip, Cyrix, VIA, Geode, and related 32-bit CPU-family options. `MODULE_ARCH_VERMAGIC` is `MODULE_PROC_FAMILY` for `CONFIG_X86_32` and empty for 64-bit.

Control flow: Preprocessor-only selection at build time. Unsupported 32-bit processor-family configurations hit `#error unknown processor family`.

State and persistence: No runtime state. The selected string becomes part of module metadata used during module loading.

Dependencies and integration points: Integrates with Linux module versioning and x86 Kconfig CPU-family selection.

Risks: Missing a new 32-bit CPU family config breaks builds. Incorrect vermagic strings can reject compatible modules or allow incompatible ones.

Test signals: Module builds across x86_32 CPU-family configs, `modinfo vermagic`, and module load/reject behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vermagic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vga.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/vga.h

Purpose: Defines x86 direct VGA framebuffer memory mapping and byte access helpers.

Important APIs/types/functions: `VGA_MAP_MEM(x, s)` converts a physical VGA address to a virtual address with `phys_to_virt()` and, when AMD memory encryption is enabled, calls `set_memory_decrypted()` for the region. `vga_readb(x)` and `vga_writeb(x, y)` are direct byte load/store macros.

Control flow: VGA users call `VGA_MAP_MEM()` before accessing framebuffer memory. The macro conditionally changes page encryption attributes, then returns the virtual start address.

State and persistence: It can mutate kernel page attributes for VGA memory by marking pages decrypted. The VGA memory contents persist in device memory, not in this header.

Dependencies and integration points: Includes `asm/set_memory.h`; relies on `phys_to_virt`, `PAGE_SHIFT`, and `CONFIG_AMD_MEM_ENCRYPT`. Used by generic VGA console/framebuffer code.

Risks: Page count is `(s) >> PAGE_SHIFT`, so non-page-rounded sizes need callers to be careful. Failing to decrypt on encrypted-memory systems breaks device access; decrypting the wrong range affects memory confidentiality/integrity.

Test signals: VGA console/framebuffer boot tests, SME/SEV encrypted-memory boots with VGA output, and build tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vga.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vgtod.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/vgtod.h

Purpose: Acts as the x86 vDSO gettimeofday bridge header while avoiding unwanted dependencies for UML builds.

Important APIs/types/functions: When `CONFIG_GENERIC_GETTIMEOFDAY` is enabled, it includes compiler helpers, x86 clocksource definitions, vDSO datapage/helpers, and UAPI time types.

Control flow: No runtime code. The preprocessor guard controls which dependencies are visible.

State and persistence: No state. It exposes types and helper declarations used by vDSO time code.

Dependencies and integration points: Integrates `asm/vdso/gettimeofday.h`, generic vDSO time helpers, and x86 clocksource definitions. The comment calls out `ARCH=um` as a reason for the config guard.

Risks: Including too much unconditionally can break UML. Including too little under `CONFIG_GENERIC_GETTIMEOFDAY` can break vDSO time compilation.

Test signals: Builds for native x86 and UML, plus vDSO time selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vgtod.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/video.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/video.h

Purpose: Provides x86 architecture hooks for framebuffer page protections and primary video-device detection.

Important APIs/types/functions: `pgprot_framebuffer(pgprot_t prot, unsigned long vm_start, unsigned long vm_end, unsigned long offset)` adjusts mmap protections for framebuffer memory and is exported via a macro of the same name. Under `CONFIG_VIDEO`, `video_is_primary_device(struct device *dev)` is declared and similarly advertised. The header then includes `asm-generic/video.h` for fallback/default behavior.

Control flow: Driver or generic video code calls the architecture hook to choose page attributes for framebuffer mappings and optionally to identify the primary display device.

State and persistence: No local state. The hooks affect VMA/page-protection decisions and device selection state elsewhere.

Dependencies and integration points: Depends on `linux/types.h`, `asm/page.h`, `struct device`, and generic video hooks. It integrates with DRM/fbdev/video driver mmap paths.

Risks: Wrong framebuffer cache/encryption attributes can cause display corruption, performance issues, or unsafe MMIO caching. Primary-device logic affects console handoff.

Test signals: Framebuffer mmap tests, boot console handoff, DRM/fbdev primary device detection, and builds with/without `CONFIG_VIDEO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/virt.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/virt.h

Purpose: Declares x86 virtualization lifetime and emergency-disable coordination APIs used by KVM and reboot/panic paths.

Important APIs/types/functions: `cpu_emergency_virt_cb` is a per-CPU emergency callback type. With `CONFIG_KVM_X86`, `virt_rebooting`, `x86_virt_init()`, `x86_virt_get_ref(int feat)`, `x86_virt_put_ref(int feat)`, `x86_virt_emergency_disable_virtualization_cpu()`, and callback register/unregister functions are declared. Without KVM, init is a no-op and emergency disable returns `-ENOENT`.

Control flow: Architecture init calls `x86_virt_init()`. Virtualization users take/release feature refs. Reboot or emergency paths can disable CPU virtualization and invoke registered callbacks.

State and persistence: Runtime state is external: refcounts, callback lists, and `virt_rebooting`. This header only exposes the API.

Dependencies and integration points: Includes `asm/reboot.h` and is tied to KVM x86, CPU virtualization enable/disable code, and emergency reboot/shutdown paths.

Risks: Refcount bugs can leave VMX/SVM enabled during emergency paths or disable it while still in use. Callback registration must be synchronized in implementation. Stubs must preserve callers' ability to build without KVM.

Test signals: KVM module load/unload, reboot and panic tests while VMs run, nested virtualization toggles, and non-KVM build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/virt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vm86.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/vm86.h

Purpose: Defines kernel-private structures and helpers for 32-bit x86 VM86 mode support.

Important APIs/types/functions: `struct kernel_vm86_regs` wraps normal `pt_regs` plus real VM86 segment registers. `struct vm86` tracks the user VM86 control block, saved 32-bit regs, virtual EFLAGS and mask, saved `sp0`, flags, CPU type, interrupt revectors, and `vm86plus` info. With `CONFIG_VM86`, it declares `handle_vm86_fault()`, `handle_vm86_trap()`, `save_v86_state()`, `release_vm86_irqs()`, `free_vm86(t)`, `FIRST_VM86_IRQ`, `LAST_VM86_IRQ`, and `invalid_vm86_irq()`. Without VM86, stubs compile out support.

Control flow: Trap/fault handling routes VM86 exceptions through the declared handlers; state is saved back to the user VM86 frame; IRQ allocations are released on task teardown; `free_vm86()` releases per-thread VM86 state.

State and persistence: Per-task VM86 state lives in `thread_struct->vm86` and points to user VM86 data. IRQ revectors and VM86 flags persist for the running task until freed or released.

Dependencies and integration points: Includes `asm/ptrace.h` and UAPI `asm/vm86.h`. Integrates with x86 traps, signal/task state, legacy DOS/real-mode emulation support, and IRQ handling.

Risks: VM86 is legacy and stateful. Segment layout must match trap entry assumptions. User pointers and IRQ requests require validation. `free_vm86()` assumes a `thread_struct`-like object and uses `kfree()`.

Test signals: 32-bit VM86 userspace tests, trap/fault/IRQ revectored paths, task exit cleanup, and builds with and without `CONFIG_VM86`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vm86.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vmalloc.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/vmalloc.h

Purpose: Advertises whether x86 can use huge-page mappings for vmalloc/vmap areas.

Important APIs/types/functions: Under `CONFIG_HAVE_ARCH_HUGE_VMAP`, `arch_vmap_pud_supported(pgprot_t prot)` exists on x86-64 and returns whether boot CPU has `X86_FEATURE_GBPAGES`; `arch_vmap_pmd_supported(pgprot_t prot)` returns whether boot CPU has `X86_FEATURE_PSE`.

Control flow: Generic vmalloc/vmap code calls these hooks before using PUD- or PMD-sized mappings.

State and persistence: No local state. It reads boot CPU feature state.

Dependencies and integration points: Depends on `asm/cpufeature.h`, `asm/page.h`, and `asm/pgtable_areas.h`; integrates with vmalloc mapping creation and TLB/page-table code.

Risks: Returning true without hardware support would create invalid page tables. Returning false loses performance but is safer. The `prot` argument is currently unused, so future protection-specific constraints must be added carefully.

Test signals: Huge-vmap boot tests, vmalloc stress tests, page-table validation, and CPU-feature matrix builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vmware.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/vmware.h

Purpose: Defines VMware hypervisor command constants and inline hypercall helpers for x86 guests, including I/O-port, `vmcall`, `vmmcall`, TDX, and high-bandwidth transfer variants.

Important APIs/types/functions: Constants include `VMWARE_HYPERVISOR_PORT`, `_PORT_HB`, `VMWARE_HYPERVISOR_MAGIC`, command IDs such as `GETVERSION`, `GETHZ`, `GETVCPU_INFO`, and `STEALCLOCK`, and `VMWARE_CMD_MASK`. External fallbacks are `vmware_hypercall_slow()` and `vmware_tdx_hypercall()`. Inline helpers `vmware_hypercall1/3/4/5/6/7()` cover low-bandwidth calls with different output sets. `vmware_hypercall_hb_out()` and `_hb_in()` perform high-bandwidth `rep outsb`/`rep insb` transfers.

Control flow: Low-bandwidth helpers first route TDX guests to `vmware_tdx_hypercall()`. Before alternatives are patched in built-in code, they use `vmware_hypercall_slow()`. Otherwise inline asm emits the `VMWARE_HYPERCALL` alternative sequence, selecting I/O port, `vmcall`, or `vmmcall` based on CPU features. High-bandwidth helpers always use I/O-port string instructions and save/restore frame pointer around `%bp` use.

State and persistence: No kernel state is stored here. Hypercalls read/write hypervisor state and optionally write output registers into caller-provided `u32 *` destinations.

Dependencies and integration points: Uses x86 cpufeatures, alternatives, stringify/asm helpers, TDX guest detection, and unwind hints. Integrated with VMware platform detection, paravirtual clock/steal-time code, and guest drivers.

Risks: Register ABI is strict. Output pointer arguments must be valid and non-null where asm writes them. High-bandwidth calls are documented as unsupported for encrypted-memory guests; callers must check memory-encryption attributes. Early boot before alternatives patching must take the slow path.

Test signals: VMware guest boot tests, hypervisor version and clock commands, TDX guest hypercall tests, high-bandwidth transfer users, alternatives-patching coverage, and encrypted-memory guest negative tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vmx.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/vmx.h

Purpose: Central x86 Intel VMX hardware definition header. It provides VMCS layouts, control-bit masks, VMX capability decoders, VMCS field encodings, exit qualification masks, EPT/VPID constants, error numbers, mitigation state, and #VE information structures used primarily by KVM and nested virtualization code.

Important APIs/types/functions: `struct vmcs_hdr` and `struct vmcs` model VMCS memory. `VMCS_CONTROL_BIT()` maps `VMX_FEATURE_*` numbers to control masks. Control constants cover primary, secondary, tertiary, pin-based, VM-exit, VM-entry, and VMFUNC controls. Inline decoders parse `IA32_VMX_BASIC` and `IA32_VMX_MISC` values: `vmx_basic_vmcs_revision_id()`, `vmx_basic_vmcs_size()`, `vmx_basic_vmcs_mem_type()`, `vmx_basic_encode_vmcs_info()`, `vmx_misc_preemption_timer_rate()`, `vmx_misc_cr3_count()`, `vmx_misc_max_msr()`, and `vmx_misc_mseg_revid()`. `enum vmcs_field` is the VMREAD/VMWRITE encoding list for guest/host state, controls, bitmaps, EPT, posted interrupts, CET fields, and more. EPT helpers include `vmx_eptp_page_walk_level()` and `EPT_VIOLATION_RWX_TO_PROT()`. `struct vmx_msr_entry`, `enum vm_entry_failure_code`, `enum vm_instruction_error_number`, `VMX_VMENTER_INSTRUCTION_ERRORS`, `enum vmx_l1d_flush_state`, `l1tf_vmx_mitigation`, and `struct vmx_ve_information` define supporting data.

Control flow: This header supplies constants used by VMX setup and VM-exit handling. KVM reads VMX MSRs, builds allowed control masks, writes VMCS fields by enum value, decodes exit qualification using masks, validates EPTP page-walk level, reports VM-instruction errors, and applies L1TF mitigation state during vmentry.

State and persistence: VMCS memory persists per VM/vCPU. MSR entry arrays persist for VM-entry/exit load-store lists. The external `l1tf_vmx_mitigation` records the global L1D flush policy. Most definitions are stateless hardware encodings.

Dependencies and integration points: Depends on bitops, bug checks, types, UAPI VMX definitions, trap numbers, and `vmxfeatures.h`. Integrated with KVM VMX, nested VMX, EPT MMU code, APIC virtualization, posted interrupts, Intel PT, CET, SGX exits, and mitigation code.

Risks: Constants are hardware ABI. Incorrect control bits or VMCS encodings can cause VM-entry failure, guest corruption, or host instability. `vmx_eptp_page_walk_level()` assumes prevalidated EPTP and only warns on unexpected values. EPT violation bit translations are guarded by `static_assert`, which is an important compile-time safety signal.

Test signals: KVM unit tests, VMX capability selftests, nested-VMX tests, EPT violation/MMIO tests, vmentry failure trace coverage, APICv/posted interrupt tests, and boot/runtime tests across Intel CPUs with different VMX feature sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vmx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vmxfeatures.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/vmxfeatures.h

Purpose: Defines Linux-internal VMX feature bit numbers used to represent Intel VMX controls and capabilities.

Important APIs/types/functions: `NVMXINTS` says the feature bitmap uses five 32-bit words. `VMX_FEATURE_*` macros assign bit numbers for pin-based controls, EPT/VPID, aggregated APIC features, VMFUNC, primary/secondary/tertiary processor controls, and named features displayed in `/proc/cpuinfo` when comments provide quoted strings.

Control flow: No executable code. VMX capability parsing populates these bits; `vmx.h` converts them to control masks with `VMCS_CONTROL_BIT()`.

State and persistence: Feature bits are stored in CPU capability data elsewhere. This header is the numbering contract.

Dependencies and integration points: Included by `vmx.h` and VMX CPU feature reporting code. Tied to `/proc/cpuinfo` feature-name generation conventions.

Risks: Bit renumbering breaks control-mask mapping and user-visible feature reporting. Aggregated features such as `FLEXPRIORITY` and `APICV` must match the implementation's combined control requirements.

Test signals: VMX feature enumeration tests, `/proc/cpuinfo` checks on Intel hosts, KVM capability tests, and build checks for `NVMXINTS` coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vmxfeatures.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vsyscall.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/vsyscall.h

Purpose: Declares x86 legacy vsyscall mapping and emulation hooks.

Important APIs/types/functions: With `CONFIG_X86_VSYSCALL_EMULATION`, `map_vsyscall()`, `set_vsyscall_pgtable_user_bits(pgd_t *root)`, `emulate_vsyscall_pf()`, and `emulate_vsyscall_gp()` are declared. Without emulation, map is a no-op and emulation helpers return false. `is_vsyscall_vaddr(unsigned long vaddr)` checks whether an address falls on the legacy vsyscall page.

Control flow: Boot or mm setup maps the vsyscall page when enabled. Fault handlers call page-fault or GP emulation helpers for instruction fetches or faults involving the vsyscall page. Address checks mask the input with `PAGE_MASK` and compare to `VSYSCALL_ADDR`.

State and persistence: The legacy vsyscall page is a fixed user-accessible mapping in the kernel portion of the address space. Emulation state is implemented elsewhere.

Dependencies and integration points: Includes seqlock, UAPI vsyscall constants, page types, and page-table types. Integrated with x86 fault handling, page tables, and legacy libc compatibility.

Risks: Vsyscall is security-sensitive because it is a fixed-address mapping. Emulation must validate faults and preserve legacy ABI behavior without widening executable attack surface.

Test signals: Legacy vsyscall mode tests, page-fault and GP emulation tests, ASLR/security regression checks, and builds with emulation disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/vsyscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/word-at-a-time.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/word-at-a-time.h

Purpose: Provides optimized x86 word-at-a-time zero-byte detection and safe unaligned word loading used by string/usercopy-style helpers.

Important APIs/types/functions: `struct word_at_a_time` stores `one_bits` and `high_bits`; `WORD_AT_A_TIME_CONSTANTS` initializes them to repeated `0x01` and `0x80`. `has_zero()` detects zero bytes with the classic `(a - one_bits) & ~a & high_bits` expression. `prep_zero_mask()`, `create_zero_mask()`, `zero_bytemask()`, and `find_zero()` transform detection masks differently on 64-bit and 32-bit. `load_unaligned_zeropad()` loads an unaligned word and uses an exception-table entry with `EX_TYPE_ZEROPAD` to zero-fill missing bytes on a page-crossing fault.

Control flow: Callers load a word, call `has_zero()`, derive a mask, then find the first zero byte or byte mask. `load_unaligned_zeropad()` executes one `mov`; if the access faults on an unmapped next page, exception-table fixup resumes after the load with zero padding semantics.

State and persistence: No persistent state. It reads memory and may take a handled exception.

Dependencies and integration points: Depends on bitops, wordpart helpers, x86 asm exception-table macros, and string routines in the kernel.

Risks: Bit tricks are width-specific. Exception-table correctness is critical; an incorrect fixup can turn a safe string load into a kernel fault. Unaligned access assumptions are x86-specific.

Test signals: String/memchr/strlen style tests, KASAN/KCSAN builds, page-boundary fault tests for zeropad behavior, and 32-bit/64-bit build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/word-at-a-time.h -->
