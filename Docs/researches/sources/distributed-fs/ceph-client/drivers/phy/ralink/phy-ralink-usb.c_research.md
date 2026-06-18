# sources/distributed-fs/ceph-client/drivers/phy/ralink/phy-ralink-usb.c

Purpose: Implements the Ralink/MediaTek USB2 PHY driver for RT3352, MT7620, MT7628, and MT7688 style SoCs, controlling syscon clock/reset bits and optional MT7628 PHY register initialization.

Important APIs/types/functions: `struct ralink_usb_phy` stores host/device resets, clock-enable mask, PHY, optional MMIO base, and sysctl regmap. `ralink_usb_phy_power_on()` and `_power_off()` implement the generic PHY ops, while `ralink_usb_phy_init()` writes the MT7628-specific analog/digital sequence.

Control flow: Probe reads the match-data clock mask, looks up `ralink,sysctl`, maps a local PHY resource only for `mediatek,mt7628-usbphy`, gets `host` and `device` resets, creates the PHY, and registers a simple provider. Power-on enables the selected UPHY clocks through syscon, forces USB0 host mode, deasserts resets, waits 10 ms, optionally programs MT7628 registers, and logs wakeup/UTMI width status. Power-off clears clock bits and asserts both resets.

State and persistence: The driver stores resource handles and the SoC-specific clock mask. Syscon clock, host-mode, reset, and MT7628 PHY register state persists until power-off or SoC reset.

Dependencies and integration points: Depends on generic PHY, reset controller, syscon/regmap, platform MMIO, OF match data, and Ralink/MediaTek USB controller consumers.

Risks: Host mode is forced unconditionally, so device/OTG use would need additional handling. Register programming for MT7628 is a fixed vendor sequence with no readiness checks. Power-on logs info every time, which may be noisy across repeated power cycles.

Test signals: Probe all compatibles, verify syscon clock masks, reset sequencing, USB host enumeration, MT7628 register initialization, power cycle behavior, and wakeup/UTMI status logs.
