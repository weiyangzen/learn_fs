# sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_ingress_egress_chaining.sh

## Purpose
`test_ingress_egress_chaining.sh` validates tc mirred chaining between ingress and egress paths. It sets up two veth pairs and confirms TCP benchmark traffic can traverse an ingress-to-egress redirection chain plus an egress-to-ingress shortcut.

## Important APIs, Types, And Functions
Functions are `fail()`, `cleanup()`, `config()`, and `test_run()`. The script uses `tc qdisc add ingress`, `tc qdisc add clsact`, flower filters, `act_mirred` redirect actions, `ip netns`, and the `udpgso_bench_rx`/`udpgso_bench_tx` test binaries.

## Control Flow
The script checks root privileges and required modules `act_mirred`, `cls_flower`, and `sch_ingress`, then creates randomized namespace and device names. `config()` creates two veth pairs, places one peer in a namespace, assigns addresses, brings links up, installs reciprocal ingress redirects between the two host-side veths, and installs an egress redirect from `peer1` back to `veth1`. `test_run()` starts the receiver and runs a namespaced sender using TCP mode toward `peer1`.

## State, Persistence, And Dependencies
State is temporary namespace, veth devices, tc qdiscs/filters, and benchmark processes. Cleanup kills `udpgso_bench_rx`, deletes veths, and removes the namespace. Dependencies include root, kernel tc modules, `ip`, `tc`, and compiled benchmark binaries.

## Integration Points
The test covers interaction between tc ingress qdisc, clsact egress hook, mirred redirect semantics, and veth delivery. It is intended to catch regressions in chaining an ingress redirect into an egress redirect.

## Risks
`killall -q -9 udpgso_bench_rx` is broad and can kill unrelated same-named processes. Module skip messages report only `act_mirred` even when a different module is missing. Random names reduce collision risk but do not eliminate it completely.

## Test Signals
Passing signal is successful completion of `udpgso_bench_tx -t` within the timeout and printed `Test passed`. Failure signal is sender timeout/error or setup command failure.
