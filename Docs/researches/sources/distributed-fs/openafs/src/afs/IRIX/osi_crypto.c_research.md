# sources/distributed-fs/openafs/src/afs/IRIX/osi_crypto.c

## sources/distributed-fs/openafs/src/afs/IRIX/osi_crypto.c

Purpose: supplies the IRIX implementation of kernel random-byte generation, but the implementation is intentionally unsupported.

Important APIs/types/functions: `osi_readRandom(void *data, afs_size_t len)` calls `osi_Panic` with a message that the platform lacks a kernel cryptographic PRNG, then returns 0 only for compiler flow.

Control flow: unconditional panic.

State/persistence: none.

Dependencies/integration: used by OpenAFS crypto/rand consumers if they request kernel randomness on IRIX.

Risks/test signals: any feature requiring kernel random bytes will panic the kernel on IRIX. Test signal is negative: callers must avoid this path or provide another platform implementation before enabling crypto features needing randomness.
