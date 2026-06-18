# sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgso.sh

Purpose: Shell regression matrix for `udpgso`, setting up loopback and dummy-device MTU/offload conditions to exercise software and hardware UDP GSO and checksum combinations.

Important APIs/functions: setup helpers configure loopback addresses/MTU, local routes with MTU 1500, and dummy `sink` with IPv4/IPv6 addresses. Offload helpers toggle `tx-checksum-ip-generic` and `tx-udp-segmentation` on the dummy device.

Control flow: when invoked with a helper name, it runs that setup, shifts past `--`, and execs the requested command. Normal no-arg flow runs `udpgso` through `in_netns.sh` for IPv4/IPv6 cmsg, setsockopt, connected route MTU, MSG_MORE, hardware GSO/hardware checksum no-receive, software GSO/hardware checksum no-receive, and software GSO/software checksum no-receive.

State and persistence: all state is inside the namespace provided by `in_netns.sh`: loopback addresses, local routes, dummy link, and ethtool offload flags. No persistent files.

Dependencies and integration: requires `ip`, `ethtool`, dummy netdev, namespace wrapper, and compiled `udpgso`.

Risks: uses `set -o errexit` and `nounset`, so setup failures stop the matrix. It assumes ethtool can manipulate dummy offloads as expected. `shift 2` assumes the helper-call ABI includes `test_* --`.

Test signals: all nested `udpgso` commands must exit 0. Echo labels identify which configuration failed.
