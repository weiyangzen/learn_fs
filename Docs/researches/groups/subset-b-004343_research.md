# subset-b-004343 research

Grouped research for the requested Ethernet driver sources. Each section is bounded by the required reconciliation markers and keeps the original source path as its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe.h

Purpose: this header is the central contract for the AMD XGBE 10GbE driver. It names the driver, descriptor and queue limits, DMA/AXI defaults, MTU and FIFO constants, timestamp and PTP parameters, RSS sizes, auto-negotiation timing, PCI IDs, and all shared data structures used by the platform, PCI, PHY, descriptor, ethtool, DCB, PTP, I2C, and debugfs implementation files.

Important APIs, types, and data: `struct xgbe_packet_data` carries per-packet TX/RX parse state including SKB, descriptor count, VLAN tag, checksum/RSS/timestamp metadata, and byte counters. `struct xgbe_ring_desc`, `struct xgbe_ring_data`, and `struct xgbe_ring` define DMA descriptors, software descriptor shadow state, RX page allocations, TX BQL accounting, `cur`/`dirty` indexes, and queue-stopped state. `struct xgbe_channel` binds a DMA channel to a TX/RX ring pair, NAPI context, per-channel IRQ, timer, and CPU affinity. `struct xgbe_hw_if`, `struct xgbe_phy_if`, `struct xgbe_i2c_if`, and `struct xgbe_desc_if` are operation tables filled by version-specific implementation files. `struct xgbe_prv_data` is the persistent device context: it stores MMIO bases, interrupts, workqueues/timers, channel arrays, queue counts, coalescing settings, RSS tables, flow-control state, PTP state, auto-negotiation state machine data, I2C state, debugfs state, and hardware feature flags.

Control flow and integration: implementation files allocate `xgbe_prv_data`, initialize the operation tables with `xgbe_init_function_ptrs_*`, configure a `net_device` via `xgbe_config_netdev`, and run data path callbacks through the function tables. TX maps SKBs through descriptor helpers, advances ring indexes, starts DMA via `hw_if.dev_xmit`, and reclaims descriptors through channel NAPI/interrupt paths. RX uses page-backed buffers, saved partial receive state, RSS and checksum fields, and optional split-header support. PHY control is abstracted through Clause 37/73/KR/SFP modes and mailbox commands. PTP and PPS helpers provide hardware timestamp configuration, TX timestamp work, and clock registration.

State and persistence: all long-lived device state is in `xgbe_prv_data`, while ring state is split between coherent descriptor memory and software shadows. State bits in `dev_state` distinguish down, link initialization, link error, and stopped paths. Timers and work items handle service, restart, stop, TX timestamp, auto-negotiation, I2C, ECC, and bottom-half work. RSS key/table, active VLAN bitmap, flow control, coalescing, DCB mappings, PTP addend/time, debugfs selected registers, and PHY negotiation status persist across netdev callbacks until reconfigured or freed.

Dependencies and integration points: the header depends on Linux netdev, DMA, NAPI, PHY/MDIO, PTP, DCB, ethtool, PCI/platform/ACPI, clock, debugfs, and UDP tunnel infrastructure. External entry points include `xgbe_platform_init/exit`, optional `xgbe_pci_init/exit`, `xgbe_get_netdev_ops`, `xgbe_get_ethtool_ops`, `xgbe_get_udp_tunnel_info`, optional DCB ops, PTP helpers, selftest helpers, and loopback/debugfs helpers.

Risks: the header encodes broad cross-file coupling; mismatched descriptor counts, function-table initialization, timestamp frequency constants, or queue count limits can break unrelated files. Ring and packet state contain many DMA ownership transitions, so missing barriers or stale saved RX state can corrupt packets. Several duplicated declarations and fields are visible, so edits should avoid broad refactors without compiling the full driver. Feature flags in `xgbe_version_data` gate hardware quirks; wrong defaults can expose ECC, I2C, timestamp, RX adaptation, or prefetch bugs.

Test signals: compile with platform and PCI variants, `CONFIG_AMD_XGBE_DCB`, `CONFIG_DEBUG_FS`, and PCI disabled to exercise inline fallbacks. Runtime signals are probe/remove, `ip link set up/down`, MTU and ring count changes, ethtool statistics/selftests, PTP timestamp tests, RSS/VXLAN traffic, pause/DCB configuration, SFP/I2C module reads, and RX adaptation/link renegotiation under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/Kconfig

Purpose: this top-level APM Ethernet Kconfig file delegates configuration to the two APM X-Gene Ethernet driver generations.

Important APIs, types, and functions: it has no C APIs; its only behavior is sourcing `drivers/net/ethernet/apm/xgene/Kconfig` and `drivers/net/ethernet/apm/xgene-v2/Kconfig`.

Control flow, state, and dependencies: Kconfig evaluation includes the legacy X-Gene and v2 driver menus in this directory. No persistent runtime state exists; build-time state is the selected symbols exported by the sourced files.

Integration points: used by the parent Ethernet Kconfig to expose APM vendor drivers. It must stay in sync with the subdirectory names and Makefile object gates.

Risks: a stale source path hides all APM driver options from configuration. Because it contains only includes, test coverage is mainly configuration discovery.

Test signals: run kernel config menu or `make olddefconfig` with `ARCH_XGENE`/`COMPILE_TEST`; verify `NET_XGENE` and `NET_XGENE_V2` remain visible and selectable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/Makefile

Purpose: this Makefile connects Kconfig symbols to the APM Ethernet subdirectories.

Important APIs, types, and functions: it contributes `xgene/` when `CONFIG_NET_XGENE` is enabled and `xgene-v2/` when `CONFIG_NET_XGENE_V2` is enabled.

Control flow, state, and dependencies: build state is purely Kbuild object inclusion. The file depends on matching Kconfig symbols and the existence of the two subdirectory Makefiles.

Integration points: parent kernel networking Makefiles recurse here; subdirectory Makefiles define the actual module objects.

Risks: symbol/name drift breaks module builds while leaving source code intact. Since both drivers are independent, accidental unconditional inclusion can build unsupported hardware paths.

Test signals: build `drivers/net/ethernet/apm/` with each symbol as built-in and module; verify `xgene-enet.o` and `xgene-enet-v2.o` are included only under their configured symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/Kconfig

Purpose: defines `NET_XGENE_V2`, the selectable APM X-Gene Ethernet v2 driver.

Important APIs, types, and functions: the symbol is tristate, named "APM X-Gene SoC Ethernet-v2 Driver", depends on `ARCH_XGENE || COMPILE_TEST`, and documents that the module name is `xgene-enet-v2`.

Control flow, state, and dependencies: build-time selection controls whether the v2 platform driver and helpers compile. The help text identifies the linked-list DMA descriptor architecture used by this generation.

Integration points: paired with `xgene-v2/Makefile`, which builds `main.o`, `mac.o`, `enet.o`, `ring.o`, `mdio.o`, and `ethtool.o` into `xgene-enet-v2.o`.

Risks: the driver uses PHYLIB APIs in code but this Kconfig does not explicitly select PHYLIB in this file; it may rely on other dependency paths. Changes should verify compile-test coverage on non-X-Gene architectures.

Test signals: enable as module and built-in under `COMPILE_TEST`; build should include ACPI/platform, PHY, MDIO, DMA, and ethtool references without unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/Makefile

Purpose: defines the object composition of the X-Gene Ethernet v2 module.

Important APIs, types, and functions: `xgene-enet-v2-objs` is composed from `main.o`, `mac.o`, `enet.o`, `ring.o`, `mdio.o`, and `ethtool.o`; `obj-$(CONFIG_NET_XGENE_V2)` emits `xgene-enet-v2.o`.

Control flow, state, and dependencies: Kbuild links the platform driver core, MAC register programming, ENET reset, descriptor setup, MDIO/PHY management, and ethtool statistics into one module.

Integration points: mirrors the function declarations in `main.h`, `mac.h`, `enet.h`, `ring.h`, and `ethtool.h`.

Risks: dropping a helper object can compile some declarations but fail final link, because `main.c` calls into every listed component.

Test signals: `make M=drivers/net/ethernet/apm/xgene-v2` with `CONFIG_NET_XGENE_V2=m`; verify the module exports the platform driver named `xgene-enet-v2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/enet.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/enet.c

Purpose: provides basic CSR access, ENET block reset, memory/ECC readiness polling, coherency configuration, and initial port bring-up for the v2 driver.

Important APIs, types, and functions: `xge_wr_csr` and `xge_rd_csr` wrap `iowrite32`/`ioread32` against `pdata->resources.base_addr`. `xge_port_reset` enables ENET clocks, asserts/deasserts reset, toggles memory shutdown, polls `BLOCK_MEM_RDY` until `MEM_RDY`, then configures coherent read/write auxiliary bits in `ENET_SHIM`. `xge_port_init` sets default speed to `SPEED_1000`, initializes the MAC, and resumes traffic.

Control flow, state, and persistence: `main.c` calls `xge_init_hw`, which calls `xge_port_reset` and `xge_port_init` during probe before MDIO setup and registration. The reset path updates hardware state only; persistent driver state is `pdata->phy_speed`, later adjusted by PHY link callbacks in `mdio.c`.

Dependencies and integration points: depends on register constants in `enet.h`, MAC setup in `mac.c`, platform resource mapping in `main.c`, and Linux delay/MMIO APIs.

Risks: the readiness loop has a small fixed retry count; slow hardware initialization will fail probe with `-ETIMEDOUT`. The code assumes a single MMIO base and coherent DMA support; wrong resource mapping or missing coherency bits can cause descriptor corruption.

Test signals: probe logs should not show "ECC init failed"; `ip link set up` should receive and transmit after `xge_port_init`; fault injection around `BLOCK_MEM_RDY` should produce deterministic `-ETIMEDOUT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/enet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/enet.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/enet.h

Purpose: declares ENET CSR offsets, reset/coherency bit values, traffic-resume registers, and the public ENET helper API for v2.

Important APIs, types, and functions: constants include `ENET_CLKEN`, `ENET_SRST`, `ENET_SHIM`, memory shutdown/readiness registers, `DEVM_ARAUX_COH`, `DEVM_AWAUX_COH`, forced link status, link aggregation resume, and RX data valid gate registers. It declares `xge_wr_csr`, `xge_rd_csr`, `xge_port_reset`, and `xge_port_init`.

Control flow, state, and dependencies: it is included by `main.h`, making ENET access available to `main.c`, `mac.c`, `ring.c`, `mdio.c`, and `ethtool.c`. It has no runtime state itself.

Integration points: its offsets must match the hardware resource mapped by `xge_get_resources`; its prototypes are implemented in `enet.c`.

Risks: incorrect register offsets affect reset, DMA coherency, and traffic gating globally. The include guard comment has a typo but does not affect compilation.

Test signals: compile all v2 objects, then validate reset and traffic resume by observing successful probe and packet I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/enet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/ethtool.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/ethtool.c

Purpose: supplies v2 ethtool operations for driver information, PHY-backed link settings, statistic names, statistic values, and link reporting.

Important APIs, types, and functions: `struct xge_gstrings_stats` maps generic netdev stats to offsets in `rtnl_link_stats64`; `struct xge_gstrings_extd_stats` maps hardware statistic names to register addresses. `xge_get_drvinfo` reports driver name `xgene_enet`. `xge_get_link_ksettings` and `xge_set_link_ksettings` delegate to PHYLIB. `xge_get_strings`, `xge_get_sset_count`, and `xge_get_ethtool_stats` expose basic and extended counters. `xge_set_ethtool_ops` installs the static `ethtool_ops`.

Control flow, state, and persistence: ethtool reads netdev statistics through `dev_get_stats`, then reads hardware counters directly from CSR offsets. There is no accumulation array in v2, so values reflect current hardware counter reads plus software stats maintained in `main.c`.

Dependencies and integration points: depends on `ethtool.h` register constants, `xge_rd_csr`, `get_stats64` in `main.c`, and PHY device setup in `mdio.c`. It is installed during probe before netdev registration.

Risks: direct hardware reads may clear or wrap counters depending on hardware behavior; the code does not mask all widths. Link settings fail with `-ENODEV` if the PHY did not attach. The driver string differs from the module name, which can confuse tests that expect `xgene-enet-v2`.

Test signals: `ethtool -i`, `ethtool <dev>`, `ethtool -S`, and `ethtool -s` via PHY should work. Traffic should increment both software and hardware counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/ethtool.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/ethtool.h

Purpose: defines v2 ethtool statistic mapping structures, MAC statistics register offsets, and the ethtool installation prototype.

Important APIs, types, and functions: `struct xge_gstrings_stats` stores an ethtool stat name and structure offset. `struct xge_gstrings_extd_stats` stores an ethtool stat name, CSR address, and sampled value. Register constants cover RX/TX size buckets, multicast/broadcast counters, pause/control frames, alignment/FCS/length errors, drops, jabbers, overruns, underruns, and fragments. It declares `xge_set_ethtool_ops`.

Control flow, state, and dependencies: included through `main.h`; no runtime state lives here. `ethtool.c` uses the offsets to build ethtool string and value arrays.

Integration points: offsets must match MAC counter registers used by the v2 hardware block and must remain aligned with the names array in `ethtool.c`.

Risks: wrong addresses silently report bad diagnostics. Adding/removing counters requires updating count/string/value logic together.

Test signals: `ethtool -S` should print stable names and plausible increments under directed traffic and error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/ethtool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/mac.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/mac.c

Purpose: programs the v2 RGMII MAC for reset, speed, station address, and TX/RX enablement.

Important APIs, types, and functions: `xge_mac_reset` toggles `SOFT_RESET`. `xge_mac_set_speed` programs MAC, interface control, ICM/ECM, and RGMII registers for 10/100/1000 speeds based on `pdata->phy_speed`. `xge_mac_set_station_addr` writes the netdev MAC address into `STATION_ADDR0/1`. `xge_mac_init` resets, sets speed, and writes the address. `xge_mac_enable` and `xge_mac_disable` set/clear `TX_EN` and `RX_EN`.

Control flow, state, and persistence: probe defaults to 1Gbps through `xge_port_init`; PHY adjustment in `mdio.c` updates `pdata->phy_speed`, disables MAC, reprograms speed, and re-enables MAC when link settings change. MAC address changes flow from `ndo_set_mac_address` in `main.c`.

Dependencies and integration points: depends on register bit helpers in `mac.h`, CSR wrappers in `enet.c`, PHYLIB speed constants, and `net_device` address state.

Risks: bit helper masks use `GENMASK(pos + len, pos)`, so field definitions must be consistent with that convention. Reprogramming speed while RX/TX are active is guarded by the link adjust path but direct callers should avoid racing with data path. The enable function reads back `MAC_CONFIG_1` but does not use the value.

Test signals: PHY speed changes at 10/100/1000 should update link without packet corruption; MAC address changes should be reflected in hardware and visible on the network.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/mac.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/mac.h

Purpose: centralizes v2 MAC, RGMII, ICM/ECM, and MDIO management register offsets and bitfield helpers.

Important APIs, types, and functions: constants cover `MAC_CONFIG_1/2`, MII management registers, `INTERFACE_CONTROL`, station address registers, `RGMII_REG_0`, ICM/ECM registers, enable/reset bits, speed/interface fields, FIFO threshold fields, and MII busy/read controls. Inline helpers `xgene_set_reg_bits` and `xgene_get_reg_bits`, plus macros `SET_REG_BITS`, `SET_REG_BIT`, `GET_REG_BITS`, and `GET_REG_BIT`, perform field packing. It declares all `xge_mac_*` functions.

Control flow, state, and dependencies: the header carries no state but is included by `main.h`, `mac.c`, and `mdio.c`. It depends on Linux bit macros.

Integration points: MDIO and MAC code both rely on the management register definitions; mistakes affect PHY access and link setup.

Risks: field helper semantics are easy to misuse because the length parameter is passed into `GENMASK(pos + len, pos)`. Changes require hardware-register review. `GET_REG_BIT` is a raw mask test, unlike `GET_REG_BITS`.

Test signals: compile with `W=1`; validate MDIO reads/writes, 10/100/1000 speed changes, station address programming, and TX/RX enable toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/main.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/main.c

Purpose: implements the X-Gene Ethernet v2 platform netdev driver, including probe/remove, resource discovery, descriptor allocation, TX/RX data path, NAPI/IRQ handling, timeout recovery, statistics, and netdev operations.

Important APIs, types, and functions: `xge_probe` allocates `net_device`, records `xge_pdata`, installs `xgene_ndev_ops`, obtains MMIO/MAC/PHY/IRQ resources, coerces 64-bit DMA, initializes hardware, configures MDIO, adds NAPI, and registers the netdev. `xge_open` creates TX/RX rings, enables NAPI and IRQs, starts PHY, enables MAC, and starts the queue. `xge_close` reverses that order. `xge_start_xmit` copies the SKB head into a coherent DMA buffer, writes TX descriptor address/length/E bit, and starts TX DMA. `xge_txc_poll` reclaims completed TX descriptors. `xge_rx_poll` consumes RX descriptors, unmaps SKB buffers, handles errors, pushes packets to GRO, refills descriptors, and acknowledges RX status. `xge_timeout` resets stalled TX state under RTNL. `xge_get_stats64` reports software counters.

Control flow, state, and persistence: descriptor rings are allocated on open and freed on close. `xge_desc_ring` head/tail indexes track software ownership, while descriptor `E` and packet size fields track hardware ownership. `pdata->stats` accumulates packet, byte, and error counters for the lifetime of the netdev. Probe-time state includes the platform device, mapped CSR base, IRQ number, MAC address, PHY mode, NAPI object, and PHY device. Timeout recovery stops the queue and interrupts, drains/frees pending TX buffers, resets the TX ring, reinitializes MAC, and restarts NAPI/interrupts/queue.

Dependencies and integration points: uses platform resources, ACPI matching (`APMC0D80`), PHYLIB, DMA mapping/coherent allocation, NAPI, netdev ops, ethtool setup, and helper files `enet.c`, `mac.c`, `mdio.c`, and `ring.c`.

Risks: TX allocates a coherent buffer per packet and stores `dma_addr` in a `static` local, which is unusual and risky under concurrency even though only the current value is copied into ring metadata. The TX path only sends `skb_headlen`, so fragmented SKBs/GSO are not fully supported despite feature flags `NETIF_F_GSO | NETIF_F_GRO`. Error unwinding after `request_irq` failure does not delete rings in `xge_open`, so open failure paths should be reviewed. RX refill failure can leave the ring partially depleted. The driver only accepts RGMII.

Test signals: build with `COMPILE_TEST`; boot/probe on ACPI device; run `ip link up/down`, continuous ping/iperf, forced TX timeout, MTU-sized frames, PHY link toggles, `ethtool -S`, and DMA mapping failure injection. Packet tests should include fragmented/GSO SKBs to expose feature mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/main.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/main.h

Purpose: shared v2 driver header that imports kernel dependencies and defines resource, statistics, descriptor ring, packet metadata, and private device state structures.

Important APIs, types, and functions: `XGENE_ENET_STD_MTU`, `XGENE_ENET_MIN_FRAME`, and `IRQ_ID_SIZE` set common limits. `struct xge_resource` holds the mapped CSR base, PHY mode, and IRQ. `struct xge_stats` accumulates software TX/RX packets, bytes, and RX errors. `struct xge_pkt_info` records an SKB, DMA address, and optional coherent TX packet buffer. `struct xge_desc_ring` stores netdev pointer, coherent descriptor memory, DMA base, packet metadata array, and head/tail indexes. `struct xge_pdata` holds platform/netdev pointers, resources, TX/RX rings, NAPI, IRQ name, stats, buffer count, and current PHY speed.

Control flow, state, and dependencies: all v2 C files include this header, so it is the shared ABI between probe, ring setup, MAC, ENET reset, MDIO, and ethtool code. Runtime state is owned by `xge_pdata` and ring structures allocated in `main.c`.

Integration points: includes Linux ACPI, platform, OF, PHY, DMA/I/O, VLAN, NAPI, and networking headers, then local `mac.h`, `enet.h`, `ring.h`, and `ethtool.h`.

Risks: broad includes can hide missing direct dependencies in individual C files. The private data is small and assumes one TX ring, one RX ring, and one IRQ; extending queues requires structural changes.

Test signals: compile every v2 object; runtime checks should confirm head/tail ring state, stats accumulation, and PHY speed persistence across link changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/mdio.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/mdio.c

Purpose: implements v2 MDIO bus access, PHY discovery/connection, and PHY link adjustment.

Important APIs, types, and functions: the file configures MII management clocking, waits for `MII_MGMT_BUSY` to clear, implements MDIO read/write through MAC management registers, registers an `mii_bus`, connects the netdev PHY, and tears the bus down. The link adjustment callback updates `pdata->phy_speed`, disables the MAC, calls `xge_mac_set_speed`, re-enables the MAC, and reports link changes through netdev/PHY helpers.

Control flow, state, and persistence: `xge_probe` calls `xge_mdio_config` after hardware reset. On open, `phy_start` begins PHY state machine callbacks. On close/remove, `phy_stop` and MDIO removal disconnect and unregister the bus. Current negotiated speed persists in `pdata->phy_speed`.

Dependencies and integration points: depends on PHYLIB/MDIO APIs, OF/ACPI device properties, MAC register definitions in `mac.h`, CSR access in `enet.c`, and netdev lifecycle in `main.c`.

Risks: MDIO busy polling has bounded wait loops; hung hardware can fail reads/writes. Link adjustment reprograms MAC while traffic may be active, so ordering with PHY state and MAC enablement matters. Probe requires a valid PHY attachment for useful link behavior.

Test signals: `mdiobus` registration, PHY probe, `ethtool` link settings, forced speed/duplex changes, cable unplug/replug, and MDIO timeout fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/ring.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/ring.c

Purpose: initializes v2 linked-list DMA descriptors and publishes TX/RX descriptor base addresses to hardware.

Important APIs, types, and functions: `xge_setup_desc` creates a circular linked list of `XGENE_ENET_NUM_DESC` descriptors by setting each descriptor empty and pointing `NEXT_DESC_ADDRL/H` to the next descriptor. `xge_update_tx_desc_addr` writes `DMATXDESCL/H` and resets TX head/tail. `xge_update_rx_desc_addr` writes `DMARXDESCL/H` and resets RX head/tail.

Control flow, state, and persistence: `main.c` calls setup when creating rings and during TX timeout recovery. Descriptor memory is coherent and persists for the open lifetime; head/tail software indexes are reset whenever the base address is republished.

Dependencies and integration points: depends on descriptor field macros from `ring.h`, CSR writes from `enet.c`, DMA addresses allocated in `main.c`, and hardware registers consumed by the DMA engine.

Risks: wrong next-descriptor links break the hardware ring permanently until reset. The ring size must be power-of-two for mask wrapping. Republish during live traffic must be done after stopping DMA/queue.

Test signals: ring initialization inspection, successful TX/RX after open, wraparound traffic beyond descriptor count, and timeout recovery that resumes TX after `xge_setup_desc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/ring.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/ring.h

Purpose: defines v2 DMA descriptor count/size, descriptor bitfields, DMA control/status registers, and descriptor helper prototypes.

Important APIs, types, and functions: constants include descriptor count, descriptor size, buffer count, empty-slot marker, `DMATX/RXDESCL/H`, `DMATX/RXCTRL`, `DMATX/RXSTATUS`, and fields such as `E`, `PKT_ADDRL/H`, `PKT_SIZE`, `NEXT_DESC_ADDRL/H`, `D`, `TXPKTCOUNT`, and `RXPKTCOUNT`. `struct xge_raw_desc` represents descriptor words `m0` through `m2`. Macros `GET_BITS` and `SET_BITS` pack/unpack fields. It declares descriptor setup and address update helpers.

Control flow, state, and dependencies: included by `main.h` and used by TX/RX/refill paths in `main.c` and setup in `ring.c`.

Integration points: hardware descriptor format and CSR definitions must match the v2 linked-list DMA engine.

Risks: field position/length errors directly affect DMA addresses, ownership bits, packet lengths, and interrupt/status accounting. `SET_BITS` truncates through masks, so callers must pass correct width values.

Test signals: DMA to/from high addresses, descriptor wraparound, packet length correctness, RX error bit handling, and TX/RX status count acknowledgement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/ring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/Kconfig

Purpose: defines `NET_XGENE`, the original APM X-Gene SoC Ethernet driver.

Important APIs, types, and functions: the symbol is tristate, depends on `ARCH_XGENE || COMPILE_TEST`, selects `PHYLIB`, `MDIO_XGENE`, and `GPIOLIB`, and documents module name `xgene_enet`.

Control flow, state, and dependencies: build-time selection enables the multi-file X-Gene driver supporting RGMII, SGMII, and XGMII modes with PHY, MDIO, GPIO/SFP, and classifier dependencies.

Integration points: paired with `xgene/Makefile`; selected symbols match code paths in `xgene_enet_main.c` and hardware helpers.

Risks: removing selected dependencies will break optional but compiled code paths such as PHY connection, MDIO bus setup, and SFP GPIO lookup. `COMPILE_TEST` should remain available because hardware-specific code benefits from broad build coverage.

Test signals: enable as module and built-in; compile with ACPI/OF, PHYLIB, MDIO_XGENE, and GPIO combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/Makefile

Purpose: defines the original X-Gene Ethernet module object list.

Important APIs, types, and functions: `xgene-enet-objs` links `xgene_enet_hw.o`, `xgene_enet_sgmac.o`, `xgene_enet_xgmac.o`, `xgene_enet_main.o`, `xgene_enet_ring2.o`, `xgene_enet_ethtool.o`, and `xgene_enet_cle.o`; `obj-$(CONFIG_NET_XGENE)` emits `xgene-enet.o`.

Control flow, state, and dependencies: all MAC variants, ring variants, ethtool, classifier, and platform netdev code are compiled into one module so runtime PHY mode and hardware version choose operation tables.

Integration points: must include every file that implements operation-table symbols referenced by `xgene_enet_main.c`.

Risks: object omissions produce link failures for `xgene_gmac_ops`, `xgene_sgmac_ops`, `xgene_xgmac_ops`, `xgene_ring2_ops`, or `xgene_cle3in_ops`. Reordering is low risk but symbol inclusion is critical.

Test signals: build `M=drivers/net/ethernet/apm/xgene`; verify a single `xgene-enet.o` module and no unresolved operation-table symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_cle.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_cle.c

Purpose: programs the X-Gene 10G classifier/preclassifier engine for parser tree routing and RSS setup in XGMII mode.

Important APIs, types, and functions: conversion helpers pack sideband, indirection-table, database-pointer, key-node, and extended-word decision-node structures into hardware register words. `xgene_cle_dram_wr` writes CLE DRAM regions through indirect command registers and polls completion. Static `xgene_init_ptree_dn` encodes the parser tree for Ethernet/IPv4/TCP/UDP decisions. `xgene_cle_setup_node`, `xgene_cle_setup_dbptr`, and `xgene_cle_setup_ptree` write nodes and result pointers and enable the tree. RSS helpers write sideband packet RAM, random IPv4 hash secret keys, and a 128-entry indirection table that maps to RX rings and buffer pools. `xgene_enet_cle_init` builds default accept/drop DB pointers and installs `xgene_cle3in_ops`.

Control flow, state, and persistence: `xgene_enet_init_hw` configures `pdata->cle` and calls `cle_ops->cle_init` only for XGMII. CLE state is stored in hardware DRAM and in `pdata->cle` metadata such as parser count, active parser, start node, start DB pointer, and jump bytes. RSS secret keys are random at initialization and not persisted across reset.

Dependencies and integration points: uses structures and constants from `xgene_enet_cle.h`, ring IDs from `xgene_enet_main.c`, destination queue numbers from `xgene_enet_dst_ring_num`, and MMIO base `pdata->cle.base` set by resource discovery.

Risks: classifier table programming is tightly packed and difficult to validate visually. A bad DB pointer can drop all traffic or route packets to the wrong queue/buffer pool. Command polling returns `-EBUSY` on timeout, so hardware stalls block probe. RSS keys are random, complicating deterministic flow tests.

Test signals: XGMII probe should complete CLE init; multi-queue RSS traffic should distribute across RX queues; invalid command timeout tests should fail probe cleanly; non-XGMII modes should bypass CLE instead.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_cle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_cle.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_cle.h

Purpose: describes the classifier engine register layout, DRAM encodings, parser node formats, RSS constants, and CLE operation export.

Important APIs, types, and functions: defines indirect access registers (`INDADDR`, `INDCMD`, `DATA_RAM0`), parser pointers, default class-result registers, RSS control, command timeouts, packet RAM size, DRAM register count, node and branch field positions, jump modes, parser/node/operation enums, DRAM and command types, RSS hash type, protocol type/version, DB pointer indexes, sideband fields, IDT fields, and data structures for branches, decision nodes, key nodes, DB pointers, parser trees, and `struct xgene_enet_cle`.

Control flow, state, and dependencies: included by `xgene_enet_main.h` and implemented by `xgene_enet_cle.c`. It carries no live state except the structures embedded in `xgene_enet_pdata`.

Integration points: `xgene_cle3in_ops` is consumed by `xgene_enet_setup_ops` for XGMII; ring/buffer pool IDs from the main driver feed DB pointer and RSS IDT construction.

Risks: packed bitfield constants are hardware ABI. Small changes can invalidate parser trees, default routing, or RSS queue selection. The data structures contain pointers to temporary setup arrays in init paths, so use after setup must not assume permanent storage beyond programmed hardware.

Test signals: compile CLE users, initialize XGMII hardware, verify default packet acceptance, packet drops for unsupported paths if expected, and RSS queue distribution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_cle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_ethtool.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_ethtool.c

Purpose: exposes original X-Gene driver information, link settings, software and hardware statistics, and pause configuration through ethtool.

Important APIs, types, and functions: `gstrings_stats` maps generic `rtnl_link_stats64` counters; `gstrings_extd_stats` maps MAC statistic registers and masks. `xgene_get_link_ksettings` delegates to PHYLIB for RGMII or MDIO-backed SGMII, synthesizes fixed 1G SGMII settings without MDIO, and fixed 10G fiber settings for XGMII. `xgene_set_link_ksettings` only permits PHY-backed modes. `xgene_get_extd_stats` reads hardware counters, applies errata corrections, and adds MAC drop counts. `xgene_extd_stats_init` allocates and zeroes accumulated extended stats. Pause operations validate PHY pause for RGMII/SGMII and directly program MAC flow control for XGMII. `xgene_enet_set_ethtool_ops` installs the ops table.

Control flow, state, and persistence: `xgene_enet_probe` installs ops and initializes extended stats. Stats accumulate in `pdata->extd_stats` and are adjusted by software errata counters `false_rflr` and `vlan_rjbr`. Pause settings persist in `pdata->pause_autoneg`, `tx_pause`, and `rx_pause`.

Dependencies and integration points: relies on `xgene_enet_rd_stat`, MAC operation callbacks for drop counters and flow control, PHYLIB helpers, and netdev stats from `xgene_enet_get_stats64`.

Risks: extended stat accumulation assumes sane hardware counter semantics and masks. Errata corrections subtract counters and can underflow if ordering/width assumptions are wrong. Link settings intentionally reject non-PHY 10G changes.

Test signals: `ethtool -i`, `ethtool -S`, pause toggles, PHY-backed speed changes, fixed XGMII link reporting, and traffic/error generation to verify errata-adjusted counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_hw.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_hw.c

Purpose: implements X-Gene1 ring programming, GMAC register access, reset/clock/MAC setup, MDIO/PHY integration, error parsing, flow control, and the GMAC port/ring operation tables.

Important APIs, types, and functions: ring helpers write ring state, type, recombination buffer settings, ring IDs, interrupt mode, command counts, and queue length. `xgene_enet_parse_error` maps ingress hardware error codes to netdev stats. Indirect MAC/stat access helpers `xgene_enet_wr_mac`, `xgene_enet_rd_mac`, and `xgene_enet_rd_stat` serialize register operations. GMAC functions set MAC address, initialize ECC/clock, set RGMII speed/delays, frame size, pause thresholds, TX/RX enablement, CLE bypass, and shutdown. `xgene_ring_mgr_init`, `xgene_enet_reset`, MDIO config, PHY connect/disconnect, and the exported `xgene_gmac_ops`, `xgene_gport_ops`, and `xgene_ring1_ops` are core integration points.

Control flow, state, and persistence: `xgene_enet_setup_ops` selects these ops for RGMII and X-Gene1 ring mode. Probe maps CSR bases, then `port_ops->reset`, ring creation, buffer pool setup, `port_ops->cle_bypass`, and `mac_ops->init` program hardware. PHY link changes call adjust-link logic to update speed and flow control. Ring configuration persists in hardware until clear/delete.

Dependencies and integration points: depends on main private data, register constants in `xgene_enet_hw.h`, PHYLIB/MDIO_XGENE, ACPI/OF PHY lookup, clock APIs, and port/ring allocation in `xgene_enet_main.c`.

Risks: indirect MAC access has timeout loops; failures can leave stale register values. Ring programming differs from X-Gene2, so selecting the wrong `ring_ops` corrupts queue ownership. RGMII delay validation and clock assumptions are platform-sensitive. MDIO setup has multiple firmware paths, so ACPI/DT coverage is important.

Test signals: RGMII probe, MDIO bus registration, PHY connect and link adjustment, ring allocation and interrupt delivery, pause control, statistics reads, reset/shutdown, and descriptor error injection for all ingress error codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_hw.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_hw.h

Purpose: declares X-Gene1 hardware register constants, descriptor encodings, bit helpers, ring layout helpers, error codes, and GMAC/ring exported symbols.

Important APIs, types, and functions: inline `xgene_set_bits` and `xgene_get_bits`, resource-manager enum, ring CSR offsets, ring type/mode constants, descriptor field positions, buffer pool helpers, MAC/stat register offsets, MDIO fields, clock/reset bits, error enums, and helper prototypes such as `xgene_enet_parse_error`, `xgene_enet_wr_mac`, `xgene_enet_rd_mac`, `xgene_enet_rd_stat`, MDIO/PHY functions, and extern operation tables.

Control flow, state, and dependencies: included by most original X-Gene C files and paired with `xgene_enet_hw.c`. It has no live state, but its macros define how software interprets descriptor and register state.

Integration points: ring creation in `xgene_enet_main.c`, ring setup in `xgene_enet_hw.c`, X-Gene2 ring code, ethtool stats, and MAC variants all depend on these definitions.

Risks: any bitfield change affects DMA descriptor ownership, buffer length decoding, ring IDs, interrupt mode, and MAC/MDIO access. Header-level helper semantics must remain consistent with existing `SET_VAL`/`GET_VAL` call sites.

Test signals: compile all original driver objects; runtime validation should include descriptor ownership transitions, ring length, MDIO reads/writes, stats reads, and all supported PHY modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_main.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_main.c

Purpose: core platform netdev driver for the original APM X-Gene Ethernet hardware, covering probe/remove, resource mapping, runtime operation selection, ring and buffer-pool allocation, TX/RX/NAPI data path, classifier setup, MDIO/PHY link handling, stats, MTU changes, and netdev operations.

Important APIs, types, and functions: TX/RX helpers include buffer/page pool refill, SKB header parsing, checksum/TSO work-message construction, MSS slot management, scatter-gather descriptor setup, TX completion, RX frame construction, jumbo page-frag handling, ingress errata handling, and ring processing. Lifecycle functions include `xgene_enet_get_resources`, `xgene_enet_setup_ops`, `xgene_enet_create_desc_rings`, `xgene_enet_init_hw`, `xgene_enet_open`, `xgene_enet_close`, `xgene_enet_probe`, and `xgene_enet_remove`. Netdev ops provide open/stop/start_xmit/timeout/get_stats64/change_mtu/set_mac_address.

Control flow, state, and persistence: probe allocates a multi-queue netdev, maps ENET/ring CSR/ring command resources, derives port/PHY mode/delays/IRQs/GPIOs, chooses MAC/port/ring/CLE ops based on PHY mode and `enet_id`, coerces DMA, connects PHY or configures local MDIO, initializes hardware, adds NAPI, and registers the netdev. Hardware init resets the port, creates CPU/RX/TX/completion/buffer/page rings, refills pools, initializes CLE for XGMII or bypass for lower-speed modes, and initializes MAC. Open enables NAPI/IRQs, starts PHY or link polling, enables MAC TX/RX, and starts queues. NAPI processes RX and TX completion rings until budget, then re-enables IRQ. Close stops queues/MAC/PHY/work, frees IRQs, disables NAPI, and drains RX rings. Persistent state lives in `xgene_enet_pdata`, rings, hardware descriptors, software counters, MSS refcounts, and extended stats.

Dependencies and integration points: uses platform OF/ACPI match data for X-Gene1/2, PHYLIB and MDIO_XGENE, GPIO descriptors for SFP/rxlos, DMA mapping/coherent allocation, NAPI, ethtool setup, operation tables from GMAC/SGMAC/XGMAC/ring/CLE files, and Kconfig-selected dependencies.

Risks: the data path is complex and hardware-specific. Scatter-gather/TSO mapping has partial failure paths that can leak mappings if later fragment mapping fails. Buffer pool deletion unmaps using `XGENE_ENET_MAX_MTU` while refill maps standard MTU-sized buffers, which deserves DMA API scrutiny. Queue accounting uses wrapping 16-bit levels and must stay consistent with completion descriptor counts. MTU changes close and reopen the device. RX errata intentionally reclassify some hardware errors. Wrong PHY mode or operation-table selection will program the wrong MAC/ring model.

Test signals: multi-mode compile and runtime tests for RGMII, SGMII, and XGMII; multi-queue XGMII RSS; SG and TSO traffic; jumbo frames; pause settings; MTU changes; TX timeout; open/close loops; PHY link toggles; SFP GPIO state changes; DMA mapping fault injection; ingress error injection; and remove/shutdown while interface is up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_main.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_main.h

Purpose: shared header for the original X-Gene Ethernet driver, defining queue limits, ring state, operation tables, private driver state, and common helper prototypes.

Important APIs, types, and functions: constants cover MTU, buffer sizes, queue/ring counts, starting buffer/ring numbers for ports/hardware generations, IRQ name size, and PHY polling intervals. `struct xgene_enet_desc_ring` stores ring identity, head/tail indexes, IRQ/NAPI, coherent descriptors, command addresses, completion SKB arrays, RX SKB/page pools, expanded buffers, and per-ring stats. `struct xgene_mac_ops`, `xgene_port_ops`, `xgene_ring_ops`, and `xgene_cle_ops` abstract MAC variants, port reset/clear/bypass/shutdown, ring setup/clear/commands/length/coalescing, and classifier init. `struct xgene_enet_pdata` is the main persistent context for netdev, resources, rings, queue counts, MMIO bases, ops, link work, MSS slots, delays, MDIO/GPIO state, and pause state.

Control flow, state, and dependencies: included by all original X-Gene implementation files. Runtime behavior is largely selected by assigning operation-table pointers in `xgene_enet_setup_ops`; the rest of the driver calls through those pointers.

Integration points: connects hardware headers, CLE, ring2 definitions, ethtool setup, and extended stats init. Helper `xgene_enet_dst_ring_num` combines resource manager and ring number for hardware queue routing.

Risks: this header defines cross-file ABI. Changing ring/private data layout affects every implementation file. Queue constants and starting ring numbers are hardware contracts. Optional fields such as `page_pool`, `cle_ops`, and `mdio_driver` must be checked by mode-specific code.

Test signals: compile all objects; runtime tests should verify correct operation-table selection, queue counts, ring ID derivation, stats, link polling, and MDIO/GPIO-dependent paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_ring2.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_ring2.c

Purpose: implements X-Gene2-specific ring programming and command semantics for the original driver.

Important APIs, types, and functions: ring setup initializes interrupt line and dequeue interrupt bits for CPU-owned rings, writes coherent queue base and message addressing fields, sets ring type/buffer pool mode, recombination timeout, ring IDs, interrupt mailbox DMA address, descriptor empty markers, command counts with interrupt-clear bits, queue length reads, and PBM coalescing registers. It exports `xgene_ring2_ops` with six ring config registers, ring ID shift 13, setup/clear/command/length/coalescing callbacks.

Control flow, state, and persistence: `xgene_enet_setup_ops` selects `xgene_ring2_ops` for `XGENE_ENET2`. Ring creation allocates an interrupt mailbox for CPU-owned rings when required, and setup writes the mailbox base to `CSR_VMID0_INTR_MBOX`.

Dependencies and integration points: depends on shared ring helpers/constants from `xgene_enet_hw.h`, X-Gene2 constants from `xgene_enet_ring2.h`, and private data MMIO bases from `xgene_enet_main.h`.

Risks: X-Gene2 skips ring ID writes for CPU-owned rings but configures interrupt mailboxes; applying X-Gene1 logic would break interrupts. Command writes combine count and interrupt clear, so signed count handling must remain correct for dequeue notifications.

Test signals: X-Gene2 probe, CPU-owned ring interrupts, TX/RX completion, queue length reads, interrupt coalescing behavior, and ring clear on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_ring2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_ring2.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_ring2.h

Purpose: declares X-Gene2 ring configuration constants and the exported ring operation table.

Important APIs, types, and functions: constants define `X2_NUM_RING_CONFIG`, interrupt mailbox size and CSR offset, interrupt clear bit, X-Gene2-specific ring state fields for message/base address mode, interrupt line, config CRID, threshold, ring type, dequeue interrupt enable, recombination timeout, and queue length field. It declares `xgene_ring2_ops`.

Control flow, state, and dependencies: included by `xgene_enet_main.h` and implemented in `xgene_enet_ring2.c`. It carries no live state.

Integration points: selected by `xgene_enet_setup_ops` for X-Gene2 hardware.

Risks: these bitfields determine interrupt delivery and descriptor addressing. Mismatch with `xgene_enet_ring2.c` or hardware docs will cause silent ring hangs.

Test signals: compile X-Gene2 path; verify interrupt mailbox programming and RX/TX activity under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_ring2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_sgmac.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_sgmac.c

Purpose: implements SGMII MAC/port operations for the original X-Gene driver.

Important APIs, types, and functions: the file provides CSR, clock/reset, ring-interface, diagnostic, and MCX register accessors; ECC init; drop counter reads; ring-interface association; internal MII/TBI reads and writes; SGMAC reset/address/speed/frame-size/autoneg configuration; RX/TX enable/disable; flow-control; CLE bypass; port clear/shutdown; and delayed link-state polling. It exports `xgene_sgmac_ops` and `xgene_sgport_ops`.

Control flow, state, and persistence: selected for `PHY_INTERFACE_MODE_SGMII`. During hardware init the port reset and MAC init configure clocks, ECC, ring association, MAC address, SGMII settings, and autoneg. If no external MDIO driver attaches, delayed work polls internal SGMII link state and updates carrier and MAC speed.

Dependencies and integration points: depends on `xgene_enet_sgmac.h`, shared main private data, ring IDs, CLE bypass path, PHYLIB speed constants, and operation-table calls from `xgene_enet_main.c`.

Risks: internal MII operations are bounded by busy polling and can misread link state if timing changes. Link polling and MAC enable/disable must coordinate with open/close delayed work. CLE bypass must program correct destination and buffer pool IDs.

Test signals: SGMII probe, internal/external PHY modes, autoneg completion, 10/100/1000 speed transitions, pause control, delayed link polling, and traffic after link flap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_sgmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_sgmac.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_sgmac.h

Purpose: defines SGMII/TBI MDIO field helpers, internal PHY addresses, link/autoneg bits, RX gate register, speed enum, and exported SGMAC operation tables.

Important APIs, types, and functions: macros pack PHY/register/control values, extract link speed, identify internal PHY and SGMII control/status/base-page registers, and define `AUTO_NEG_COMPLETE`, `LINK_STATUS`, `LINK_UP`, `MPA_IDLE_WITH_QMI_EMPTY`, and `SGMII_EN`. `enum xgene_phy_speed` represents 10/100/1000. Externs expose `xgene_sgmac_ops` and `xgene_sgport_ops`.

Control flow, state, and dependencies: included by SGMAC implementation and main setup. No live state is stored here.

Integration points: supports SGMII operation-table selection and internal PHY link polling.

Risks: incorrect field packing breaks internal PHY management and link speed interpretation. Changes need hardware validation.

Test signals: internal MDIO reads/writes, SGMII autoneg, link status extraction, and MAC speed programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_sgmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_xgmac.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_xgmac.c

Purpose: implements 10G XGMAC/AXGMAC operations and port control for the original X-Gene driver.

Important APIs, types, and functions: provides direct and indirect CSR/PCS/AXG access, ECC init, drop counter reads, ring-interface association, XGMAC and PCS reset, MAC address programming, MSS register programming for TSO, frame size, link status, pause/flow control, MAC init, RX/TX enable/disable, full reset, XG CLE bypass, clear/shutdown, optional GPIO/SFP readiness lookup, and delayed link-state handling. Exports `xgene_xgmac_ops` and `xgene_xgport_ops`.

Control flow, state, and persistence: selected for XGMII/default high-speed mode. Probe enables TSO/RX checksum and initializes MSS locks. Hardware init configures rings and CLE for RSS, then MAC init programs 10G-specific registers. If no PHY is present, delayed link work checks hardware link and optional SFP GPIO state and updates carrier.

Dependencies and integration points: depends on `xgene_enet_xgmac.h`, resource bases set in main, CLE setup for XGMII, TSO MSS setup from TX path, GPIO descriptors, and ethtool pause/drop-counter callbacks.

Risks: indirect PCS/AXG register access uses polling and can fail silently if status bits change. SFP GPIO readiness can keep carrier down. MSS register refcounts in main must match completions. XG CLE bypass differs from classifier mode and must route to correct rings.

Test signals: 10G link bring-up, SFP ready/not-ready transitions, TSO traffic with multiple MSS values, RSS/CLE operation, pause frames, jumbo frames, reset/shutdown, and link work cancellation during close/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_xgmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_xgmac.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_xgmac.h

Purpose: defines XGMAC/AXGMAC/PCS register offsets, reset/clock bits, pause/CLE/RSIF registers, MSS and link status registers, and exported XGMAC operation tables.

Important APIs, types, and functions: constants cover block offsets for X-Gene2 MAC CSR, AXG MAC/stats/CSR, PCS, XGENET config/reset/clock bits, AXGMAC configuration/address/frame length, RX gate, ECM/ICM drop counters, CLE bypass, link aggregation resume, link status, TSO MSS registers, PCS reset, and RSIF thresholds. Externs expose `xgene_xgmac_ops` and `xgene_xgport_ops`.

Control flow, state, and dependencies: included by `xgene_enet_main.c` and `xgene_enet_xgmac.c`. It carries no live state.

Integration points: main resource mapping uses these offsets to derive MAC/stats/PCS bases for XGMII; XGMAC implementation writes the listed registers during reset/init/link/flow-control paths.

Risks: offset errors affect all 10G operation. The header mixes X-Gene1 and X-Gene2 offsets, so edits must respect hardware generation differences.

Test signals: 10G probe, PCS reset, MAC address programming, link status reads, frame-size changes, pause control, and TSO MSS programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_xgmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/Kconfig

Purpose: defines the Apple Ethernet vendor menu and legacy Apple/Macintosh Ethernet driver symbols.

Important APIs, types, and functions: `NET_VENDOR_APPLE` gates the menu and defaults yes on supported PowerMac/Mac platforms. `MACE` enables Power Mac MACE support and selects `CRC32`; `MACE_AAUI_PORT` chooses AAUI as the default MACE port; `BMAC` enables G3 BMAC support and selects `CRC32`; `MACMACE` enables onboard AMD 79C940 MACE support for Macintosh AV machines and selects `CRC32`.

Control flow, state, and dependencies: Kconfig state controls which object files are built by the Apple Makefile. Runtime state is in the corresponding driver C files, not here. Dependencies restrict options to `PPC_PMAC && PPC32` or `MAC`.

Integration points: sourced by parent Ethernet Kconfig and paired with `apple/Makefile` object gates.

Risks: these are legacy platform-specific options; loosening dependencies can expose drivers to unsupported architectures. Help text/module names must match Makefile outputs.

Test signals: configuration menu visibility on PPC_PMAC/PPC32 and MAC targets; compile each selected symbol as built-in/module with `CRC32` selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/Makefile

Purpose: maps Apple Ethernet Kconfig symbols to their driver object files.

Important APIs, types, and functions: builds `mace.o` for `CONFIG_MACE`, `bmac.o` for `CONFIG_BMAC`, and `macmace.o` for `CONFIG_MACMACE`.

Control flow, state, and dependencies: Kbuild includes objects according to selected config symbols. No runtime state exists in this file.

Integration points: paired with Apple Kconfig module names and the parent Ethernet Makefile.

Risks: symbol/object drift prevents selected legacy drivers from building. Because the file is tiny, accidental unconditional objects are the main build risk.

Test signals: build each Apple Ethernet option as module and built-in; confirm object inclusion matches selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/Makefile -->
