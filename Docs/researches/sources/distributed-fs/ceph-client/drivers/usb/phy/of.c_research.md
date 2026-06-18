<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/of.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/of.c

## Purpose

`of.c` provides a small Device Tree helper for legacy USB PHY users. It parses a node's `phy_type` string and returns the corresponding `enum usb_phy_interface`.

## Important APIs, Types, and Functions

The exported API is `of_usb_get_phy_mode(struct device_node *np)`. It maps `""`, `utmi`, `utmi_wide`, `ulpi`, `serial`, and `hsic` through the `usbphy_modes[]` table to values of `enum usb_phy_interface`.

## Control Flow

The function reads `phy_type` with `of_property_read_string()`. Missing or invalid strings return `USBPHY_INTERFACE_MODE_UNKNOWN`; a matching table entry returns its index.

## State and Persistence Behavior

There is no runtime state beyond the static string table. The parsed value is a transient interpretation of Device Tree data.

## Dependencies and Integration Points

The file depends on OF APIs and `linux/usb/of.h`/`linux/usb/otg.h` enum definitions. Controller and PHY drivers use it to translate firmware description into register programming choices.

## Risks and Test Signals

Risks are binding-string drift and the legacy `phy_type` property differing from newer PHY bindings. Tests should pass nodes with missing, known, and unknown `phy_type` values and verify callers handle `UNKNOWN` gracefully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/of.c -->
