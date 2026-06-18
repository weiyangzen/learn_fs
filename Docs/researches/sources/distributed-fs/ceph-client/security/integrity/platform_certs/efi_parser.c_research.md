# sources/distributed-fs/ceph-client/security/integrity/platform_certs/efi_parser.c

Purpose: Parses EFI signature lists and dispatches certificate/hash elements to caller-selected handlers.

Important APIs/types/functions: Exports `parse_efi_signature_list(source, data, size, get_handler_for_guid)`, where the callback maps each `signature_type` GUID to an `efi_element_handler_t` or NULL.

Control flow: The parser iterates through sublists, copies each `efi_signature_list_t` header, validates total size, header size, element size, and divisibility, asks for a handler, skips uninterested lists, and invokes the handler for each element’s `signature_data` excluding the owner GUID header.

State and persistence: Stateless parser. Persistence depends on handlers adding certificates or hashes to keyrings/blacklists.

Dependencies and integration: Used by UEFI, powerpc secure variable, and other platform certificate loaders. Integrates with EFI GUID definitions and platform keyring/blacklist handlers.

Risks and test signals: Bounds validation is critical because firmware blobs are untrusted. Tests should include truncated list headers, overruns, zero/too-small element sizes, header padding, uninterested GUID skipping, mixed-list blobs, and exact-size termination.
