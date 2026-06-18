# sources/distributed-fs/ceph-client/security/integrity/platform_certs/keyring_handler.c

Purpose: Maps EFI signature-list GUIDs to handlers that load certificates into platform/machine/secondary keyrings or blacklist/revoke hashes and certificates.

Important APIs/types/functions: Provides `get_handler_for_db()`, `get_handler_for_mok()`, `get_handler_for_ca_keys()`, `get_handler_for_code_signing_keys()`, and `get_handler_for_dbx()`. Internal handlers call `mark_hash_blacklisted()`, `add_key_to_revocation_list()`, `add_to_platform_keyring()`, `add_to_machine_keyring()`, and `add_to_secondary_keyring()`.

Control flow: DB accepts X.509 certs into the platform keyring. MOK accepts X.509 certs into machine keyring when configured and `imputed_trust_enabled()` is true, otherwise platform keyring. CA and code-signing key databases route X.509 certs to machine and secondary keyrings respectively. DBX maps X.509 TBS hashes, executable hashes, and X.509 certs to blacklist/revocation handlers.

State and persistence: No local state beyond initdata GUID constants. Handlers persist data in global keyrings/blacklists.

Dependencies and integration: Invoked by EFI signature parser from UEFI and powerpc loaders. Depends on system keyring, blacklist, integrity keyring, and machine/platform keyring config.

Risks and test signals: Risks include trust-domain confusion for MOK, unsupported GUID silently skipped, and config-dependent handler changes. Tests should validate GUID-to-handler mapping for all supported GUIDs and machine-keyring fallback behavior.
