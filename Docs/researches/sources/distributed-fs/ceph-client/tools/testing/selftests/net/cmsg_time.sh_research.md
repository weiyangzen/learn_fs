# sources/distributed-fs/ceph-client/tools/testing/selftests/net/cmsg_time.sh

Purpose: this script verifies transmit timestamping and `SCM_TXTIME` scheduling through `cmsg_sender`. It checks that packets without options print no timestamp output, that timestamping yields scheduler and send timestamps, and that a TXTIME delay is reflected in absolute and relative timing.

Important APIs and commands: it uses `setup_ns`, a dummy device, `tc qdisc replace dev dummy0 root fq` because TXTIME requires fq, `./cmsg_sender -t` for timestamping, `-d` for TXTIME delay, and shell filters `wc`, `sed`, and `awk` to parse output.

Control flow: the script creates a namespace and dummy IPv4/IPv6 connectivity, installs fq, then loops over IPv4 and IPv6 targets and UDP/ICMP/raw protocols. It verifies no output without timestamp options, exactly two lines with `-t`, one `SCHED ts0` line, one `SND ts0` line, a send timestamp greater than 1000 usec with `-d 1000`, and a send-minus-schedule delta greater than 500 usec. The last relative-delay check is treated as xfail on slow machines.

State and persistence: only namespace-local network and qdisc state is mutated. No files are written.

Dependencies and integration points: depends on `cmsg_sender` timestamp/error-queue logic, fq qdisc, Linux timestamping support, and root/net admin capabilities.

Risks and test signals: timestamp timing is scheduler-sensitive and can be flaky; the script has an explicit `KSFT_MACHINE_SLOW=yes` xfail path for the relative delay. Strong signals are expected printed timestamp line count and parsed `SCHED`/`SND` entries.
