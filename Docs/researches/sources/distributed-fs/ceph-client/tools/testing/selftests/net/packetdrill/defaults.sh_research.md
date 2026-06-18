# sources/distributed-fs/ceph-client/tools/testing/selftests/net/packetdrill/defaults.sh

## Purpose
`defaults.sh` programs a deterministic TCP environment for packetdrill tests. It resets cached TCP metrics and applies production-like sysctl defaults that packetdrill scripts assume.

## Important APIs and settings
The script uses `ip tcp_metrics flush`, many `sysctl -q net.ipv4.*` writes, and `tc qdisc add dev tun0 root pfifo`. It sets receive/send buffer ranges, timestamps, SYN retry counts, F-RTO, SACK/DSACK, FACK off, reordering threshold, CUBIC, slow-start-after-idle off, RACK/TLP, TSO divisor, ECN off, pacing ratios, `tcp_notsent_lowat`, TCP Fast Open and a fixed Fast Open key, and SYN cookies.

## Control flow
Commands run sequentially and mostly suppress output. There are no functions or traps. The final qdisc override changes `tun0` from a potentially pacing FQ default to pfifo to avoid packetdrill timing failures.

## State and persistence
It mutates sysctls and qdisc state in the current network namespace. Under `ksft_runner.sh`, packetdrill is run inside `unshare -n`, so these changes are intended to be namespace-local.

## Dependencies and integration points
It depends on `ip`, `sysctl`, `tc`, a `tun0` device prepared by packetdrill, and kernel support for the named sysctls. Packetdrill `.pkt` tests rely on these values for stable TCP behavior.

## Risks and edge cases
If not run in an isolated network namespace, the sysctl changes can affect the host. Missing sysctls or qdisc support can fail commands. The pfifo override assumes `tun0` exists when this script is run.

## Test signals
Packetdrill timing and TCP behavior should become reproducible; failures often manifest later as packetdrill timing mismatches rather than direct output from this script.
