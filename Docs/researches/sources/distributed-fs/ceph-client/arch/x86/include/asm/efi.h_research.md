
# sources/distributed-fs/ceph-client/arch/x86/include/asm/efi.h

Purpose: x86 EFI runtime, stub, mixed-mode, memory-map, and boot-mode interface.

Important APIs and control flow: declares EFI firmware/config addresses, mixed-mode stack, runtime mapping constants, argument-count checking for assembler thunks, FPU begin/end wrappers, and 64-bit `efi_call()`/`arch_efi_call_virt()` with optional IBT disable/restore. EFI setup functions reserve ranges, allocate/setup page tables, map runtime regions, apply quirks, sync mappings, and unmap boot services. Mixed-mode support maps native arguments to 32-bit EFI thunk calls, zeroes upper halves of output pointers, splits 64-bit arguments, widens status values, and dispatches through `efi_fn_call()`.

State, dependencies, and risks: state includes EFI memory maps, runtime mappings, firmware tables, mixed-mode stack, boot mode, and runtime-map exports. Dependencies include FPU API, page tables, TLB/MMU context, IBT, EFI core, KASAN stub constraints, and boot compressed code. Risks include thunk argument count/width mistakes, runtime mapping instability across kexec, calling firmware with wrong FPU/IBT state, and mixed 32/64-bit pointer truncation. Test signals are EFI boot/runtime service tests, mixed-mode boot, kexec, secure boot mode checks, and runtime map sysfs coverage.
