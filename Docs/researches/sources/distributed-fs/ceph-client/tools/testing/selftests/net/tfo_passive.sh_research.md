# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tfo_passive.sh

## Purpose
`tfo_passive.sh` is an integration selftest for passive TCP Fast Open and NAPI ID propagation using `netdevsim`. It creates two simulated net devices in separate namespaces, links them through netdevsim sysfs, runs `tfo` server/client across the link, and verifies the accepted passive TFO socket has a nonzero incoming NAPI ID.

## Important APIs, Functions, and Types
The script sources `lib.sh`, defines random `NSIM_SV_ID` and `NSIM_CL_ID`, sysfs paths under `/sys/bus/netdevsim`, namespace names `nssv` and `nscl`, addresses, and port. `setup_ns` creates namespaces, moves netdevsim interfaces into them, assigns addresses, brings links up, and enables passive TFO using `sysctl net.ipv4.tcp_fastopen=519`. `cleanup_ns` deletes the namespaces.

## Control Flow
The script loads `netdevsim`, creates two devices through `new_device`, waits for udev, calls setup, opens namespace file descriptors, reads each interface index, and writes `fd:ifindex` pairs to `link_device`. It starts `./tfo` in server mode under the server namespace with a temp output file, waits for the local port to listen, then runs `./tfo` in client mode under the client namespace. After both processes finish it reads the server result, rejects zero NAPI ID, checks client/server exit statuses, unlinks and deletes netdevsim devices, removes namespaces, unloads `netdevsim`, and exits.

## State and Persistence
State includes netdevsim kernel devices, namespace file descriptors held by the shell, namespaces, IP addresses, passive TFO sysctl in the server namespace, a temporary output file, and sysfs link/unlink state. Cleanup removes namespaces and netdevsim devices on the success path; several failure branches manually call `cleanup_ns`.

## Dependencies and Integration Points
Dependencies are root, `modprobe`, `netdevsim`, sysfs control files, `udevadm`, `ip netns`, `sysctl`, `timeout`, the local `./tfo` binary, and `wait_local_port_listen` from `lib.sh`. Integration points are netdevsim device linking, namespace file descriptors, passive TCP Fast Open, NAPI ID reporting, and kselftest shell conventions.

## Risks and Test Signals
Risks include random netdevsim ID collision, missing netdevsim module, sysfs permission issues, stale devices after early failures, and reliance on the helper binary being built in the current directory. The decisive signals are successful netdevsim link setup, client/server zero exit status, and an output NAPI ID other than `0`.
