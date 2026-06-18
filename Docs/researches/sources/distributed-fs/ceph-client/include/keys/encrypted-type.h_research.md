# sources/distributed-fs/ceph-client/include/keys/encrypted-type.h

Source read summary: 36 lines, 1118 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/encrypted-type.h` defines the RCU-protected payload wrapper for encrypted keys and the external encrypted key type.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: `encrypted_key_payload`. Important constants/macros: none.

Control flow: The encrypted key implementation stores decrypted data, IV, encrypted data, datablob metadata, and master-key description in `struct encrypted_key_payload`; key operations update or read that payload through RCU-safe replacement.

State and persistence behavior: Payloads persist inside key objects, while decrypted bytes must be protected in memory and cleared on destroy. RCU allows readers to finish while updates replace payloads.

Dependencies and integration points: It includes `linux/key.h`, `linux/rcupdate.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Incorrect datalen/encrypted_datalen handling, master-key lookup failures, or incomplete zeroization can expose secret material.

Test signals: Run encrypted key add/update/read tests, master-key revoke tests, RCU update stress, and memory-sanitizer checks for cleanup paths.
