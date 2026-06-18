# sources/distributed-fs/ceph-client/security/integrity/platform_certs/load_uefi.c

Purpose: Loads UEFI db/dbx/MokListRT/MokListXRT certificates and revocations into kernel keyrings and blacklists.

Important APIs/types/functions: Includes DMI `uefi_skip_cert` quirk table, `uefi_check_ignore_db()`, `get_cert_list()`, `load_moklist_certs()`, and `load_uefi_certs()` as a late initcall.

Control flow: `load_uefi_certs()` skips known Apple T2 systems, requires EFI get-variable support, optionally reads db unless `MokIgnoreDB` is set, reads dbx, and only when secure boot is enabled reads MokListXRT and MokListRT. `load_moklist_certs()` first tries the EFI MOKvar config table and falls back to the UEFI variable. Each blob is parsed by `parse_efi_signature_list()` with db, dbx, or MOK handlers and then freed.

State and persistence: Uses transient kmalloc buffers; imported certs/hashes persist in platform/machine keyrings or revocation/blacklist infrastructure.

Dependencies and integration: EFI runtime services, shim MOK variables, secure boot status, DMI quirks, keyring handlers, IMA secure boot policy inputs, and system keyrings.

Risks and test signals: Risks include firmware crashes mitigated by quirks, silent skip when variables are absent, secure-boot trust semantics for MOK, and buffer-size probing errors. Tests should cover quirk skip, `MokIgnoreDB`, missing variables, MOK table fallback, secure boot disabled behavior, and malformed ESL blobs.
