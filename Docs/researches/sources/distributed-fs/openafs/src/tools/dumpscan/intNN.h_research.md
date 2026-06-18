# sources/distributed-fs/openafs/src/tools/dumpscan/intNN.h

Purpose: abstracts fixed-width integer support for dumpscan, especially unsigned 64-bit dump offsets.

Important definitions: when `NATIVE_UINT64` is defined, `dt_uint64` aliases that native type and macros implement construction, extraction, comparison, arithmetic, and network byte-order conversion directly. Otherwise `dt_uint64` is a struct of `afs_uint32 hi, lo` with equivalent macro operations. It declares `hexify_int64`, `decimate_int64`, and `shift_int64`.

State/dependencies: header-only macro logic depends on `afs/stds.h` and byte-order macros such as `htonl`/`ntohl` available in including sources. The build makefile defines `NATIVE_UINT64=afs_uint64`, so modern OpenAFS builds take the native branch.

Risks/test signals: macro arguments may be evaluated more than once in some operations and have type assumptions. The non-native `get64` loses high bits by returning only `.lo`, so callers must not use it for full-width values. Test signals come from `int64.c` with `TEST_INT64` and from large/seekable dump parsing.
