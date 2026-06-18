# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_pcol.h lines 5381-10729

## Chunk Scope

This chunk is a generated MCDI protocol-definition range for the Solarflare/Xilinx
SFC network driver. It does not contain executable C functions. Instead, it
defines firmware command IDs, privilege categories, request/response byte
layouts, field offsets, bit positions, variable-length array sizing macros, and
enumerated values used by host driver code when building Management Controller
Diagnostic Interface messages.

The range starts in the extended `MC_CMD_ETH_TECH` values for 50G/100G/200G/400G
media technologies, then covers unified link and MAC control, legacy and
descriptor-based statistics, Wake-on-LAN filters, NVRAM/flash update commands,
MC reboot, static and dynamic sensor queries, PHY/media/module access, network
port handle enumeration/events, and ends in the large `NVRAM_PARTITION_TYPE`
namespace.

## Purpose and Responsibilities

- Publish the wire ABI between the Linux SFC driver and MC/NMC firmware for
  port, link, MAC, module, sensor, statistics, WoL, and NVRAM operations.
- Provide stable offsets and lengths consumed by `MCDI_DECLARE_BUF`,
  `MCDI_SET_*`, `MCDI_*`, `MCDI_ARRAY_*`, and `MCDI_FIELD` helpers in
  `mcdi.h`.
- Preserve compatibility across protocol versions by defining V1/V2/V3 request
  and response layouts side by side, such as `GET_LINK_OUT_V2`,
  `SET_LINK_IN_V3`, `SET_MAC_V3_IN`, `NVRAM_INFO_V2_OUT`,
  `NVRAM_UPDATE_FINISH_V3_OUT`, and `GET_FIXED_PORT_PROPERTIES_OUT_V2`.
- Define state and capability encodings for link negotiation, FEC, pause,
  loopback, MAC configuration, sensors, statistics descriptors, NVRAM
  partitions, secure update verification results, and port/module events.

## Important APIs, Types, and Constants

- Link technology and link status:
  `MC_CMD_ETH_TECH_*` covers modern Ethernet technologies up to 400G plus
  invalid/automatic sentinels. `MC_CMD_LINK_STATUS_FLAGS` reports detailed
  link failure causes across PMD/MDI, PMA, PCS, FEC, autonegotiation, and link
  training. `MC_CMD_ETH_AN_FIELDS` packs advertised/supported/link-partner
  technology, FEC, requested FEC, and pause masks.
- Unified link control:
  `MC_CMD_LINK_CTRL` and `MC_CMD_LINK_STATE` operate on explicit port handles.
  `LINK_CTRL_IN` carries control flags, advertised technology and pause
  abilities, FEC mode, forced link technology, module-change sequence number,
  and V2 loopback mode. `LINK_STATE_OUT`, V2, and V3 report configured
  technology, FEC, pause, loopback, advertised/link-partner/supported
  abilities, control flags, link/module sequence numbers, local AN support,
  link speed, and duplex.
- Legacy link and MAC configuration:
  `MC_CMD_GET_LINK`, `MC_CMD_SET_LINK`, `MC_CMD_SET_ID_LED`, and
  `MC_CMD_SET_MAC` define the established driver-facing commands used by much
  of the existing SFC code. They carry capability masks, loopback mode/speed,
  module sequence validation, MAC MTU, MAC address, unicast/broadcast reject
  bits, flow control, include-FCS flags, and selective configuration control
  bits.
- Statistics:
  `MC_CMD_PHY_STATS` provides fixed 32-bit PHY statistic indexes.
  `MC_CMD_MAC_STATS` provides legacy fixed 64-bit MAC counter indexes,
  including generation markers, TX/RX counters, PM/RXDP counters, FEC counters,
  CTPIO counters, and later V4/V5 extensions. Newer
  `MC_CMD_STAT_ID`, `MC_CMD_STAT_DESC`, `MC_CMD_MAC_STATISTICS_DESCRIPTOR`,
  `MC_CMD_MAC_STATISTICS`, and `MC_CMD_GET_NETPORT_STATISTICS` describe and
  retrieve a runtime descriptor-defined statistics buffer for a port handle.
- Wake-on-LAN:
  `MC_CMD_WOL_FILTER_SET`, `REMOVE`, and `RESET` define simple/structured WoL
  filters for magic packet, Windows magic packet, IPv4/IPv6 SYN, bitmap, and
  link-up/link-down wake conditions. `WOL_FILTER_SET_OUT` returns a firmware
  filter ID used for later removal.
- NVRAM and flash:
  `MC_CMD_NVRAM_TYPES`, `INFO`, `PARTITIONS`, and `METADATA` enumerate
  available virtual partitions and expose size, erase size, write size,
  protection, TLV, read-only/write-only, A/B, version, subtype, and description
  metadata. `MC_CMD_NVRAM_UPDATE_START`, `READ`, `WRITE`, `ERASE`, and
  `UPDATE_FINISH` form the update transaction API. `NVRAM_UPDATE_FINISH_V2_OUT`
  and V3 report secure verification status and required reboot/power actions.
  `MC_CMD_NVRAM_TEST` reports partition validity. `NVRAM_PARTITION_TYPE`
  defines concrete flash partition IDs for MC/NMC firmware, expansion ROM,
  static/dynamic config, logs, dumps, licenses, PHY, FPGA, MUM/SUC, UEFI,
  bundle update artifacts, manufacturing/deployment data, FRU information, and
  recovery partition maps.
- MC reboot and workarounds:
  `MC_CMD_REBOOT` supports reboot after assertion and is marked
  `SRIOV_CTG_ADMIN_TSA_UNBOUND`. `MC_CMD_WORKAROUND` toggles firmware
  workarounds for named hardware/firmware bugs and has an extended output for
  bug 26807 indicating whether an FLR was performed.
- Sensors:
  `MC_CMD_SENSOR_INFO` and `MC_CMD_READ_SENSORS` define the older paged sensor
  table and DMA reading ABI. `MC_CMD_SENSOR_INFO_ENTRY_TYPEDEF` stores warning
  and fatal limit ranges; `MC_CMD_SENSOR_VALUE_ENTRY_TYPEDEF` stores value and
  state. `MC_CMD_DYNAMIC_SENSORS_LIMITS`, `DESCRIPTION`, `READING`,
  `DYNAMIC_SENSORS_LIST`, `DYNAMIC_SENSORS_GET_DESCRIPTIONS`, and
  `DYNAMIC_SENSORS_GET_READINGS` define the newer handle/generation-count
  sensor model used by dynamic platforms.
- PHY, media, modules, and ports:
  `MC_CMD_GET_PHY_STATE` reports low-power and power-off PHY state.
  `MC_CMD_GET_PHY_MEDIA_INFO` reads raw media pages/banks for SFP/QSFP/DSFP.
  `MC_CMD_GET_TRANSCEIVER_PROPERTIES` exposes decoded module technology, FEC,
  medium/subtype, vendor, part number, serial number, and module-change
  sequence. `MC_CMD_GET_MODULE_DATA` returns raw module EEPROM data with bank,
  page, offset, length, and V2-aligned module address fields.
  `MC_CMD_GET_ASSIGNED_PORT_HANDLE`, `NET_PORT_HANDLE_DESC`, and
  `MC_CMD_ENUM_PORTS` introduce explicit network-port handles with physical,
  virtual, and MAE mport type information.
- Newer port/MAC controls:
  `MC_CMD_MAC_CTRL` and `MC_CMD_MAC_STATE` configure and query a selected port
  handle with explicit control flags for address, max frame length, flow
  control, transmission mode, include-FCS, and QBB priority flow-control mask.
  `MC_CMD_SET_NETPORT_EVENTS_MASK`, `GET_NETPORT_EVENTS_MASK`, and
  `GET_SUPPORTED_NETPORT_EVENTS` control delivery of port link-change and
  module-change events.

## Control Flow and Protocol Flow

There are no branches or call graphs inside this header chunk. Runtime flow is
encoded as command sequences that driver code executes through `efx_mcdi_rpc()`
or the Siena variant.

- Link flow typically reads `MC_CMD_GET_LINK` or `MC_CMD_LINK_STATE`, maps
  firmware flags and speeds into the driver's link state, then applies changes
  through `MC_CMD_SET_LINK` or `MC_CMD_LINK_CTRL`. The module-change sequence
  fields provide optimistic concurrency: if firmware observed a later module
  insertion/removal than the driver knew about, `SET_LINK`/`LINK_CTRL` can fail
  with `EAGAIN` instead of applying stale capabilities.
- MAC configuration flow writes MTU, address, flow control, reject filters, FCS
  handling, and newer port-handle-specific controls through `MC_CMD_SET_MAC` or
  `MC_CMD_MAC_CTRL`, then reads negotiated or configured state through
  `GET_LINK`, `MAC_STATE`, and MAC fault fields.
- Statistics flow has two variants. Legacy paths use fixed counter indexes from
  `MC_CMD_MAC_STATS_*` and `MC_CMD_PHY_STATS_*`, often in DMA mode. Newer
  paths first call `MC_CMD_MAC_STATISTICS_DESCRIPTOR` to learn the descriptor
  list and required DMA buffer size, then call `MC_CMD_MAC_STATISTICS` or
  `MC_CMD_GET_NETPORT_STATISTICS`. Generation start/end markers are part of the
  buffer protocol for detecting torn DMA updates.
- NVRAM update flow is transactional: enumerate/query partition, start update,
  read/erase/write data in bounded MCDI payload chunks, finish update, then
  interpret secure verification result and required action. V2/V3 finish
  responses allow long-running signature verification, pending status, abort,
  polling, and human-readable configuration errors.
- Sensor flow starts by enumerating supported sensors and limits, allocates a
  DMA buffer for readings, and refreshes values with `MC_CMD_READ_SENSORS`.
  Dynamic sensors add a persistent generation count and handles: when firmware
  signals a dynamic sensor table change, the driver must list again and fetch
  descriptions/readings for handles that still exist.
- Port-handle flow for newer devices starts from `GET_ASSIGNED_PORT_HANDLE` or
  `ENUM_PORTS`; subsequent link, MAC, transceiver, module, event, and
  statistics commands are scoped to that handle. `ENUM_PORTS` is clear-on-read
  and reset-sensitive, so consumers must drain `MORE` responses and re-enumerate
  after FLR or entity reset.

## State and Persistence Behavior

Most definitions represent firmware-owned state rather than Linux-side
persistent structures.

- Link and MAC state persists in MC/NMC firmware across individual RPC calls
  and is queried through link/MAC state commands. Sequence numbers for link and
  module changes are monotonic synchronization tokens used to avoid stale
  configuration after asynchronous events.
- WoL filters persist in firmware until removed or reset and are represented to
  the host by filter IDs.
- Statistics state is maintained by firmware and may be transferred
  periodically through DMA. The driver must zero-initialize DMA buffers for
  consistent results and validate generation markers when using descriptor or
  legacy DMA layouts.
- Sensor state is owned by firmware. Legacy sensor masks are paged, while
  dynamic sensors have persistent handles for the lifetime of a sensor and a
  generation counter that survives reboots and increments when the table
  changes.
- NVRAM state is non-volatile. Commands in this chunk can alter firmware,
  configuration, expansion ROM, logs, FPGA images, bundle metadata, and recovery
  partitions. A/B partition modes allow reading current versus backup targets
  during update transactions. Verification status may remain pending while the
  firmware holds the partition lock.
- Port enumeration state is maintained per control interface. The port list is
  cleared after reset and command output is clear-on-read, so host software
  must preserve its own copy after enumeration.

## Dependencies and Integration Points

- `mcdi.h` is the direct accessor layer. Its MCDI helpers concatenate `MC_CMD_`
  field names with `_OFST`, `_LEN`, `_LBN`, and `_WIDTH` definitions from this
  header, enforce alignment/length assumptions with `BUILD_BUG_ON`, and perform
  endian conversion for 16-bit and 64-bit fields.
- `mcdi_port.c` and `mcdi_port_common.c` consume `GET_LINK`, `SET_LINK`,
  `GET_PHY_STATE`, `GET_PHY_MEDIA_INFO`, `SET_MAC`, `MAC_STATS`, flow-control,
  link flag, FEC, and capability definitions to implement link polling,
  advertised capability conversion, PHY power state, media EEPROM reads, MAC
  reconfiguration, and DMA statistics.
- `ef10.c` consumes MAC statistic indexes and NVRAM metadata/partition
  definitions for EF10 statistics exposure, FEC/CTPIO counter availability, and
  MTD partition naming/version metadata.
- `mcdi.c` implements shared NVRAM and WoL operations using the NVRAM read,
  write, erase, update-start/finish, verify-result, metadata, partition, and
  WoL filter definitions in this chunk.
- `efx_reflash.c` uses `MC_CMD_NVRAM_WRITE_IN_WRITE_BUFFER_MAXNUM` and
  `_MAXNUM_MCDI2` to choose per-RPC firmware update write sizes.
- `mcdi_mon.c` uses `SENSOR_INFO`, `READ_SENSORS`, sensor entry layouts, and
  sensor state/value encodings to populate hardware monitoring data.
- The `siena/` driver subtree has parallel consumers for many legacy commands,
  so changes to shared protocol constants affect both current and Siena paths.
- Several newer commands reference structure definitions outside this chunk,
  especially `MAE_LINK_ENDPOINT_SELECTOR`, `FEC_TYPE`, and `AN_TYPE`; the
  fields here embed or point to those structures by offset.

## Risks and Edge Cases

- These constants are a firmware ABI. Any offset, length, enum value, or bit
  position change can silently corrupt MCDI requests or misparse firmware
  responses.
- Variable-length macros must be paired with output-length validation. Several
  responses have different maximum payloads for legacy MCDI and MCDI2; using
  the smaller maximum on an MCDI2 path can truncate data, while trusting a
  larger length without allocation checks can overrun buffers.
- Many commands have legacy and newer layouts with overlapping semantics.
  Drivers must select a layout supported by the firmware and check returned
  `outlen` before reading V2/V3-only fields.
- Statistics DMA buffers require zero initialization, sufficient size from the
  descriptor/capability path, and generation-marker validation. Otherwise
  counters can be inconsistent or stale.
- NVRAM update commands can be destructive and may be restricted by TSA binding,
  partition protection, PHY locks, read-only/write-only flags, A/B mode,
  sequential-write requirements, or secure verification failures.
- Module and link sequence numbers are important race guards. Ignoring them can
  apply link settings computed for a removed module to a newly inserted module.
- Dynamic sensor handles can disappear between list and read/description calls;
  response entries are the intersection of driver-known handles and current
  firmware-known handles.
- `GET_MODULE_DATA_IN` V1 has a deprecated unaligned 7-bit address field; V2
  should be preferred to avoid ambiguous access and alignment mistakes.
- `ENUM_PORTS` being clear-on-read means diagnostic or parallel consumers can
  drain pending port changes before the intended owner reads them.

## Test Signals

- Build-time signals: any protocol field typo or length mismatch in consumers
  should fail through `BUILD_BUG_ON` in `mcdi.h` helpers or missing macro
  references during kernel compilation.
- Link tests: exercise `GET_LINK`/`SET_LINK` and newer
  `LINK_STATE`/`LINK_CTRL` paths with autonegotiation, forced speed, FEC,
  pause, loopback, module insertion/removal, and stale sequence-number
  scenarios.
- MAC tests: verify MTU, MAC address, reject flags, flow control, include-FCS,
  QBB, and port-handle-specific `MAC_CTRL`/`MAC_STATE` behavior.
- Statistics tests: compare legacy MAC stats and descriptor-based stats,
  validate generation markers, DMA/non-DMA modes, clear behavior, periodic DMA,
  and MCDI versus MCDI2 response limits.
- NVRAM/reflash tests: enumerate partitions, read metadata, run update
  start/read/erase/write/finish against safe test partitions, verify chunk
  sizing, pending verification polling, failure code mapping, and required
  reboot/action handling.
- Sensor tests: query multi-page legacy sensors and dynamic sensors, validate
  threshold/state mapping, DMA buffer size handling, and generation-count table
  refresh after sensor-change events.
- Module/port tests: enumerate assigned and all port handles, enable/disable
  link/module events, read decoded transceiver properties and raw module data,
  and verify behavior across FLR/entity reset.
