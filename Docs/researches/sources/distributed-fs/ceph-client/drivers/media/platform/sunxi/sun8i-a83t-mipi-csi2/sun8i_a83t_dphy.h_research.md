# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/sun8i_a83t_dphy.h

Purpose: declares A83T D-PHY register definitions and the D-PHY registration hook.

Important APIs and constants: defines D-PHY control/status/analog register offsets, reset/shutdown/debug/status bits, initial control value, and analog field helpers. Declares `sun8i_a83t_dphy_register`.

Control flow: included by both D-PHY implementation and CSI-2 controller implementation so controller initialization can write D-PHY magic init values and resource setup can register the PHY provider.

State and persistence: no software state. Constants describe hardware state in the shared CSI-2 register space.

Dependencies and integration points: includes the A83T CSI-2 device header for the device type. It is the interface between the controller and integrated PHY provider.

Risks: several status bits are defined but not read by the implementation; bring-up diagnostics may need them. Fixed magic/init values are hardware-specific and poorly self-documenting.

Test signals: compile coverage and register traces during runtime resume and PHY power-on.
