# sources/distributed-fs/ceph-client/security/keys/Makefile

Purpose: Kbuild object list for core key management and optional key features.

Important APIs/types/functions: Always builds core key management objects (`gc.o`, `key.o`, `keyring.o`, `keyctl.o`, `permission.o`, `process_keys.o`, `request_key.o`, `request_key_auth.o`, `user_defined.o`). Adds compat, proc, sysctl, persistent keyrings, DH, public-key ops, big key, trusted keys, and encrypted keys based on config.

Control flow: Config symbols choose object inclusion and compat DH support.

State and persistence: No runtime state.

Dependencies and integration: Coordinates subdirectories `trusted-keys/` and `encrypted-keys/` plus syscall compatibility code.

Risks and test signals: Risks include missing objects under unusual config combinations, especially compat DH. Build matrix is the primary signal.
