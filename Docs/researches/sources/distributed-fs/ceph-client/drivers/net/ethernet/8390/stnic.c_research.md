# sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/stnic.c

Purpose: this is a SuperH SolutionEngine-specific National Semiconductor DP83902A ST-NIC Ethernet driver. It supplies board-specific register access, reset, and remote-DMA callbacks to the generic 8390 core.

Important APIs, types, and functions: `stnic_probe()` is the module init and only probes when `MACH_SE` is true. `STNIC_READ()`, `STNIC_WRITE()`, and `STNIC_DELAY()` encapsulate the SH7750 memory-mapped 16-bit register access pattern. `stnic_reset()`, `stnic_get_hdr()`, `stnic_block_input()`, and `stnic_block_output()` implement the 8390 operations. `stnic_init()` resets and calls `NS8390_init()`. `stnic_cleanup()` unregisters and frees the singleton device. `stnic_eadr` is a fallback MAC address and can be overwritten by `sh_bios_get_node_addr()` when `CONFIG_SH_STANDARD_BIOS` is enabled.

Control flow: initialization checks the machine vector, allocates an 8390 netdev, resolves the MAC, assigns a fake `base_addr` plus the fixed `IRQ_STNIC`, sets `ei_netdev_ops`, requests an unshared IRQ, initializes `ei_status` for 16-bit access and endianness, attaches ST-NIC callbacks, initializes hardware, stores `msg_enable`, and registers the netdev. RX and TX use remote DMA through the `PA_83902_IF` register with explicit endian byte ordering. Reset toggles `PA_83902_RST` and delays. Cleanup unregisters the netdev, frees the IRQ, and frees the netdev.

State and persistence: the driver is singleton state: `stnic_dev`, `stnic_eadr`, the netdev, and global `ei_status`. Hardware state is fixed physical mappings from the SolutionEngine board headers. No state persists beyond the loaded module and hardware registers.

Dependencies and integration points: depends on SuperH board headers, `mach-se/mach/se.h`, optional SH BIOS, IRQ_STNIC, raw volatile memory-mapped access, and the 8390 core. It is tightly coupled to SolutionEngine hardware and is not a generic platform driver.

Risks: the hardcoded fallback MAC address is explicitly marked as needing board-specific replacement. Pointer casts to physical addresses and volatile accessors are architecture-specific and bypass common `ioremap` patterns. `stnic_cleanup()` assumes `stnic_dev` is valid after successful init. Odd-length TX/RX rounds up and reads/writes extra bytes, requiring the caller buffers and hardware to tolerate it. There is little probe-time validation beyond `MACH_SE`.

Test signals: build coverage must include SuperH/SolutionEngine configs. Runtime signs include successful IRQ request, logged ST-NIC registration, correct MAC from SH BIOS if available, packet RX/TX on little- and big-endian configurations, reset behavior, unload cleanup, and absence of packet byte swapping or odd-length corruption.
