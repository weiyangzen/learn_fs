# sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/sign_key.S

## Purpose
Embeds the PEM private signing key into the host test binary as read-only data for SIGSTRUCT generation.

## Important APIs, types, and functions
Defines global symbols `sign_key` and `sign_key_end` around `.incbin "sign_key.pem"`.

## Control flow
No executable control flow.

## State and persistence
The key bytes are immutable `.rodata` in `test_sgx`. `sigstruct.c` computes the range length from the two symbols.

## Dependencies and integration points
Consumed by `gen_sign_key()` in `sigstruct.c`; requires `sign_key.pem` to be available at assembly time.

## Risks
Missing or malformed PEM breaks enclave measurement/signing. The key is a test key and should not be treated as production secret material.

## Test signals
OpenSSL PEM parsing failure causes SGX setup failure before enclave initialization.
