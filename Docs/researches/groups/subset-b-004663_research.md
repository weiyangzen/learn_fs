# Research: subset-b-004663

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_config.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_config.c

## Purpose

`icssg_config.c` is the firmware and shared-memory configuration layer for the TI ICSSG Ethernet driver. It programs MII/MIIG registers, hardware queue descriptors, MSMC buffer pools, VLAN/FDB tables, R30 firmware commands, port speed/duplex state, PVIDs, and management-queue messages used by switch, HSR/PRP offload, and EMAC modes.

## Important APIs, Types, and Functions

Key exported functions are `icssg_config_ipg()`, `icssg_config()`, `icssg_set_port_state()`, `icssg_config_half_duplex()`, `icssg_config_set_speed()`, `icssg_send_fdb_msg()`, `icssg_fdb_add_del()`, `icssg_fdb_lookup()`, `icssg_vtbl_modify()`, `icssg_get_pvid()`, `icssg_set_pvid()`, and `emac_fdb_flow_id_updated()`. Internal helpers initialize MII TX config, MIIG queue descriptors, EMAC versus firmware-offload buffer pools, and R30 command slots.

## Control Flow

`icssg_config()` clears the slice DRAM config region, initializes MIIG queues and shared-memory packet descriptors, selects link defaults, sets interface mode, configures MII/IPG/RGMII, sets PRUSS GPI/XFR/constant-table state, writes RX flow IDs, initializes the proper MSMC buffer layout, and resets R30 command words. Firmware offload paths call `icssg_init_fw_offload_mode()` and use forwarding/local-injection pools; EMAC mode calls `icssg_init_emac_mode()` and disables forwarding pools. FDB operations allocate a firmware management buffer from ICSSG hardware queues, write a `mgmt_cmd`, push it to firmware, poll for a response queue entry, copy `mgmt_cmd_rsp`, and recycle the buffer.

## State and Persistence Behavior

The file writes persistent runtime state into PRUSS DRAM, shared RAM, MSMC RAM, MIIG/MII regmaps, VLAN table entries, PVID words, buffer-pool descriptors, and firmware command queues. It updates `prueth->vlan_tbl`, `prueth->icssg_hwcmdseq`, and shared-memory FDB/VLAN material guarded by `vtbl_lock` or `cmd_lock` where required.

## Dependencies and Integration Points

It depends on register and memory offsets from `icssg_config.h`, `icssg_switch_map.h`, and `icssg_mii_rt.h`; queue primitives from `icssg_queues.c`; classifier helpers; PRUSS remoteproc/pruss config APIs; kernel `regmap`, `iopoll`, CRC/hash helpers, and Ethernet address helpers. `icssg_prueth.c`, `icssg_switchdev.c`, VLAN callbacks, multicast sync, link adjustment, and HSR/switch mode changes call into this file.

## Risks and Edge Cases

MSMC buffer base addresses must be 64 KiB aligned or setup fails. The hardware management command path can block up to 20 seconds waiting for firmware. FDB hashing and VLAN support are limited to firmware assumptions such as 256 effective VLAN IDs in callers and fixed bucket sizing. `icssg_fdb_lookup()` returns `0` both for no membership and some error-like absence cases after a successful command, so callers must handle zero as no entry. R30 commands rely on firmware clearing all command words to `EMAC_NONE`.

## Test Signals

Useful checks include EMAC and switch/HSR open-close cycles, bridge VLAN add/delete, multicast membership add/delete, PVID changes, FDB add/delete/lookup, link speed changes at 10/100/1000, half-duplex-capable DT variants, firmware command timeout injection, and regmap/trace validation of queue, buffer-pool, VLAN, and port-state writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_config.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_config.h

## Purpose

`icssg_config.h` defines the shared firmware configuration contract consumed by ICSSG configuration, main driver, SR1 support, switchdev, and statistics code. It describes packet descriptor sizing, MSMC buffer-pool sizing, management command formats, port-state command IDs, SR1 config layout, FDB/VLAN table formats, and firmware queue IDs.

## Important APIs, Types, and Functions

Important types include `struct icssg_buffer_pool_cfg`, `struct icssg_flow_cfg`, `struct icssg_rxq_ctx`, `struct icssg_r30_cmd`, `struct icssg_sr1_config`, `struct icssg_setclock_desc`, `struct mgmt_cmd`, `struct mgmt_cmd_rsp`, `struct prueth_vlan_tbl`, and `struct prueth_fdb_slot`. Key enums/macros define `enum icssg_port_state_cmd`, `ICSSG_FW_MGMT_*`, SR1 RX/management flow constants, hardware queue IDs, FDB membership bits, buffer pool totals for EMAC and switch mode, and IETF preemption verification states.

## Control Flow

The header has no executable flow. Its definitions shape `icssg_config.c` buffer setup and R30 command paths, `icssg_prueth_sr1.c` SR1 load-time config and management commands, `icssg_prueth.c` timestamp setclock descriptors, and switchdev/FDB code that passes membership flags to firmware.

## State and Persistence Behavior

Most structures are `__packed` and map directly to PRUSS DRAM/shared RAM or DMA-visible firmware command buffers. Any field layout change is an ABI change with ICSSG firmware. Buffer-size macros determine the SRAM allocation size in probe and the per-slice pool offsets written during interface start.

## Dependencies and Integration Points

The header relies on Linux endian/types helpers and on `SIZE_OF_FDB`/`NUMBER_OF_FDB_BUCKET_ENTRIES` from `icssg_switch_map.h` through include ordering in `icssg_prueth.h`. It is included by `icssg_prueth.h`, which makes these constants part of the broader driver internal API.

## Risks and Edge Cases

The file encodes firmware assumptions that are easy to break silently: SR1 command bitfields, queue IDs, FDB valid/membership bits, packed command response layout, and MSMC pool sizes. Comments note firmware-specific limitations such as only 4 real QoS levels and SR1 management queues. The `PRUETH_SWITCH_FDB_MASK` computation must stay consistent with firmware FDB bucket sizing and ageing logic.

## Test Signals

Build coverage across SR1 and non-SR1 platform drivers is the main compile-time signal. Runtime validation should exercise all modes that use the packed layouts: SR1 command responses, SR2 FDB management commands, VLAN table updates, PVID programming, and SRAM allocation sizing on banked and non-banked MSMC platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_ethtool.c

## Purpose

`icssg_ethtool.c` exposes ICSSG netdev controls and counters through `struct ethtool_ops`. It bridges standard ethtool requests to PHY settings, ICSSG hardware stats, PTP timestamp capability reporting, TX/RX interrupt coalescing state, channel count selection, EEE, and RMON histograms.

## Important APIs, Types, and Functions

The exported object is `icssg_ethtool_ops`. Local callbacks include driver info, message level get/set, link ksettings, EEE get/set, autonegotiation reset, stats string/count/data export, timestamp info, channel get/set, global and per-queue coalescing get/set, and RMON stats. It consumes `icssg_all_miig_stats`, `icssg_all_pa_stats`, `emac_update_hardware_stats()`, and `emac_get_stat_by_name()`.

## Control Flow

Stats reads first refresh hardware counters with `emac_update_hardware_stats()`, then copy non-standard MIIG counters and optional PA counters into the ethtool buffer. Channel changes are allowed only while the interface is down; SR1 reports one user-visible TX queue while internally reserving an extra management TX channel. Coalescing setters clamp nonzero values below `ICSSG_MIN_COALESCE_USECS` and store nanosecond delays in `emac->rx_pace_timeout_ns` or `tx_chn->tx_pace_timeout_ns`.

## State and Persistence Behavior

This file mutates `emac->msg_enable`, `emac->tx_ch_num`, RX coalescing timeout, and per-TX-channel coalescing timeout. It reads and accumulates stats through `icssg_stats.c` and reports PTP clock index from `emac->iep`. State persists in the in-memory driver structures until device close/reprobe.

## Dependencies and Integration Points

It integrates with PHY library ethtool helpers, ICSSG stats tables, netdev private `struct prueth_emac`, `icss_iep_get_ptp_clock_idx()`, and kernel ethtool APIs including `kernel_ethtool_ts_info`, `ethtool_channels`, `ethtool_coalesce`, and RMON histogram ranges.

## Risks and Edge Cases

`emac_get_stat_by_name()` returns an `int` even though backing counters are `u64`, so RMON values can truncate if counters exceed `INT_MAX`. Per-queue coalescing validates against `PRUETH_MAX_TX_QUEUES`, not current `emac->tx_ch_num`, so inactive queues may be writable. Channel count changes do not validate `ch->tx_count` against zero or max directly in the setter, relying on ethtool core constraints and reported limits.

## Test Signals

Run `ethtool -i`, `-S`, `-c`, `-C`, `-l`, `-L`, `--show-eee`, `--set-eee`, and timestamp info queries on SR1 and SR2 devices. Validate channel changes while down versus `-EBUSY` while up, PA-stats-present and absent paths, coalescing clamp messages, and RMON counter consistency under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_mii_cfg.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_mii_cfg.c

## Purpose

`icssg_mii_cfg.c` is a small register helper layer for ICSSG MII-RT and MII-G-RT configuration. It updates inter-packet gap, MTU frame bounds, RGMII speed/duplex/in-band bits, interface mode selection, and reads RGMII status bitfields.

## Important APIs, Types, and Functions

Exported functions are `icssg_mii_update_ipg()`, `icssg_mii_update_mtu()`, `icssg_update_rgmii_cfg()`, `icssg_miig_set_interface_mode()`, `icssg_rgmii_cfg_get_bitfield()`, `icssg_rgmii_get_speed()`, and `icssg_rgmii_get_fullduplex()`.

## Control Flow

Callers pass a regmap, slice/MII number, and link parameters. IPG writes go to `PRUSS_MII_RT_TX_IPG0/1`, with MII1 preserving TX_IPG0 around the write. MTU updates add Ethernet header and FCS before programming RX frame max fields. RGMII config computes slice-specific masks and sets gigabit, in-band 10M RGMII, and full-duplex bits. Interface mode writes MII or RGMII mode fields in `ICSSG_CFG_OFFSET`.

## State and Persistence Behavior

All state is hardware register state in MII-RT or MII-G-RT regmaps. The helpers do not store software state; they reflect values from `struct prueth_emac` and are called during configuration and link adjustment.

## Dependencies and Integration Points

It depends on `icssg_mii_rt.h` register definitions, PHY interface helpers, `prueth_emac_slice()`, `regmap`, and Ethernet constants. Main users are `icssg_config.c`, `icssg_prueth.c`, `icssg_prueth_sr1.c`, and SR1 speed command construction.

## Risks and Edge Cases

The MII1 IPG path temporarily reads and rewrites TX_IPG0, implying hardware side effects or ordering constraints that should not be simplified without datasheet confirmation. MTU programming assumes callers already validate netdev MTU limits. RGMII in-band enable is only set for 10M RGMII, matching driver workaround behavior.

## Test Signals

Validate register writes during link transitions for MII and RGMII, 10/100/1000 speeds, full/half duplex, and MTU changes. SR1 tests should confirm speed/duplex readback used for firmware commands matches `RGMII_CFG` fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_mii_cfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_mii_rt.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_mii_rt.h

## Purpose

`icssg_mii_rt.h` defines MII-RT and MII-G-RT register offsets, bit masks, speed encodings, interface mode encodings, and helper prototypes for ICSSG MII/RGMII programming.

## Important APIs, Types, and Functions

The file defines `PRUSS_MII_RT_*` offsets for RX/TX config, CRC, IPG, parser status, frame size, preamble count, and error registers; `ICSSG_CFG_*` and `RGMII_CFG_*` masks; `enum mii_mode`; `ICSS_MII0/ICSS_MII1`; and prototypes implemented in `icssg_mii_cfg.c`.

## Control Flow

There is no runtime flow. These definitions are consumed by configuration and link-adjustment code to build `regmap_update_bits()` operations and decode RGMII speed/full-duplex state.

## State and Persistence Behavior

The constants describe persistent hardware register state, not software state. Values written through these masks remain in the ICSSG hardware until reconfigured, reset, or power-cycled.

## Dependencies and Integration Points

The header includes Linux Ethernet and PHY definitions and forward declares `struct regmap` and `struct prueth_emac`. It is included by MII config, general config, SR1, and main PRU Ethernet driver files.

## Risks and Edge Cases

Bit definitions are hardware ABI. Incorrect masks or shifts can break link mode, frame sizing, TX mux selection, and speed/duplex reporting. `PRUSS_MII_RT_RX_FRMS_MAX_FRM_LRE` references `ICSS_LRE_TAG_RCT_SIZE`, so include ordering must provide that macro where LRE max-frame support is used.

## Test Signals

Build coverage catches missing macro dependencies. Runtime signals include successful MII/RGMII link up at supported speeds, correct MTU enforcement, no RX frame-size errors after MTU changes, and expected speed/full-duplex readback in SR1 speed command paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_mii_rt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_prueth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_prueth.c

## Purpose

`icssg_prueth.c` is the main SR2/non-SR1 platform driver for TI PRUSS ICSSG Ethernet. It owns probe/remove, netdev creation, PHY connection, PRU/RTU/TX_PRU firmware boot, common start/stop, link adjustment, PTP clock integration, TX timestamp handling, DMA queue bring-up/teardown, multicast/VLAN/FDB synchronization, bridge switchdev mode transitions, HSR/PRP offload mode transitions, XDP/AF_XDP hooks, and netdevice/switchdev notifier registration.

## Important APIs, Types, and Functions

The file defines `emac_netdev_ops`, platform `prueth_driver`, platform data for AM654 and AM64x, `prueth_iep_clockops`, `prueth_dev_check()`, and `prueth_xsk_wakeup()`. Important internal routines include `prueth_emac_common_start/stop()`, `prueth_emac_start/stop()`, `emac_adjust_link()`, `emac_ndo_open/stop()`, multicast and HSR FDB helpers, VLAN add/delete, `emac_ndo_bpf()`, `emac_xdp_xmit()`, `prueth_netdev_init()`, bridge/HSR link/unlink handlers, notifier callbacks, firmware-name generation, `prueth_probe()`, and `prueth_remove()`.

## Control Flow

Probe parses `ethernet-ports`, gets regmaps, PRUSS cores, shared RAM, SRAM pool, IEPs, firmware names, and creates/registers netdevs. `ndo_open` initializes TX/RX DMA channels and NAPI, requests RX and TX timestamp IRQs, starts common firmware on the first active port, writes RX flow IDs, enables queues, starts PHY, and starts stats work. Common start clears SRAM/SHRAM, configures classifier defaults and HSR filtering, initializes EMAC or offload mode, configures each slice, boots firmwares, and initializes IEP. Link changes update duplex/speed, IPG, RGMII config, firmware speed byte, and port state. Bridge or HSR upper-device events restart firmware into switch/HSR/PRP firmware mode once both physical ports participate.

## State and Persistence Behavior

Persistent runtime state spans `struct prueth` mode flags (`is_switch_mode`, `is_hsr_offload_mode`), bridge/HSR membership bitmaps, `default_vlan`, firmware name arrays, registered netdevs, PRUSS memory regions, IEP handles, `emacs_initialized`, multicast shadow lists, XDP/XSK pointers, DMA channels, NAPI, TX timestamp skb slots, coalescing timers, VLAN/PVID/FDB firmware state, and shared-memory time sync descriptors. Mode changes persist until bridge/HSR unlink or device removal.

## Dependencies and Integration Points

The file integrates with remoteproc/pruss APIs, syscon regmaps, genalloc SRAM, K3 UDMA glue, CPPI descriptor pools, PHY/MDIO, netdevice ops, switchdev, bridge, HSR/PRP helpers, XDP/AF_XDP, page-pool, PTP/IEP, classifier helpers, common TX/RX helpers from `icssg_common.c`, config helpers, stats work, and firmware files named from DT.

## Risks and Edge Cases

Mode changes restart both ports and require both netdevs to exist; failures can leave devices detached or firmware stopped until recovery. HSR multicast membership has complex refcount/synced handling and must avoid sleeping under address locks. XSK enable/disable tears RX down while running and must restore port state on every failure path. TX timestamp cookies are bounded by `PRUETH_MAX_TX_TS_REQUESTS`; invalid firmware cookies produce errors and may leak pending state. Firmware-name replacement silently falls back to the original string if replacement/allocation fails. Probe error unwind spans many resources and needs platform-specific coverage.

## Test Signals

Use dual-port and single-port probe/remove, repeated `ip link set up/down`, PHY speed changes, PTP get/set/perout and TX/RX timestamp tests, bridge enslave/leave with VLAN/MDB/FDB operations, HSR and PRP offload attach/detach, multicast sync on physical/VLAN/HSR devices, XDP attach/detach, AF_XDP bind/unbind and wakeup, fault injection in DMA/channel/IRQ/firmware boot paths, and traffic under mode restarts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_prueth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_prueth.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_prueth.h

## Purpose

`icssg_prueth.h` is the central internal header for the ICSSG Ethernet driver. It defines port/MAC IDs, queue/channel state, TX software descriptor metadata, per-port EMAC state, top-level PRUETH device state, timestamp response layouts, constants for MTU, firmware commands, VLAN defaults, XDP results, coalescing, and prototypes shared across ICSSG source files.

## Important APIs, Types, and Functions

Core types are `struct prueth_tx_chn`, `struct prueth_rx_chn`, `struct prueth_swdata`, `struct prueth_emac`, `struct prueth_pdata`, `struct icssg_firmwares`, `struct prueth`, `struct emac_tx_ts_response`, and `struct emac_tx_ts_response_sr1`. Important helpers include `prueth_emac_slice()`, `icssg_read_time()`, prototypes for classifier/config/queue/FDB/stats/common RX/TX/timestamp/core-management helpers, and `prueth_xdp_is_enabled()`.

## Control Flow

The header has no executable lifecycle beyond inline helpers. `prueth_emac_slice()` maps MII0/MII1 port IDs to slice indexes and returns `-EINVAL` for invalid ports. `icssg_read_time()` performs a stable high/low 64-bit read by rechecking the high word.

## State and Persistence Behavior

`struct prueth` persists device-wide ownership of PRUSS cores, shared SRAM, SRAM pool, regmaps, IEPs, mode flags, firmware names, bridge/HSR state, VLAN table lock, and stats lock. `struct prueth_emac` persists per-netdev PHY/link state, DMA/NAPI/channel state, timestamp slots, command completion, RX mode work, stats arrays, VLAN multicast lists, XDP program and AF_XDP queue registration.

## Dependencies and Integration Points

The header includes Linux networking, PHY, remoteproc, PRUSS, PTP, DMA, page-pool, XDP, AF_XDP, `icssg_config.h`, `icss_iep.h`, and `icssg_switch_map.h`. It is included by nearly every ICSSG C file and forms the private cross-file ABI.

## Risks and Edge Cases

Many fields have implicit concurrency rules enforced outside the type definitions: `cmd_lock`, `stats_lock`, `vtbl_lock`, NAPI state, workqueue cancellation, and XDP pointer updates. `PRUETH_MAX_TX_QUEUES` is 4, while SR1 reserves a management channel and presents fewer queues to users. Packed TX timestamp response layouts differ between SR1 and SR2. Changes to `struct prueth_swdata` must remain within `PRUETH_NAV_SW_DATA_SIZE`, enforced by a build bug in the main driver.

## Test Signals

Compile all ICSSG objects together with SR1/SR2 platform variants, XDP sockets, HSR, PTP, and switchdev enabled. Runtime tests should stress concurrent link changes, open/close, timestamping, stats reads, XDP attach, AF_XDP pool changes, bridge and HSR mode transitions, and DMA teardown to validate the state model described by these structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_prueth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_prueth_sr1.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_prueth_sr1.c

## Purpose

`icssg_prueth_sr1.c` is the AM654 SR1.0-specific ICSSG Ethernet platform driver. It reuses common ICSSG RX/TX/config/stat helpers but provides different firmware boot, shared-memory load-time config, command transport, management RX flows, timestamp handling, receive-mode programming, probe/remove, and netdev lifecycle for SR1 hardware.

## Important APIs, Types, and Functions

Key routines include `icssg_config_sr1()`, `emac_send_command_sr1()`, `icssg_config_set_speed_sr1()`, `emac_adjust_link_sr1()`, SR1 `emac_phy_connect()`, `prueth_process_rx_mgm()`, `prueth_tx_ts_sr1()`, management IRQ threads, SR1 `prueth_emac_start/stop()`, SR1 `emac_ndo_open/stop()`, `emac_ndo_set_rx_mode_sr1()`, SR1 `prueth_netdev_init()`, `prueth_probe()`, and `prueth_remove()`. It defines fixed SR1 firmware names and platform match data for `"ti,am654-sr1-icssg-prueth"`.

## Control Flow

Probe parses available ports, gets MII regmaps, PRUSS cores, shared RAM, an SRAM pool sized by `MSMC_RAM_SIZE_SR1`, both IEP instances, initializes IEPs, creates netdevs, registers them, and connects PHYs. Open clears shared memory on first port, sets classifier MAC/default state, creates TX, RX data, and RX management channels, requests IRQs for data RX, management responses, and management timestamps, boots PRU/RTU firmware for that slice, prepares RX buffers, enables DMA channels and NAPI, starts PHY, and queues stats work. Commands are sent as CPPI command packets on the highest-priority TX channel and completed by management response IRQs.

## State and Persistence Behavior

SR1 stores `struct icssg_sr1_config` in shared RAM per slice, including MSMC base address, RX flow IDs, management flow ID, buffer sizes, and random seed. It keeps an extra RX management channel and an extra TX management channel in `struct prueth_emac`. Unlike SR2, each port starts/stops its own PRU/RTU pair and there is no TX_PRU firmware in the SR1 firmware table.

## Dependencies and Integration Points

It depends on common `icssg_prueth.h` state, MII helpers, classifier helpers, K3 UDMA glue, CPPI descriptor pools, page pool helpers through common RX code, PHY/MDIO, remoteproc/pruss, genalloc SRAM, and IEP APIs. It uses shared ethtool ops and common TX/RX/stat/timestamp netdev callbacks where compatible.

## Risks and Edge Cases

`emac_send_command_sr1()` returns the raw `wait_for_completion_timeout()` value on success rather than normalizing to zero, which callers treat mostly as truthy/nonzero only in stop paths. `prueth_process_rx_mgm()` pushes replacement buffers through `emac->rx_chns` instead of `rx_mgm_chn`, which is worth checking against common helper expectations. Probe connects PHYs without checking `emac_phy_connect()` return in the success path. SR1 intentionally disables multi-TX-channel user exposure due to timeouts.

## Test Signals

Validate SR1 probe/remove, both-port and one-port configurations, command response IRQ completion for shutdown and speed/duplex commands, management timestamp IRQs, open/close loops, PHY speed transitions, multicast/promiscuous/allmulti receive-mode changes, TX queue timeout absence with one visible TX queue, and error unwinds for management IRQ/channel setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_prueth_sr1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_queues.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_queues.c

## Purpose

`icssg_queues.c` provides minimal helper functions for ICSSG firmware/hardware queues backed by MIIG registers. These queues are used for descriptor pools, management commands, command responses, and timestamp responses.

## Important APIs, Types, and Functions

Exported functions are `icssg_queue_pop()`, `icssg_queue_push()`, and `icssg_queue_level()`. Local constants mirror queue count, queue data, peek, count, and reset register offsets.

## Control Flow

`icssg_queue_pop()` validates the queue index, reads queue count, returns `-EINVAL` if empty, then reads the queue data register. `icssg_queue_push()` validates the index and writes an address to the queue data register. `icssg_queue_level()` returns the count register or zero for an invalid queue.

## State and Persistence Behavior

The helpers mutate only hardware queue register state through `prueth->miig_rt`. They do not keep software shadow state, so correctness depends on firmware and callers preserving queue ownership.

## Dependencies and Integration Points

It depends on `regmap` and `struct prueth`. `icssg_config.c` uses it for FDB management messages and timestamp response buffer recycling, and queue initialization in config uses matching offsets.

## Risks and Edge Cases

Empty queue and invalid queue both return `-EINVAL` from `icssg_queue_pop()`, so callers cannot distinguish absence of data from invalid input. There is no locking; callers must ensure firmware queue ownership and sequencing. `queue` is `int` in push/level but only upper-bound checked, so negative queue numbers could compute invalid offsets if ever passed.

## Test Signals

Exercise management command send/response, timestamp queue consumption, invalid queue calls in debug/fault tests, and queue depth observations under firmware traffic. Static analysis should flag negative queue handling if external callers are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_queues.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_stats.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_stats.c

## Purpose

`icssg_stats.c` accumulates ICSSG hardware counters into per-port software counters and provides periodic refresh and name-based lookup for ethtool/RMON/stat64 consumers.

## Important APIs, Types, and Functions

Exported functions are `emac_update_hardware_stats()`, `icssg_stats_work_handler()`, and `emac_get_stat_by_name()`. It uses `stats_base[]` for per-slice MIIG counter base offsets and stat metadata from `icssg_stats.h`.

## Control Flow

`emac_update_hardware_stats()` locks `prueth->stats_lock`, walks MIIG stats, reads each hardware counter, writes the same value back to clear it, accumulates into `emac->stats`, adjusts TX byte count by subtracting 8 bytes per packet, then optionally reads PA stats into `emac->pa_stats`. `icssg_stats_work_handler()` refreshes and reschedules itself based on link speed. `emac_get_stat_by_name()` linearly searches MIIG then PA stat tables.

## State and Persistence Behavior

The file persists cumulative counters in `emac->stats[]` and `emac->pa_stats[]`. It clears MIIG hardware counters on each read-by-writeback. PA stat reads are accumulated without an explicit clear in this file. Periodic work persists while the netdev is open and is canceled on stop.

## Dependencies and Integration Points

It depends on `icssg_prueth.h`, `icssg_stats.h`, `regmap`, and spinlocks. Ettool stats, RMON stats, and netdev stats paths consume the accumulated arrays.

## Risks and Edge Cases

In MII mode, TX counters are read from the opposite slice, but `base` is not reset inside each loop iteration after being changed; subsequent non-TX counters could read the swapped base depending on ordering. `emac_get_stat_by_name()` returns `int` from `u64` counters, risking truncation. The work reschedule divides by `emac->speed`, so speed must be a valid nonzero link speed before work runs.

## Test Signals

Generate RX/TX traffic in MII and RGMII modes, compare ethtool stats with packet counters, validate TX byte adjustment, run with and without PA stats regmap, stress periodic stats at 10/100/1000 speeds, and use RMON stat lookup after high-volume traffic to catch truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_stats.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_stats.h

## Purpose

`icssg_stats.h` defines the ICSSG MIIG and PA statistic register layouts and metadata tables used by stats refresh and ethtool export.

## Important APIs, Types, and Functions

Important definitions are `STATS_TIME_LIMIT_1G_MS`, `struct miig_stats_regs`, `struct icssg_miig_stats`, `icssg_all_miig_stats[]`, `struct icssg_pa_stats`, and `icssg_all_pa_stats[]`. Macros `ICSSG_MIIG_STATS()` and `ICSSG_PA_STATS()` build metadata entries with names, offsets, and standard-stat flags.

## Control Flow

There is no executable flow. The ordered arrays drive loops in `icssg_stats.c` and ethtool string/count/data callbacks in `icssg_ethtool.c`.

## State and Persistence Behavior

The header describes hardware counter offsets and which counters are considered standard versus ethtool-private. The arrays are static const metadata and do not hold runtime state.

## Dependencies and Integration Points

It includes `icssg_prueth.h`, which supplies Ethernet string lengths, stat count constants, and PA stat offsets through `icssg_switch_map.h`. It is consumed by `icssg_stats.c` and `icssg_ethtool.c`.

## Risks and Edge Cases

Array sizes must remain consistent with `ICSSG_NUM_MIIG_STATS`, `ICSSG_NUM_PA_STATS`, `ICSSG_NUM_STANDARD_STATS`, and `ICSSG_NUM_ETHTOOL_STATS` from `icssg_prueth.h`. Offsets are derived with `offsetof(struct miig_stats_regs, field)`, so changing struct order changes the hardware ABI assumptions.

## Test Signals

Compile-time checks should compare array lengths against constants if added. Runtime validation should compare ethtool string count with returned data count, check all named RMON stats exist, and verify optional PA stats alter ethtool stat count as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_switch_map.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_switch_map.h

## Purpose

`icssg_switch_map.h` is the firmware shared-memory map for ICSSG switch/EMAC features. It names offsets for FDB/VLAN configuration, packet descriptor memory, time sync descriptors, TAS/preemption controls, flow IDs, queue mappings, link speed, buffer pools, R30 commands, host RX queue contexts, FDB command buffer, half-duplex seed, and PA statistics.

## Important APIs, Types, and Functions

The file defines constants only. Major groups are FDB sizing and firmware speed codes, default VLAN offsets for host/P1/P2, VLAN table offset, descriptor-memory offsets, time sync offsets, TAS offsets, queue and priority mapping offsets, preemption offsets, `MGR_R30_CMD_OFFSET`, `BUFFER_POOL_0_ADDR_OFFSET`, host RX queue context offsets, `FDB_CMD_BUFFER`, `HD_RAND_SEED_OFFSET`, and `FW_*` PA stat offsets.

## Control Flow

There is no control flow. These offsets are used by config, main driver, stats, timestamp, PVID, FDB, and link-adjustment code when reading or writing shared RAM and PA stat regmaps.

## State and Persistence Behavior

The constants describe persistent firmware-visible memory layout. Writes to these offsets configure firmware behavior and remain active until the shared memory is cleared, firmware restarts, or the device resets.

## Dependencies and Integration Points

Included by `icssg_prueth.h` and `icssg_config.c`, this header is a shared ABI between Linux driver and ICSSG firmware. `icssg_stats.h` uses PA stat offsets from this map, and PTP/IEP code uses the time sync offsets.

## Risks and Edge Cases

Any offset drift from firmware breaks behavior without type checking. FDB bucket size comments explicitly tie constants to ageing calculation. Several features such as TAS and preemption have offsets even if not fully managed by this subset, so future feature work must preserve existing layout.

## Test Signals

Regression tests should validate PVID/VLAN table writes, FDB command buffer lookups, firmware speed updates, PTP settime/perout, PA stat reads, R30 port-state commands, and buffer-pool initialization after firmware updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_switch_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_switchdev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_switchdev.c

## Purpose

`icssg_switchdev.c` implements Linux switchdev notifier handling for ICSSG switch mode. It translates bridge STP state, bridge port flags, FDB events, VLAN objects, and MDB objects into ICSSG firmware port-state, VLAN table, PVID, and FDB updates.

## Important APIs, Types, and Functions

Exported functions are `prueth_switchdev_register_notifiers()` and `prueth_switchdev_unregister_notifiers()`. Important local pieces include `struct prueth_switchdev_event_work`, `prueth_switchdev_attr_set()`, STP and bridge flag helpers, `prueth_switchdev_event()`, async `prueth_switchdev_event_work()`, VLAN add/delete helpers, MDB add/delete helpers, object add/delete callbacks, and blocking notifier handling.

## Control Flow

Registration installs one atomic switchdev notifier and one blocking notifier. Attribute events may be handled directly through `switchdev_handle_port_attr_set()`. FDB add/delete events allocate work, copy the FDB address, hold the netdev, and process under RTNL in `system_long_wq`; user-added FDB entries matching the port MAC are programmed via `icssg_fdb_add_del()` and add events notify `SWITCHDEV_FDB_OFFLOADED`. Blocking object events synchronously dispatch VLAN and MDB add/delete to firmware table helpers.

## State and Persistence Behavior

The file mutates firmware port state, VLAN membership/untag masks, PVID values, and FDB/MDB entries. It does not own long-lived state except notifier blocks stored in `struct prueth` and temporary work items.

## Dependencies and Integration Points

It depends on Linux switchdev, bridge flags/VLAN/MDB objects, netdevice helpers, workqueues, `prueth_dev_check()` from the main driver, and config helpers `icssg_set_port_state()`, `icssg_vtbl_modify()`, `icssg_set_pvid()`, `icssg_get_pvid()`, `icssg_fdb_add_del()`, and `icssg_fdb_lookup()`.

## Risks and Edge Cases

`prueth_switchdev_attr_br_flags_set()` checks `mask` rather than `val`, so multicast flooding enable/disable semantics should be verified against intended bridge flag handling. FDB add/delete filters to entries equal to `emac->mac_addr`, which may ignore learned/static entries for other MACs depending on switchdev expectations. VLAN IDs above `0xff` are ignored because firmware paths support only 256 VLAN IDs. Async FDB work must balance `dev_hold()`/`dev_put()` and free copied addresses on all paths.

## Test Signals

Bridge tests should cover STP disabled/blocking/listening/forwarding states, multicast flood flag changes, VLAN add/delete with PVID and untagged flags on bridge and port devices, MDB host/port add/delete, static FDB add/delete, switchdev offload notifications, and notifier unregister during device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_switchdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_switchdev.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_switchdev.h

## Purpose

`icssg_switchdev.h` declares the private switchdev integration API for the ICSSG driver.

## Important APIs, Types, and Functions

It declares `prueth_switchdev_register_notifiers()`, `prueth_switchdev_unregister_notifiers()`, and `prueth_dev_check()`, and includes `icssg_prueth.h` for `struct prueth` and `struct net_device` visibility.

## Control Flow

There is no executable flow. The main driver calls the register/unregister helpers during probe/remove when switch mode is supported, while switchdev code calls `prueth_dev_check()` to filter events to running ICSSG switch-mode netdevs.

## State and Persistence Behavior

The header owns no state. Its declared functions manage notifier block state embedded in `struct prueth` and query netdev state in the main driver.

## Dependencies and Integration Points

It connects `icssg_prueth.c` and `icssg_switchdev.c` without exposing switchdev internals to other files.

## Risks and Edge Cases

Because `prueth_dev_check()` is declared here but implemented in the main driver, SR1 builds and non-switch configurations must continue to compile/link with the expected object set. Any signature change affects switchdev notifier registration and event filtering.

## Test Signals

Build the driver with switchdev support and validate probe/remove notifier registration. Runtime bridge enslave/leave tests confirm `prueth_dev_check()` admits only running ICSSG devices in switch mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_switchdev.h -->
