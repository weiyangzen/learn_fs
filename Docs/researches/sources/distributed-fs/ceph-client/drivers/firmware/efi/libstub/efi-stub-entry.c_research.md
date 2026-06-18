# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/efi-stub-entry.c

Purpose: provides the generic EFI PE/COFF entry point used by ARM, arm64, RISC-V, and LoongArch stubs, bridging firmware invocation to common stub setup and kernel handoff.

Important APIs/types/functions: defines `efi_pe_entry()`, `alloc_primary_display()`, private `kernel_image_addr()`, and `kernel_image_offset`.

Control flow: `efi_pe_entry()` stores the EFI system table, validates its signature, obtains the loaded image protocol, parses the EFI command line, logs boot start, calls architecture `handle_kernel_image()` to relocate or reserve the kernel image, records the image offset for in-image data references, invokes `efi_stub_common()`, and frees temporary image/reserve allocations before returning firmware status. `alloc_primary_display()` returns architecture-appropriate storage for primary display data.

State and persistence behavior: `kernel_image_offset` records relocation delta while the stub runs. Other persistent handoff state is managed by common stub code and architecture handlers.

Dependencies and integration points: depends on EFI loaded image protocol, architecture `handle_kernel_image()`, common command-line and stub setup helpers, sysfb primary display storage, and EFI boot services.

Risks and test signals: failures before `efi_stub_common()` must return EFI status without leaking allocations; freeing image/reserve ranges must match architecture allocation semantics. Test signals include valid PE entry on supported architectures, command-line parsing, correct primary display handoff, and clean return codes on missing loaded-image protocol or relocation failure.
