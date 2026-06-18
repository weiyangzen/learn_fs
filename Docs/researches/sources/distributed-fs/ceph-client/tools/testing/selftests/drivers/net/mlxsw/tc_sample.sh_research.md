<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_sample.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_sample.sh

Purpose: verifies mlxsw tc sample offload behavior and psample metadata, including rate accuracy, group conflicts, ingress/egress interface metadata, LAG metadata, output traffic class, queue occupancy, latency, and flower-policy sampling.

Important functions/APIs: topology helpers for four hosts and four router ports with two LAG paths; `psample_capture_start/stop`; tests `tc_sample_rate_test`, `tc_sample_max_rate_test`, `tc_sample_conflict_test`, `tc_sample_group_conflict_test`, metadata tests, ACL group/rate/max-rate tests. Requires external `psample` tool, mausezahn, tc matchall/flower `action sample`, jq, and mlxsw version gates.

Control flow: setup creates routed VRF paths and 802.3ad bonds. Tests install one or more sampling filters, capture psample output to a temp file, generate traffic, then grep for expected group counts or metadata fields. Some tests configure qdiscs to force output TC or occupancy.

State/dependencies: routes, bonds, clsact qdiscs, sample filters, psample background process, temp capture file. Risks include sampling randomness/tolerance, process cleanup, external psample availability, timing under high packet counts, and Spectrum-version feature differences. Test signals are sampled packet count tolerance, expected metadata strings, conflict insertion failures, and rate limit boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_sample.sh -->
