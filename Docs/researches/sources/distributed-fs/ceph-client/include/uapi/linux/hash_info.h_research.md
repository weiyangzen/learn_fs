<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hash_info.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hash_info.h

## Purpose
`hash_info.h` assigns stable numeric IDs and digest sizes for hash algorithms exposed through kernel/user ABI surfaces.

## Important APIs, types, and functions
`enum hash_algo` defines algorithm IDs such as `HASH_ALGO_MD4`, `MD5`, `SHA1`, `RIPE_MD_160`, `SHA256`, `SHA384`, `SHA512`, `SHA224`, `RIPE_MD_128`, `RIPE_MD_256`, `RIPE_MD_320`, `WP_256`, `WP_384`, `WP_512`, `TGR_128`, `TGR_160`, `TGR_192`, `SM3_256`, `STREEBOG_256`, `STREEBOG_512`, `SHA3_256`, `SHA3_384`, and `SHA3_512`, ending with `HASH_ALGO__LAST`.

## Control flow
There is no runtime flow. Kernel subsystems and tools pass or store the enum ID, then use subsystem-specific lookup tables to map it to crypto algorithm names and digest sizes.

## State and persistence behavior
Algorithm IDs may appear in persisted signatures, measurement logs, module metadata, integrity records, or policy formats. The enum ordering is therefore ABI-sensitive, and new algorithms must be appended rather than inserted.

## Dependencies and integration points
It is a small standalone UAPI header used by integrity, module-signing, key, and measurement code that needs stable hash IDs.

## Risks and test signals
Risks include reordering enum values, missing table entries for newly appended algorithms, digest-size assumptions made outside this header, and disagreement with crypto API names. Test signals include build-time table coverage for every enum, IMA/EVM/module-signing verification with each supported hash, unknown numeric ID rejection by consumers, and ABI regression tests for numeric values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hash_info.h -->
