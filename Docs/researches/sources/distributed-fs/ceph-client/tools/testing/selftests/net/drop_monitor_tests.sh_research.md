# sources/distributed-fs/ceph-client/tools/testing/selftests/net/drop_monitor_tests.sh

Purpose: this script verifies software and hardware drop-monitor reporting. It checks that active drops are captured by `dwdump` and decoded by tshark, and that inactive/drop-disabled cases produce no matching packets.

Important APIs and commands: it uses `lib.sh`, `setup_ns`, `netdevsim` sysfs (`/sys/bus/netdevsim/new_device` and `del_device`), `devlink trap set`, `tc clsact` with flower drop action, `mausezahn` traffic generation, `dwdump -o sw/hw`, `tshark`, `timeout`, and `udevadm settle`.

Control flow: startup validates root and required tools, then creates an initial namespace to derive command wrappers. `setup` loads `netdevsim`, creates a dummy interface, creates a netdevsim device inside the namespace, waits for udev, and brings its netdev up. `sw_drops_test` installs a tc egress flower drop for a destination IPv4 address, generates continuous UDP traffic with mausezahn, captures software drops, asserts at least one matching pcap record, stops traffic, captures again, and asserts zero matches. `hw_drops_test` toggles the netdevsim `blackhole_route` trap between `trap` and `drop` actions and checks hardware drop monitor output for `net_dm.hw_trap_name == blackhole_route`.

State and persistence: the script mutates module state, netdevsim devices, namespaces, tc filters, and temporary pcap files under `mktemp -d`. Cleanup deletes netdevsim device and namespace; per-test temp directories are removed.

Dependencies and integration points: requires a kernel with `NET_DROP_MONITOR` and `NETDEVSIM`, tshark with net_dm dissector, and user-space `dwdump`. It integrates with devlink traps and tc drop actions.

Risks and test signals: tool availability is the dominant skip source. `kill_process %%` relies on job control for the mausezahn background job. Hardware testing depends on netdevsim trap behavior. Strong signals are nonzero matching pcap lines during active drops and zero matching lines after traffic stops or trap action changes to drop.
