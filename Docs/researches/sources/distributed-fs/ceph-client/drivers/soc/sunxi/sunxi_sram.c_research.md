# sources/distributed-fs/ceph-client/drivers/soc/sunxi/sunxi_sram.c

## Purpose

`sunxi_sram.c` controls Allwinner SRAM routing between CPU and hardware clients, exposes selected SRAM-controller registers as a syscon/regmap, populates SRAM child devices, and provides debugfs visibility of SRAM section ownership.

## Important APIs, Types, and Functions

Core data types are `struct sunxi_sram_func`, `struct sunxi_sram_data`, `struct sunxi_sram_desc`, and `struct sunxi_sramc_variant`. Static descriptors define routeable SRAM sections such as A3-A4, C1, D, and A64 C. Public exported APIs are `sunxi_sram_claim()` and `sunxi_sram_release()`. `sunxi_sram_of_parse()` reads `allwinner,sram` phandles. `sunxi_sram_show()` implements debugfs display. `sunxi_sram_regmap_accessible_reg()` gates regmap access to EMAC clocks, LDO control, and THS offset registers. `sunxi_sram_probe()` maps MMIO, registers optional syscon regmap, populates child devices, and creates debugfs.

## Control Flow

At built-in platform-driver probe, the driver records the device, obtains variant data, maps the controller register block, optionally registers a regmap for variant-specific registers, populates child nodes, and creates `/sys/kernel/debug/sram`. A client calls `sunxi_sram_claim(dev)`, which parses its `allwinner,sram` phandle and function value, rejects unavailable or unknown SRAM nodes, checks the section's `claimed` flag under `sram_lock`, writes the function selection bits into the SRAM control register, and marks the section claimed. Release parses the same phandle and clears the claimed flag without changing the hardware mux.

## State and Persistence Behavior

Global state includes `sram_dev`, `base`, the spinlock, and static section descriptors with `claimed` flags. Hardware mux register writes persist until changed or reset. Regmap accesses share the same spinlock to serialize with claim/release writes.

## Dependencies and Integration Points

It depends on OF phandles, `mmio-sram` child layout, platform MMIO resources, regmap MMIO, syscon registration, debugfs, and the exported `<linux/soc/sunxi/sunxi_sram.h>` API used by device drivers such as EMAC, USB OTG, display, or video engines.

## Risks and Edge Cases

The singleton globals mean multiple SRAM controllers would conflict. `release()` clears only software ownership, not hardware routing back to CPU. Debugfs walks OF nodes and addresses without extensive NULL checks. Clients that fail to release can permanently block a section. Function descriptors are static and must match DT binding values exactly. The regmap access callback relies on `dev_get_drvdata()` being variant data.

## Test Signals

Test client claim/release paths, double-claim `-EBUSY`, invalid phandles, unavailable SRAM nodes, and debugfs output. Hardware tests should verify SRAM mux changes for EMAC/USB/VE/DE clients and regmap access restrictions on each variant.
