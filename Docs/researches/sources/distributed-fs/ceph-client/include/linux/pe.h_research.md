<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pe.h -->
# sources/distributed-fs/ceph-client/include/linux/pe.h

## Purpose
Provides Linux kernel definitions for PE/COFF and EFI-stub image headers. It includes Linux EFI stub version/magic constants, PE signatures, machine IDs, image flags, subsystem and DLL characteristics, section flags, debug types, executable header structs, relocation enums, and certificate structs.

## Important APIs, Types, And Functions
- `LINUX_EFISTUB_MAJOR_VERSION`, `LINUX_EFISTUB_MINOR_VERSION`, and `LINUX_PE_MAGIC` describe Linux EFI-bootable images.
- PE constants include DOS/NT signatures, optional-header magic values, machine type IDs for many architectures, image flags, subsystem IDs, DLL characteristic bits, section flags, and debug type IDs.
- Header layout structs include `struct mz_hdr`, `mz_reloc`, `pe_hdr`, `pe32_opt_hdr`, `pe32plus_opt_hdr`, `data_dirent`, `data_directory`, and `section_header`.
- Relocation enums cover x64, ARM, SH, PPC, x86, and IA64 COFF relocation types; `struct coff_reloc` overlays those enums with raw 16-bit data.
- Certificate definitions include `WIN_CERT_TYPE_*`, `WIN_CERT_REVISION_*`, and `struct win_certificate`.

## Control Flow
There is no executable control flow. Parsers or EFI-stub builders read the DOS header, follow `peaddr` to the PE header, interpret optional-header and data-directory fields, walk section headers, process relocations, and optionally inspect certificate/debug data using these definitions.

## State And Persistence
The persistent state is file-format ABI encoded in bootable images, modules, or signed PE/COFF artifacts. Struct layout must match on-disk little-endian PE fields; changing constants or field order would break image parsing and boot tooling.

## Dependencies And Integration Points
Depends on `<linux/types.h>` and is excluded from struct definitions under `__ASSEMBLY__`. It integrates with EFI stub image creation/loading, PE/COFF parsers, secure boot/certificate handling, relocation processors, and architecture-specific boot code.

## Risks And Edge Cases
Risks include on-disk endian assumptions, PE32 versus PE32+ layout differences, alignment flag interpretation, overlapping constant values that are architecture- or OS-version-specific, flexible `message[]` sizing in `mz_hdr`, and trusting unvalidated file offsets/counts from external images.

## Test Signals
Validate EFI boot of PE32/PE32+ kernels, parse known-good Linux EFI images, check machine/subsystem/magic values, fuzz malformed headers and section counts, verify relocation decoding for supported architectures, and test secure-boot certificate table parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pe.h -->
