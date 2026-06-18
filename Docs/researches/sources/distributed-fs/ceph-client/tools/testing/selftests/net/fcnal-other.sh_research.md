# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fcnal-other.sh

Purpose: this wrapper runs the non-IPv4/non-IPv6 named use cases in the functional networking suite.

Important behavior: it executes `./fcnal-test.sh -t other`. The main harness expands `other` to `use_cases`, covering bridge enslaved to VRF, multicast link-local pings across multiple VRF interfaces, and SNAT over VRF.

State and dependencies: this file owns no independent state or cleanup. All setup and teardown are in `fcnal-test.sh`.

Integration points and risks: because the selected scenarios touch bridges, VLANs, br_netfilter, netfilter NAT, and VRFs, the wrapper indirectly requires a broad set of kernel and user-space features. Its direct signal is the harness summary and exit status.
