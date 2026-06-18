# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/alloc.c

This kernel adapter implements libc-style allocation routines for hcrypto using OpenAFS kernel allocation primitives. `_afscrypto_calloc` allocates `num * len` bytes via `afs_osi_Alloc` and zeroes them if non-null; `_afscrypto_malloc` wraps `afs_osi_Alloc`; `_afscrypto_free` calls `afs_osi_Free(ptr, 0)`; `_afscrypto_strdup` duplicates with the remapped `malloc`; `_afscrypto_realloc` is a deliberately narrow workaround.

State is kernel heap memory. The realloc behavior is especially important: `realloc(NULL, len)` allocates space for 20 items via `calloc(20, len)`, while reallocating an existing pointer returns it unchanged. This matches known hcrypto call sites that shrink buffers or derive keys.

Dependencies are `kernel/config.h` macro remapping, `afs_osi_Alloc`, `afs_osi_Free`, and string functions. Integration is kernel hcrypto and RFC3961 builds. Risks include integer overflow in `num * len`, freeing without original size, and the hard-coded 20-key realloc assumption. Test signals are kernel crypto encrypt/decrypt/key-derivation tests and memory instrumentation for leaks or overwrite under derived-key workloads.
