# sources/distributed-fs/ceph-client/drivers/net/Space.c

Purpose: legacy network-device boot configuration and ISA autoprobe support. It parses `netdev=` and `ether=` boot parameters, stores up to eight device setup records, and runs a small legacy Ethernet probe sequence during init.

Important APIs and functions: `struct netdev_boot_setup` stores a device name and `struct ifmap`. `netdev_boot_setup_add()` writes into the static setup table. `netdev_boot_setup_check()` is exported and copies boot-time IRQ, base address, and memory range into a matching `net_device`. `netdev_boot_base()` returns a configured base address or 1 when the device already exists. `netdev_boot_setup()` parses numeric boot options with `get_options()`. `probe_list2()` calls legacy probe callbacks and records failed autoprobes. `ethif_probe2()` and `net_olddevs_init()` try `eth0` through `eth7`.

Control flow: early boot `__setup` handlers populate `dev_boot_setup`. Later `device_initcall(net_olddevs_init)` loops through legacy units, obtains any configured base, and tries the compiled-in `isa_probes` list. Drivers can call `netdev_boot_setup_check()` during probe to consume stored settings.

State and dependencies: all persistent runtime state is the static `dev_boot_setup[8]` table and per-probe failure status in `isa_probes`. Dependencies include legacy ISA probe symbols such as `ne_probe` and `cs89x0_probe` when configured, `init_net`, and boot parameter parsing. Risks include fixed table capacity, old-style probing side effects on ISA I/O space, and repeated failure suppression only for autoprobes. Test signals include boot parameter parsing, exported symbol users, `NETDEV_LEGACY_INIT` builds, and ISA randconfig coverage.
