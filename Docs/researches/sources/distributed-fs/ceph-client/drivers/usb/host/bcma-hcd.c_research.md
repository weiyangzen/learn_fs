<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/bcma-hcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/bcma-hcd.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/bcma-hcd.c` is Broadcom BCMA bus glue for USB host cores. It initializes Broadcom USB20/USB30 cores, applies chip-specific register sequences, controls optional VCC GPIO, and creates child platform devices for generic EHCI/OHCI or OF-populated child controllers. The source was read as a complete 499-line file.

## Important APIs, Types, and Functions

`struct bcma_hcd_device` stores the BCMA core, created EHCI/OHCI platform devices, and optional VCC GPIO. Key helpers are `bcma_wait_bits()`, `bcma_hcd_4716wa()`, `bcma_hcd_init_chip_mips()`, `bcma_hcd_usb20_old_arm_init()`, `bcma_hcd_usb20_ns_init()`, `bcma_hcd_usb20_ns_init_hc()`, `bcma_hcd_usb30_init()`, `bcma_hcd_create_pdev()`, and `bcma_hci_platform_power_gpio()`. Driver entry points are `bcma_hcd_probe()`, `bcma_hcd_remove()`, `bcma_hcd_shutdown()`, and optional PM `bcma_hcd_suspend()/resume()`.

## Control Flow

Probe allocates per-core state, requests optional `"vcc"` GPIO high, and dispatches by BCMA core ID. Old USB20 host cores use either MIPS initialization that enables/reset cores and creates `ohci-platform`/`ehci-platform` devices, or ARM initialization that sequences PMU PLL/PHY registers and populates OF children. Northstar USB20 enables the core, applies host-controller threshold/break-transfer tuning on specific chips, and populates OF children. Northstar USB30 enables the core and populates OF children. Remove unregisters created child platform devices and disables the core; shutdown and PM additionally toggle VCC low/high.

## State and Persistence Behavior

Runtime state is per-core and devm-managed. Persistent effects are BCMA core enable/disable state, Broadcom PHY/PLL/control registers, child platform devices registered into the device model, and GPIO output level. No file-backed state is used.

## Dependencies and Integration Points

The driver depends on the BCMA bus API, Broadcom chip IDs, optional MIPS/ARM code paths, GPIO descriptors, platform device registration, OF child population, and generic `ehci-platform`/`ohci-platform` pdata. Kconfig selects generic platform HCD support when the corresponding EHCI/OHCI core is enabled.

## Risks and Edge Cases

The initialization sequences use hard-coded Broadcom registers and timing delays; applying the wrong path to a chip revision can leave PHYs or PLLs unusable. MIPS-specific 4716 workaround depends on CPU clock thresholds. Child platform devices share the BCMA IRQ and fixed resource windows, so address/IRQ errors surface later in the generic HCD. ARM old-core init requires PMU discovery. PM resume only re-enables the core/GPIO and does not replay all USB20 register tuning.

## Test Signals

Test on BCMA USB20 old MIPS, old ARM, Northstar USB20, and Northstar USB30 systems. Check child HCD creation/removal, VCC GPIO polarity, suspend/resume/shutdown power behavior, DMA mask setup, OF child population, controller enumeration, and logs for timeout messages from PLL/MDIO waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/bcma-hcd.c -->
