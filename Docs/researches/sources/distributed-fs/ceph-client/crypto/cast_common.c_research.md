<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cast_common.c -->
# sources/distributed-fs/ceph-client/crypto/cast_common.c

## Purpose

`cast_common.c` provides the shared CAST S-box tables used by CAST-128 and CAST-256 implementations. It contains no transform registration and no runtime algorithm logic beyond exporting constants.

## Important APIs, Types, and Flow

The file defines `__visible const u32 cast_s1[256]`, `cast_s2[256]`, `cast_s3[256]`, and `cast_s4[256]`, each exported with `EXPORT_SYMBOL_GPL()`. CAST5 and CAST6 generic code alias these as `s1` through `s4` in their F-function macros.

There is no control flow other than module load/unload metadata. The value of the file is code and data sharing: large constant tables live in one module rather than being duplicated by each CAST implementation.

## State, Dependencies, and Integration

State is immutable static data. Dependencies are limited to `linux/module.h` and `crypto/cast_common.h`. Integration points are any GPL module that imports the exported S-box symbols, chiefly `cast5_generic.c`, `cast6_generic.c`, and architecture-specific CAST implementations.

## Risks and Test Signals

Risks are table corruption, symbol visibility, and version/linkage issues. Test signals are indirect: CAST5 and CAST6 known-answer tests will fail if a table value or export is wrong. Build and module-load tests should also confirm dependent CAST modules resolve the exported symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cast_common.c -->
