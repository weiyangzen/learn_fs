# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect_splice.sh

## Purpose
This wrapper runs the MPTCP connect transfer suite using the `splice` data path.

## Important APIs and Functions
It sets `MPTCP_LIB_KSFT_TEST` and invokes `mptcp_connect.sh -m splice "$@"`.

## Control Flow and State
The wrapper delegates all setup and validation. The selected mode causes `mptcp_connect.c` to move bytes through a pipe with `splice`.

## Dependencies and Integration
It depends on `mptcp_connect.sh`, `mptcp_connect`, regular input files, pipes, and kernel splice support for the involved descriptors.

## Risks and Test Signals
Splice mode can expose kernel/socket path differences from read/write or sendfile. Success is delegated zero exit status, TAP pass, and file equality.
