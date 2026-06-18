# sources/distributed-fs/ceph-client/tools/testing/selftests/net/txtimestamp.c

Purpose: Exhaustive software TX timestamping exerciser for TCP, UDP, raw IPv4/IPv6, and PF_PACKET sockets. It validates SCHED, SND, and TCP ACK timestamps, timestamp keys, optional cmsg configuration, pktinfo, epoll/poll/busy polling, payload/no-payload error queue modes, and timing tolerances.

Important APIs/types/functions: uses `SO_TIMESTAMPING`, `SOF_TIMESTAMPING_TX_*`, `SOF_TIMESTAMPING_OPT_CMSG`, `SOF_TIMESTAMPING_OPT_ID`, `SOF_TIMESTAMPING_OPT_TSONLY`, `SCM_TS_OPT_ID`, `SCM_TIMESTAMPING`, `MSG_ERRQUEUE`, `sock_extended_err`, IP/IPV6/PACKET timestamp error queue cmsgs, `TCP_NODELAY`, raw/PF_PACKET headers, `poll`, and `epoll`. `struct timing_event` accumulates min/max/avg deltas. `validate_key()` checks sequential timestamp IDs; `validate_timestamp()` compares kernel timestamps against recorded user time plus configured delays.

Control flow: `main()` parses options, resolves the target hostname, optionally opens local listener sockets, and runs `do_main()` per selected address family. `do_main()` calls `do_test()` for SND, ENQ, ENQ+SND, and for TCP also ACK combinations. `do_test()` creates a socket, optionally connects, configures pktinfo and timestamping, builds payload/raw headers as needed, sends `cfg_num_pkts` messages, waits via poll/epoll unless busy-polling, drains the error queue with `recv_errmsg()`, validates cmsg pairs, and prints timing aggregates.

State and persistence: global configuration variables are set by command line. `saved_tskey` tracks expected key progression per socket. `ts_usr` and timing accumulators hold process-local measurements. No persistent files are written; listener fds are left open until process exit to keep connects working.

Dependencies and integration: compiled helper driven by `txtimestamp.sh`. Requires loopback or provided host, timestamping kernel support, raw socket privileges for raw/PF_PACKET modes, and optionally slow-machine tolerance via `KSFT_MACHINE_SLOW`.

Risks: timing validation is sensitive to scheduler and virtualized environments; slow machines are exempt from hard failure for timestamp delay mismatches. Raw/PF_PACKET construction uses manual checksum/header code and assumes MTU constraints. The `-E` option intentionally falls through to `-F`, making edge-triggered epoll wait indefinitely; this is subtle but encoded in parsing.

Test signals: nonzero exit if timestamp cmsgs are missing, keys jump unexpectedly, send/read setup fails, or timing is outside tolerance on normal machines. Output includes per-family/protocol timing and payload/pktinfo diagnostics.
