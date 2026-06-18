# sources/distributed-fs/ceph-client/include/keys/system_keyring.h

Source read summary: 134 lines, 3899 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/system_keyring.h` declares system trusted keyrings, blacklist/revocation helpers, and restriction callbacks used by module signing, kexec, firmware, and certificate trust paths.

Important APIs, types, and functions: Important exported functions or hooks: `restrict_link_by_builtin_trusted`, `restrict_link_by_digsig_builtin`, `load_module_cert`, `restrict_link_by_builtin_and_secondary_trusted`, `restrict_link_by_digsig_builtin_and_secondary`, `add_to_secondary_keyring`, `restrict_link_by_builtin_secondary_and_machine`, `set_machine_trusted_keys`, `mark_hash_blacklisted`, `is_hash_blacklisted`, `is_binary_blacklisted`, `add_key_to_revocation_list`, `is_key_on_revocation_list`, `set_platform_trusted_keys`. Important types: `blacklist_hash_type`, `pkcs7_message`. Important constants/macros: `restrict_link_by_builtin_trusted`, `restrict_link_by_digsig_builtin`, `restrict_link_by_builtin_and_secondary_trusted`, `restrict_link_by_digsig_builtin_and_secondary`, `restrict_link_by_builtin_secondary_and_machine`.

Control flow: Loaders query builtin, secondary, platform, machine, and blacklist keyrings through these helpers; restriction callbacks decide whether a new cert may link into a trusted keyring.

State and persistence behavior: Trust anchors and blacklist hashes persist in global keyrings for the boot lifetime. Some objects are only present under Kconfig options, so many declarations compile to stubs.

Dependencies and integration points: It includes `linux/key.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Configuration-dependent stubs can change security behavior. Incorrect restriction callbacks or blacklist checks can allow untrusted modules/images or reject valid signed content.

Test signals: Run module-signing, kexec/image verification, certificate import, blacklist hash matching, and Kconfig matrix builds for secondary/platform/machine keyrings.
