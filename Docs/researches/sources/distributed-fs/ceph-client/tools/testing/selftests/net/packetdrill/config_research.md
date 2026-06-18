# sources/distributed-fs/ceph-client/tools/testing/selftests/net/packetdrill/config

## Purpose
The packetdrill `config` file lists kernel configuration requirements for TCP/IP packetdrill selftests.

## Important settings
It requires 1000 Hz timer granularity, IPv6, network namespaces, FIFO/FQ qdiscs, proc sysctl support, SYN cookies, CUBIC congestion control, TCP MD5 signatures, and TUN support.

## Control flow
The file is declarative and has no executable flow. It informs kselftest/environment checks about required kernel capabilities.

## State and persistence
No runtime state is created. The values describe kernel build configuration.

## Dependencies and integration points
The settings match assumptions in `defaults.sh` and `ksft_runner.sh`, including namespace isolation, TUN device setup, sysctl tuning, TCP Fast Open/cookies, IPv6 runs, and timing-sensitive packetdrill expectations.

## Risks and edge cases
Packetdrill tests can fail or skip unpredictably if a kernel lacks one of these capabilities, especially `CONFIG_HZ_1000`, network namespaces, qdisc support, or TCP feature support.

## Test signals
The downstream signal is packetdrill scripts passing for their selected IP versions under `ksft_runner.sh`.
