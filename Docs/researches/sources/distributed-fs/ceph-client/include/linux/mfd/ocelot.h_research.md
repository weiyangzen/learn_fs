# sources/distributed-fs/ceph-client/include/linux/mfd/ocelot.h

## Purpose

This header provides helper functions for obtaining regmaps from Ocelot/VSC7512-style platform resources in both standalone MMIO and MFD-child configurations.

## Important APIs, Types, and Functions

`ocelot_regmap_from_resource_optional()` attempts to map an `IORESOURCE_MEM` resource at a given index with `devm_ioremap_resource()` and create a MMIO regmap with `devm_regmap_init_mmio()`. If no memory resource exists and the platform device has a parent, it falls back to an `IORESOURCE_REG` resource and returns a named regmap from the parent with `dev_get_regmap()`. Missing optional resources return `NULL`; mapping errors return `ERR_PTR`. `ocelot_regmap_from_resource()` wraps the optional helper and converts a missing resource to `ERR_PTR(-ENOENT)`.

## Control Flow

The control path is a two-stage lookup: first direct MMIO resource, then MFD parent regmap by named register resource. The non-optional wrapper preserves errors and converts `NULL` to a standard missing-resource error. Consumers call this during probe before registering pinctrl, SGPIO, or MDIO functionality.

## State and Persistence Behavior

The functions allocate devm-managed mappings/regmaps when direct MMIO is present. Parent-regmap fallback returns an existing parent-owned regmap and does not create new persistent state. Hardware state is the target register region; this header only standardizes how child drivers acquire access.

## Dependencies and Integration Points

The header includes platform device, resource, regmap, error, and type helpers. Direct users include `drivers/pinctrl/pinctrl-microchip-sgpio.c`, `drivers/pinctrl/pinctrl-ocelot.c`, and `drivers/net/mdio/mdio-mscc-miim.c`. It integrates standalone platform devices with MFD cells that expose `IORESOURCE_REG` names matching parent regmaps.

## Risks and Edge Cases

The optional helper intentionally avoids noisy resource lookup for absent optional MMIO resources; callers must distinguish `NULL` from an error pointer. In MFD mode, resource names must match parent regmap names exactly. If a device has neither direct memory nor parent regmap resources, the required wrapper returns `-ENOENT`. Passing the wrong `regmap_config` for a direct mapping can produce invalid register stride/width behavior.

## Test Signals

Build Ocelot pinctrl, SGPIO, and MSCC MIIM consumers; probe both standalone MMIO and MFD child device-tree descriptions; verify optional second MDIO regmap absence returns `NULL` without probe failure where expected; validate required resources fail with `-ENOENT`; and use regmap debugfs to confirm operations target direct or parent-backed maps as intended.
