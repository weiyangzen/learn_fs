# sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-rzn1-miic.c

Purpose: Implements the Renesas RZ/N1, RZ/N2H, and RZ/T2H MII converter PCS driver. It configures SoC Ethernet mux/converter registers and provides per-port `phylink_pcs` objects for MAC drivers.

Important APIs, types, and functions: `struct miic` stores MMIO base, device, lock, reset controls, OF data, and PHY_LINK config. `struct miic_port` is the per-port PCS wrapper. Exported APIs are `miic_create()` and `miic_destroy()`. Phylink ops are `miic_config()`, `miic_link_up()`, and `miic_pre_init()`. Platform lifecycle is `miic_probe()`/`miic_remove()`. OF data tables describe RZ/N1 and RZ/T2H mux match tables, port ranges, reset IDs, write-lock behavior, and switch-mode masks.

Control flow: Probe allocates `miic`, parses device tree requested converter inputs into `dt_val`, validates them against SoC match tables, maps registers, deasserts resets, enables runtime PM, writes MODCTRL, disables converters and switch speed/duplex overrides, programs PHY_LINK polarity bits, and finally publishes driver data. `miic_create()` finds the parent platform device, validates the port number, device-links the consumer, allocates a port PCS, and advertises MII/RMII/RGMII modes. Config sets converter mode and initial speed, enables the converter, and link-up updates speed/duplex.

State and persistence behavior: Hardware mux mode and PHY_LINK bits persist in MIIC registers. Per-port interface cache avoids changing speed while an interface is already active. Runtime PM remains active while the platform driver is bound.

Dependencies and integration points: It depends on OF bindings, Renesas dt-bindings constants, reset controller, runtime PM, platform devices, phylink, and consumer MAC drivers calling `miic_create()` from child PCS nodes.

Risks and edge cases: Device-tree mux combinations must match fixed tables; invalid combinations print the requested configuration. RZ/N1 and RZ/T2H differ in port numbering, lock/unlock sequence, resets, and active polarity rules. `miic_parse_dt()` allocates `dt_val` for multiple entries but clears only `sizeof(*dt_val)`, which is a suspicious bug because uninitialized entries can affect match results. `miic_create()` uses driver-data presence as readiness and returns `-EPROBE_DEFER` before probe completion.

Test signals: Validate all documented mux table combinations, invalid DT diagnostics, RZ/N1 register unlock and RZ/T2H locked writes, reset deassert/assert actions, PHY_LINK active-high/low mapping, per-port create/destroy, MII/RMII/RGMII config and link-up speeds, `rxc_always_on` pre-init, runtime PM error paths, and KASAN/UBSAN around DT parsing.
