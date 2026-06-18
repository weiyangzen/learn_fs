# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_pcol.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004628`: lines 1-5380, `Docs/researches/chunks/subset-b-004628_research.md`
- `subset-b-004629`: lines 5381-10729, `Docs/researches/chunks/subset-b-004629_research.md`
- `subset-b-004630`: lines 10730-15422, `Docs/researches/chunks/subset-b-004630_research.md`
- `subset-b-004631`: lines 15423-19480, `Docs/researches/chunks/subset-b-004631_research.md`
- `subset-b-004632`: lines 19481-24505, `Docs/researches/chunks/subset-b-004632_research.md`
- `subset-b-004633`: lines 24506-25920, `Docs/researches/chunks/subset-b-004633_research.md`

## Chunk Research

### subset-b-004628: lines 1-5380

# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_pcol.h lines 1-5380

## Scope And Purpose

This chunk is the first 5,380 lines of the Solarflare/Xilinx SFC driver's generated MCDI protocol header. It defines the host-to-management-controller ABI used by the Linux `sfc` Ethernet driver to talk to firmware: MCDI request headers, shared-memory layout, event formats, public error codes, command IDs, request/response payload layouts, field offsets, bit positions, length helpers, and protocol enums.

There is no executable C control flow in this chunk. Its purpose is to be the single source of constants consumed by MCDI packing/unpacking helpers and by driver subsystems such as attach/probe, devlink version reporting, PHY/link setup, PTP hardware clock support, BIST diagnostics, event handling, MAE/table offload support, and management-controller recovery. The values are firmware ABI, so compatibility depends on exact numeric command IDs, offsets, bit numbers, lengths, and variable-length payload formulas.

The assigned range covers the base protocol definitions, common firmware error and table enums, the full `MCDI_EVENT` layout, early MCDI commands from `MC_CMD_READ32` through `MC_CMD_GET_LOOPBACK_MODES`, and the beginning of the link technology structures through the start of `MC_CMD_ETH_TECH`. Link control and later command families continue after this chunk.

## Protocol Header And Shared Memory ABI

The file starts with firmware boot/reset state bits written to `FMCR_CZ_RESET_STATE_REG` or read from shared reset state. These distinguish power-on reset, booting, scheduler-running, warm/tepid boot readiness, recovery-mode entry, PCIe initialization state, and BIST initialization. The distinction between warm boot and tepid/recovery boot matters because the driver and firmware must decide whether MC persistent data can be reused or must be reinitialized.

The Siena shared-memory constants define per-port doorbells, request/response PDU locations, PDU length, PTP time/status offsets, and per-port status dwords. The doorbells are hardware-significant addresses used to alert the MC after a request has been staged. `MC_STATUS_DWORD_REBOOT` and `MC_STATUS_DWORD_ASSERT` are out-of-band failure markers written in shared memory on reboot or assertion.

The `MCDI_HEADER_*` macros describe the 32-bit MCDI v1 request/response header. Important fields include:

- `CODE`, `DATALEN`, and `SEQ`, which identify the command, payload size, and in-flight request.
- `RESYNC`, `ERROR`, and `RESPONSE`, which separate command submission from firmware completion state.
- `XFLAGS`, including `MCDI_HEADER_XFLAGS_EVREQ` for event completion and `MCDI_HEADER_XFLAGS_DBRET` for early doorbell return.

The chunk defines both v1 and v2 maximum control SDU sizes: 0xfc bytes for v1 and 0x400 bytes for v2. Many command response arrays below include separate `*_LENMAX` and `*_LENMAX_MCDI2` values, and callers must pick buffers that match the negotiated protocol.

The event introduction explains the shared event shape and the special command-done interpretation. `FSE_AZ_EV_CODE_MCDI_EVRESPONSE` is the event-code nibble used to distinguish MC-generated events from normal MCDI responses. This is consumed by event dispatch code in `mcdi.c` and the Siena variant to translate firmware notifications into driver actions.

## Error Namespace And Generic Enums

`MC_CMD_ERR_*` defines public MCDI error values. POSIX-like values intentionally match Linux errno values where applicable, while Solarflare-specific firmware errors live in the 0x1000 range. Drivers use these values when decoding MCDI error responses and when deciding whether to retry, wait for proxy authorization, report privilege failures, or treat firmware state as transient.

Notable error cases include:

- `MC_CMD_ERR_PROXY_PENDING`, `PROXY_INPROGRESS`, and `PROXY_UNEXPECTED`, which implement SR-IOV/admin-function authorization. `MC_CMD_ERR_PROXY_PENDING_HANDLE_OFST` and `MC_CMD_ERR_ARG_OFST` define optional error payload fields.
- `MC_CMD_ERR_NO_PCIE`, `NO_DATAPATH`, `DATAPATH_DISABLED`, `VIS_PRESENT`, and `PIOBUFS_PRESENT`, which describe hardware/resource state rather than just malformed requests.
- `MC_CMD_ERR_FILTERS_PRESENT`, used when firmware cannot apply a workaround or configuration change because filters already exist.

The chunk then defines several broad enumerations used later in the protocol:

- `PCIE_INTERFACE_*` identifies primary host, embedded NIC, logical host interfaces, and caller-relative interface selection.
- `MC_CMD_CLIENT_ID_SELF` is the caller-relative client ID sentinel.
- `MAE_FIELD_SUPPORT_STATUS`, `MAE_FIELD_*`, `MAE_CT_VNI_MODE`, `MAE_MCDI_ENCAP_TYPE`, `MAE_MPORT_END`, `MAE_COUNTER_TYPE`, and `MAE_COUNTER_ID_NULL` describe the Match Action Engine match fields, encapsulation modes, conntrack VNI construction, mport endpoint selection, and counter namespaces.
- `TABLE_ID_*` and `TABLE_FIELD_ID_*` describe MAE, VNIC RX, and DPU offload engine table IDs and field IDs. Although the actual MAE commands are later in the header, these values are included here and are consumed by MAE/offload code through `mae.c`, `mae.h`, `tc_counters.h`, and related TC offload logic.

These enum values are not arbitrary application constants. Comments explicitly note that some values are constrained by hardware table access ABI, table encoding layouts, and packet parser semantics. Unknown support statuses must be handled conservatively by zeroing masks rather than trying to match unsupported fields.

## MCDI Event Layout

`MCDI_EVENT` is an 8-byte firmware event structure. The chunk defines the common fields:

- `DATA`, `CONT`, `LEVEL`, `SRC`/`PTP_DATA`, `CODE`, `EV_CODE`, and EF100 phase bit.
- Command-completion subfields: sequence, returned data length, and errno.
- Link-change, module-change, sensor, firmware alert, FLR, TX/RX error, flush, PTP, AOE, MUM, SUC, proxy, DBRET, dynamic sensor, descriptor proxy, mport journal, and port-enumeration event payload interpretations.

`MCDI_EVENT_CODE_*` enumerates the event dispatch namespace. Important codes in this range include command done, link change, reboot, MAC stats DMA, PTP RX/fault/PPS/time, TX/RX flush and error, proxy request/response, DBRET, link-change v2, module-change, dynamic sensor updates, descriptor proxy function state changes, mport journal changes, per-port link/module changes, enum-ports changes, and test-generated events.

Driver integration is direct. `mcdi.c` and `siena/mcdi.c` switch on these codes to finish MCDI requests, detect MC reboot/assertion, forward PTP events, handle flush completions, report queue errors, and process proxy authorization responses. `ptp.c` also depends on the PTP event fields for RX timestamps, PPS events, and time-event subscriptions.

Risk is high because the same 32-bit `DATA` field is reinterpreted by event type, while additional bits live in `SRC` or higher event bits. A field-position regression would be silent at compile time but would break runtime event dispatch, timestamp reconstruction, queue flush completion, or reboot detection.

## Early Memory And Boot Commands

`MC_CMD_READ32` and `MC_CMD_WRITE32` provide raw MC memory access. `READ32` is marked admin despite comments noting it is required by shared-memory boot and normally belongs to an insecure category with extra handler checks. `WRITE32` is explicitly `SRIOV_CTG_INSECURE`. Both use variable-length arrays of 32-bit words with MCDI v1/v2 maximums.

`MC_CMD_GET_BOOT_STATUS` reports the MC boot offset and flags indicating watchdog reset, primary image boot, or backup image boot. `MC_CMD_GET_ASSERTS` returns assertion state and saved register information. Its response has several versions:

- Base response with global fail flags, saved PC, 31 general-purpose registers, failing thread address, and reserved data.
- V2 response for MicroBlaze CPUs with additional special-function registers.
- V3 response with asserted firmware build ID, build timestamp, version, security level, extra info, and build name.

`MC_CMD_LOG_CTRL` configures log output to UART and/or event queue. This controls where firmware-generated notifications and MCDI completions can appear.

These commands are used during bring-up, recovery, diagnostics, and failure reporting. The assertions path is especially stateful: the input has a `CLEAR` flag, so a diagnostic read can mutate firmware assertion state.

## Version And Component Inventory Commands

`MC_CMD_GET_VERSION` is the central adapter component inventory command. The base request is empty; `GET_VERSION_EXT_IN` asks for extended version data. The response evolved through multiple layouts:

- V0/base response reports firmware boot/build value, protocol version, supported function bitmask, firmware version, and extra text.
- V2 adds component data for MC firmware, SUC, CMC, FPGA, board name/revision/serial, and build dates.
- V3 adds explicit presence flags and datapath hardware/firmware versions.
- V4 adds SoC boot, u-boot, main rootfs, and recovery buildroot versions.
- V5 adds board version and bundle version.

`efx_devlink.c` consumes the V5-sized response for devlink info reporting, walking the presence flags before exposing optional fields. `mcdi.c` and `siena/mcdi.c` issue the base command during MCDI version negotiation and firmware capability discovery. The command also carries a 128-bit supported-functions mask used to detect whether later MCDI commands are available.

Compatibility depends on careful `outlength` checking. Older firmware may return shorter payloads, while newer firmware may include optional data behind presence bits. Consumers must not assume V5-sized output unless firmware returned enough bytes.

## PTP Command Family

`MC_CMD_PTP` multiplexes many PTP operations behind one command ID and an operation byte/word. This chunk defines request and response layouts for:

- Enable/disable timestamping and legacy PTP modes.
- Firmware-assisted transmit timestamping on older Siena/Huntington paths.
- Reading NIC time in 32-bit and extended 64-bit-major forms.
- Status/statistics reporting.
- Clock adjustment by seconds/nanoseconds or major/minor units, including V2 high-major fields.
- Frequency adjustment using fixed-point representations.
- Synchronization samples containing host-start, NIC time, host-end, and firmware wait time.
- Manufacturing tests, FPGA register access, filter programming, PPS enablement, clock source selection, time-event subscription/unsubscription, sync-status reporting, sync-timeout querying, timestamp correction querying, and attribute discovery.

`ptp.c` and `siena/ptp.c` are heavy consumers. They allocate buffers using the generated `MC_CMD_PTP_*_LEN` and `*_LENMAX` macros, select PTP modes, read `GET_ATTRIBUTES` and `GET_TIMESTAMP_CORRECTIONS`, perform synchronization through start/finish MCDI RPC calls, subscribe to time events, and parse events using the `MCDI_EVENT_CODE_PTP_*` definitions.

The PTP ABI is version-sensitive. `GET_ATTRIBUTES` is described as an extension of the older `GET_TIME_FORMAT` operation, and comments specify fallbacks when the newer operation or fields are not supported. Time values may be seconds/nanoseconds, 16-second/8-ns units, seconds plus 2^-27 fraction, or quarter-nanosecond minor units. Drivers must transform values according to the reported format and capability bits such as `REPORT_SYNC_STATUS`, `RX_TSTAMP_OOB`, `64BIT_SECONDS`, and `FP44_FREQ_ADJ`.

Stateful behavior includes persistent PTP enablement while the driver is attached, PPS event forwarding, event queue subscriptions, firmware clock offset/frequency adjustments, and synchronization status timeout. Test signals should include PHC registration, PTP enable/disable, `ethtool -T`, hardware timestamp RX/TX paths, frequency/offset adjustments, PPS/time events, and fallback behavior on firmware that lacks newer attribute responses.

## Board, Attach, Reset, And Debug Output

`MC_CMD_GET_BOARD_CFG` returns board identity and legacy Siena configuration: board type/name, per-port capabilities, base MAC address pools, MAC counts/strides, and firmware subtype list. Comments mark many fields as Siena-only and direct EF10+ users to newer commands such as `GET_CAPABILITIES`, `GET_MAC_ADDRESSES`, and `NVRAM_METADATA`.

`MC_CMD_DRV_ATTACH` informs firmware that a host driver is attached or detached and can request datapath firmware variants. The input carries state bits such as attach, preboot, subvariant awareness, VI spreading, V2 link-change events, RX VI spreading inhibit, and TX-only spreading. It also carries a preferred firmware ID such as full-featured, low-latency, packed-stream, high-TX-rate, rules-engine, DPDK, L3XUDP, or plugin-assisted modes. The V2 input adds driver-specific version metadata including low/high version fields, link date, driver build branch, and flags.

The output reports old attach state and, in the extended form, function flags: primary function, link-control privilege, trusted privilege, no active port, current VI spreading state, and TX-only spreading state. `mcdi.c`, `siena/mcdi.c`, `ef10.c`, `ef100_netdev.c`, and PTP paths use these flags to decide primary-function behavior, link-control authority, trusted operations, and whether a function has an active network port.

`MC_CMD_PORT_RESET` and `MC_CMD_ENTITY_RESET` share command ID 0x20. `PORT_RESET` is deprecated; `ENTITY_RESET` extends it with a flags field such as function-resource reset. This aliasing means callers must use request length to select legacy versus extended semantics, and firmware must preserve compatibility.

`MC_CMD_PUTS` copies an ASCII string to UART and/or the network port, optionally with a destination host MAC. It is insecure-category debug output and accepts a variable-length string payload.

## PHY Configuration

`MC_CMD_GET_PHY_CFG` reports the current PHY configuration and is guaranteed to succeed even if the PHY is in a "zombie" state. The V2 input can target a specific network endpoint using an embedded `MAE_LINK_ENDPOINT_SELECTOR` layout. That selector includes mport selector fields for physical ports, function interface IDs, PF/VF IDs, link end, and flat 64-bit views.

The output reports:

- PHY state flags: present, short/long cable BIST availability, low-power, powered-off, TX disabled, and BIST support.
- PHY type, channel, port, stats mask, name, media type, MMD mask, and revision string.
- Supported capability bitmask including 10M/100M/1G/10G/25G/40G/50G/100G/200G full-duplex modes, pause/asymmetric pause, autonegotiation, DDM, and multiple FEC capability/requested bits.
- Media enums such as XAUI, CX4, KX4, XFP, SFP+, BASE-T, QSFP+, and DSFP.
- Clause 22/45 MMD identifiers.

`mcdi_port_common.c` and `siena/mcdi_port_common.c` use these offsets to fill local PHY configuration, publish ethtool link capabilities, decide power/TX-disabled labels, determine BIST availability, and guard output length. They also use `BUILD_BUG_ON` for expected fixed sizes, so layout drift is intentionally caught at compile time for some fields.

## BIST Commands

`MC_CMD_START_BIST` starts PHY, SerDes, MC loopback, RAM, port RAM, or register tests. It is admin/TSA-unbound and comments indicate `PHY_LOCK` is required for PHY BISTs. `MC_CMD_POLL_BIST` returns running/passed/failed/timeout status and optional test-specific data.

Specialized poll response layouts include:

- `POLL_BIST_OUT_SFT9001`: cable lengths and per-pair cable status for four pairs.
- `POLL_BIST_OUT_MRSFP`: module/I2C test progress or failure point.
- `POLL_BIST_OUT_MEM`: memory/register/ECC failure detail including test phase, failure address, bus, expected/actual values, and ECC masks.

These definitions are consumed by ethtool self-test and diagnostics paths in `mcdi_port_common.c` and the Siena copy. Risks are mostly around output-length validation: the generic result field is always meaningful, but the driver must only parse optional PHY-specific payloads after checking response length and PHY type.

## Loopback Modes And Link Technology Structures

`MC_CMD_GET_LOOPBACK_MODES` returns per-speed bitmasks of supported loopbacks. The base response covers 100M, 1G, 10G, suggested, and 40G masks. V2 adds 25G, 50G, and 100G masks; V3 adds 200G. The loopback enum covers internal datapath, MAC, PCS/PMA/PHY, SerDes, wireside, cross-port, AOE, Medford wireside datapath, and force-link-up modes. As with other V2 inputs, the command can target a MAE link endpoint selector.

`mcdi_port_common.c` reads this command to populate driver loopback capability masks. Tests and runtime checks should cover older firmware returning only base length and newer firmware returning V2/V3 lengths.

Near the chunk boundary, the file begins link technology support definitions:

- `AN_TYPE` for none, Clause 28, Clause 37, and Clause 73 autonegotiation.
- `FEC_TYPE` for none, BASE-R, RS, IEEE interleaved RS, Ethernet Consortium low-latency RS, and auto FEC.
- `MC_CMD_ETH_TECH`, a 16-byte technology mask/enum namespace for IEEE 802.3, Ethernet Technology Consortium, and proprietary Ethernet PHY technologies.

The visible `MC_CMD_ETH_TECH_*` enum values include 1G backplane/X, 10G KR/CR/SR/LR/LRM/ER, 25G CR/KR/SR, 40G KR4/CR4/SR4/LR4, 50G CR2/KR2/SR2/KR/SR/CR/LR/DR, 100G KR4/SR4/CR4/LR4/ER4/KR2/SR2/CR2/LR2/DR2, and early 200G KR4/SR4/LR4 definitions. The structure continues after the assigned range.

## Dependencies And Integration Points

This header is included across the SFC driver tree:

- `mcdi.c` and `siena/mcdi.c` use the base header, error, command, attach, version, and event definitions for RPC transport and event dispatch.
- `mcdi.h` documents and stores function flags returned by `MC_CMD_DRV_ATTACH`.
- `efx_devlink.c` uses `MC_CMD_GET_VERSION_V5_OUT_*` fields to expose component versions through devlink.
- `ptp.c`, `siena/ptp.c`, and `ef10.c` use `MC_CMD_PTP_*` and PTP event constants for PHC operations, timestamp corrections, sync, and time-event subscription.
- `mcdi_port_common.c` and `siena/mcdi_port_common.c` use PHY, BIST, and loopback definitions for ethtool and link setup.
- `mae.c`, `mae.h`, `tc_counters.h`, and other offload code use MAE field, table, encapsulation, mport, and counter IDs.
- `ef10.c`, `ef100_nic.c`, `ef100_netdev.c`, `efx_common.c`, `efx_reflash.c`, `mcdi_filters.h`, and monitoring/reflash code include the header for command IDs and layout constants defined in this and later chunks.

The header depends on generated-field access conventions used elsewhere: `MCDI_DECLARE_BUF`, `MCDI_SET_DWORD`, `MCDI_DWORD`, `MCDI_QWORD`, and related macros take symbolic field names and compose the full `MC_CMD_*` constants from this header. The field names and suffixes therefore form an internal compile-time API as well as a firmware ABI.

## State And Persistence Behavior

The header itself stores no runtime state, but many definitions describe persistent or state-mutating firmware behavior:

- Boot/reset flags persist across MC boot stages and tell the driver whether firmware memory/data can be reused.
- Shared-memory doorbells and PDUs are the transport state for one outstanding MCDI request per channel/port.
- `LOG_CTRL` changes where future firmware events are emitted.
- `GET_ASSERTS` can clear assertion state.
- `DRV_ATTACH` changes the firmware's record of host-driver attachment, requested datapath firmware, and event/link-change behavior.
- `ENTITY_RESET` can reset function resources.
- PTP commands enable/disable timestamping, alter NIC clock offset/frequency, configure event subscriptions, PPS forwarding, filters, clock source, and sync-status timeout.
- BIST commands start hardware tests whose completion is later polled.
- Board/PHY/loopback/version commands report firmware and hardware state that the driver caches into local structures and exposes through netdev, ethtool, PHC, or devlink APIs.

Because most of these definitions are ABI descriptors, persistence bugs usually arise when a caller sends an incorrect flag or mis-parses output, not from state held by this header. A wrong bit number can turn a read-only query into a state update or request the wrong datapath/link behavior.

## Risks And Edge Cases

- Generated ABI drift is the primary risk. Numeric changes to command IDs, offsets, lengths, bit positions, or enum values can compile cleanly while breaking firmware communication.
- Output-length compatibility is recurring. Many commands have base, V2, V3, V4, and V5 response layouts; callers must check `outlen` before reading newer fields.
- MCDI v1 versus v2 payload limits affect variable-length buffers. Using v1 `LENMAX` with MCDI2 output truncates valid responses; using MCDI2 assumptions with older firmware can expose uninitialized reads if outlength checks are weak.
- `MC_CMD_PORT_RESET` and `MC_CMD_ENTITY_RESET` share command ID 0x20. Callers and firmware must distinguish semantics by payload length and flags.
- `MC_CMD_PTP_OP_GET_ATTRIBUTES` aliases the old `GET_TIME_FORMAT` operation number. Consumers must handle old short responses and new capability-bearing responses.
- PTP time formats vary by NIC. Misinterpreting major/minor units as seconds/nanoseconds will produce wrong PHC time, timestamp correction, and frequency adjustment behavior.
- Some flags intentionally alias bit positions in evolved layouts, for example RX VI spreading inhibit and TX-only spreading in driver attach flags. Consumers must interpret them in the correct firmware context.
- MAE and table field IDs are constrained by hardware ABI. Treating them as purely software enums risks breaking offload rule construction or hardware table access.
- `READ32`, `WRITE32`, and `PUTS` are sensitive or insecure-category commands. Exposure to untrusted functions must remain controlled by privilege categories and firmware checks.
- Event payload reuse is dense. A wrong event code or data-field interpretation can cause lost command completions, false reboot detection, missed PTP events, or incorrect TX/RX queue error reporting.
- PHY/BIST parsing requires validating both response length and PHY type. Optional BIST payloads should not be parsed from a generic 8-byte poll result.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware/firmware-facing:

- Build the SFC driver with `W=1` or equivalent to catch macro name/size regressions, especially `BUILD_BUG_ON` checks in `mcdi_port_common.c`.
- Exercise probe/attach/detach on supported adapters and confirm `MC_CMD_GET_VERSION`, `MC_CMD_DRV_ATTACH`, and event completion paths succeed without MCDI protocol errors.
- Verify devlink info reports component versions correctly on firmware returning base, V2/V3/V4, and V5 `GET_VERSION` payload lengths.
- Trigger/log MC reboot and assertion paths and confirm `GET_ASSERTS`, reboot events, and shared-memory status markers are decoded correctly.
- Run PTP tests: PHC registration, `phc2sys`/`ptp4l` smoke tests, `ethtool -T`, RX/TX timestamping, frequency and offset adjustment, PPS/time-event subscription, and fallback behavior on firmware lacking newer PTP attributes.
- Run ethtool PHY/link diagnostics: link modes, media reporting, loopback mode enumeration, BIST start/poll, and cable test output.
- Exercise SR-IOV/admin-function scenarios that return proxy pending/response events and privilege errors.
- Exercise firmware event queue handling for command completion, link change, module change, TX/RX flush, TX/RX errors, MAC stats DMA, PTP events, and MC reboot.
- For MAE/offload consumers, install representative TC flower/offload rules and counters that use MAE field IDs, counter types, table IDs, encapsulation fields, and unsupported-field handling.

### subset-b-004629: lines 5381-10729

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

### subset-b-004630: lines 10730-15422

# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_pcol.h lines 10730-15422

## Chunk Scope

This chunk is a generated MCDI protocol header slice for the Solarflare/Xilinx
`sfc` Ethernet driver. It is not executable C logic; it defines command IDs,
privilege categories, request/response byte layouts, bit positions, enum values,
and variable-length message helpers shared between the Linux driver and NIC
management-controller firmware.

The range starts at the tail of NVRAM partition identifiers, then defines small
wire structures for licensed applications, licensed firmware feature masks, TX
timestamp event decoding, and RSS mode selectors. The main body covers MCDI
datapath setup and teardown commands: event, RX, and TX queue initialisation;
filter operations; parser-dispatcher capability queries; VI and PIO buffer
resource allocation; VI PCIe TLP processing controls; and the first five
versions of the `MC_CMD_GET_CAPABILITIES` response. The chunk ends part-way
through `MC_CMD_GET_CAPABILITIES_V5_OUT`, so later capability fields are owned
by the following chunk.

## Purpose and Responsibilities

- Publish the exact firmware ABI for datapath queue lifecycle commands:
  `MC_CMD_INIT_EVQ`, `MC_CMD_INIT_RXQ`, `MC_CMD_INIT_TXQ`, and their matching
  `MC_CMD_FINI_*` operations.
- Define variable-length queue backing-buffer arrays, where the host passes one
  64-bit DMA address per 4 KiB page of EVQ/RXQ/TXQ descriptor memory.
- Encode queue feature flags for interrupting EVQs, event merging, event timers,
  RX prefix/timestamp/CRC/scatter behavior, RX packed-stream and equal-stride
  modes, TX checksum controls, TSOv2, CTPIO, descriptor proxying, Qbb, and
  Riverhead/QDMA buffer sizing.
- Define the filter insertion/removal ABI, including legacy, encapsulation-aware,
  and V3 forms of `MC_CMD_FILTER_OP`.
- Provide capability discovery layouts used by the driver to gate features such
  as RX prefixes, timestamps, batching, RSS modes, VXLAN/NVGRE, TSO, TSOv2,
  EVQ v2 initialisation, PIO/CTPIO, VI window size, descriptor cache sizes, per
  PF/VF resource counts, and MAC statistics buffer sizing.
- Describe firmware-owned resource handles for VI allocation, push-I/O buffers,
  filter handles, port assignment, SR-IOV configuration, and VI TLP processing
  overrides.

## Important APIs, Types, and Constants

- NVRAM partition identifiers:
  `NVRAM_PARTITION_TYPE_BUNDLE_LOG`, `EXPANSION_ROM_INTERNAL`,
  `BUNDLE_SIGNATURE`, SUC FPGA/SOC/failure-log/config partitions,
  `SOC_UPDATE`, `AUTO`, `BOOTLOADER`, reserved ranges, `RECOVERY_MAP`/
  `RECOVERY_FPT`, and `PARTITION_MAP`/`FPT`. These are persistent flash
  partition type constants, not commands in this chunk.
- Licensing structures:
  `LICENSED_APP_ID` is a 32-bit application/license bitmask for Onload, PTP,
  SolarCapture variants, SolarSecure, TCP Direct, Low Latency, and related
  licensed features. `LICENSED_V3_FEATURES` is a 64-bit firmware feature mask
  with bits for RX/TX timestamps, PIO, event timers, clock, sniffing, proxy
  filter ops, cut-through, and related licensed datapath controls.
- Event/RSS helpers:
  `TX_TIMESTAMP_EVENT` identifies ordinary TX completions, CTPIO completions,
  CTPIO timestamp low/high parts, and ordinary timestamp low/high parts while
  splitting timestamp payload across two 16-bit fields. `RSS_MODE` defines the
  4-bit hash selector using source/destination address and port bits.
- `MC_CMD_INIT_EVQ` (`0x80`):
  legacy, V2, and V3 request formats define queue size, function-local instance,
  timer load/reload/mode, interrupt target or wakeup EVQ, event counter mode,
  packet count threshold, and up to 64 DMA page addresses. V2 adds firmware
  policy selection for manual, low-latency, throughput, or auto queue flags and
  an extended-width flag. V3 adds per-queue RX/TX event merge timeout fields in
  nanoseconds. V2/V3 responses return the IRQ and the actual flags firmware
  applied.
- `MC_CMD_INIT_RXQ` (`0x81`):
  legacy and extended layouts define RX queue size, target EVQ, event label,
  queue instance, owner/port IDs, DMA page list, and flags for buffer mode,
  header split, timestamps, CRC mode, chaining, prefix delivery, and scatter
  disablement. Extended/V3/V4/V5 layouts add DMA modes for single-packet,
  packed-stream, and equal-stride super-buffer receive; snapshot length; outer
  classification requests; forced event merging; no-continuation and event
  suppression flags; equal-stride bucket/stride/backpressure parameters; V4
  QDMA buffer size; and V5 RX prefix ID selection.
- `MC_CMD_INIT_TXQ` (`0x82`):
  legacy and extended layouts define TX queue size, target EVQ, event label,
  queue instance, owner/port IDs, DMA page list, checksum disable/enable bits,
  CRC mode, timestamping, pacer bypass, inner checksum controls, TSOv2, CTPIO,
  CTPIO thresholding, memory-to-memory D2C, descriptor proxy, absolute target
  EVQ selection, and Qbb priority flags.
- Queue teardown and driver/proxy commands:
  `MC_CMD_FINI_EVQ`, `MC_CMD_FINI_RXQ`, and `MC_CMD_FINI_TXQ` take only the
  queue instance and return no payload. `MC_CMD_DRIVER_EVENT` lets the host
  inject an event code/data into a target EVQ. `MC_CMD_PROXY_CMD` carries an
  opaque proxy handle to the server side and returns no response body.
- `MC_CMD_FILTER_OP` (`0x8a`):
  supports insert, remove, subscribe, unsubscribe, and replace. Request fields
  include opaque filter handle, v-adaptor port ID, match-field bitmask, RX
  destination, queue, RX mode, RSS or .1p context, TX destination hints, L2/L3/L4
  match values, VLANs, firmware-defined match registers, and IPv4/IPv6 source
  and destination addresses in network byte order. `EXT_IN` adds VXLAN/Geneve/
  NVGRE VNI/VSID and inner-frame match fields. `V3_IN` extends this with match
  action flags and mark values for DPDK/rte_flow-style metadata mutations.
  Responses return the operation and an opaque 64-bit filter handle, with
  `0xffffffffffffffff` reserved as invalid.
- Parser-dispatcher discovery:
  `MC_CMD_GET_PARSER_DISP_INFO` (`0xe4`) reports supported RX match sequences,
  insertion restrictions, SolarSecure security-rule metadata, supported
  encapsulated-frame match types, VNIC encapsulation-rule matches, supported
  VNIC encapsulation types, and low-latency queue match support.
- Resource and PCIe control commands:
  `MC_CMD_GET_PORT_ASSIGNMENT` reports the function's network port or
  `NULL_PORT`; `MC_CMD_ALLOC_VIS`/`FREE_VIS` manage function-local VIs and
  report VI base/count/shift; `MC_CMD_GET_SRIOV_CFG` reports VF counts, enable
  state, RID offset, and stride; `MC_CMD_ALLOC_PIOBUF`/`FREE_PIOBUF` manage
  push-I/O buffers; `MC_CMD_GET_VI_TLP_PROCESSING` and
  `MC_CMD_SET_VI_TLP_PROCESSING` read/write TPH tags, relaxed ordering, ID-based
  ordering, no-snoop, TPH enablement, and sync-data relaxed-ordering overrides.
- `MC_CMD_GET_CAPABILITIES` (`0xbe`):
  base through V5 response layouts are cumulative, length-gated structures.
  The base response has flags1, RX/TX DPCPU firmware IDs, RX/TX packet-datapath
  firmware version/type fields, hardware capabilities, and licensed
  capabilities. V2 adds flags2, TSOv2 context counts, per-PF VF counts,
  `NUM_VIS_PER_PORT`, descriptor cache sizes, and PIO buffer count/size. V3 adds
  `VI_WINDOW_MODE` for 8 KiB/16 KiB/64 KiB VI windows. V4 adds VFIFO stuffing
  counts and `MAC_STATS_NUM_STATS`. V5 starts in this chunk and repeats the same
  leading fields while extending the capability ABI beyond this slice.

## Control Flow and Firmware Protocol Flow

This header has no functions, loops, or local branches, but it encodes the
control flow that driver code follows when bringing up and tearing down NIC
datapath resources:

1. The driver queries capabilities with `MC_CMD_GET_CAPABILITIES` and checks the
   returned length before reading fields introduced by V2, V3, V4, or V5. EF10
   and EF100 code use these fields to decide whether RX prefixes, TSOv2, PIO,
   CTPIO, EVQ v2, VI window modes, and MAC-stat buffer sizing are available.
2. The driver allocates VIs with `MC_CMD_ALLOC_VIS`. The returned VI base,
   count, and optional VI shift define how queue instances and wakeup events are
   interpreted for the current PCI function.
3. Event queues are initialised before RX/TX queues. `MC_CMD_INIT_EVQ` binds a
   function-local EVQ instance to interrupt or wakeup routing, event timer/count
   configuration, event-merge policy, and host DMA pages.
4. RX and TX queues are then initialised against a target EVQ and vport/port
   identifier. RX queue setup chooses prefix/timestamp/scatter and DMA mode
   semantics. TX queue setup chooses checksum, TSO, timestamp, CTPIO, and Qbb
   semantics. Both queue types persist firmware state until the corresponding
   `MC_CMD_FINI_*` command completes.
5. Filters are programmed after the v-adaptor/vport and queues exist.
   `MC_CMD_FILTER_OP` maps driver `efx_filter_spec` data to MCDI match bits,
   match values, receive destination, RSS context, and opaque filter handles.
   Insert/subscribe returns a handle; remove/unsubscribe consumes it; replace may
   return a different handle.
6. Parser-dispatcher queries provide firmware-supported match combinations and
   restrictions that higher-level filter code can use to select valid match
   forms, especially for encapsulated traffic and VNIC encapsulation rules.
7. Teardown reverses the setup order: queues are finalised, active queue counts
   drain, filters/resource handles are removed, PIO buffers are freed, and VIs
   are released. Several consumer paths tolerate `-EALREADY` when firmware has
   already torn resources down after MC reboot or recovery.

## State and Persistence Behavior

Most definitions in this range describe firmware state that persists beyond a
single host function call:

- Queue state persists in NIC firmware after `INIT_EVQ`, `INIT_RXQ`, or
  `INIT_TXQ` until `FINI_*`, management-controller reboot, PCI function reset,
  or recovery. The host-provided DMA page arrays remain part of that queue
  contract; the driver must keep descriptor/event memory allocated and correctly
  aligned while the queue is live.
- VI allocations persist for the PCI function and determine how queue instance
  numbers map to MMIO windows, wakeup events, and VI-local queue handles.
- PIO buffer allocations return handles that remain valid until explicitly freed
  or until VI/function teardown. `FREE_VIS` unlinks linked PIO buffers but does
  not free the PIO buffer allocation itself.
- Filter state persists in firmware parser/dispatcher tables. The returned
  64-bit handles are opaque; host code must not derive meaning from the handle
  except that all-ones is never valid.
- Capability responses are snapshots of inherent device/firmware capability and
  licensed availability. Driver code caches many fields in NIC-private state and
  gates later configuration decisions on those cached bits.
- NVRAM partition identifiers refer to persistent flash storage. This chunk only
  defines the type constants; actual NVRAM read/write/update commands are
  defined elsewhere.

The ABI is byte-offset based. Consumers use the local `MCDI_DECLARE_BUF`,
`MCDI_SET_DWORD`, `MCDI_SET_QWORD`, `MCDI_SET_ARRAY_QWORD`, `MCDI_DWORD`,
`MCDI_WORD`, `MCDI_BYTE`, `MCDI_QWORD`, and `MCDI_POPULATE_DWORD_*` helpers to
avoid manual pointer arithmetic. The filter value comments are a notable
exception to normal little-endian MCDI usage: L2/L3/L4 match values are copied
in network byte order.

## Dependencies and Integration Points

- `mcdi_functions.c` consumes the EVQ/RXQ/TXQ, VI allocation, queue teardown,
  and VI window-mode capability definitions. It builds queue init buffers,
  writes DMA address arrays, checks zero-length responses with `BUILD_BUG_ON`,
  retries TX initialisation when TSOv2 contexts are unavailable, and maps
  capability VI window modes to `efx->vi_stride`.
- `mcdi_filters.c` consumes `MC_CMD_FILTER_OP`, encapsulation match bits, VNI
  type constants, RX destination/mode constants, opaque filter handles, and
  `RSS_MODE` bit definitions. It converts `efx_filter_spec` match flags into
  MCDI match fields and populates VXLAN/Geneve/NVGRE-specific fields when
  encapsulation filtering is requested.
- `ef10.c` and `ef100_nic.c` query `MC_CMD_GET_CAPABILITIES`, gate feature use
  by response length, cache datapath capability words, interpret RX/TX DPCPU
  firmware IDs, read PIO buffer sizing, validate RX-prefix support, set VI
  stride from V3+ `VI_WINDOW_MODE`, size MAC statistics buffers from V4, allocate
  PIO buffers with `MC_CMD_ALLOC_PIOBUF`, and decode TX timestamp events using
  `TX_TIMESTAMP_EVENT` fields.
- `nic.h` and EF100 helpers use capability bits as stable feature tests for
  queue mapping, datapath offloads, and architecture-specific features.
- The firmware is the primary integration partner. Every `*_OFST`, `*_LEN`,
  `*_LBN`, and `*_WIDTH` value is part of a host/firmware ABI; changing these
  macros without matching firmware changes would corrupt MCDI request or
  response interpretation.
- SR-IOV privilege category macros (`SRIOV_CTG_GENERAL`, `SRIOV_CTG_ONLOAD`)
  attach access-control expectations to each command. Queue, VI, PIO, filter,
  and TLP-processing calls also depend on function ownership semantics such as
  the current VI user set by `MC_CMD_SET_VI_USER` outside this chunk.

## Risks and Edge Cases

- ABI drift is the main risk. Renaming is usually harmless, but changing command
  IDs, message lengths, offsets, bit numbers, enum values, or variable-array
  length formulas can silently break firmware communication.
- Versioned capability layouts must be length-gated. Reading V2/V3/V4/V5 fields
  when firmware returned only the base response can produce stale buffer data or
  invalid feature decisions.
- Variable-length DMA address arrays must match descriptor allocation size.
  `INIT_EVQ_IN_LEN(num)`, `INIT_RXQ_IN_LEN(num)`, and `INIT_TXQ_IN_LEN(num)`
  assume one 64-bit address per 4 KiB page and have different MCDI1/MCDI2
  maximums.
- Queue ownership is security-sensitive under SR-IOV. Many queue instance fields
  require the caller to be the currently assigned VI user or an ancestor; using a
  wrong function-local instance can fail or target another resource.
- Filter values mix byte-order domains. Match-value payloads are documented as
  network byte order, while most scalar MCDI fields are accessed with MCDI
  little-endian helper macros.
- `MC_CMD_FILTER_OP_IN_OP_REPLACE` warns that the filter handle may change. Any
  caller that keeps the old handle after replace risks leaking or removing the
  wrong firmware filter entry.
- Encapsulation match fields overlap VNI and VSID interpretation. VXLAN and
  Geneve use UDP plus VNI type, NVGRE uses GRE plus VSID type; the type byte is
  required even when the tenant ID itself is not being matched.
- Some capability flags are licensed or firmware-variant dependent. For example,
  timestamping, low-latency, PIO/CTPIO, event cut-through, and DPDK-style filter
  actions can be advertised, denied, or overridden depending on firmware
  variant, license bits, and privilege category.
- V3/V4/V5 queue formats add fields at fixed tail offsets. Code that sends a
  shorter legacy length while setting flags from a later layout may rely on
  firmware compatibility behavior and should be reviewed carefully.
- The V5 capability definition is incomplete in this chunk. Research consumers
  should merge it with the following chunk before making final statements about
  all V5 fields.

## Test Signals

- Build-level checks: successful compilation of `sfc` consumers, especially
  `BUILD_BUG_ON` assertions around zero-length queue responses and fixed MCDI
  buffer sizes, indicates that local constants still match consumer
  expectations.
- Probe logs: EF10/EF100 probe should successfully read datapath capabilities,
  require RX prefix support where expected, report a valid VI stride for V3+
  firmware, and size MAC stats from V4+ firmware without `-EIO`.
- Queue lifecycle: interface bring-up should allocate VIs, initialise EVQs,
  initialise RX/TX queues with the expected DMA page counts, and tear them down
  without active queue drain timeouts or unexpected `MC_CMD_FINI_*` errors.
- TX/RX feature behavior: timestamped TX should produce ordered low/high
  timestamp events decoded by `TX_TIMESTAMP_EVENT`; RX prefix/timestamp/scatter,
  TSOv2 fallback, and CTPIO/PIO setup should follow capability bits.
- Filter behavior: unicast, multicast, RSS, drop, replace, remove, and
  encapsulation filters should program through `MC_CMD_FILTER_OP`, return valid
  non-all-ones handles, and cleanly remove during reset or interface teardown.
- Negative/recovery signals: short MCDI responses must be rejected; `-ENOSPC`
  from TSOv2 context allocation should trigger fallback; `-EALREADY` during
  resource cleanup should be tolerated where consumers already handle it; MC
  reboot recovery should not leave stale active queue counts or filter handles.

### subset-b-004631: lines 15423-19480

# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_pcol.h lines 15423-19480

## Scope

This chunk covers the generated MCDI protocol definitions for the Solarflare/Xilinx `sfc` driver. It starts in the second capability-word field definitions for `MC_CMD_GET_CAPABILITIES_V5_OUT`, then defines complete response layouts for `MC_CMD_GET_CAPABILITIES_V6_OUT` through `MC_CMD_GET_CAPABILITIES_V12_OUT`, and ends at the start of the `MC_CMD_V2_EXTN` encapsulation command.

The content is a C preprocessor ABI map. It defines command response lengths, byte offsets, field lengths, low-bit numbers, field widths, and enum values. It does not implement functions or own runtime storage, but the constants are consumed by MCDI request/response helpers and by NIC initialization code that translates management-controller capability reports into driver feature flags.

## Purpose

The purpose of this range is to preserve the wire-format contract between the Linux `sfc` host driver and NIC management-controller firmware:

- `GET_CAPABILITIES` response versions describe datapath, firmware, virtualization, queue, RSS, MAE, vDPA, NVRAM, event, and address-window capabilities.
- Later response versions append fields while preserving earlier offsets, so older drivers can parse a prefix and newer drivers can check `outlen` before reading appended fields.
- `MC_CMD_V2_EXTN` provides the v2 command header extension used when the normal MCDI v1 command field is insufficient for newer command IDs and response lengths.

This header is effectively part of the firmware ABI. Callers should treat the generated offsets and bit positions as authoritative and avoid duplicating the numbers in handwritten code.

## Important Macro Families

### `MC_CMD_GET_CAPABILITIES_V5_OUT` Tail

The chunk begins at the tail of the V5 response, specifically in the `FLAGS2` capability word. The fields include low-latency and advanced datapath features such as `EVENT_CUT_THROUGH`, `RX_CUT_THROUGH`, `TX_VFIFO_ULL_MODE`, `INIT_EVQ_V2`, TX/RX timestamping, sniffing, CTPIO, TSA support, filter mark/action support, equal-stride packed stream/super-buffer support, L3-over-UDP support, `INIT_RXQ_WITH_BUFFER_SIZE`, bundle update, `TX_TSO_V3`, dynamic sensors, and NVRAM verify-result polling.

The V5 tail also defines appended scalar and array fields:

- `TX_TSO_V2_N_CONTEXTS` gives FATSOv2 context count when the relevant capability bit is set.
- `PFS_TO_PORTS_ASSIGNMENT` maps PF indexes to external ports and uses special values for access denied, absent PFs, unassigned PFs, and incompatible future mappings.
- `NUM_VFS_PER_PF` reports VF counts per PF, again with special values.
- `NUM_VIS_PER_PORT` reports VI counts for ports 0-3.
- Descriptor cache sizes are encoded as binary logarithms.
- PIO buffer count, PIO buffer size, and `VI_WINDOW_MODE` describe VI MMIO layout and whether CTPIO can be mapped.
- VFIFO stuffing limits, MAC stats count, and filter mark maximum support queue setup, statistics DMA sizing, and filter validation.

These fields are not directly executable, but they are high-value integration points because later NIC setup relies on `outlen` and capability bits before enabling features such as PIO/CTPIO, TSO variants, queue formats, and MAC statistics.

### `GET_CAPABILITIES_V6_OUT` through `V8_OUT`

Versions V6, V7, and V8 repeat the stable capability prefix and append more fields. Each response has:

- `FLAGS1` at offset 0, covering core datapath features such as vport reconfigure, TX striping, vAdaptor query, EVB behavior, RX batching, VLAN insertion/stripping, RX prefix lengths, RX timestamping, multicast filter chaining, PM/RXDP counters, VXLAN/NVGRE, TSO, RSS, packed-stream, and related RX/TX capabilities.
- RX and TX DPCPU firmware IDs and firmware-version subfields, with enums for standard, low-latency, packed-stream, rules-engine, DPDK, BIST, test, and other firmware variants.
- `HW_CAPABILITIES` and `LICENSE_CAPABILITIES`.
- `FLAGS2`, preserving the V5 advanced capability word.
- PF/port/VF/VI arrays, descriptor-cache sizes, PIO parameters, VI-window mode, VFIFO stuffing values, MAC-stat count, filter-mark maximum, and guaranteed RX buffer sizes.

V7 adds `FLAGS3` at offset 148. V8 extends the response to 160 bytes by appending `TEST_RESERVED`, an opaque 64-bit area for host-side test software. Production drivers should not interpret that test field.

### `GET_CAPABILITIES_V9_OUT` through `V12_OUT`

Versions V9-V12 continue the append-only layout:

- V9 length is 184 and adds RSS sizing/resource fields: minimum and maximum indirection-table size, maximum queues for exclusive RSS contexts, maximum queues for even-spreading mode, total RSS context count, and the shared RSS table-pool size.
- V10 length is 192 and appends `SUPPORTED_QUEUE_SIZES` and `GUARANTEED_QUEUE_SIZES` bitmaps. Bit `N` means a `2**N` queue size is supported or guaranteed respectively; supported does not imply always available.
- V11 length is 196 and appends `INDIRECT_MAP_INDEX_COUNT`, the number of available indirect memory maps.
- V12 length is 204 and appends `NUM_VIS_PER_PORT2`, extending VI counts to external ports 4-7 while ports 0-3 remain in the older `NUM_VIS_PER_PORT` field.

The V7-and-later `FLAGS3` word is repeated through V12. It advertises newer features such as Wake-on-LAN Etherwake, RSS even spreading, selectable RSS table size, MAE support, vDPA support, per-encap-rule VLAN stripping, extended-width EVQs, unsolicited event credits, encapsulated MCDI, external MAE support, NVRAM update abort, MAE action-set allocation V2/V3, RSS steer-on-outer, dynamic mport journal, client-command VF proxy, low-latency RX event suppression, and CXL config enable.

### `MC_CMD_V2_EXTN`

The range ends with the beginning of the v2 command extension definition:

- `MC_CMD_V2_EXTN` uses command code `0x7f` as an envelope.
- `MC_CMD_V2_EXTN_IN_LEN` is 4 bytes for the extension dword.
- `EXTENDED_CMD` occupies 15 bits and carries the actual command number.
- `ACTUAL_LEN` occupies 10 bits and carries the encapsulated command payload length, which is not represented in the v1 MCDI header.
- `MESSAGE_TYPE` occupies 4 bits. The range includes the `MC` message type enum and the comment introducing the TSA type; the actual TSA enum value is just beyond the requested line range.

The implementation in `mcdi.c` uses these definitions when `efx->type->mcdi_max_ver` is greater than 1: it emits a normal MCDI header with command `MC_CMD_V2_EXTN`, then populates the second dword with `MC_CMD_V2_EXTN_IN_EXTENDED_CMD` and `MC_CMD_V2_EXTN_IN_ACTUAL_LEN`. Response parsing similarly recognizes `MC_CMD_V2_EXTN` and reads `ACTUAL_LEN` from the second response dword.

## Control Flow

There is no direct control flow in this header chunk. The relevant runtime flow is in consumers:

1. NIC probe or datapath initialization sends `MC_CMD_GET_CAPABILITIES` with no input payload.
2. The caller checks `outlen` against the minimum response version it needs before reading fields appended by later firmware.
3. Capability words are copied into driver-owned NIC data, such as `datapath_caps`, `datapath_caps2`, and, on EF100, `datapath_caps3`.
4. Driver feature decisions are derived from those words and scalar fields: RX prefix requirement checks, TSO enablement, VI-window stride selection, PIO/CTPIO layout, MAC statistics buffer sizing, and feature-specific capability predicates.
5. For MCDI v2 controllers, every request is wrapped in `MC_CMD_V2_EXTN`; the response path unwraps the second header dword to recover the actual response data length.

Concrete examples in this tree include `efx_ef10_init_datapath_caps()` reading `FLAGS1`, `FLAGS2`, PIO size, RX/TX DPCPU IDs, `VI_WINDOW_MODE`, and MAC stats count, and `efx_ef100_init_datapath_caps()` reading the same stable prefix plus V7 `FLAGS3` when present. `ef100_check_caps()` then checks a capability by switching on the generated flag offset and testing the corresponding cached capability word.

## State and Persistence Behavior

The macros themselves have no state. Runtime state is split between firmware-owned capability responses and driver-owned cached copies:

- Firmware provides capability snapshots in an MCDI response. The response format is versioned by length, not by a separate explicit version field.
- The driver persists selected values for the lifetime of the probed NIC instance in structures such as EF10/EF100 NIC data. Those cached values gate later queue setup, offload feature exposure, statistics sizing, and capability checks.
- `VI_WINDOW_MODE`, PIO buffer size/count, queue-size bitmaps, RSS resource sizes, and VI-per-port arrays describe hardware allocation constraints. They are not allocations by themselves, but later code must respect them when creating queues, RSS contexts, or MMIO mappings.
- Test-reserved capability bits are explicitly opaque to production drivers and should not become driver state with semantic meaning.

The management controller may change behavior across firmware versions or after reboot/recovery. Existing MCDI infrastructure tracks request state, epochs, response lengths, and reboot recovery separately; this chunk supplies the field constants used after a valid response is received.

## Dependencies and Integration Points

This chunk depends on the local MCDI helper layer:

- `MCDI_DECLARE_BUF`, `MCDI_DWORD`, `MCDI_WORD`, `MCDI_BYTE`, and `MCDI_SET_DWORD` build and parse buffers using `MC_CMD_*` field macros from this header.
- `EFX_POPULATE_DWORD_*` and `EFX_DWORD_FIELD` use the `_LBN` and `_WIDTH` definitions to compose and extract packed fields.
- `efx_mcdi_rpc()` is the main synchronous command path that sends `MC_CMD_GET_CAPABILITIES` and receives the versioned response.
- `efx_mcdi_send_request()` and `efx_mcdi_read_response_header()` integrate `MC_CMD_V2_EXTN` into the common MCDI transport.

Important consumers are in EF10 and EF100 NIC setup:

- EF10 datapath setup requires a usable `GET_CAPABILITIES` prefix, enforces RX prefix support, records DPCPU firmware IDs, derives VI stride, records PIO buffer size, and sizes MAC stats.
- EF100 datapath setup reads V7-length responses when available and caches `FLAGS3`; feature checks use the generated offsets to select `datapath_caps`, `datapath_caps2`, or `datapath_caps3`.
- PIO/CTPIO-related fields integrate with later PIO buffer allocation and link/unlink flows, even though the specific `LINK_PIOBUF` command definitions are outside this requested range.
- MAE, RSS, queue-size, vDPA, event-credit, and encapsulated-MCDI capability bits are integration points for higher-level EF100 switching, representor, TC offload, queue creation, and event handling code.

## Risks

- Length-gating mistakes can read beyond an older firmware response. Every field appended after a prior response length must be protected by an `outlen >= MC_CMD_GET_CAPABILITIES_V*_OUT_LEN` style check.
- Capability aliases and repeated layouts can hide incorrect assumptions. For example, later response versions preserve offsets, but code using a V8-named macro may still be checking a field present in earlier or later layouts.
- A wrong `_LBN`, `_WIDTH`, or `_OFST` value would corrupt the firmware ABI and can enable/disable the wrong feature. This is especially risky for packed capability words and arrays indexed by PF or port.
- Queue and RSS resource fields are limits, not guarantees in all cases. The supported queue-size bitmap explicitly warns that a supported size may still fail if resources are unavailable.
- `TEST_RESERVED` must remain opaque in production code. Depending on it would couple the driver to test firmware behavior.
- PF/VF/port assignment arrays contain special values. Treating `0xff`, `0xfe`, `0xfd`, or `0xfc` as real port or VF counts would create invalid topology decisions.
- VI-window mode affects MMIO mapping and CTPIO availability. Incorrect parsing can map the wrong offsets or expose CTPIO when the window mode does not support it.
- MCDI v2 encapsulation uses packed bitfields in a second header dword. Incorrect actual-length handling can truncate requests/responses or make the response parser consume the wrong amount of data.

## Test Signals

Useful validation for consumers of this chunk includes:

- Build coverage for `sfc` with EF10 and EF100 support, catching missing or mismatched generated macro names.
- Probe tests against firmware that returns old and new `GET_CAPABILITIES` lengths, verifying that absent V7/V9/V10/V11/V12 fields default safely and present fields are parsed.
- Unit or compile-time checks around buffer lengths, such as existing `BUILD_BUG_ON(MC_CMD_GET_CAPABILITIES_IN_LEN != 0)` and output-buffer sizing.
- Hardware probe logs confirming expected `num_mac_stats`, VI stride/window mode, RX prefix support, and TSO feature exposure.
- Feature-gating tests for EF100 `FLAGS3` capabilities, especially MAE/RSS/event features that should remain disabled when firmware returns a shorter response.
- RSS and queue creation tests that exercise selectable table sizes, even-spreading limits, supported queue-size bitmaps, and guaranteed queue-size behavior.
- MCDI transport tests with v2-capable firmware, confirming that requests are sent with `MC_CMD_V2_EXTN`, that `EXTENDED_CMD` preserves the real command ID, and that response `ACTUAL_LEN` is honored.
- SR-IOV/topology tests that validate PF-to-port and VF-count array handling, including the special no-access, not-present, not-assigned, and incompatible-assignment values.

### subset-b-004632: lines 19481-24505

# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_pcol.h lines 19481-24505

## Purpose

This chunk is a generated MCDI protocol definition slice for the Solarflare/Xilinx `sfc` Ethernet driver. It contains no executable functions; instead it defines wire-format constants that the driver uses when composing requests to, and decoding responses from, NIC firmware. The covered range spans virtual switching, vPorts/vAdaptors, RSS contexts, diagnostic dump and KR tuning commands, licensing, privilege and link-state control, tunnel/EVQ timer control, dynamic client ownership, virtio/vDPA queues, descriptor-address mapping, scheduler credit diagnostics, and the early MAE (Match-Action Engine) capability/resource/action-set APIs.

The source path matters because consumers include this header directly to build binary MCDI payloads. Offsets, lengths, bit positions, array count formulas, null-handle values, and privilege categories are the API.

## Important APIs, Types, And Protocol Blocks

The chunk starts with message-type constants for extended MCDI transport (`MCDI_MESSAGE_TYPE_TSA` and `MCDI_MESSAGE_TYPE_PLATFORM`), then defines command IDs and request/response layouts.

Key command families:

- Push I/O buffer binding: `MC_CMD_LINK_PIOBUF` and `MC_CMD_UNLINK_PIOBUF` bind an allocated PIO buffer handle to a TxQ instance and remove that association. These are `SRIOV_CTG_ONLOAD` commands and depend on a valid function-local VI/TxQ instance.
- EVB/vSwitch/vPort/vAdaptor management: `MC_CMD_VSWITCH_ALLOC/FREE`, `MC_CMD_VPORT_ALLOC/FREE`, `MC_CMD_VADAPTOR_ALLOC/FREE`, `MC_CMD_VADAPTOR_SET_MAC`, `MC_CMD_VADAPTOR_QUERY`, `MC_CMD_EVB_PORT_ASSIGN`, `MC_CMD_VPORT_ADD_MAC_ADDRESS`, `MC_CMD_VPORT_DEL_MAC_ADDRESS`, `MC_CMD_VPORT_GET_MAC_ADDRESSES`, and `MC_CMD_VPORT_RECONFIGURE`. These establish virtual switch topology, vPort handles, VLAN tag insertion/removal policy, MAC address lists, vAdaptor MACs, and PF/VF assignment.
- RSS context management: `MC_CMD_RSS_CONTEXT_ALLOC` plus V2 input, `FREE`, `SET/GET_KEY`, `SET/GET_TABLE`, and `SET/GET_FLAGS`. V2 adds explicit indirection table size and failure on common-pool exhaustion. Flags support legacy `_EN` bits and newer per-protocol RSS mode nibbles gated by the `ADDITIONAL_RSS_MODES` capability.
- Miscellaneous platform/device commands: `MC_CMD_GET_CLOCK`, `MC_CMD_TRIGGER_INTERRUPT`, `MC_CMD_GET_FUNCTION_INFO`, and `MC_CMD_ENABLE_OFFLINE_BIST`.
- Dump and debug: `MC_CMD_DUMP_DO` and `MC_CMD_DUMP_CONFIGURE_UNSOLICITED` describe flexible source/destination dump locations including NVRAM, host memory, multi-level indirection host memory, and UART. These are categorized as insecure.
- KR SerDes tuning: `MC_CMD_KR_TUNE` multiplexes operations for RXEQ/TXEQ get/set, recalibration, eye plot start/poll, FOM read, link training run, and coefficient control. The sub-layouts define variable arrays of packed lane/parameter/value records, lane selectors, retimer-side parameter IDs, and link-training status/value responses.
- Licensing: legacy `MC_CMD_LICENSING`, V3 `MC_CMD_LICENSING_V3`, and `MC_CMD_GET_LICENSED_APP_STATE` expose license update/report operations, key validity counts, private firmware licensing state, self-test status, and V3 app/feature bitmasks.
- Parser/dispatcher and workaround control: `MC_CMD_SET_PARSER_DISP_CONFIG` toggles entity-specific parser-dispatcher behavior; `MC_CMD_GET_WORKAROUNDS` returns implemented/enabled firmware workaround bitmasks for known hardware/firmware issues.
- Privilege and VF link-state control: `MC_CMD_PRIVILEGE_MASK` reads or changes privilege bits for a PF/VF function when `DO_CHANGE` is set; `MC_CMD_LINK_STATE_MODE` reads or sets VF link state mode.
- Tunnel and EVQ timer support: `TUNNEL_ENCAP_UDP_PORT_ENTRY`, `MC_CMD_SET_TUNNEL_ENCAP_UDP_PORTS`, `MC_CMD_SET_EVQ_TMR`, and `MC_CMD_GET_EVQ_TMR_PROPERTIES` define tunnel UDP port acceleration configuration and timer granularity/range reporting.
- Dynamic clients and address mapping: `CLIENT_HANDLE`, `MC_CMD_GET_DESC_ADDR_INFO`, `GET_DESC_ADDR_REGIONS`, `SET_DESC_ADDR_REGIONS`, `MC_CMD_CLIENT_CMD`, `MC_CMD_CLIENT_ALLOC/FREE`, `MC_CMD_SET_VI_USER`, `MC_CMD_GET_CLIENT_HANDLE`, `MC_CMD_GET_CLIENT_MAC_ADDRESSES`, and `MC_CMD_SET_CLIENT_MAC_ADDRESSES` define resource ownership, descendant client command proxying, VI user reassignment, permanent MAC address hints, and descriptor-to-target address region programming.
- Scheduler diagnostics: `SCHED_CREDIT_CHECK_RESULT` and `MC_CMD_CHECK_SCHEDULER_CREDITS` describe paged, generation-counted snapshots of expected versus actual scheduler credits.
- Virtio/vDPA support: `MC_CMD_VIRTIO_GET_FEATURES`, `TEST_FEATURES`, `INIT_QUEUE`, `FINI_QUEUE`, and `GET_DOORBELL_OFFSET` expose virtio feature negotiation, queue creation/destruction, queue migration indices, PASID/MSI-X settings, descriptor/avail/used ring addresses, MAE mport association, and BAR doorbell offsets for net and block devices.
- PCIe function selectors: `PCIE_FUNCTION` carries interface/PF/VF identity with wildcard and null encodings.
- MAE match structures: `MAE_FIELD_FLAGS`, `MAE_ENC_FIELD_PAIRS`, `MAE_FIELD_MASK_VALUE_PAIRS`, and `MAE_FIELD_MASK_VALUE_PAIRS_V2` define packed match key/mask layouts for Ethernet, VLAN, IPv4/IPv6, L4 ports, encapsulated fields, VNI, flags, conntrack fields, private CT flags, and recirculation. V2 extends the original layout with additional flags and CT/recirc selectors.
- MAE selectors and endpoints: `MAE_MPORT_SELECTOR` and `MAE_LINK_ENDPOINT_SELECTOR` encode physical port/function/mport selectors and link endpoints, with compatibility values and caller-relative addressing.
- MAE capabilities and resources: `MC_CMD_MAE_GET_CAPS` V1/V2/V3, `GET_AR_CAPS`, `GET_OR_CAPS`, `COUNTER_ALLOC/FREE`, `COUNTERS_STREAM_START/STOP/GIVE_CREDITS`, `ENCAP_HEADER_ALLOC/UPDATE/FREE`, `MAC_ADDR_ALLOC/FREE`, and the start of `ACTION_SET_ALLOC`/V2 define MAE capacity discovery, match-field support discovery, counter lifecycle and streaming, encap metadata lifecycle, MAC ID lifecycle, and action-set construction.

## Control Flow And State Transitions

This header encodes command-level protocols rather than C control flow. The implied flow is request buffer construction using `_IN_*_OFST`, `_LEN`, `_LBN`, and `_WIDTH` constants, dispatch through the driver's MCDI transport, then response parsing using `_OUT_*` constants and variable-length macros such as `*_LEN(num)` and `*_NUM(len)`.

Several command families impose ordering:

- EVB resources are hierarchical: allocate a vSwitch on an upstream port, allocate vPorts under that topology, allocate vAdaptors, assign EVB ports to PF/VF functions, then mutate MAC/VLAN state or free objects in reverse dependency order. `VPORT_RECONFIGURE` can reset the vPort's user before applying changes.
- RSS context lifecycle is allocate, configure key/table/flags, use in receive filtering/queue selection, then free. Shared RSS contexts cannot have key/table changed; exclusive contexts require explicit setup; even-spreading contexts do not allocate an indirection table.
- KR tuning is a multiplexed state machine: choose an op, pass operation-specific arguments, repeatedly poll eye plots until no more rows are returned, and use link-training commands/status to steer coefficients.
- Tunnel UDP port reconfiguration can force resets across all functions, so callers must treat the output `RESETTING` bit as a control-flow signal and recover queue/function state.
- EVQ timer setting returns actual rounded/truncated nanosecond values; callers must use returned values rather than assuming requested values were programmed exactly.
- Dynamic clients form a parent/descendant tree. `CLIENT_CMD` proxies the next command as a descendant client; `CLIENT_FREE` recursively frees that client's owned resources and child clients; `SET_VI_USER` fails if child resources are outstanding on the VI.
- Virtio queues flow through feature discovery/test, queue init with DMA ring addresses and negotiated feature bits, runtime doorbell use, and queue fini that returns final avail/used indices for migration or restart.
- MAE resources are explicit object lifecycles: caps discovery, per-field support discovery, object allocation returning IDs, references from rules/action sets, streaming counters through RxQs with optional credit flow control, generation-aware object freeing, and final ID release.

## State And Persistence Behavior

Most state lives in NIC firmware/hardware, not in this header. The macros define how the host names, creates, mutates, and destroys that firmware state.

Persistent or durable state includes license partitions and licensing results, vSwitch/vPort/vAdaptor topology while configured, permanent client MAC address hints, dynamic client ownership trees, descriptor address region bases, tunnel UDP port parser configuration, EVQ timer programming, virtio queue state, and MAE allocated resources. Some state is explicitly volatile or invalidated: licensed app state can be invalidated by license update or MC reboot, virtio final queue indices are snapshots at queue teardown, scheduler credit results are snapshot/paged by generation, and MAE counter generation counts wrap from `0xffffffff` to `1` with zero reserved.

Important sentinel values include invalid RSS context `0xffffffff`, `CLIENT_HANDLE_NULL` `0xffffffff`, `CLIENT_HANDLE_SELF` `0xfffffffe`, virtio/EVB VF-null encodings `0xffff`, MAE null IDs such as encap header/MAC/counter/action-related null values, `MAE_MPORT_SELECTOR_NULL`, and function wildcard/null values in `PCIE_FUNCTION`.

## Dependencies And Integration Points

The chunk depends on protocol definitions elsewhere in the same header for shared enums and structures referenced by comment, including `SRIOV_CTG_*`, `RSS_MODE`, `PCIE_INTERFACE`, `DESC_ADDR_REGION`, `MAE_COUNTER_TYPE`, `MAE_COUNTER_ID`, `MAE_MPORT_END`, capability bits such as `ADDITIONAL_RSS_MODES` and `MAE_ACTION_SET_ALLOC_V2_SUPPORTED`, and general MCDI error codes such as `EINVAL`, `ENOSPC`, `ENOSUP`, `EAGAIN`, `EALREADY`, and `EPERM`.

Driver integration points include:

- MCDI buffer helpers that use these offsets and lengths to pack little-endian scalar fields, network-order MAC/IP/L4 fields where named `_BE`, and 64-bit values split into `_LO` and `_HI`.
- SR-IOV and administration code enforcing privilege categories before issuing commands that affect other functions, dynamic clients, MAE, insecure dump paths, or TSA-bound adapters.
- RX/TX queue setup, RSS setup, filter/offload programming, EVB/vDPA control, MAE rule management, and diagnostic paths in the `sfc` driver.
- Firmware feature detection: V2/V3 command layouts and optional fields must be used only when matching capabilities or response lengths indicate support.
- External specs referenced in comments, notably virtio 1.1 and internal XN/SF documents for dynamic clients, schedulers, MAE endpoints, and descriptor address mapping.

## Risks And Edge Cases

- Wire-layout drift is high impact. Any incorrect `_OFST`, `_LEN`, `_LBN`, `_WIDTH`, or variable array count macro can corrupt MCDI payloads or misdecode firmware responses.
- Many structures contain aliases and deprecated fields. Drivers must preserve backward compatibility while preferring newer aliases such as RSS mode fields, MAE V2 match fields, `MAE_MPORT_SELECTOR_ASSIGNED`, and `PCIE_INTERFACE_CALLER`-style semantics where available.
- Privilege bits are security boundaries. `PRIVILEGE_MASK`, `CLIENT_CMD`, dynamic clients, arbitrary DMA privileges, MAE privileges, insecure dump commands, and tunnel/global reset commands can cross function or tenant boundaries if packed incorrectly or issued without policy checks.
- Resource lifecycle leaks are plausible for vPorts, RSS contexts, virtio queues, dynamic clients, MAE counters, encap headers, MAC IDs, and action sets. Free commands often return partial arrays or generation counts that callers should validate.
- Variable-length responses must be bounded by both MCDI1 and MCDI2 maxima. The header often provides separate `LENMAX_MCDI2` and `MAXNUM_MCDI2` values; callers that size only for MCDI1 can truncate newer firmware data.
- Endianness is mixed. Many MAE match fields and MAC addresses are explicitly network/big-endian, while MCDI scalar fields are normally host-packed through MCDI helpers. RSS Toeplitz key comments still note endianness uncertainty.
- Reset side effects are explicit for vPort reconfiguration, tunnel UDP port changes, offline BIST, and possibly function assignment flows. Callers need recovery paths for queues, filters, and client-owned resources.
- Hardware limitation notes are part of the contract, for example MAE matching on IP TTL values other than 1 can return `MC_CMD_ERR_EINVAL(BAD_IP_TTL)`.
- Snapshot/generation protocols can be misused. Scheduler credit pages require matching generations, and MAE counter allocation/free/stream stop generation values determine when counter packets are valid or final.

## Test Signals

Useful validation signals for code using this chunk:

- Compile-time checks that generated field offsets/lengths match the expected MCDI payload sizes and that arrays obey `LEN(num)`/`NUM(len)` formulas for MCDI1 and MCDI2 maximum lengths.
- MCDI mock tests for EVB/vPort/vAdaptor allocation, RSS context V1/V2 allocation, RSS flags on old versus new firmware, and MAE caps V1/V2/V3 response-length handling.
- Negative tests for unsupported capabilities: additional RSS modes without `ADDITIONAL_RSS_MODES`, MAE V2 action set allocation without advertised support, unsupported MAE counter types, and virtio unsupported/missing-required feature sets.
- Lifecycle tests that allocate and free RSS contexts, dynamic clients, virtio queues, MAE counters, encap headers, MAC IDs, and action sets, asserting IDs are non-null and free responses/generation counts are interpreted.
- Security tests that non-admin/non-MAE/non-insecure clients cannot issue commands outside their privilege category or proxy commands for non-descendant clients.
- Reset/recovery tests for tunnel UDP port changes, `VPORT_RECONFIGURE` with assigned users, and offline BIST entry behavior.
- Endianness tests for MAE field-pair packing, MAC address packing, IPv4/IPv6 fields, L4 port fields, and 64-bit split fields.
- Paged/snapshot tests for `MC_CMD_CHECK_SCHEDULER_CREDITS`, verifying page-zero generation capture and subsequent page consistency.

## Unresolved Cross-Chunk References

This slice references definitions outside lines 19481-24505, including `DESC_ADDR_REGION`, `MAE_COUNTER_TYPE`, `MAE_COUNTER_ID`, `MAE_MPORT_END`, `RSS_MODE`, `PCIE_INTERFACE`, `MAE_ACTION_SET_ALLOC` fields beyond line 24505, and the lower-level MCDI accessor macros used by driver C files. The later chunk should complete `MC_CMD_MAE_ACTION_SET_ALLOC_V2_IN` and the remaining MAE rule/action APIs.

### subset-b-004633: lines 24506-25920

# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_pcol.h lines 24506-25920

## Scope

This chunk covers the tail of the Solarflare/Xilinx SFC MCDI protocol header. It starts part-way through the `MC_CMD_MAE_ACTION_SET_ALLOC_V2_IN` request layout, defines the full `MC_CMD_MAE_ACTION_SET_ALLOC_V3_IN` extension, and then continues through MAE action-set/list lifecycle, outer/action rule lifecycle, m-port lookup/allocation/free/journaling, a generic firmware table API, X4 queue-handle encoding, and low-latency queue allocation/free commands. The chunk ends at the `MCDI_PCOL_H` include guard terminator.

The file is a firmware protocol ABI header: it defines command numbers, privilege categories, request/response message lengths, field offsets, bit positions, array bounds, enum sentinel values, and structure layouts consumed by the SFC driver MCDI marshalling helpers. It does not contain local executable algorithms, but changes here directly alter how driver code packs messages sent to management-controller firmware.

## Purpose

The covered definitions expose late MAE and table-programming capabilities to the Linux SFC driver:

- MAE action set allocation variants describe packet edit and delivery actions such as VLAN push/pop, encapsulation/decapsulation, mark/flag, NAT, TTL decrement, source m-port reporting, MAC replacement, DSCP/ECN rewrite/copy, RDP route-field overwrite, network-channel override, LACP plugin controls, delivery m-port selection, and MAE counter updates.
- MAE action set/list commands allocate reusable hardware action objects and compound action lists that action rules can reference.
- Outer-rule and action-rule commands program match/action entries with priorities, connection tracking and recirculation controls, counters, and variable-length match criteria.
- M-port commands map m-port selectors to firmware m-port IDs, allocate/free VNIC or alias m-ports, and enumerate m-port topology from a clear-on-read firmware journal.
- The generic table API lets the driver discover firmware-accessible tables and their field descriptors, then insert/delete entries in direct, BCAM, TCAM, or STCAM tables.
- Queue-handle and low-latency queue commands define X4 queue identity encoding and allocation/free APIs for X3-style LL TX/RX/event queues.

## Important APIs, Types, and Constants

### MAE Action Set Allocation V2/V3

The chunk begins with the latter part of `MC_CMD_MAE_ACTION_SET_ALLOC_V2_IN` and then defines `MC_CMD_MAE_ACTION_SET_ALLOC_V3_IN_LEN` as 53 bytes. V3 is advertised by `MAE_ACTION_SET_ALLOC_V3_SUPPORTED` in `MC_CMD_GET_CAPABILITIES_V10_OUT`; V2 is tied to `MC_CMD_GET_CAPABILITIES_V7_OUT` in the immediately preceding context.

Important V2/V3 fields include:

- `FLAGS` at offset 0, with bitfields for `VLAN_PUSH`, `VLAN_POP`, `DECAP`, `MARK`, `FLAG`, `DO_NAT`, `DO_DECR_IP_TTL`, `DO_SET_SRC_MPORT`, `SUPPRESS_SELF_DELIVERY`, `DO_REPLACE_RDP_C_PL`, `DO_REPLACE_RDP_D_PL`, `DO_REPLACE_RDP_OUT_HOST_CHAN`, `DO_SET_NET_CHAN`, `LACP_PLUGIN`, and `LACP_INC_L4`.
- VLAN insertion fields at offsets 4, 6, 8, and 10 for outer/inner TCI and TPID values in big-endian packet order.
- `ENCAP_HEADER_ID`, `DELIVER`, `COUNTER_LIST_ID`, `COUNTER_ID`, `MARK_VALUE`, `SRC_MAC_ID`, `DST_MAC_ID`, and `REPORTED_SRC_MPORT`.
- DSCP control at offset 48 with copy-on-encap, copy-on-decap, replace, and six-bit DSCP value subfields.
- ECN control at offset 50 with copy/replace fields, two-bit ECN value, and ECT(0)/ECT(1)-to-CE transformation bits.
- V3-only `RDP_OVERWRITE` at offset 51 and `NET_CHAN` at offset 52. The header states that `NET_CHAN` for `DO_SET_NET_CHAN` cannot be used with `DO_SET_SRC_MPORT`.

`MC_CMD_MAE_ACTION_SET_ALLOC_OUT` returns a four-byte `AS_ID`; non-null action-set IDs have a clear MSB so they can be distinguished from action-set-list IDs. The null sentinel is `MC_CMD_MAE_ACTION_SET_ALLOC_OUT_ACTION_SET_ID_NULL` (`0xffffffff`).

### MAE Action Set and Action Set List Lifecycle

`MC_CMD_MAE_ACTION_SET_FREE` (`0x14e`, `SRIOV_CTG_MAE`) accepts a variable-length array of 1-32 action-set IDs and returns the IDs actually freed. Its comments explicitly say it follows `MC_CMD_MAE_COUNTER_FREE` semantics, so callers should expect partial-progress reporting rather than a purely scalar success/fail contract.

`MC_CMD_MAE_ACTION_SET_LIST_ALLOC` (`0x14f`, `SRIOV_CTG_MAE`) allocates an action set list. Input contains `COUNT` plus an array of action-set IDs. The last element may itself be an already allocated ASL ID, allowing one superlist to share a trailing sublist allocated earlier. The output `ASL_ID` has the MSB set, while `AS_ID` has the MSB clear, which is a deliberate type-tagging convention in the firmware ID namespace. `MC_CMD_MAE_ACTION_SET_LIST_FREE` (`0x150`) mirrors action-set free semantics for 1-32 ASL IDs.

Driver integration is visible in `mae.c`: `efx_mae_alloc_action_set_list()` builds `MC_CMD_MAE_ACTION_SET_LIST_ALLOC` requests, enforces `MC_CMD_MAE_ACTION_SET_LIST_ALLOC_IN_AS_IDS_MAXNUM_MCDI2`, sends `efx_mcdi_rpc()`, and stores the returned firmware ID. TC action handling later compares IDs against `MC_CMD_MAE_ACTION_SET_LIST_ALLOC_OUT_ACTION_SET_LIST_ID_NULL`.

### Outer Rules and Action Rules

`MC_CMD_MAE_OUTER_RULE_INSERT` (`0x15a`, `SRIOV_CTG_MAE`) programs encapsulation parsing and may affect lookup sequencing. Inputs include:

- `ENCAP_TYPE`, referencing `MAE_MCDI_ENCAP_TYPE`;
- `PRIO`, where lower values are higher priority and the value must be below firmware-reported encapsulation priority capacity;
- `ACTION_CONTROL`/deprecated `LOOKUP_CONTROL`, with CT enable, CT VNI mode, counting, TCP-flags inhibit, recirculation ID, and CT domain subfields;
- optional OR counter ID, which must have been allocated as counter type `OR` when `DO_COUNT` is set;
- variable-length `MAE_ENC_FIELD_PAIRS` match criteria.

`MC_CMD_MAE_OUTER_RULE_REMOVE` removes 1-32 outer-rule IDs and returns the removed IDs.

`MAE_ACTION_RULE_RESPONSE` is the action-rule response structure. It contains `ASL_ID`, `AS_ID`, `LOOKUP_CONTROL`, and `COUNTER_ID`. Exactly one of `ASL_ID` or `AS_ID` may be non-null. The lookup control word has mutually exclusive `DO_CT` and `DO_RECIRC` flags, CT VNI mode, recirculation ID, and CT domain. The counter ID is valid only when CT or recirculation is requested and must be an action-rule (`AR`) counter.

`MC_CMD_MAE_ACTION_RULE_INSERT` (`0x15c`) inserts a priority-ordered rule with a `MAE_ACTION_RULE_RESPONSE`, a reserved zero word, and variable-length `MAE_FIELD_MASK_VALUE_PAIRS` match criteria. The output is an action-rule ID with null sentinel `0xffffffff`. `MC_CMD_MAE_ACTION_RULE_UPDATE` (`0x15d`) atomically changes only a rule response and may return `ENOTSUP`, in which case the driver must delete/insert. `MC_CMD_MAE_ACTION_RULE_DELETE` (`0x155`) deletes 1-32 action-rule IDs and reports the deleted IDs.

One ABI detail worth preserving during reconciliation: `MAE_ACTION_RULE_RESPONSE_LEN` is defined as 16, but `MC_CMD_MAE_ACTION_RULE_INSERT_IN_RESPONSE_LEN` and `MC_CMD_MAE_ACTION_RULE_UPDATE_IN_RESPONSE_LEN` are 20 in this chunk. Current driver code uses the symbolic MCDI structure accessors into the larger request field, so this may be intentional padding or generated-header drift; it should be treated as an ABI risk and verified against firmware/protocol generation rather than manually normalized.

### M-Port Lookup, Allocation, Descriptors, and Journal

`MC_CMD_MAE_MPORT_LOOKUP` (`0x160`, `SRIOV_CTG_GENERAL`) maps an m-port selector to a concrete m-port ID.

`MC_CMD_MAE_MPORT_ALLOC` (`0x163`, `SRIOV_CTG_MAE`) allocates driver-owned m-ports. Generic, alias, and VNIC request layouts are all defined:

- `MPORT_TYPE_ALIAS` traffic can be sent through an override descriptor and received on a nominated VNIC with alias metadata.
- `MPORT_TYPE_VNIC` creates an m-port with an attached VNIC; queues can be created against it by passing the m-port selector at queue creation.
- all allocation forms include a 128-bit driver UUID;
- alias allocation additionally includes `DELIVER_MPORT`, currently required to be the assigned caller m-port;
- alias output includes both `MPORT_ID` and a VNIC-unique metadata `LABEL`.

`MC_CMD_MAE_MPORT_FREE` frees a previously allocated m-port ID. `MAE_MPORT_DESC` is a 52-byte descriptor used by the journal. It includes m-port ID, common flags, caller-relative flags (`CAN_RECEIVE_ON`, `CAN_DELIVER_TO`, `CAN_DELETE`, `IS_ZOMBIE`), m-port type (`NET_PORT`, `ALIAS`, `VNIC`), UUID, and a type-specific tail for net-port index, alias delivery m-port, or VNIC owner information. VNIC ownership distinguishes function and plugin clients and includes PCIe interface, PF index, and VF index; `MAE_MPORT_DESC_VF_IDX_NULL` denotes a PF.

`MC_CMD_MAE_MPORT_READ_JOURNAL` (`0x147`, `SRIOV_CTG_MAE`) exposes a per-client m-port creation/deletion journal. The journal is clear-on-read and is regenerated from scratch after FLR or `MC_CMD_ENTITY_RESET`. The response carries a `MORE` flag, descriptor count, `SIZEOF_MPORT_DESC`, and a byte array of descriptors. The comments require drivers to stride by `SIZEOF_MPORT_DESC` because `MAE_MPORT_DESC` may grow in future protocol versions.

`mae.c` consumes this carefully in `efx_mae_enumerate_mports()`: it allocates an MCDI2-sized journal buffer, loops while firmware reports more data, rejects undersized responses, rejects descriptor strides smaller than `MAE_MPORT_DESC_LEN`, checks `outlen` against `MC_CMD_MAE_MPORT_READ_JOURNAL_OUT_LEN(count * stride)`, and reads each descriptor through structure macros before adding it to the driver's m-port hash table.

### Generic Table API

`TABLE_FIELD_DESCR` is an 8-byte field descriptor for a field inside a wider key, mask, or response value. It records field ID, least-significant bit number, width, mask type, and scheme. Mask types cover never-selected, exact, ternary, whole-field, and LPM semantics. The scheme field is a semantic-version hook and is currently version 0.

`MC_CMD_TABLE_LIST` (`0x1c9`, `SRIOV_CTG_GENERAL`) returns the list of firmware tables accessible through this API. The input is `FIRST_TABLE_ID_INDEX` for pagination; the output includes total table count and a variable-length array of table IDs. Standard MCDI responses can carry up to 62 IDs, while MCDI2 can carry up to 254.

`MC_CMD_TABLE_DESCRIPTOR` (`0x1ca`, `SRIOV_CTG_GENERAL`) returns table properties and a paginated list of field descriptors. It reports maximum entries, table type (`DIRECT`, `BCAM`, `TCAM`, `STCAM`), key width, response width, key-field count, response-field count, priority count for masked tables, max masks for STCAM, flags such as `ALLOC_MASKS`, scheme, and then key descriptors followed by response descriptors. A client that does not understand the descriptor scheme must not program the table.

`MC_CMD_TABLE_INSERT` (`0x1cd`) and `MC_CMD_TABLE_DELETE` (`0x1cf`) program generic tables. Both use the same core input shape: table ID, key width, mask width or STCAM mask ID, response width or priority, reserved zero padding, and packed 32-bit data words. The data area contains key, optional mask, and optional response values as little-endian 32-bit words, with fields packed according to descriptor LBN/width and padded at the most significant end. Insert may fail with `EINVAL`, `EEXIST`, `ENOSPC`, or `EPERM`; delete may fail with `EINVAL`, `ENOENT`, or `EPERM`. The comments note that the additional MCDI error argument returns the raw underlying CAM-driver error code.

`mae.c` has direct consumers: `efx_mae_table_get_desc()` paginates descriptors, rejects unsupported flags/schemes, and allocates per-field metadata; `efx_mae_table_hook_find()` binds known field IDs to software metadata; `efx_mae_insert_ct()` and `efx_mae_remove_ct()` use descriptor widths to size command buffers, pack conntrack keys/responses, and send `MC_CMD_TABLE_INSERT` or `MC_CMD_TABLE_DELETE`.

### Queue Handles and Low-Latency Queues

`MC_CMD_QUEUE_HANDLE` is a four-byte structure used on X4 to distinguish full-featured VIs from low-latency queues. Bits 0-23 contain the queue number; bits 24-31 contain queue type. Defined types are full-featured VI, LL TXQ, LL RXQ, and LL EVQ. The comment states that the top type bits must be masked off when indexing queues in the BAR.

`MC_CMD_ALLOC_LL_QUEUES` (`0x1dd`, `SRIOV_CTG_GENERAL`) allocates X3-style low-latency queues for the current PCI function. Inputs provide minimum and maximum useful counts for TXQ, RXQ, and EVQ. Output reports actual counts and then a non-necessarily-contiguous list of `MC_CMD_QUEUE_HANDLE` values ordered as TXQs, then RXQs, then EVQs.

`MC_CMD_FREE_LL_QUEUES` (`0x1de`, `SRIOV_CTG_GENERAL`) frees a counted list of queue handles previously returned by `MC_CMD_ALLOC_LL_QUEUES`. The queue type should be encoded in the top bits for each handle.

## Control Flow

This chunk's control flow is protocol-level:

1. The driver probes capabilities and decides which command variant or optional field set is available, for example V2/V3 action-set allocation or generic table access.
2. Driver code declares or allocates an MCDI input buffer using the `_IN_LEN`, `_IN_LEN(num)`, and max-size macros from this header.
3. The driver writes fields with `MCDI_SET_*` or `MCDI_STRUCT_SET_*` using the offset, length, and bitfield macros defined here. Variable payloads use array max/count helpers.
4. `efx_mcdi_rpc()` sends the command ID and buffer to firmware under the privilege category encoded near each command definition.
5. Firmware allocates, updates, deletes, or queries MAE/table/queue state and returns an output buffer matching the `_OUT_*` layout.
6. The driver validates output length, null sentinels, counts, pagination flags, and scheme/version fields before updating local mirrors or returning errors up stack.

The m-port journal adds a loop: callers repeatedly issue `MC_CMD_MAE_MPORT_READ_JOURNAL`, process zero or more descriptors, and continue while `MORE` is set. Table listing and table-descriptor access use index-based pagination through `FIRST_TABLE_ID_INDEX` and `FIRST_FIELDS_INDEX`.

## State and Persistence Behavior

The state modeled here lives primarily in firmware/hardware, with local driver mirrors:

- action sets and action set lists persist in MAE firmware resources until freed, function reset, or firmware reset; their IDs are later embedded in action-rule responses;
- outer rules and action rules persist as priority-ordered match/action entries and may consume counters, CT domains, recirculation IDs, and action object references;
- m-ports persist after allocation until explicitly freed, and firmware maintains a per-client clear-on-read journal of m-port topology changes;
- table descriptors describe persistent firmware table schemas, while table insert/delete mutates entries such as conntrack table state;
- LL queues are allocated against the current PCI function and freed by handle;
- ID spaces use explicit null sentinels and, for AS/ASL, MSB tagging to distinguish object classes.

Reserved fields are part of the ABI. The request-side comments repeatedly require unused or reserved fields to be zero, or in one action-set reserved field case zero or `0xffffffff`. Output-side reserved flags must be ignored unless defined by a future protocol revision.

## Dependencies and Integration Points

The definitions depend on the rest of `mcdi_pcol.h` for shared enums and constants such as `MAE_COUNTER_ID`, `MAE_MCDI_ENCAP_TYPE`, `MAE_CT_VNI_MODE`, `MAE_FIELD_MASK_VALUE_PAIRS`, `MAE_ENC_FIELD_PAIRS`, `TABLE_ID`, and `TABLE_FIELD_ID`. They also depend on the SFC MCDI access layer for message packing and RPC transport.

Concrete integration points found in the source tree include:

- `drivers/net/ethernet/sfc/mae.c`, which uses the table list/descriptor/insert/delete commands, m-port journal descriptors, action-set list allocation, action-rule responses, and action-rule insert/update/delete paths;
- `drivers/net/ethernet/sfc/tc.c`, which stores and compares action-set/action-list firmware IDs when managing TC offload rules;
- `drivers/net/ethernet/sfc/mae.h`, where m-port hash-table state and MAE resource tracking are declared;
- the generic MCDI layer in `mcdi.c`/`mcdi.h` and generated-style accessor macros that turn these offset/length constants into packed command buffers.

The privilege categories matter operationally. MAE mutation commands generally require `SRIOV_CTG_MAE`, while lookup/table/LL-queue commands in this chunk are marked `SRIOV_CTG_GENERAL`; permission failures may therefore reflect function privileges rather than malformed messages.

## Risks and Edge Cases

- ABI drift is the main risk. Renumbering command IDs, changing offsets, or changing field widths breaks firmware communication even if C compilation succeeds.
- Variable-length request/response formulas must match allocation sizes. Off-by-one errors in `*_LEN(num)` or `*_NUM(len)` use can truncate match criteria, AS ID arrays, table fields, or queue-handle lists.
- V3 action-set `NET_CHAN` and `DO_SET_SRC_MPORT` are documented as mutually exclusive; callers must enforce that before sending the command.
- `COUNTER_LIST_ID` and single `COUNTER_ID` are mutually exclusive in action-set allocation, and `COUNTER_ID` must have been allocated with the right counter type.
- `AS_ID` and `ASL_ID` in `MAE_ACTION_RULE_RESPONSE` are mutually exclusive, and `DO_CT` and `DO_RECIRC` are also mutually exclusive.
- The `MAE_ACTION_RULE_RESPONSE_LEN` versus request response field length discrepancy should be verified against generated protocol sources and firmware behavior.
- M-port journal handling must use the returned descriptor stride, not a hard-coded structure size, because firmware may extend descriptors.
- Table programming must reject unknown descriptor schemes and must obey descriptor mask types. Treating BCAM, TCAM, and STCAM packing identically can corrupt masks, priorities, or mask IDs.
- For generic table insert/delete, `MASK_ID` overlays `MASK_WIDTH` and `PRIORITY` overlays `RESP_WIDTH`; callers must populate the interpretation appropriate for table type and operation.
- Queue handles include type bits in the top byte; using the raw handle as a BAR queue index without masking the queue type violates the header contract.

## Test and Validation Signals

Useful validation is mostly compile-time, MCDI-marshalling, and hardware/firmware integration oriented:

- compile coverage of `sfc` with MAE/TC offload enabled, including `mae.c` users of action rules, action-set lists, m-port journals, and generic tables;
- static or generated ABI checks for command IDs, request/response lengths, array maximums, field offsets, and bit positions against the authoritative MCDI protocol generator;
- unit-style packing tests around action-rule responses, V2/V3 action sets, table data packing, AS/ASL ID null sentinels, and queue-handle queue-number/type extraction;
- negative tests for mutually exclusive fields: `AS_ID`/`ASL_ID`, `DO_CT`/`DO_RECIRC`, `COUNTER_LIST_ID`/`COUNTER_ID`, and `DO_SET_NET_CHAN`/`DO_SET_SRC_MPORT`;
- hardware or firmware smoke tests that allocate/free action sets, action set lists, outer rules, action rules, alias/VNIC m-ports, table entries, and LL queues;
- pagination tests for table list, table descriptor, and m-port journal paths, including zero-count responses, `MORE` handling, maximum MCDI2 response sizes, and short-response rejection;
- error-path tests for table `EEXIST`, `ENOENT`, `ENOSPC`, `EPERM`, descriptor `EINVAL`, action-rule update `ENOTSUP`, and resource-free partial-progress reporting.

## Cross-Chunk Notes

This is the final chunk of `drivers/net/ethernet/sfc/mcdi_pcol.h`. Earlier chunks define the shared MCDI header guard, common command framework, capability bits, MAE field IDs, counter APIs, encapsulation/header IDs, and the beginning of `MC_CMD_MAE_ACTION_SET_ALLOC`/V2 that this chunk relies on. The merge lane should produce one per-file report for the whole generated protocol header and should keep this chunk's source path aligned with the `sfc` driver tree rather than moving it into a slug-only bucket.
