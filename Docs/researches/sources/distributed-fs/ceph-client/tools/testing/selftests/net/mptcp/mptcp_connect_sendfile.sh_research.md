# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect_sendfile.sh

## Purpose
This wrapper runs the MPTCP connect transfer suite using the `sendfile` data path.

## Important APIs and Functions
It sets `MPTCP_LIB_KSFT_TEST` and invokes `mptcp_connect.sh -m sendfile "$@"`.

## Control Flow and State
All test state is owned by the delegated script. The selected mode causes `mptcp_connect.c` to transfer regular-file input with `sendfile`.

## Dependencies and Integration
It depends on `mptcp_connect.sh`, `mptcp_connect`, and kernel support for `sendfile` from regular files to TCP/MPTCP sockets.

## Risks and Test Signals
Risks are inherited from the main transfer matrix plus sendfile-specific syscall behavior. Success is delegated TAP pass and matching received files.
