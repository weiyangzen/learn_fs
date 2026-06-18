# sources/distributed-fs/openafs/src/rxkad/fcrypt.h

Purpose: Defines the small public type contract for the rxkad fcrypt primitive.

Important APIs/types: `ENCRYPTIONBLOCKSIZE` is fixed at 8 bytes. `fc_InitializationVector` is two 32-bit words. `MAXROUNDS` is 16 and `fc_KeySchedule` is an array of 16 32-bit words. `FCRYPT_ENCRYPT` and `FCRYPT_DECRYPT` encode operation direction.

Control flow and state: Header-only definitions; no runtime state. It deliberately undefines prior `ENCRYPTIONBLOCKSIZE` and `MAXROUNDS` macros to keep the rxkad cipher ABI stable.

Dependencies and integration: Included by `rxkad_prototypes.h`, `private_data.h`, `fcrypt.c`, packet crypto, and tests. The types assume `afs_int32` is already visible through OpenAFS headers.

Risks: The 8-byte block and 16-round schedule are hard ABI assumptions across connection-private structures and packet layout. Any change breaks encrypted challenge packets and packet sealing.

Test signals: Build coverage comes from every rxkad object; direct functional signals come from `fc_test` and `tcrypt`.
