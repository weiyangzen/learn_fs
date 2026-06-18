
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/zboot-header.S

Purpose: emits the EFI PE/COFF and Linux zboot image header for compressed EFI boot images, including payload metadata, optional SBAT, optional debug directory, and section table layout.

Important APIs/types/functions: defines global `__efistub_efi_zboot_header` in `.head`, DOS/zimg metadata fields, PE header, optional header, data directories, `.text`, optional `.sbat`, and `.data` section headers, and optional CodeView/extended DLL characteristics records.

Control flow: assembly is declarative. Firmware reads the PE/COFF header to load the zboot EFI application, while Linux/zboot tooling can read the `zimg` fields for payload offset, payload size, and `COMP_TYPE`.

State and persistence behavior: creates immutable image-header data in the binary. It does not maintain runtime state.

Dependencies and integration points: depends on PE constants, architecture `MACHINE_TYPE`, 32/64-bit config, `COMP_TYPE`, compressed-data linker symbols, SBAT config, debug EFI path config, and zboot entry symbol.

Risks and test signals: header offsets, section sizes, file alignment, payload size subtraction, and optional table sizes must match linker output. Test signals include firmware loading the zboot image, PE inspection, Secure Boot/SBAT validation, debug table presence under config, and decompressor locating `_gzdata_start`.
