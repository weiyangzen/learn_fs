## sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/Kconfig

Purpose: defines the Apple Ethernet vendor menu and legacy Apple/Macintosh Ethernet driver symbols.

Important APIs, types, and functions: `NET_VENDOR_APPLE` gates the menu and defaults yes on supported PowerMac/Mac platforms. `MACE` enables Power Mac MACE support and selects `CRC32`; `MACE_AAUI_PORT` chooses AAUI as the default MACE port; `BMAC` enables G3 BMAC support and selects `CRC32`; `MACMACE` enables onboard AMD 79C940 MACE support for Macintosh AV machines and selects `CRC32`.

Control flow, state, and dependencies: Kconfig state controls which object files are built by the Apple Makefile. Runtime state is in the corresponding driver C files, not here. Dependencies restrict options to `PPC_PMAC && PPC32` or `MAC`.

Integration points: sourced by parent Ethernet Kconfig and paired with `apple/Makefile` object gates.

Risks: these are legacy platform-specific options; loosening dependencies can expose drivers to unsupported architectures. Help text/module names must match Makefile outputs.

Test signals: configuration menu visibility on PPC_PMAC/PPC32 and MAC targets; compile each selected symbol as built-in/module with `CRC32` selected.
