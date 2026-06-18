# sources/distributed-fs/ceph-client/tools/include/uapi/linux/module_signature.h

Purpose: defines the trailer format and algorithm identifiers for signed Linux kernel modules. It is used by tooling that appends or inspects module signatures and by kernel module signature verification.

Important APIs/types: enums list public-key algorithm (`PKEY_ALGO_RSA`, `PKEY_ALGO_ECDSA`) and hash algorithms (`PKEY_HASH_MD4` through SHA variants and SM3). `struct module_signature` records algorithm, hash, signer/key ID lengths, reserved fields, and big-endian signature length. `MODULE_SIG_STRING` is the magic trailer marker.

Control flow, state, and persistence: signing tools append signature data, signer/key identifiers, a `module_signature` record, and the magic string to a module. Kernel module loading parses the trailer from EOF backward, validates the signature against trusted keys, then accepts or rejects loading. Signature data persists in the module file.

Dependencies and integration points: depends on Linux integer types. Integrates module build/signing tools, kernel keyrings, crypto/public-key verification, secure boot policies, and module loader enforcement.

Risks and test signals: risks include endian mistakes in signature length, unsupported hash/pubkey algorithms, malformed trailer lengths, and trusting unsigned or appended data incorrectly. Tests should sign modules with supported algorithms, reject corrupted signatures/trailers, validate absent signatures under permissive and enforcing modes, and inspect signer/key ID lengths.
