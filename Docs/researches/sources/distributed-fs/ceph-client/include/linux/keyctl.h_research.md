# sources/distributed-fs/ceph-client/include/linux/keyctl.h

## Purpose

`keyctl.h` defines kernel-private structures for public-key operations used by the keyctl interface. It complements the UAPI keyctl command definitions with in-kernel query and operation parameter blocks. The source was read as a complete 42-line file.

## Important APIs, Types, and Functions

`struct kernel_pkey_query` reports supported operations, key size, maximum raw data size, signature size, encryption size, and decryption size. `enum kernel_pkey_operation` distinguishes encrypt, decrypt, sign, and verify. `struct kernel_pkey_params` carries the key pointer, encoding, hash algorithm, temporary info string, input and output sizes, and selected operation.

## Control Flow

This header has no implementation flow. Keyctl command handlers and asymmetric key implementations fill or consume these structures when dispatching public-key operations.

## State and Persistence Behavior

The structures are transient call descriptors. They hold a borrowed `struct key *` and, for `info`, ownership of a temporary string that the caller must release according to the implementation contract.

## Dependencies and Integration Points

It includes `uapi/linux/keyctl.h` and relies on `struct key` from the key subsystem. It integrates with asymmetric key types, crypto helpers, and keyctl syscall handling.

## Risks and Edge Cases

Size fields are ABI-sensitive and must match user buffer validation. Verify uses a second input length instead of output length through a union, so callers must branch by `op` correctly. Encoding/hash strings require strict validation by key type backends.

## Test Signals

Keyctl public-key selftests, asymmetric key sign/verify/encrypt/decrypt tests, unsupported operation tests, max-size boundary tests, and bad encoding/hash input tests are useful coverage.
