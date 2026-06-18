# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/efi.h

## Purpose

`efi.h` declares LoongArch EFI boot/runtime interfaces. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 35 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: efi_init, efi_runtime_init, efi_fdt_pointer, efifb_setup_from_dmi, EFI_ALLOC_ALIGN, EFI_RT_VIRTUAL_OFFSET, efi_get_max_initrd_addr, efi_get_kimg_min_align. Symbol extraction from the file shows representative defines `_ASM_LOONGARCH_EFI_H`, `ARCH_EFI_IRQ_FLAGS_MASK`, `arch_efi_call_virt_setup`, `arch_efi_call_virt_teardown`, `EFI_ALLOC_ALIGN`, `EFI_RT_VIRTUAL_OFFSET`, `EFI_KIMG_PREFERRED_ADDRESS`, representative callable declarations or inline helpers `efi_init`, `efi_runtime_init`, `efi_fdt_pointer`, `efifb_setup_from_dmi`, `efi_get_max_initrd_addr`, `efi_get_kimg_min_align`, and representative local types none visible in this header. Direct includes seen in the header are `linux/efi.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header connects EFI stub, runtime services, framebuffer setup and kernel image placement. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: runtime virtual offset and IRQ flag mask must match CSR/DMW layout; initrd placement affects boot reliability. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
