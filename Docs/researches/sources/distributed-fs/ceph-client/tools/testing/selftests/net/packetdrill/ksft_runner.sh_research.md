# sources/distributed-fs/ceph-client/tools/testing/selftests/net/packetdrill/ksft_runner.sh

## Purpose
`ksft_runner.sh` is the KTAP wrapper for packetdrill `.pkt` scripts. It runs each script under packetdrill for the requested IP version(s), translating results into kselftest pass/fail/xfail/skip output.

## Important APIs and data
- Sources `../../kselftest/ktap_helpers.sh`.
- `ip_args` maps `ipv4`, `ipv4-mapped-ipv6`, and `ipv6` to packetdrill command-line options, local/gateway/remote addresses, Fast Open cookies, and socket error cmsg constants.
- `KSFT_MACHINE_SLOW` adds `--tolerance_usecs=14000` and downgrades failures to expected failures via `ktap_test_xfail`.
- The script discovers requested IP versions by grepping `^--ip_version=` in the `.pkt` file; absent means run all three supported variants.

## Control flow
It requires exactly one script argument, skips all tests if `packetdrill` is not in `PATH`, computes packetdrill options, prints a KTAP header and plan, then loops over each selected IP version. Each run executes `unshare -n packetdrill ... $script` and records pass or fail/xfail.

## State and persistence
Packetdrill runs in a fresh network namespace for each IP version, limiting sysctl, interface, and qdisc state to that run. The runner itself persists no files.

## Dependencies and integration points
It depends on Bash associative arrays, `packetdrill`, `unshare`, KTAP helpers, and packetdrill scripts that may include `defaults.sh` or `set_sysctls.py`. The `-D` definitions provide constants consumed by `.pkt` scripts.

## Risks and edge cases
The grep-based IP-version parser accepts only zero or one explicit `--ip_version=ipv4`/`ipv6`; multiple declarations are treated as unsupported. Slow-machine mode can hide real regressions as xfails. Packetdrill must be installed outside the kernel tree.

## Test signals
A missing packetdrill binary produces a KTAP skip-all. Otherwise each IP version emits one KTAP pass/fail/xfail line, and the script exits through `ktap_finished`.
