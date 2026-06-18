## sources/distributed-fs/ceph-client/arch/arm64/kernel/efi-header.S

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/efi-header.S` emits the ARM64 kernel's UEFI
PE/COFF header data. It lets firmware recognize the kernel image as an EFI application while still
keeping a valid non-EFI entry opcode when EFI support is disabled.

### Important APIs, Types, And Functions
The file defines two assembler macros: `efi_signature_nop` and `__EFI_PE_HEADER`. With
`CONFIG_EFI`, `efi_signature_nop` emits an instruction whose opcode encodes the UEFI `MZ` DOS
signature. Without EFI it emits a normal `nop`. `__EFI_PE_HEADER` writes the PE signature, COFF file
header, PE32+ optional header, section table, optional debug directory entries, CodeView path data,
BTI forward-CFI DLL characteristics, and alignment padding.

### Control Flow
There is no runtime control flow beyond the first header instruction. The assembler emits a static
binary layout controlled by `CONFIG_EFI`, `CONFIG_DEBUG_EFI`, `CONFIG_ARM64_BTI_KERNEL`,
`CONFIG_RELOCATABLE`, linker symbols such as `_end`, `__initdata_begin`, and EFI constants from
`linux/pe.h`.

### State, Persistence, And Dependencies
The persistent artifact is the kernel image header on disk/in memory. Dependencies include PE/COFF
constants, segment and file alignment definitions, EFI stub entry symbol
`__efistub_efi_pe_entry`, linker-provided size symbols, `VMLINUX_PATH` for debug builds, and BTI
kernel configuration.

### Integration Points
Firmware and bootloaders consume this header before Linux runs. EFI stub code uses the declared
entry point and section metadata. Debug EFI and BTI metadata allow firmware/tooling to understand
debug path and branch protection properties.

### Risks
Any offset, size, alignment, section count, or signature error can make the kernel unbootable via
UEFI. Debug-table RVAs are subtle because the header itself is not covered by a section, so payload
placement must remain synchronized with the comments. BTI metadata must agree with actual kernel BTI
support.

### Test Signals
Build with and without `CONFIG_EFI`, inspect the image with PE/COFF tools, boot via UEFI firmware and
common bootloaders, verify debug EFI builds expose the expected path data, and test BTI-kernel images
on firmware that interprets DLL characteristics.
