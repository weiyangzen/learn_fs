# sources/distributed-fs/ceph-client/security/integrity/platform_certs/keyring_handler.h

Purpose: Internal platform certificate handler declarations and DMI quirk macro support for EFI/platform certificate loaders.

Important APIs/types/functions: Declares blacklist helpers and handler selector functions for db, MOK, CA keys, code-signing keys, and dbx. Defines `UEFI_QUIRK_SKIP_CERT(vendor, product)` if not already provided.

Control flow: No runtime flow. Consumers pass the declared handler selectors to `parse_efi_signature_list()`.

State and persistence: No state. It defines compile-time interface and DMI match helper data shape.

Dependencies and integration: Includes EFI types and is included by UEFI and powerpc certificate loaders and handler implementation.

Risks and test signals: Risks are declaration drift and quirk macro mismatch with DMI arrays. Build coverage across EFI and powerpc configurations is the main signal.
