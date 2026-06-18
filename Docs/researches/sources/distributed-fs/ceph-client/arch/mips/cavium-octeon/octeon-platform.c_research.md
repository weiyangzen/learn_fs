# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/octeon-platform.c

Purpose: publishes Octeon platform devices and mutates built-in or appended device trees so Linux sees only hardware actually present on a given Octeon board. It also initializes Octeon USB clock/reset sequences, RNG platform resources, MAC addresses, PHY bindings, fixed links, and bootbus-attached devices.

Important APIs and functions: USB code registers EHCI/OHCI platform data through `octeon_ehci_device_init()` and `octeon_ohci_device_init()`, with clock control in `octeon2_usb_clocks_start()` and `octeon2_usb_clocks_stop()`. `octeon_rng_device_init()` registers `octeon_rng`. Device-tree mutation flows through `octeon_fill_mac_addresses()`, `octeon_prune_device_tree()`, `octeon_fdt_set_phy()`, `octeon_fdt_set_mac_addr()`, `octeon_fdt_pip_iface()`, and `octeon_fdt_pip_port()`. `octeon_publish_devices()` calls `of_platform_populate()`.

Control flow: arch/device initcalls reset USB if necessary, attach USB platform data after OF devices exist, register RNG resources, and populate OF platform devices matching `simple-bus` and Octeon compatibles. During early boot, setup code calls FDT pruning and MAC filling: aliases are resolved, unavailable interfaces and buses are nopped out, PHY addresses are rewritten from board helper results, UART clock properties are updated, CompactFlash and LED bootbus ranges are repaired, and USB reference-clock properties are adjusted.

State and persistence: `octeon2_usb_clock_start_cnt` and its mutex refcount USB clock usage while EHCI/OHCI share the same UCTL. FDT changes happen in-place in `initial_boot_params` before unflattening, so the resulting live device tree persists for all later drivers but is not written back to storage.

Dependencies and integration points: uses libfdt, Linux OF platform population, USB platform driver pdata, CVMX board helpers, Octeon CSR definitions, `octeon_get_io_clock_rate()`, and `octeon_bootinfo`. It integrates with Ethernet drivers through corrected `local-mac-address`, `phy-handle`, `fixed-link`, and delay properties.

Risks: in-place FDT mutation requires properties to have compatible existing sizes for `fdt_setprop_inplace()`. Wrong board detection can delete live devices or expose absent devices. USB clock sequencing is hardware-specific and timing-sensitive. PHY alternate-handle replacement rewrites property names and assumes valid phandles and compatible property lengths.

Test signals: boot with internal, appended, and bootloader-passed DTBs; inspect `/proc/device-tree` for pruned nodes and MAC addresses; verify Ethernet PHY probing on affected boards; exercise EHCI/OHCI probe/remove and suspend-like power callbacks; confirm RNG platform resources register; check boot logs for FDT rename/property errors.
