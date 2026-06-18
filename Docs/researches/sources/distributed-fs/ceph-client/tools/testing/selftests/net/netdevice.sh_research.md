## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netdevice.sh

Purpose: broad legacy selftest for basic Ethernet-like network device operations: bring device up, set MAC address, exercise mutable ethtool offload features, query ethtool dump/stats, and bring device back down.

Important APIs and tools: uses `ip link`, `ip address`, `ethtool --version`, `ethtool -k`, `ethtool --offload`, `ethtool -d`, `ethtool -S`, root checks, temp files, and optional veth creation when no matching physical device exists.

Control flow: validates root and `ip`, builds a temp list of devices matching `eth*` or `enp*s*`, creates a veth pair if no valid device is found, then runs `kci_test_netdev()` per device. That wrapper detects VLAN-style names, calls `kci_net_start()` if the master/down device can be brought up, `kci_net_setup()` to set a fixed MAC and skip IP assignment, `kci_netdev_ethtool()` to iterate non-fixed feature toggles off/on/restore, and `kci_netdev_stop()` if the script brought the device up.

State and persistence: may alter live network interfaces by changing state, MAC address, and offload settings; it attempts to restore offload values but does not restore original MAC. Temporary device list and fallback veth are cleaned. Dependencies include root, iproute2, ethtool, and devices tolerant of offload toggles. Risks are high on real hosts because it can disrupt active NICs and does not aggregate failures into final nonzero status. Test signals are PASS/FAIL/SKIP/XFAIL lines, but final exit is always 0 unless setup fails.
