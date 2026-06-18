# sources/distributed-fs/ceph-client/arch/riscv/kernel/efi-header.S

Purpose: Emits the PE/COFF header needed for booting the RISC-V kernel as a UEFI application.

Important APIs/types/functions: Defines the `__EFI_PE_HEADER` macro, COFF header fields, optional header fields, `.text` and `.data` section table entries, and RISC-V machine type selection.

Control flow: Build-time assembly only; `head.S` includes the macro when `CONFIG_EFI` is enabled so firmware recognizes the image and jumps to the EFI stub entry.

State and persistence: Produces immutable image header bytes at the start of the kernel image.

Dependencies and integration points: Depends on PE constants, EFI stub symbols, linker-provided section bounds, and RISC-V image header layout.

Risks and test signals: Header size, alignment, section virtual/raw sizes, or entry point mistakes can make firmware reject the kernel. Test UEFI boot on RV32/RV64, Clang/GCC data size paths, PE inspection, and secure-boot tooling compatibility.
