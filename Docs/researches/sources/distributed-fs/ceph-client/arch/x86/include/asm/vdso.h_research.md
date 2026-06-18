# sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso.h

Purpose: Declares the x86 kernel-side vDSO image metadata and mapping/fault-repair entry points. It is the architecture contract between vDSO image generation, process memory setup, signal-return trampolines, and exception fixup.

Important APIs/types/functions: `struct vdso_image` contains the image data pointer, page-rounded size, alternative-instruction metadata, exception-table metadata, and symbol offsets for `__kernel_sigreturn`, `__kernel_rt_sigreturn`, `__kernel_vsyscall`, `int80_landing_pad`, and compat sigreturn landing pads. `vdso64_image`, `vdsox32_image`, and `vdso32_image` are the architecture image instances. `init_vdso_image()` validates/prepares an image during init, `map_vdso_once()` maps an image at a requested user address, and `fixup_vdso_exception()` resolves faults against the vDSO exception table.

Control flow: The header only declares data and functions. Runtime flow is: init code calls `init_vdso_image()`, process setup maps the selected image with `map_vdso_once()`, user code executes vDSO symbols, and kernel exception handling can call `fixup_vdso_exception()` when a vDSO access faults.

State and persistence: `struct vdso_image` instances are read-mostly kernel metadata around embedded ELF/image bytes. Mappings are per-mm user virtual memory state; no file-backed persistence is involved.

Dependencies and integration points: Includes page types, linkage/init annotations, and `linux/mm_types.h` for `pt_regs` consumers. It integrates with x86 signal delivery, compat ABI support, alternative patching, exception-table fixups, ELF/vDSO mapping, and syscall fallback paths.

Risks: Incorrect symbol offsets or exception-table bounds can break signal return, compat entry paths, or fault recovery. Mapping size must remain page-aligned. 32-bit, x32, and 64-bit images have different ABI expectations and must not be mixed.

Test signals: Boot-time vDSO init, `clock_gettime`/`gettimeofday`/`getcpu` vDSO use from user space, signal return tests across 32-bit/x32/64-bit ABIs, and fault-injection or selftests that exercise vDSO exception fixups.
