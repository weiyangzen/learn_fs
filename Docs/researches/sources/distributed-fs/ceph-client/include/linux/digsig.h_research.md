<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/digsig.h -->
# sources/distributed-fs/ceph-client/include/linux/digsig.h

## Purpose
Declares compact public-key and signature header formats plus the kernel digital signature verification entry point.

## Important APIs, Types, And Functions
Defines `enum pubkey_algo`, `enum digest_algo`, packed `struct pubkey_hdr`, packed `struct signature_hdr`, and `digsig_verify()`. The only public algorithms in this header are RSA, SHA1, and SHA256. If signature support is not built, `digsig_verify()` returns `-EOPNOTSUPP`.

## Control Flow
Callers provide a keyring, signature blob, digest pointer, and digest length. The implementation validates the signature header, locates a matching key, and checks that the signature covers the supplied digest. The stub path fails immediately.

## State And Persistence
The header defines serialized blob layouts but owns no mutable state. Key persistence is handled by the kernel keyring subsystem.

## Dependencies And Integration Points
Depends on `linux/key.h`, packed binary formats, and the asymmetric-key/signature code selected by `CONFIG_SIGNATURE`.

## Risks And Edge Cases
The packed flexible-array formats are length-sensitive; callers must validate `siglen`, `digestlen`, algorithm fields, MPI counts, and key IDs. SHA1 support may be legacy-sensitive. Stub behavior must be handled by consumers that can build without signature verification.

## Test Signals
Validation should include supported and unsupported algorithms, malformed short headers, bad MPI counts, keyring misses, correct and incorrect digests, module and built-in signature configurations, and the `CONFIG_SIGNATURE=n` stub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/digsig.h -->
