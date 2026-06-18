# sources/distributed-fs/ceph-client/drivers/net/ethernet/cortina/Kconfig

## Purpose
`cortina/Kconfig` exposes the Cortina Ethernet vendor menu and the Gemini Ethernet driver option.

## Important APIs, types, and functions
- `NET_VENDOR_CORTINA` is a vendor gate boolean defaulting to `y`.
- `GEMINI_ETHERNET` is a tristate for StorLink/Cortina Gemini dual Gigabit Ethernet.
- Dependencies: `OF` and `HAS_IOMEM`.
- Selected subsystems: `PHYLIB` and `CRC32`.

## Control flow and state
The Kconfig state controls whether `gemini.o` is built into the kernel, as a module, or not built. The vendor gate hides or shows the driver option but does not itself add code.

## Dependencies and integration points
The Gemini platform driver needs device tree probing, MMIO register access, PHY library support, and CRC32 for multicast filter hashing.

## Risks and test signals
Incorrect dependencies would allow impossible builds or hide valid configurations. Test with `COMPILE_TEST`-style configs where appropriate, built-in/module builds, and OF platform boot with PHYLIB enabled.
