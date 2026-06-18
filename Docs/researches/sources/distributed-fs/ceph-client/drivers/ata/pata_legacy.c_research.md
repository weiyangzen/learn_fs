# sources/distributed-fs/ceph-client/drivers/ata/pata_legacy.c

`pata_legacy.c` probes traditional ISA-side IDE ports on PC-class systems and registers them as PIO-only libata SFF hosts. It covers primary/secondary addresses plus optional tertiary legacy ranges while trying to avoid ports already owned by PCI or bridge-specific drivers.

Module parameters drive scan policy: `all`, `probe_all`, `probe_mask`, `autospeed`, `pio_mask`, and `iordy_mask`. `struct legacy_probe` records candidate port/IRQ/type, `struct legacy_data` stores per-slot state and platform device, and `struct legacy_controller` describes ops and flags. `legacy_probe_add()` builds an ordered candidate list. `legacy_set_mode()` leaves BIOS-configured hardware in PIO0. `legacy_init_one()` creates a platform device, requests/maps command and control I/O regions, allocates a host, fills SFF addresses, activates it, then drops the port if libata finds no device.

At module init, the driver scans PCI devices for resources overlapping `0x1f0`/`0x170` and applies Cyrix/MPIIX special-case exclusions. It adds default and optional extra probes, resolves unknown types through `probe_chip_type()`, and attempts activation. Exit detaches recorded hosts and unregisters platform devices.

State is global arrays for probes, per-slot data, and hosts. Dependencies are PCI enumeration for avoidance, platform devices for resource ownership, devm I/O mapping, async synchronization, and libata SFF. Risks include probing someone else's port, missing valid non-PCI ports, parameter interactions, and partial cleanup. Tests should cover PCI overlap, `all`, `probe_all`, `probe_mask`, autospeed/snooping, IORDY mask, no-device cleanup, special-case bridges, and unload.
