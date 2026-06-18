# sources/distributed-fs/ceph-client/include/linux/stringhash.h

Purpose: defines non-cryptographic byte-string hashing helpers optimized for pathname components and dcache-style lookup.

Important APIs and types: `init_name_hash(salt)` seeds a hash, `partial_name_hash()` updates it one byte at a time, and `end_name_hash()` folds it to 32 bits with `hash_long()`. `full_name_hash()` hashes a byte range, and `hashlen_string()` returns a packed hash/length value. `hashlen_hash()`, `hashlen_len()`, and `hashlen_create()` manipulate the packed `u64`.

Control flow: simple callers may stream characters through `partial_name_hash()` and finalize with `end_name_hash()`. Faster implementations can use `full_name_hash()`/`hashlen_string()`, which may vary with architecture and configuration.

State and persistence: no state is kept here; callers supply salt and input. The file explicitly warns that hashes are not stable across versions, architectures, or boots and are not collision-resistant.

Dependencies and integration points: depends on `linux/hash.h` and compiler purity attributes. It integrates with VFS/dcache and server auth hashing through `svcauth.h`.

Risks and test signals: risks include treating values as persistent on-disk/network identifiers, using them for adversarial security boundaries, or mixing case/encoding incorrectly. Test signals include dcache/hash distribution tests, boot-to-boot non-persistence assumptions, and collision stress under long and short names.
