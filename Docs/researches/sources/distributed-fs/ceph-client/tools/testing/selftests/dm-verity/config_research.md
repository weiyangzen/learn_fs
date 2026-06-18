# sources/distributed-fs/ceph-client/tools/testing/selftests/dm-verity/config

## Purpose

This config declares kernel features needed by the dm-verity keyring selftest.

## Important APIs, Types, and Functions

It requests device mapper, dm-verity as module, root hash signature verification, module unload, keyrings, asymmetric key types, X.509 parsing, PKCS#7 parsing, and system data verification.

## Control Flow

There is no executable flow; config tooling consumes the symbols.

## State and Persistence Behavior

It persists only required kernel configuration.

## Dependencies and Integration Points

The script relies on these features to load dm-verity with parameters, manage `.dm-verity` keyrings, add asymmetric certs, and verify PKCS#7 root-hash signatures.

## Risks and Edge Cases

Even with config support, runtime tools such as openssl, veritysetup, keyctl, losetup, and dmsetup must be present.

## Test Signals

Matching kernels should allow both unsealed and sealed keyring test modes to execute.
