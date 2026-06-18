<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-fsl.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-fsl.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/ehci-fsl.c` is the Freescale/NXP SoC EHCI host wrapper for ARC-derived USB controllers. It consumes Freescale platform data, validates host/OTG modes, configures PHY/interface registers, handles several Freescale errata, sets cache snooping and arbitration registers, integrates optional OTG host registration, and implements SoC-specific PM restore paths. The source was read as a complete 732-line file.

## Important APIs, Types, and Functions

Important functions include `fsl_ehci_drv_probe()`, `usb_phy_clk_valid()`, `ehci_fsl_setup_phy()`, `ehci_fsl_usb_setup()`, `ehci_fsl_reinit()`, `ehci_fsl_setup()`, PM helpers `ehci_fsl_mpc512x_drv_suspend()/resume()`, `ehci_fsl_drv_suspend()/resume()/restore()`, optional OTG `ehci_start_port_reset()`, and `fsl_ehci_drv_remove()`. `struct ehci_fsl_priv` stores USB control register state across deep sleep. The driver uses `struct fsl_usb2_platform_data` extensively for mode, PHY, endian, controller version, errata flags, power budget, init/exit callbacks, and saved PM registers.

## Control Flow

Probe requires platform data and host-capable operating mode, obtains IRQ, creates the HCD under the parent device, maps registers, stores mapped registers in platform data, runs platform-specific `init()`, applies pre-reset controller enables and erratum A007792 setup, and calls `usb_add_hcd()`. In OTG mode it obtains a USB2 PHY and registers the EHCI root hub as OTG host. The EHCI reset override `ehci_fsl_setup()` sets endian flags, points EHCI caps at offset `0x100`, marks integrated root-hub TT, runs common `ehci_setup()`, applies MPC5121 SBUSCFG tuning, and then `ehci_fsl_reinit()` configures Freescale non-EHCI registers and PHYs.

`ehci_fsl_setup_phy()` programs ULPI, serial, UTMI, UTMI-wide, or dual UTMI port settings, checks PHY clock validity on supported controller versions, handles erratum A006918 by refusing initialization, and enables the USB controller bit. `ehci_fsl_usb_setup()` configures snooping, priority/age/SI control registers, root-hub TT and errata flags, and per-port PHYs for DR, OTG, or MPH host modes. PM suspend/resume uses generic EHCI port preparation for most SoCs, saves/restores `FSL_SOC_USB_CTRL` for deep sleep, and has a special MPC512x path that saves EHCI operational registers, cuts port power, restores USBMODE/SBUSCFG/registers, and resumes the root hub.

## State and Persistence Behavior

Runtime state spans HCD/EHCI state, Freescale platform data, non-EHCI SoC control registers, PHY mode selection, errata flags, OTG PHY host attachment, and PM-saved register snapshots. No file-backed persistence exists. Deep sleep can lose hardware register state; this file explicitly restores PHY/control state and marks the root hub as lost power when needed.

## Dependencies and Integration Points

The file depends on `linux/fsl_devices.h`, Freescale USB platform data, optional `CONFIG_USB_OTG`, optional `CONFIG_PPC_MPC512x`, OF compatibility checks on the parent node, the common EHCI core, and register constants from `ehci-fsl.h`. It integrates with board/platform code through `pdata->init`, `pdata->exit`, power budget, and errata fields.

## Risks and Edge Cases

Missing or wrong platform data prevents probe. PHY setup is highly version- and erratum-sensitive; incorrect flags can either refuse valid hardware or initialize unsafe hardware. Several registers are big-endian non-EHCI registers while EHCI registers follow configured endian flags; mixing accessors can break hardware. OTG error paths after `usb_add_hcd()` jump to cleanup that may not fully remove the added HCD before `usb_put_hcd()`, so host/OTG probe failures need scrutiny. PM paths differ sharply for MPC512x, deep sleep, and ordinary suspend; incomplete restore can lose root-hub or PHY state.

## Test Signals

Test DR_HOST, MPH_HOST, and DR_OTG modes with ULPI, serial, UTMI, UTMI-wide, and dual UTMI PHY settings; all Freescale errata flags; big- and little-endian MMIO/descriptor combinations; deep sleep restore; MPC5121 suspend/resume; OTG HNP start-port-reset; overcurrent port-power cycling; and high-speed/full-speed devices through integrated TT. Build coverage should include PowerPC and COMPILE_TEST-style configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-fsl.c -->
