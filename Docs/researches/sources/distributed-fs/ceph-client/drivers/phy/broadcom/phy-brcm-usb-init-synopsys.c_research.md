# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-brcm-usb-init-synopsys.c

Purpose: Supplies Broadcom STB Synopsys USB initialization callbacks for newer controllers such as BCM7216, BCM7211 B0, and BCM74110. It is part of the composite `phy-brcm-usb-dvr` driver and fills `brcm_usb_init_ops`.

Important APIs and types: It consumes `struct brcm_usb_init_params` and installs one of `bcm74110_ops`, `bcm7216_ops`, or `bcm7211b0_ops` through `brcm_usb_dvr_init_74110()`, `brcm_usb_dvr_init_7216()`, and `brcm_usb_dvr_init_7211b0()`. Helpers cover IPP/IOC polarity, common init/uninit, XHCI soft reset, dual-select get/set, 7211b0 MDIO writes, and wake-enable programming.

Control flow: `usb_init_ipp()` optionally overrides strap-selected power polarity and waits when polarity changes. Common init programs port mode, BDC reset behavior, and chip-specific PHY power/PLL details. 7211b0 powers up USB PHY LDO/bandgap, waits up to 200 ms for PLL lock, sets PHY mode, adjusts BDC read transaction size, disables the power-up FSM, and applies a USB2 eye fix through MDIO. 7216 toggles USB power, disables suspend clock switching, optionally forces COMMONONN, and disables wake. 74110 extends 7216 with S2 clock changes and USB2 tune values. Uninit either enables wake/PME paths or powers down/reset PHY and XHCI depending on `wake_enabled`.

State and persistence: The file mutates only hardware registers and fields inside the caller-owned init params (`family_name`, `ops`). Wake behavior depends on `params->wake_enabled`, and selected port mode is stored in controller registers.

Dependencies and integration: It depends on `phy-brcm-usb-init.h` register helpers, BRCMSTB SoC definitions, optional `syscon_piarbctl`, and mapped register slots for CTRL, XHCI global, USB PHY, USB MDIO, and BDC EC blocks.

Risks and test signals: MDIO helper loops busy-wait without timeout on GMDIO busy. 7211b0 PLL lock timeout is polled but common init continues after the loop without returning status. Test init/uninit with and without wake, host/device/DRD port modes, IPP/IOC polarity changes, 7211b0 PLL and MDIO behavior, 7216/74110 suspend-clock settings, XHCI reset sequencing, and dual-select sysfs or role-control users.
