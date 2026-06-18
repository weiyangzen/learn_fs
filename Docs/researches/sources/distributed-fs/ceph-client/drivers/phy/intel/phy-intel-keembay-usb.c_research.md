# sources/distributed-fs/ceph-client/drivers/phy/intel/phy-intel-keembay-usb.c

## Purpose
Intel Keem Bay USB PHY provider. It maps CPR and slave APB register windows, enables USB subsystem clocks/resets, exits IDDQ, initializes USB PHY SRAM/parallel CR interface, and releases DWC3 core reset.

## Important APIs, types, and functions
- `struct keembay_usb_phy` stores device and CPR/slave regmaps.
- `keembay_usb_clocks_on()` sets clock/reset masks, disables IDDQ, waits, and selects pad ref clock.
- `keembay_usb_phy_init()` sequences core reset, PHY reset release, CR parallel interface selection, SRAM init polling, SRAM load done, and core release.
- Probe maps named resources `cpr-apb-base` and `slv-apb-base`.

## Control flow
Probe creates regmaps and generic PHY, registers provider, then immediately enables subsystem clocks and turns on the DWC3 core for the controller driver. Later PHY init performs PHY-specific SRAM and reset sequencing.

## State and persistence
No persisted state. Runtime state is USB subsystem clocks/resets and regmap register contents.

## Dependencies and integration points
Generic PHY, regmap MMIO, platform named resources, and DWC3 integration through early core reset release.

## Risks and test signals
Risks include no explicit power-off/exit path, core turned on during probe before PHY init, and SRAM init timeout. Test with DWC3 probe, missing named resources, clock/reset register readback, repeated init calls, and SRAM timeout fault injection.
