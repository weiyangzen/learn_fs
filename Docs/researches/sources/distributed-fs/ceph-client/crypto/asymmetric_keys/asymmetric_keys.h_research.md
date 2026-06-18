# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/asymmetric_keys.h

Purpose: provides private declarations shared by asymmetric key implementation files.

Important APIs/types/functions: declares `asymmetric_key_hex_to_key_id()`, `__asymmetric_key_hex_to_key_id()`, and `asymmetric_key_eds_op()`. The first two convert hexadecimal key-id strings into `struct asymmetric_key_id` values, while `asymmetric_key_eds_op()` is the encryption/decryption/signing operation dispatch for asymmetric keys.

Control flow: implementation files include this header to avoid exposing private helper declarations in public keyring headers. Restriction parsing uses the hex helpers, and the key type operation table points at `asymmetric_key_eds_op()`.

State and persistence: no state is stored here. The types referenced are owned by keyring and public key payload code.

Dependencies and integration points: depends on `<keys/asymmetric-type.h>` and the kernel pkey parameter definitions reachable through it. Integrated by `asymmetric_type.c`, `restrict.c`, `x509_public_key.c`, and related parser code.

Risks: declarations must match exported definitions exactly; signature drift breaks builds or keyctl operation dispatch. Keeping this header private limits accidental ABI expansion.

Test signals: compile coverage of asymmetric key type, restriction, X.509, and pkey operation configs validates the header.
