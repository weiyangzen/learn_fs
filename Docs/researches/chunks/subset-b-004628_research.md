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
