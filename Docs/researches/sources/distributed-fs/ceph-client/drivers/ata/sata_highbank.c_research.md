# sources/distributed-fs/ceph-client/drivers/ata/sata_highbank.c

## Purpose
`sata_highbank.c` is the Calxeda Highbank AHCI platform driver. It extends generic AHCI with Calxeda combo-PHY lane programming, repeated hardreset workarounds for flaky Gen3 link bring-up, and SGPIO enclosure LED message bit-banging.

## Important APIs, Types, and Functions
Important types are `struct phy_lane_info` and `struct ecx_plat_data`. SGPIO helpers include `ecx_parse_sgpio()`, `ecx_led_cycle_clock()`, `ecx_transmit_led_message()`, and `highbank_set_em_messages()`. PHY helpers include combo-PHY read/write routines, `highbank_cphy_disable_overrides()`, `cphy_override_tx_attenuation()`, `cphy_override_rx_mode()`, `highbank_cphy_override_lane()`, and `highbank_initialize_phys()`. AHCI integration centers on `ahci_highbank_hardreset()`, `ahci_highbank_probe()`, suspend/resume, and `ahci_highbank_ops`.

## Control Flow, State, and Persistence
Probe obtains memory and IRQ resources, allocates AHCI and Calxeda private data, maps MMIO, initializes PHY lane mapping from `calxeda,port-phys`, saves AHCI config, enables NCQ/PMP flags based on controller caps, sets up SGPIO LED support, allocates ports, marks disabled ports dummy, resets and initializes AHCI, and activates the host. Hardreset stops the AHCI engine, clears D2H FIS state, repeatedly disables PHY overrides, performs SATA hardreset, reapplies lane overrides, and retries up to 100 times when presence is detected but the link is not online. LED messages update a cached SGPIO bit pattern and bit-bang clock/load/data GPIO lines under a spinlock.

## Dependencies and Integration Points
The driver depends on generic AHCI internals, OF properties for PHY lane and LED ordering, GPIO descriptors for SGPIO, platform resources, global static PHY/SGPIO locks, and libata enclosure management flags. It uses `ahci_host_activate()` and overrides only hardreset and LED message transmission relative to generic AHCI.

## Risks and Test Signals
Risks include global `port_data` lifetime across multiple instances, unbounded-looking busy waits if PHY registers never clear, PHY phandle mapping leaks or partial setup, SGPIO GPIO acquisition failures that still leave LED flags enabled, hardreset retry latency, and suspend refusal when AHCI flags disallow it. Tests should cover multi-port AHCI activation, disabled port maps, Calxeda PHY DT parsing, Gen3 hardreset retries, SGPIO LED activity/locate/fault states and port ordering, suspend/resume, NCQ/PMP capability flags, and error paths for missing GPIO or PHY mappings.
