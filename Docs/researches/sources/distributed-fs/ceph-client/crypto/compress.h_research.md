<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/compress.h -->
# sources/distributed-fs/ceph-client/crypto/compress.h

## Purpose

`compress.h` is a local internal header for Crypto API compression support. It declares shared helpers used by compression implementation files without exposing them as public API.

## Important APIs, Types, and Flow

The header forward-declares `struct acomp_req` and `struct comp_alg_common`, includes local `internal.h`, and declares `crypto_init_scomp_ops_async(struct crypto_tfm *tfm)` plus `comp_prepare_alg(struct comp_alg_common *alg)`. There is no executable control flow in this file.

`crypto_init_scomp_ops_async()` is intended to initialize asynchronous operations for synchronous compression transforms, while `comp_prepare_alg()` prepares common compression algorithm metadata before registration.

## State, Dependencies, and Integration

There is no persistent state in the header. It depends on local crypto internals and is included by compression source files in this directory. Its integration role is to keep compression helper declarations source-local rather than part of installed public headers.

## Risks and Test Signals

Risks are declaration drift from implementation signatures, accidental public/private API confusion, and include-order dependency through `internal.h`. Test signals are compile coverage of compression modules and registration tests for sync and async compression algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/compress.h -->
