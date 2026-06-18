# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect_mmap.sh

## Purpose
This wrapper runs the MPTCP connect transfer suite using the `mmap` send path in `mptcp_connect`.

## Important APIs and Functions
It sets `MPTCP_LIB_KSFT_TEST` to its basename and invokes `mptcp_connect.sh -m mmap "$@"`.

## Control Flow and State
The wrapper has no internal test logic. It selects mmap mode, where `mptcp_connect.c` memory maps a regular input file and writes it to the socket, while `mptcp_connect.sh` handles topology and validation.

## Dependencies and Integration
It depends on `mptcp_connect.sh`, a regular generated input file, and kernel/userspace support for `mmap`.

## Risks and Test Signals
Failures usually indicate delegated transfer mismatch or mmap/write path errors in the helper. TAP naming is adjusted by `MPTCP_LIB_KSFT_TEST`.
