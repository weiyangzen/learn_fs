# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-ipq4019-usb.c

This Qualcomm IPQ4019 USB PHY driver provides separate HS and SS generic PHY behavior selected by OF compatible data. State is `struct ipq4019_usb_phy`, containing MMIO base, POR reset, optional SRIF reset, device, and created PHY.

Probe maps the register resource, obtains `por_rst` and optional `srif_rst`, creates a PHY using the matched ops table, stores private data, and registers `of_phy_simple_xlate`. SS power-on first calls SS power-off, then deasserts POR. SS power-off asserts POR and waits. HS power-off asserts POR, waits, asserts SRIF, waits. HS power-on performs power-off, deasserts SRIF, waits, then deasserts POR.

State is almost entirely reset-line state; the mapped base is not used by current callbacks. Dependencies are reset controls, generic PHY, OF match data, platform MMIO, and delays. Risks include no error checking on reset assert/deassert callbacks, optional SRIF reset use in HS paths without NULL concerns delegated to reset API semantics, fixed 10 ms delays, and unused MMIO suggesting either future expansion or unnecessary resource requirement. Test signals are reset behavior and USB enumeration.
