# `sources/distributed-fs/ceph-client/drivers/phy/tegra/xusb.h` Research

## Purpose

This header defines the internal data model and SoC abstraction for the Tegra XUSB pad controller driver family. It is shared by the common platform driver and SoC-specific backends. The header describes lanes, pads, ports, padctl controller state, ops tables, inline type conversions, register access helpers, and exported SoC descriptors.

## Important APIs, Types, and Functions

- Lane model: `struct tegra_xusb_lane_soc`, `struct tegra_xusb_lane`, typed lane wrappers for USB3/USB2/ULPI/HSIC/PCIe/SATA, and `struct tegra_xusb_lane_ops`.
- Pad model: `struct tegra_xusb_pad_soc`, `struct tegra_xusb_pad`, typed pad wrappers, and `struct tegra_xusb_pad_ops`.
- Port model: `struct tegra_xusb_port`, typed USB2/ULPI/HSIC/USB3 port wrappers, `struct tegra_xusb_lane_map`, and `struct tegra_xusb_port_ops`.
- Controller model: `struct tegra_xusb_padctl_soc`, `struct tegra_xusb_padctl_ops`, and `struct tegra_xusb_padctl`.
- Helpers: `padctl_readl()`, `padctl_writel()`, `padctl_readl_poll()`, `tegra_xusb_find_lane()`, `tegra_xusb_find_port()`, typed find/release/remove helpers, and pad registration functions.
- Conditional externs expose SoC descriptors only when their architecture configs are enabled.

## Control Flow

The header itself has no executable top-level flow, but it defines how flow is dispatched. The common driver owns generic object lifecycle and calls padctl/pad/lane/port ops through these structures. SoC files populate static `tegra_xusb_padctl_soc` descriptors with pad arrays, port counts, supply names, and ops. A pad's lane ops probe/remove lane-private objects and optionally provide IDDQ, sleepwalk, wake, and remote-wake behavior. A port's ops map logical ports to lanes and enable/disable port-specific hardware. Padctl ops provide SoC-level probe/remove, PM, context, VBUS, LFPS, HSIC idle, and UTMI hooks.

## State and Persistence

The defined state is hierarchical. `tegra_xusb_padctl` is the root and owns MMIO registers, reset, regulators, mutex, and lists of pads/lanes/ports. Pads own PHY provider state and arrays of lane PHYs. Lanes keep parsed function index, DT node, lane index, and back-pointer to their pad. Ports retain lane association, role-switch/USB PHY bridge state, index, and typed per-port fields such as VBUS regulator, mode, fake USB3 port, saved USB3 tuning, and companion mapping. SoC-specific files extend this with private containers that embed `struct tegra_xusb_padctl`.

## Dependencies and Integration Points

The header depends on Linux IO, polling, mutex, workqueue, USB chapter 9, OTG, and role-switch definitions, with forward declarations for PHY, platform device, provider, and regulator types. It integrates all Tegra XUSB sources by providing the stable private ABI between `xusb.c` and SoC backends. It also defines the compatible SoC descriptor symbols that the common match table references.

## Risks and Edge Cases

- Because type-specific wrappers rely on `container_of()`, each typed object must embed the base structure exactly as expected.
- Ops are optional in many places; callers must test for null callbacks or return unsupported errors consistently.
- `padctl_readl_poll()` returns the `readl_poll_timeout()` error but is typed as `u32`, which can obscure negative error handling in callers.
- State is protected primarily by `padctl->lock`, but some fields are manipulated by generic PHY callbacks, role-switch work, and PM paths; lock ordering must stay consistent.
- Conditional externs mean build coverage depends on architecture config combinations.

## Test Signals

Header-level validation comes from all Tegra XUSB compile configurations, sparse/build warnings for struct declarations, Coccinelle or compiler checks around container casts, runtime tests for optional ops returning expected unsupported values, lockdep coverage for padctl lock usage, and probe/remove tests that exercise every release callback path.
