# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect_checksum.sh

## Purpose
This wrapper runs the standard MPTCP connect transfer suite with MPTCP data checksums enabled.

## Important APIs and Functions
It sets `MPTCP_LIB_KSFT_TEST` to the wrapper basename and execs `mptcp_connect.sh -C "$@"`.

## Control Flow and State
All substantive setup, transfer, and validation happens in `mptcp_connect.sh`; this file only selects checksum mode and forwards user arguments.

## Dependencies and Integration
It depends on the sibling `mptcp_connect.sh` script and `mptcp_lib.sh` conventions for naming KTAP tests.

## Risks and Test Signals
Risks are inherited from `mptcp_connect.sh`, with added dependence on `net.mptcp.checksum_enabled` support. Pass/fail is the delegated script's exit status and TAP output.
