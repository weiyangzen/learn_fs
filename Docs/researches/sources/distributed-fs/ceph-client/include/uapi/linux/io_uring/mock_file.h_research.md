
# sources/distributed-fs/ceph-client/include/uapi/linux/io_uring/mock_file.h

## Purpose

`io_uring/mock_file.h` defines a small test/mock-file UAPI for probing and creating io_uring mock files with configurable features and delay behavior. The complete 47-line file was read.

## Important APIs, Types, and Functions

It defines feature bits `IORING_MOCK_FEAT_*`, `io_uring_mock_probe`, create flags `IORING_MOCK_CREATE_F_SUPPORT_NOWAIT` and `IORING_MOCK_CREATE_F_POLL`, `io_uring_mock_create`, manager commands `IORING_MOCK_MGR_CMD_PROBE`/`CREATE`, mock command `IORING_MOCK_CMD_COPY_REGBUF`, and copy flag `IORING_MOCK_COPY_FROM`.

## Control Flow

Test/user code probes supported mock features, requests creation of a mock file with size and read/write delay, then exercises io_uring operations and mock commands against that fd.

## State and Persistence Behavior

Mock file state includes file size, delay, nowait/poll support, and feature set. It persists for the lifetime of the created fd.

## Dependencies and Integration Points

It includes `linux/types.h` and integrates with io_uring testing infrastructure, `IORING_OP_URING_CMD`, registered buffers, nowait, async, and poll behavior.

## Risks and Edge Cases

Because this is test-oriented UAPI, risk is mostly semantic drift between mock features and io_uring tests. Reserved fields must remain zeroed for forward compatibility.

## Test Signals

Mock-file tests should probe features, create files with and without nowait/poll, verify delayed I/O behavior, exercise registered-buffer copy commands, and reject unsupported flags.
