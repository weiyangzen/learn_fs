# sources/distributed-fs/ceph-client/samples/pktgen/parameters.sh

Purpose: common option parser and default initializer for pktgen scripts.

Important APIs/functions: `usage`, `getopts` over packet size, interface, destination IP/MAC/port, first thread, thread count, clone count, packet count, burst, delay, verbose/debug, IPv6, append mode, and UDP checksum. Exports variables consumed by scripts.

Control flow: parses options, sets defaults (`PKT_SIZE=60`, `F_THREAD=0`, `THREADS=1`, `DELAY=0`), computes `L_THREAD`, warns for missing destination details, requires `DEV`, and loads `pktgen` with `modprobe` if `/proc/net/pktgen` is absent.

State and persistence: exported shell variables and possible kernel module load.

Dependencies and integration: intended to be sourced after `functions.sh`; uses `err`, `warn`, and `info`.

Risks: being sourced exits the parent script on invalid input. Missing MAC/IP are warnings, so individual scripts may enforce them later. Assumes `modprobe` and sufficient privileges.

Test signals: invoke sample scripts with `-h`, invalid options, missing `-i`, IPv6 mode, and verify exported defaults in verbose mode.
