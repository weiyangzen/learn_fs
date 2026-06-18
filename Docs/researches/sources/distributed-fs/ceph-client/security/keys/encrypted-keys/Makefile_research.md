# sources/distributed-fs/ceph-client/security/keys/encrypted-keys/Makefile

Purpose: Builds the encrypted key type and optional trusted master key support.

Important APIs/types/functions: Builds `encrypted-keys.o` from `encrypted.o` and `ecryptfs_format.o`, and conditionally adds `masterkey_trusted.o` based on `CONFIG_TRUSTED_KEYS` and `CONFIG_ENCRYPTED_KEYS`.

Control flow: Kbuild combines objects into the encrypted-keys composite object when `CONFIG_ENCRYPTED_KEYS` is enabled.

State and persistence: No runtime state.

Dependencies and integration: Connects encrypted key type with eCryptfs payload formatting and trusted-key master support.

Risks and test signals: Risks are conditional object expression mistakes for built-in/module combinations. Build tests should cover encrypted keys with trusted keys disabled, built-in, and modular.
