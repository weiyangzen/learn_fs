# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_pcol.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004638`: lines 1-5896, `Docs/researches/chunks/subset-b-004638_research.md`
- `subset-b-004639`: lines 5897-11301, `Docs/researches/chunks/subset-b-004639_research.md`
- `subset-b-004640`: lines 11302-15705, `Docs/researches/chunks/subset-b-004640_research.md`
- `subset-b-004641`: lines 15706-17204, `Docs/researches/chunks/subset-b-004641_research.md`

## Chunk Research

### subset-b-004638: lines 1-5896

# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_pcol.h lines 1-5896

## Scope And Purpose

This chunk is the opening 5,896 lines of the Solarflare/Xilinx SFC Siena `mcdi_pcol.h` protocol header. It is not executable driver logic; it is the generated C preprocessor contract that tells host-side driver code how to encode and decode Management Controller Diagnostic Interface (MCDI) requests, responses, events, boot state, reset state, statistics buffers, PHY/MAC/link configuration, Wake-on-LAN filters, SR-IOV setup, and NVRAM update operations.

The file starts with boot, shared-memory, MCDI header, error-code, and event definitions, then defines command numbers and request/response field offsets for commands from `MC_CMD_READ32` through the beginning of `MC_CMD_REBOOT_MODE`. This chunk ends mid-command at the `MC_CMD_REBOOT_MODE_IN` enum list after the normal and power-on reset values; later reboot-mode fields and all later protocol definitions are outside this work item.

Because these definitions are a wire ABI shared by the Linux driver and NIC firmware, correctness depends on exact command IDs, payload lengths, offsets, bit positions, maximum element counts, and versioned response shapes. The SFC driver code that includes this header typically uses these constants with MCDI buffer access helpers rather than with C structs, so this header's macros are the primary source of truth for the binary layout.

## Protocol Foundation

The first section defines MC boot and shared-memory state:

- `MC_FW_STATE_POR`, `MC_FW_STATE_BOOTING`, `MC_FW_STATE_SCHED`, warm/tepid boot flags, recovery-mode flags, and BIST initialization flags describe firmware boot progress and whether persistent MC data must be reinitialized.
- `MC_SMEM_P0_DOORBELL_OFST`, `MC_SMEM_P1_DOORBELL_OFST`, `MC_SMEM_P0_PDU_OFST`, `MC_SMEM_P1_PDU_OFST`, `MC_SMEM_PDU_LEN`, PTP-time, and per-port status offsets describe the Siena shared-memory transport. Doorbell writes notify the MC; request and response PDUs are placed in fixed per-port shared-memory windows.
- `MC_STATUS_DWORD_REBOOT` and `MC_STATUS_DWORD_ASSERT` are special status dwords used when firmware reboots or asserts.
- `MC_FW_VERSION_IS_BOOTLOADER()` identifies bootloader versions by checking for the `0xb007` high halfword.

`MCDI_PCOL_VERSION` is set to `2`. The comments explicitly note that the ROM on the card only speaks protocol version 0, so drivers must remain compatible with the boot ROM command subset while also supporting the current protocol version.

The MCDI request/response header is a 32-bit word at `MCDI_HEADER_OFST`. The bit fields define command code, resync flag, data length, sequence number, epoch marker, error bit, response bit, and `XFLAGS`. `MCDI_HEADER_XFLAGS_EVREQ` requests event completion, while `MCDI_HEADER_XFLAGS_DBRET` requests an early doorbell-return event. Payload limits are versioned: v1 supports 0xfc bytes and v2 supports 0x400 bytes. Variable-length request and response macros later in the file consistently expose both legacy `LENMAX` and `_LENMAX_MCDI2` values.

The protocol model is single in-flight request per client: the driver writes a request into shared memory, rings the doorbell, and waits for exactly one response by shared-memory polling or event completion before sending the next request. That sequencing requirement is a key control-flow constraint for all commands in this chunk.

## Error And Privilege Surface

The chunk defines MCDI error values that mirror common `errno` cases, plus firmware-specific failures. Standard-style codes include permission, no entry, interrupted/asserted MC, I/O, already exists, retry, no memory, lock access, busy, invalid argument, broken pipe, read-only, range, deadlock, unsupported, address unavailable, not connected, and already in progress.

Firmware-specific codes cover resource allocation, v-adaptor/EVB/vswitch/vport lookup failures, VLAN and MAC conflicts, missing datapath or PCIe link, absent slave core, proxy authorization workflow, lack of SR-IOV privilege, filters/VIs/PIO buffers already present, missing clocks, unreachable assertion tests, background queue exhaustion, and temporary datapath absence.

The error layout starts at `MC_CMD_ERR_CODE_OFST`; protocol v2 can also include `MC_CMD_ERR_ARG_OFST`, the first unprocessed argument number. `MC_CMD_ERR_PROXY_PENDING` carries an extra handle at `MC_CMD_ERR_PROXY_PENDING_HANDLE_OFST` and changes driver behavior: the driver must wait for a proxy-response event and resend the original command after authorization.

Most command blocks include `MC_CMD_0xNN_PRIVILEGE_CTG` macros with categories such as `SRIOV_CTG_GENERAL`, `SRIOV_CTG_ADMIN`, `SRIOV_CTG_LINK`, and `SRIOV_CTG_INSECURE`. These category macros are not defined in this chunk, so callers depend on other SFC headers for the actual privilege model. The distinction matters: several low-level memory, DBI, random seed, and reboot-mode operations are explicitly insecure or admin-only, while link/MAC state operations use link or general categories.

## Event Types

`MCDI_EVENT` is an 8-byte event format with data, continuation, level, source, and code fields. The comments explain that command completions and asynchronous notifications share this structure. `FSE_AZ_EV_CODE_MCDI_EVRESPONSE` is `0xc`, allowing MC-generated events to be recognized in event queues or UART output.

The MCDI event code space includes:

- Command lifecycle: `CMDDONE`, `DBRET`, reboot, MC reboot, proxy request/response.
- Link and module lifecycle: `LINKCHANGE`, `LINKCHANGE_V2`, `MODULECHANGE`, local-device capability changes, flow-control fields, link-up flags, and module sequence numbers.
- Sensors: legacy sensor events plus dynamic sensor table changes and state/value event pairs.
- Datapath errors: TX/RX queue errors, TX/RX flush completion, MAC stats DMA completion, parity and ECC errors.
- PTP: RX timestamps, PPS, HW PPS, PTP fault, and PTP time events with NIC clock validity/sync bits.
- Firmware and auxiliary processors: firmware alerts, AOE faults, MUM faults, SUC faults, descriptor proxy function events, and test-generated events.

The event definitions include many overlay field layouts for the same 32-bit `DATA` area. A consumer must branch on `MCDI_EVENT_CODE` before interpreting payload bits. Some event families, such as PTP timestamp events and descriptor proxy driver-attach events, require multi-event or continuation handling.

The chunk also defines `FCDI_EVENT` and `MUM_EVENT` 8-byte formats, plus `FCDI_EXTENDED_EVENT_PPS`. These describe firmware-controller and management-unit events forwarded through the MC ecosystem. FCDI covers FC reboot/assert, DDR tests/ECC, link state, timed reads, PPS, PTP, port config, and boot results. MUM events cover reboot/assert, sensors, QSFP/LASI link faults, PHY readiness/link/loss/fault flags, module technology, and per-port source data identifiers.

## Boot, Version, Assertion, And Logging Commands

`MC_CMD_READ32`, `MC_CMD_WRITE32`, and `MC_CMD_COPYCODE` are the boot ROM/shmboot command surface. They read/write MC memory and copy code between addresses before optionally jumping. The boot ROM supported-function mask includes these plus `MC_CMD_GET_VERSION`. `MC_CMD_COPYCODE` carries boot-magic bit fields for satellite CPU loading, config ignore, boot ICORE sync skipping, standalone forcing, and XIP disabling. The comments warn that read/copy operations are security-sensitive but required for shared-memory boot.

`MC_CMD_SET_FUNC` selects the function used by function-specific commands. `MC_CMD_GET_BOOT_STATUS` reports boot offset and flags including watchdog, primary/backup boot, fallback, and flash mode. `MC_CMD_GET_ASSERTS` returns assertion diagnostics. The chunk defines three response layouts:

- Legacy response with global flags, saved PC, 31 GP registers, failing thread, and reserved data.
- V2 response for MicroBlaze CPUs with saved special-function registers.
- V3 response with MC firmware build ID, build timestamp, version, security level, extra info, and build name.

`MC_CMD_LOG_CTRL` controls log destination, either UART or event queue. This is the integration point that enables asynchronous link, sensor, and command-completion notifications. `MC_CMD_GET_VERSION` has deprecated v0, standard, extended, and v2 responses. The v2 response describes firmware, protocol version, supported command mask, MC firmware build details, SUC/CMC versions and build dates, FPGA version and extra text, board name/revision, and serial number with validity flags for each component.

## PTP Command Family

`MC_CMD_PTP` is a multiplexed command with an operation byte in `MC_CMD_PTP_IN_OP`. The chunk defines operations for enabling/disabling timestamping, transmitting PTP packets on older platforms, reading NIC time, status, frequency and offset adjustment, host/NIC synchronization, manufacturing tests, debug, FPGA register access, VLAN/UUID/domain filters, clock source, PPS forwarding, time format/attributes, timestamp corrections, time-event subscription, PPS manufacturing tests, and sync-status reporting.

The input layouts show how all PTP subcommands share a command/peripheral-ID prefix, then append operation-specific fields. Important stateful inputs include:

- Timestamping mode for enable, with PTP v1/v2, VLAN-deprecated modes, enhanced v2 UUID filtering, and FCoE.
- Fixed-point frequency adjustment with either 40 fractional bits or 44 fractional bits if `FP44_FREQ_ADJ` is advertised by attributes.
- Seconds/nanoseconds aliases and major/minor aliases, plus V2 variants with upper 32 bits of major seconds for 64-bit time.
- Synchronize operation count and a 64-bit host start-address DMA write for "synchronization started".
- Time-event subscribe/unsubscribe queue IDs and sync-status reporting flags.

The output layouts include transmit timestamp, NIC time and V2 NIC time, 64-byte PTP status/statistics, synchronization time sets, manufacturing-test result codes, FPGA read buffers, time format, attributes, and timestamp-correction values. PTP attributes advertise time format, minimum sync window, sync-status reporting, out-of-band RX timestamps, 64-bit seconds, and FP44 frequency adjustment.

Risks here are mostly version and units mismatches: old firmware assumes seconds/nanoseconds if attributes are unsupported, while newer firmware can use major/minor formats. Callers must check capabilities before choosing 64-bit seconds or FP44 adjustment, and must respect the smaller legacy PDU lengths when talking to older firmware.

## Low-Level Register, Board, And Attach Commands

`MC_CMD_CSR_READ32` and `MC_CMD_CSR_WRITE32` access an indirect memory map with address, step, and variable word buffers. CSR read returns a buffer whose final dword is status rather than a read value. `MC_CMD_MDIO_READ` and `MC_CMD_MDIO_WRITE` access internal or external MDIO buses, support Clause 45 by default, and use `MC_CMD_MDIO_CLAUSE22` to request Clause 22 access. `MC_CMD_DBI_WRITE` and `MC_CMD_DBI_READX` operate on DBI registers using typed records that carry address plus VF/CS2 parameters.

`MC_CMD_PORT_READ32`, `PORT_WRITE32`, `PORT_READ128`, and `PORT_WRITE128` access indirect per-port register maps. The comments say the port is implied by the shared-memory channel, so callers must use the correct channel or function context. These port commands do not include explicit privilege-category macros in this chunk.

`MC_CMD_GET_BOARD_CFG` returns board type/name, legacy Siena per-port capabilities, base MAC address pools, MAC counts/strides, and firmware subtype list values used by drivers to select firmware updates. The comments mark many fields as Siena-only or unused on EF10 and later, where newer commands such as `GET_CAPABILITIES`, `GET_MAC_ADDRESSES`, and `NVRAM_METADATA` supersede them.

`MC_CMD_DRV_ATTACH` tells firmware whether a host driver manages the port/function, whether the attach is preboot, whether the driver is subvariant-aware, and whether it wants VI spreading, V2 link-change events, RX VI spreading inhibition, or TX-only spreading. It also lets Huntington-era drivers request a datapath firmware flavor such as full-featured, low-latency, packed-stream, high-TX-rate, rules-engine, DPDK, L3XUDP, keep-current-test-only, or don't-care. V2 adds a 20-byte zero-terminated driver version string. Extended output reports old state and function flags such as primary, link-control capable, trusted, no active port, and current spreading status.

## Reset, Debug, Queue, And Diagnostic Commands

`MC_CMD_SHMUART` routes UART output to a circular shared-memory buffer. `MC_CMD_PORT_RESET` is deprecated in favor of `MC_CMD_ENTITY_RESET`, which reuses command code `0x20` and adds a function-resource-reset flag. This aliasing is intentional but risky for dispatch tables or human audits that assume command IDs are unique.

`MC_CMD_PCIE_CREDITS` exposes current/minimum PCIe posted and non-posted header/data credit thresholds, with polling and wipe controls. `MC_CMD_RXD_MONITOR` exposes RX queue ring/cache fill and histograms, again with polling and wipe controls. `MC_CMD_PUTS` copies an ASCII string to UART and/or out a network port, with destination flags and destination host MAC.

`MC_CMD_START_BIST` starts PHY, BPX SerDes, MC loopback, MC memory, port memory, or register BISTs. `MC_CMD_POLL_BIST` returns running/pass/fail/timeout and provides variant-specific result payloads for SFT9001 cable testing, MRSFP I2C/module tests, and memory/register/ECC failures. The comments state that drivers should only parse PHY-specific BIST payloads after checking response length and `GET_PHY_CFG.TYPE`; otherwise they should still honor the generic pass/fail result.

`MC_CMD_FLUSH_RX_QUEUES` initiates RX queue flushes, especially for SR-IOV configurations, but completion is asynchronous. The command returning success is not enough; the driver must still wait for flush done/failure events.

`MC_CMD_SCHEDINFO` returns scheduler timing data for MC threads. `MC_CMD_REBOOT` reboots the MC and can be issued after assertion detection with `MC_CMD_REBOOT_FLAGS_AFTER_ASSERTION`. The command's comment is unusual: it says the caller gets back an error response with `ERR=1` and `DATALEN=0`, so command-handling code must not interpret that shape as a normal failure path without considering reboot semantics.

## PHY, Link, Loopback, And MAC Configuration

`MC_CMD_GET_PHY_CFG` returns a 72-byte PHY description that includes presence, BIST availability, low-power/poweroff/TX-disable/BIST state flags, PHY type, supported capability bitmask, channel/port, stats mask, human-readable name, media type, supported MMDs, and revision string. PHY capabilities cover 10M/100M/1G/10G/25G/40G/50G/100G, half/full duplex where applicable, pause/asymmetric pause, autonegotiation, DDM, BASE-R FEC, RS-FEC, and requested FEC flags. Media types include XAUI, CX4, KX4, XFP, SFP+, 10GBaseT, and QSFP+.

`MC_CMD_GET_LOOPBACK_MODES` returns 64-bit masks of loopback modes by speed. The V1 response covers 100M, 1G, 10G, suggested, and 40G; V2 adds 25G, 50G, and 100G. The loopback enum is broad, including MAC/datapath, GMAC/XGMII/XGXS/XAUI/GMII/SGMII/XFI, far and wireside variants, PHYXS/PCS/PMA-PMD, cross-port, KR SerDes near/far, AOE internal, Medford wireside datapath, and force external link for snapper use.

`AN_TYPE` and `FEC_TYPE` define auto-negotiation and forward-error-correction enum payloads. `MC_CMD_GET_LINK` returns advertised capabilities, partner capabilities, speed, loopback mode, link flags, negotiated flow control, and MAC fault flags. V2 extends the link response with local device capability after PMD/MDI state, AN type, FEC type, and low-level PMD/PMA/PCS/alignment/BER/FEC/AN/shutdown flags.

`MC_CMD_SET_LINK` writes advertised capabilities, low-power/poweroff/TX-disable/linkdown flags, loopback mode, and loopback speed. V2 adds a one-byte module sequence control so the command can be tied to the latest `MODULECHANGE` event; the high bit can ignore sequence validation. This guards against configuring link based on stale module capability data.

`MC_CMD_SET_ID_LED` sets the identification LED off, on, or default. `MC_CMD_SET_MAC` programs MTU, drain, MAC address, reject unicast/broadcast behavior, flow control, and include-FCS behavior. The extended input adds a control mask allowing selective parameter updates when enhanced SET_MAC support exists. The V2 output returns the configured MTU, allowing a query by sending a control mask of zero.

## PHY And MAC Statistics

`MC_CMD_PHY_STATS` reads generic PHY statistics either by DMA or directly in the MCDI response when `DMA_ADDR` is zero. The sparse 32-bit statistic enum includes OUI, PMA/PMD link/fault/signal/SNR, PCS link/fault/BER/block errors, PHYXS link/fault/align/sync, autonegotiation state, 10GBaseT status, and Clause 22 link-up.

`MC_CMD_MAC_STATS` reads or schedules MAC statistics. The input includes a 64-bit DMA address, command bits for DMA, clear, periodic change, periodic enable, periodic clear, no-event, a 16-bit period in milliseconds, a DMA length, and a port ID for v-adapter stats. The comments say drivers should zero-initialize the buffer for consistency and set DMA length to the value advertised by capabilities, falling back to legacy `MC_CMD_MAC_NSTATS * sizeof(uint64_t)` for old firmware.

The base MAC statistic enum covers generation markers, TX/RX packet and byte counters, pause/control/unicast/multicast/broadcast counters, length bins, bad FCS, collision/defer counters, non-TCP/UDP and source-error counters, RX overflow/false-carrier/symbol/alignment/length/internal/jabber/no-desc counters, lane character/disparity errors, match fault, PM/RXDP counters, v-adapter RX/TX counters, legacy Siena GMAC buffer range, and `MC_CMD_MAC_GENERATION_END`. V2 adds FEC uncorrected/corrected codeword and per-lane corrected-symbol counters. V3 adds CTPIO success, failure, fallback, poison, and erase counters. V4 adds RXDP scatter-disabled truncation and head-of-line blocking idle/timeout counters.

The generation start/end values are a state-consistency protocol for DMA buffers. Consumers should verify generation markers around DMAd data and understand that in extended-stat configurations the generation-end word is at the end of the DMA buffer rather than at the legacy enum slot.

## SR-IOV, DMA Copy, Wake-On-LAN, And Multicast Hash

`MC_CMD_SRIOV` has enable, VI base, and VF count inputs, and returns VI scale plus total VFs. The command is marked "to be documented" in this chunk, so consumers should treat it as a low-level compatibility interface and cross-check later driver code before changing it.

`MC_CMD_MEMCPY_RECORD_TYPEDEF` and `MC_CMD_MEMCPY` define ordered DMA copy records. Each record includes record count (used only by the first record), destination RID/address, source RID/address, and length. The command can copy from host DMA or from inline data embedded in the request by using `MC_CMD_MEMCPY_RECORD_TYPEDEF_RID_INLINE` and an offset into the payload. Multiple records are executed in strict order, which is useful for generation-count updates around DMA-populated structures.

`MC_CMD_WOL_FILTER_SET`, `REMOVE`, and `RESET` manage Wake-on-LAN filters. Set supports simple and structured filter modes with magic packet, Windows magic packet, IPv4 SYN, IPv6 SYN, bitmap, and link filters. Specialized input layouts define MAC address, IPv4/IPv6 address and port tuples, bitmap masks/patterns, and link-up/down masks. Set returns a filter ID used by remove. Reset can target wake filters and lights-out offloads.

`MC_CMD_SET_MCAST_HASH` writes two 16-byte multicast hash chunks without otherwise reconfiguring the MAC. This separation reduces unintended MAC changes when only the multicast filter hash changes.

## NVRAM Partition And Update Protocol

`MC_CMD_NVRAM_TYPES` returns a bitmask of available virtual NVRAM partitions. This chunk defines partition IDs for MC firmware and backup, static/dynamic config per port, expansion ROM and per-port config, PHY config per port, log, FPGA and backup FPGA, FC firmware and backup, CPLD, licensing, FC log, and extra FPGA flash.

`MC_CMD_NVRAM_INFO` returns partition type, size, erase size, flags, physical device, and physical address. Flags include protected, TLV, read-only if TSA-bound, CRC, read-only, CMAC, and A/B partitioning. V2 adds write size, used by Sorrento/MUM support. The NVRAM access commands are admin-only and several comments state that PHY partitions require `PHY_LOCK`.

The update flow is stateful:

1. `MC_CMD_NVRAM_UPDATE_START` or V2 starts an update group for a partition and acquires the relevant firmware-side update lock.
2. `MC_CMD_NVRAM_READ`/`READ_V2`, `WRITE`, and `ERASE` operate on offsets and lengths within that partition. V2 read adds mode selection for A/B partitions: default, target current, or target backup. This permits read-modify-write-verify while holding the write lock.
3. `MC_CMD_NVRAM_UPDATE_FINISH` or V2 completes the update and may request reboot. V2 can request verification reporting, background execution, or polling for verify results.

The V2 finish response reports secure firmware validation results, especially for signed Medford images where signature verification may outlast a normal MCDI timeout and run in a background thread. Result codes distinguish success, pending, CMS format failures, digest failures, no valid signatures, trusted-approver failures, signer mismatch, test-signed rejection, security-level downgrade, bundle layout/manifest/component errors, component hash failures, and target-copy failures. The comments also note that the per-partition NVRAM lock is only released after verification completes.

In TSA-bound adapters, start/finish are restricted to static config, dynamic config, and expansion ROM config partitions; attempts on restricted partitions return `EPERM`. This is a persistent-state and security boundary, not just an input-validation detail.

## Dependencies And Integration Points

This header depends on the broader SFC driver infrastructure for:

- MCDI transport code that writes headers and payloads into shared memory, rings per-port doorbells, polls shared memory, and processes event queue completions.
- Buffer accessor macros or helpers that use `_OFST`, `_LEN`, `_LBN`, `_WIDTH`, `_LO_OFST`, `_HI_OFST`, `_NUM`, `_MINNUM`, `_MAXNUM`, and `_LEN(num)` definitions.
- SR-IOV privilege category definitions such as `SRIOV_CTG_GENERAL`, `SRIOV_CTG_ADMIN`, `SRIOV_CTG_LINK`, and `SRIOV_CTG_INSECURE`.
- Link, PHY, MAC, PTP, statistics, NVRAM, WoL, and reset driver code that converts Linux netdev/ethtool/PTP operations into the command layouts defined here.
- Firmware support for command masks returned by `MC_CMD_GET_VERSION`; callers cannot assume every command or response variant is implemented on all boards or firmware generations.

The source path under `sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/` indicates this is a vendored or copied Linux network driver header inside the larger `learn_fs` source tree. It does not directly reference Ceph filesystem logic, but it is part of the kernel/client source body and would affect NIC behavior when this driver is compiled.

## State And Persistence Behavior

Most definitions are stateless binary layouts, but many commands govern durable or asynchronous state:

- Shared-memory request/response state is per port/function and single-flight. Sequence and event-completion fields coordinate transient command state.
- Boot/reboot flags, copycode operations, and reboot mode affect MC execution state and can force persistent data reinitialization.
- `DRV_ATTACH` records driver ownership state and datapath firmware preference in firmware; its old-state output is used to reconcile attach/detach transitions.
- PTP enable/disable, clock adjustments, PPS forwarding, time-event subscription, and sync status alter firmware-maintained timing state and event delivery.
- Link and MAC commands persist current advertised capabilities, power/linkdown flags, loopback settings, MTU, flow control, reject flags, FCS behavior, LED state, and multicast hash until changed or reset.
- RX queue flushing is asynchronous; completion persists as later events rather than as the immediate command response.
- MAC/PHY statistics can be read, cleared, or periodically DMAed; generation counters are used to detect torn DMA snapshots.
- BIST commands start long-running tests and require polling to completion.
- WoL filters persist by firmware-assigned filter ID until removed or reset.
- NVRAM commands mutate durable flash partitions and can include A/B current/backup behavior, secure signature verification, background processing, and reboot requests.

## Risks And Edge Cases

The largest risk is ABI drift. A one-byte offset, bit number, command ID, or length macro error can make the driver send malformed firmware commands or misinterpret returned state. Variable-length macros must be used consistently with response length checks, especially for legacy v1/v0 firmware and `_MCDI2` sizes.

Event payloads are heavily overlaid. Interpreting `DATA`, `SRC`, or high bits without first checking the event code can turn unrelated notification data into false queue IDs, link state, timestamps, proxy handles, or error reasons.

Versioned response handling is central. `GET_VERSION`, `GET_ASSERTS`, `GET_LINK`, `GET_LOOPBACK_MODES`, `PTP`, `MAC_STATS`, `NVRAM_INFO`, and `NVRAM_UPDATE_FINISH` all have legacy and extended layouts. Code should use actual out length and advertised capabilities rather than assuming the newest layout.

Some commands are security-sensitive or destructive. `WRITE32`, `DBI_WRITE`, `SET_RAND_SEED`, `REBOOT_MODE`, NVRAM write/erase/update, memory copy, and direct register access require careful privilege checks and input validation. The header marks categories, but enforcement is elsewhere.

Several operations have asynchronous or unusual completion semantics. `FLUSH_RX_QUEUES` requires later events. `DBRET` can signal command acceptance before completion. `NVRAM_UPDATE_FINISH_V2` can run background verification and return pending states. `REBOOT` intentionally returns an error-shaped response. Driver code must model these cases explicitly.

Stale state is a link-management risk. `SET_LINK_IN_V2` includes module sequence validation because module changes can alter local device capabilities. Ignoring sequence handling can configure a removed or replaced module based on old capability data.

NVRAM A/B and TSA restrictions are persistent-state hazards. Reading the wrong A/B target while holding the update lock can verify the wrong partition. Attempting restricted updates on TSA-bound adapters should be surfaced as permission errors rather than retried blindly.

## Test Signals

Good test coverage for users of this header should include:

- Compile-time coverage that all command macros used by the SFC driver still resolve and that duplicate command IDs, such as `PORT_RESET`/`ENTITY_RESET`, are intentional.
- MCDI header encode/decode tests for code, resync, data length, sequence, error/response bits, and event-request/doorbell-return flags.
- Event parser tests for command done, DBRET, reboot, link-change v1/v2, module-change sequence, TX/RX flush, PTP time/timestamp events, proxy request/response, dynamic sensors, and descriptor proxy continuation events.
- Response-length tests for legacy versus extended layouts: `GET_VERSION`, `GET_ASSERTS`, `GET_LINK`, `GET_LOOPBACK_MODES`, `MAC_STATS`, `PTP_GET_ATTRIBUTES`, and `NVRAM_INFO`.
- Error-path tests covering MC assert/reboot (`EINTR` or error-shaped reboot responses), proxy-pending handle flow, queue-full retry, no-datapath/no-PCIe, and privilege failures.
- Link/PHY tests that compare `GET_PHY_CFG` capability bits with `GET_LINK`/`GET_LINK_V2` output, then exercise `SET_LINK_V2` with matching, stale, and ignore module sequence values.
- Statistics tests that verify DMA buffer length, generation start/end consistency, zero-initialization behavior, clear behavior, and v2/v3/v4 counter placement.
- PTP tests for time-format negotiation, 64-bit seconds, FP40 versus FP44 frequency adjustment, time-event subscription/unsubscription, sync-status reporting, and timestamp-correction output.
- BIST tests that start a test, poll running/pass/fail/timeout, and only parse variant payloads after validating out length and PHY type.
- NVRAM tests that enumerate partition types, inspect flags/write sizes, start an update, read current/backup A/B targets, write/erase valid chunks, finish with secure verification reporting, handle pending verification, and reject restricted TSA-bound or read-only partitions.
- WoL tests that set each filter layout, verify returned filter IDs, remove specific filters, and reset wake/lights-out classes.

For this repository's research pipeline, the main signal is that `Docs/researches/chunks/subset-b-004638_research.md` is source-tree-aligned and limited to lines 1-5896 of `mcdi_pcol.h`; the final merged per-file document should reconcile this with later chunks before drawing conclusions about commands defined after `MC_CMD_REBOOT_MODE`.

### subset-b-004639: lines 5897-11301

# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_pcol.h lines 5897-11301

## Purpose

This chunk is a generated MCDI protocol contract for the Solarflare/SFC Siena-family NIC driver. It defines command IDs, privilege classes, request/response lengths, field offsets, bit positions, variable-array sizing helpers, and enum values used by host driver code to speak to management-controller firmware. There is no executable C control flow here; the important behavior is the binary ABI described by the macros.

The range covers hardware monitoring, PHY/media queries, lights-out offloads, firmware test/workaround controls, NVRAM metadata, CLP and MUM subprotocols, dynamic sensors, event subscriptions, EVB/buffer-table/license helper structures, EVQ/RXQ/TXQ lifecycle, filter insertion/removal, parser-dispatcher discovery, VI/SR-IOV/PIO allocation, and capability discovery.

## Important APIs, Types, and Protocol Areas

- `MC_CMD_SENSOR_INFO` and `MC_CMD_READ_SENSORS` define the legacy static sensor model. Sensor info is paged, page bit 31 indicates a next page in extended responses, and sensor values are `MC_CMD_SENSOR_VALUE_ENTRY_TYPEDEF` dwords with 16-bit value, 8-bit state, and 8-bit type. States include OK, warning, fatal, broken, no-reading, and init-failed.
- `MC_CMD_DYNAMIC_SENSORS_LIST`, `MC_CMD_DYNAMIC_SENSORS_GET_DESCRIPTIONS`, and `MC_CMD_DYNAMIC_SENSORS_GET_READINGS` define the newer handle-based dynamic sensor API. Handles identify sensors, descriptions carry name/type/limits, readings carry handle/value/state, and the generation count is persistent across reboots and incremented when the table changes.
- `MC_CMD_GET_PHY_STATE`, `MC_CMD_SETUP_8021QBB`, `MC_CMD_GET_PHY_MEDIA_INFO`, and MUM QSFP commands expose PHY health, priority flow control setup, SFP/QSFP media EEPROM-like data, link capability/status, and PHY BIST polling.
- `MC_CMD_WOL_FILTER_GET`, `MC_CMD_ADD_LIGHTSOUT_OFFLOAD`, and `MC_CMD_REMOVE_LIGHTSOUT_OFFLOAD` define WoL and lights-out ARP/IPv6 neighbor-solicitation offload filters. The add call returns a filter ID later used by remove.
- `MC_CMD_TESTASSERT` and `MC_CMD_WORKAROUND` are firmware control/testing hooks. `TESTASSERT_V2` can trigger assertion, watchdog, load/store trap, or invalid jump scenarios. `WORKAROUND` toggles firmware-defined workaround IDs and has special extended output for multicast filter chaining (`BUG26807`) indicating whether FLR was performed.
- `MC_CMD_NVRAM_TEST`, `MC_CMD_NVRAM_PARTITIONS`, `MC_CMD_NVRAM_METADATA`, and `NVRAM_PARTITION_TYPE` enumerate persistent flash partitions and metadata. Partition IDs include MC firmware, expansion ROM, static/dynamic config, logs, dumps, license storage, PHY partitions, FPGA/FC/MUM/SUC partitions, factory defaults, FRU, bundle partitions, recovery map, and partition map.
- `MC_CMD_CLP` multiplexes CLP operations including setting/getting MAC and boot options. The input operation enum distinguishes no-op, set/get MAC, set/get boot, and V2 MAC forms.
- `MC_CMD_MUM` is an insecure/admin-oriented subprotocol for the MUM/SUC controller. It includes raw/read/write/register access, logging, GPIO read/write/config/enable, sensor reads, clock programming, FPGA load control, ATB sensor read, QSFP operations, and DDR information reporting.
- Shared structures include `EVB_PORT_ID`, `EVB_VLAN_TAG`, `BUFTBL_ENTRY`, `LICENSED_APP_ID`, `LICENSED_FEATURES`, `LICENSED_V3_APPS`, `LICENSED_V3_FEATURES`, `TX_TIMESTAMP_EVENT`, `RSS_MODE`, `CTPIO_STATS_MAP`, and `QUEUE_CRC_MODE`.
- `MC_CMD_INIT_EVQ`, `MC_CMD_INIT_RXQ`, and `MC_CMD_INIT_TXQ` define queue creation. EVQs accept timer/count/interrupt configuration and 4K-aligned DMA page arrays. RXQs support legacy and extended V3/V4/V5 layouts, packed stream, equal-stride super-buffer mode, snapshot mode, event merging, outer classification requests, QDMA buffer-size selection, and prefix selection. TXQs support checksum modes, timestamps, pacer bypass, inner checksum flags, TSOv2, CTPIO, M2M D2C, descriptor proxy, and Qbb flags.
- `MC_CMD_FINI_EVQ`, `MC_CMD_FINI_RXQ`, and `MC_CMD_FINI_TXQ` tear down queue instances previously created by the corresponding init commands.
- `MC_CMD_ALLOC_BUFTBL_CHUNK`, `MC_CMD_PROGRAM_BUFTBL_ENTRIES`, and `MC_CMD_FREE_BUFTBL_CHUNK` manage Onload buffer table resources by owner ID, page size, chunk handle, first ID, and DMA addresses.
- `MC_CMD_FILTER_OP` is the main filter ABI. It supports insert/remove/subscribe/unsubscribe/replace, opaque 64-bit handles, port/v-adaptor binding, match-field bitmasks, RX destinations, RX modes, RSS or dot1p contexts, TX destination controls, MAC/port/EtherType/VLAN/IP fields, unknown multicast/unicast matches, VXLAN/NVGRE/Geneve encapsulation matches in the extended forms, and DPDK `rte_flow` flag/mark actions in V3.
- `MC_CMD_GET_PARSER_DISP_INFO` returns parser-dispatcher capabilities: supported RX match masks, insertion restrictions, security-rule info, supported encapsulated matches, and VNIC encapsulation rule matches.
- `MC_CMD_ALLOC_VIS`, `MC_CMD_FREE_VIS`, `MC_CMD_GET_VI_ALLOC_INFO`, `MC_CMD_DUMP_VI_STATE`, `MC_CMD_ALLOC_PIOBUF`, and `MC_CMD_FREE_PIOBUF` manage VI and PIO resources and expose diagnostic state for queue backing tables and metadata.
- `MC_CMD_GET_SRIOV_CFG` and `MC_CMD_SET_SRIOV_CFG` expose PF/VF enablement, VF count, RID offset, and stride. Set is admin-only.
- `MC_CMD_GET_CAPABILITIES` and `GET_CAPABILITIES_V2` expose feature flags and firmware identity for RX/TX datapath CPUs and packet-dispatch firmware. Flags gate EVB, VXLAN/NVGRE, Qbb, RSS modes, packed-stream, timestamps, batching, VLAN insertion/stripping, TSO, RX prefix lengths, event merging, multicast filter chaining, and other datapath features.

## Control Flow and Lifetimes

The host driver builds MCDI request buffers using these offsets and length macros, sends command IDs to firmware, and parses response buffers by the matching output layouts. Sequencing is implied by resource lifetimes:

- Probe/configuration code queries capabilities, resource limits, port assignment, MAC address allocation, sensors, PHY state, media info, parser-dispatcher capabilities, SR-IOV state, and NVRAM partitions/metadata.
- Runtime datapath setup allocates VIs, creates EVQs, creates RXQs/TXQs backed by DMA page arrays, programs buffer table chunks for Onload paths, installs filters, and optionally allocates PIO buffers.
- Runtime monitoring reads legacy or dynamic sensors and listens for sensor/link/reboot/FW alert event classes via `MC_CMD_EVENT_CTRL`.
- Shutdown/error paths remove filters, free PIO/buffer-table resources, finish TXQ/RXQ/EVQ instances, and free VIs.
- Special test and recovery paths can generate driver events, dump VI state, read MC registers, deliberately crash firmware, toggle firmware workarounds, restore MAC state after reset, or manipulate MUM hardware controls.

Resource handles are firmware-owned and opaque to the host: filter handles, buffer-table chunk handles, PIO buffer handles, VI base/count, lights-out filter IDs, dynamic sensor handles, RSS/dot1p context IDs referenced by filters, and queue instance IDs. The header repeatedly documents that handles should be considered opaque and that sentinel all-ones values are invalid for filter handles.

## State and Persistence Behavior

Most commands describe volatile runtime state inside the NIC firmware: queue tables, filter tables, VI allocation, PIO buffers, buffer table entries, event subscriptions, port assignment, and SR-IOV configuration. These must be reconstructed after reset or firmware reboot unless the broader driver has explicit persistence logic.

Persistent or semi-persistent areas in this chunk are:

- NVRAM partition contents and metadata, including firmware, configuration, logs, licenses, bundle state, factory defaults, and partition maps.
- Dynamic sensor generation count, which the comments state is maintained by the MC, persistent across reboots, and incremented whenever the sensor table changes.
- Sensor limit programming through `MC_CMD_SENSOR_SET_LIMS`, marked as a warranty-voiding insecure operation.
- MUM/SUC GPIO, clock, FPGA-load, firmware, boot ROM, production/user ROM, fuses/lockbits, and DDR state, where some effects may outlive a single host driver session depending on underlying hardware/firmware.

## Dependencies and Integration Points

The macros depend on the driver MCDI transport and packing helpers elsewhere in the SFC driver. Consumers must use the offset/length/LBN/WIDTH definitions consistently with kernel endianness helpers and MCDI buffer accessors.

Privilege categories (`SRIOV_CTG_GENERAL`, `LINK`, `ADMIN`, `INSECURE`, `ONLOAD`) are integration boundaries for PF/VF and management policy. General calls are available for ordinary driver operation; link/admin/insecure/onload calls must be guarded by privilege checks and feature discovery.

Important cross-protocol dependencies include:

- Queue commands depend on VI allocation, interrupt/vector allocation, DMA mapping, and 4K-aligned host memory pages.
- Filter RX modes depend on RSS context allocation or dot1p mapping allocation commands defined outside this chunk.
- Filter extension support depends on parser-dispatcher discovery and capability flags such as VXLAN/NVGRE and DPDK firmware IDs.
- Dynamic sensors tie into unsolicited `CODE_DYNAMIC_SENSORS_CHANGE` events and event-control subscription.
- Legacy sensor state ties into `SENSOREVT` events and page-aware sensor info discovery.
- TX/RX timestamp fields and CTPIO events integrate with event queue parsing and PTP/timestamp feature licensing.
- `GET_CAPABILITIES` gates use of advanced queue flags, packed-stream, RSS, timestamps, VLAN, TSO, Qbb, EVB, and overlay filtering.
- NVRAM metadata integrates with update, diagnostics, license, and firmware-management tooling outside this chunk.

## Risks and Edge Cases

- ABI drift is the core risk. Any offset, length, enum, or bit-position mismatch will corrupt MCDI requests or misparse firmware responses.
- Variable-length responses have MCDI v1/v2 maxima. Callers must use the `_LEN(num)` and `_NUM(len)` helpers and avoid assuming all entries fit in a legacy 252-byte response.
- Sensor APIs are split between legacy paged masks and dynamic handle-based sensors. A driver using the wrong path for a capability can miss sensors or mishandle change events.
- DMA-backed commands require correct DMA address width, alignment, buffer length, and lifetime. `READ_SENSORS` requires a 4K-aligned buffer unless using the all-ones cmdclient response path; queue init requires arrays of 4K-aligned page addresses.
- Queue init variants are easy to misuse: some fields are ignored in packed-stream/equal-stride modes, V4 buffer size is QDMA-specific, V5 prefix selection is newer, and firmware may override EVQ flags in low-latency/throughput/auto modes.
- Filter programming is high-risk because match-field bitmasks must correspond exactly to filled fields. Encapsulation matches require different field sets, VNI/VSID type encoding, and firmware variant support. DPDK match actions fail on non-DPDK firmware and mark values must be within capability-reported limits.
- `MC_CMD_WORKAROUND_BUG26807` can FLR functions with installed filters for admin callers. Client code must treat this as disruptive state loss and not as a simple feature toggle.
- `MC_CMD_TESTASSERT`, `MC_CMD_READ_REGS`, `MC_CMD_MUM`, and `MC_CMD_SENSOR_SET_LIMS` are admin/insecure/debug surfaces and should not be exposed to untrusted paths.
- Some comments call out older firmware that does not understand newer workaround IDs. Callers should treat `EINVAL`/`ENOTSUP` according to the documented compatibility guidance.
- Opaque handles can change on filter replace, and all-ones is guaranteed invalid. Callers must update stored handles from responses rather than deriving or reusing stale values.
- SR-IOV RID offset/stride fields allow zero for no-change and `MC_CMD_RESOURCE_INSTANCE_ANY` for firmware allocation; confusing these values can produce invalid VF topology.

## Test Signals

Useful validation signals for code using this chunk:

- Compile-time checks that MCDI request/response buffer sizes match `_LEN`, `_LENMIN`, `_LENMAX`, and variant-specific constants.
- Probe tests that call `GET_CAPABILITIES`, select only supported queue/filter/sensor paths, and reject unsupported advanced flags gracefully.
- Sensor tests covering legacy page 0, extended multi-page masks, dynamic sensor list/description/reading batches, generation-count changes, and dropped stale handles.
- Queue lifecycle tests that allocate VIs, init EVQ/RXQ/TXQ with aligned DMA pages, process events, and then finish/free resources in reverse order.
- Filter tests for insert/remove/replace, opaque handle update, RSS and simple RX modes, unknown unicast/multicast filters, overlay VNI/VSID matches, and parser-dispatcher supported-match discovery.
- Reset/reboot tests ensuring queues, filters, VI allocation, PIO buffers, lights-out offloads, and event subscriptions are recreated or cleaned up after MC reboot.
- Negative tests for unsupported firmware variants, privilege failures, bad lengths, insufficient DMA buffer lengths, too many variable-array entries, invalid handles, and invalid filter mark values.
- Debug-path tests should verify `TESTASSERT` handling only in controlled environments and confirm the driver reports firmware assertion/watchdog/trap outcomes without assuming normal command completion.

### subset-b-004640: lines 11302-15705

# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_pcol.h lines 11302-15705

## Chunk Scope

This chunk is a generated-style MCDI protocol ABI slice for the Solarflare/Xilinx
SFC Siena/EF10 family. It contains no executable functions; it publishes command
IDs, message lengths, byte offsets, bit positions, field widths, enum values,
and privilege categories consumed by the host driver when building management
controller requests and decoding firmware replies.

The range starts inside `MC_CMD_GET_CAPABILITIES_V2_OUT` and continues through
versioned capability response layouts V3 through V9, then defines the MCDI v2
extended-command wrapper, PIO-buffer link/unlink commands, EVB/vSwitch/vPort/
vAdaptor provisioning commands, 64-bit region address read/write, Onload stack
handle allocation, and RSS context allocation/configuration through the opening
of `MC_CMD_RSS_CONTEXT_GET_FLAGS_OUT`.

## Purpose and Responsibilities

- Preserve the firmware/driver wire format for feature discovery. The
  `MC_CMD_GET_CAPABILITIES_V*_OUT` layouts are append-only response variants;
  each later version repeats the earlier fields and adds new tail fields that
  callers must read only after checking the returned response length.
- Expose datapath feature flags and hardware resource limits: RX/TX datapath
  firmware IDs, RX/TX PD firmware type/revision, hardware and license
  capabilities, flags1/flags2/flags3 bits, PF-to-port and VF-per-PF arrays,
  VIs per port, descriptor-cache sizes, PIO buffer count/size, VI window mode,
  VFIFO stuffing resources, MAC statistics count, filter mark maximum,
  guaranteed RX buffer sizes, WOL/RSS/MAE/vDPA/event-credit flags, and V9 RSS
  table pool limits.
- Define the `MC_CMD_V2_EXTN` v1-compatible encapsulation used to carry extended
  command numbers and actual payload lengths, including MC-directed and
  TSA-directed message types.
- Define control-plane commands for resources used by EF10 and related devices:
  PIO buffers bound to TX queues, virtual switches, virtual ports, virtual
  adaptors, EVB port assignment to PF/VF functions, A64 BAR/region addresses,
  Onload stack IDs, and RSS contexts.
- Record SR-IOV privilege categories for each command. PIO and Onload stack
  commands are `SRIOV_CTG_ONLOAD`, most EVB/vSwitch/vPort/vAdaptor/RSS commands
  are `SRIOV_CTG_GENERAL`, and `MC_CMD_RDWR_A64_REGIONS` is `SRIOV_CTG_ADMIN`.

## Important APIs, Types, and Constants

- Capability response versions:
  `MC_CMD_GET_CAPABILITIES_V2_OUT_LEN`, `V3_OUT_LEN`, `V4_OUT_LEN`,
  `V5_OUT_LEN`, `V6_OUT_LEN`, `V7_OUT_LEN`, `V8_OUT_LEN`, and `V9_OUT_LEN`
  define progressively larger response layouts. V3 adds `VI_WINDOW_MODE` and
  VFIFO stuffing counts. V4/V5 expose MAC stats count and filter mark maximum
  offsets. V6/V7 add guaranteed RX buffer sizes and flags3. V8 adds
  `TEST_RESERVED`. V9 adds detailed RSS indirection-table and context limits.
- Capability flags:
  flags1 advertise packet/queue/filter features such as vPort reconfigure, TX
  striping, vAdaptor query, EVB VLAN restriction, enhanced MAC programming,
  additional RSS modes, RX packed stream, RX FCS inclusion, VLAN insertion/
  stripping, TSO, timestamping, RX batching, multicast filter chaining, EVB, and
  VXLAN/NVGRE support. flags2 advertise later features including TSOv2/TSOv3,
  encapsulated TSO, event/RX cut-through, VFIFO ULL mode, timestamp and sniff
  modes, NVRAM verify reporting, MCDI background/doorbell return, CTPIO, TSA,
  adapter authentication, filter action flag/mark, equal-stride buffers, L3XUDP,
  VI spreading, RX queue buffer-size requirements, bundle update, and dynamic
  sensors. flags3 carries WOL Etherwake, RSS even spreading, selectable RSS
  table size, MAE, vDPA, per-encap VLAN stripping, extended-width EVQs, and
  unsolicited event credit.
- Firmware identity enums:
  `RXDP_*`, `TXDP_*`, `RXPD_FW_TYPE_*`, and `TXPD_FW_TYPE_*` distinguish
  standard, low-latency, packed-stream, rules-engine, DPDK, BIST, test, legacy
  Siena-compatible, full-featured/vSwitch, and L3XUDP firmware variants.
- Topology/resource fields:
  `PFS_TO_PORTS_ASSIGNMENT` and `NUM_VFS_PER_PF` are 16-byte arrays with
  sentinel values such as `ACCESS_NOT_PERMITTED`, `PF_NOT_PRESENT`,
  `PF_NOT_ASSIGNED`, and `INCOMPATIBLE_ASSIGNMENT`. `NUM_VIS_PER_PORT` has four
  16-bit entries. `VI_WINDOW_MODE_*` distinguishes 8K, 16K, and 64K VI windows;
  the comments state that CTPIO is unavailable with 8K windows.
- `MC_CMD_V2_EXTN`:
  command `0x7f` wraps a 15-bit extended command number, 10-bit actual length,
  and 4-bit message type. `mcdi.c` uses these fields when command IDs exceed
  the v1 header range or when payload length must be represented outside the
  v1 header.
- PIO and Onload commands:
  `MC_CMD_LINK_PIOBUF` links an allocated push-I/O buffer handle to a function
  local TXQ/VI instance. `MC_CMD_UNLINK_PIOBUF` unlinks by TXQ instance.
  `MC_CMD_ONLOAD_STACK_ALLOC` and `MC_CMD_ONLOAD_STACK_FREE` allocate/free an
  opaque Onload stack ID attached to an upstream port.
- EVB/vSwitch/vPort/vAdaptor commands:
  `MC_CMD_VSWITCH_ALLOC/FREE/QUERY`, `MC_CMD_VPORT_ALLOC/FREE`,
  `MC_CMD_VADAPTOR_ALLOC/FREE/SET_MAC/GET_MAC/QUERY`, and
  `MC_CMD_EVB_PORT_ASSIGN` define the virtual switching ABI used for SR-IOV and
  vPort filters. These commands carry upstream port IDs, vSwitch/vPort type
  enums, VLAN tag counts and packed VLAN tag fields, auto-port/auto-vAdaptor
  flags, VLAN restriction, set-MAC permission flags, six-byte MAC addresses, and
  PF/VF function selectors.
- Register region command:
  `MC_CMD_RDWR_A64_REGIONS` reads and optionally writes four 32-bit region
  address values. The request includes a 4-bit write mask at byte offset 16; the
  response always returns all four region values.
- RSS commands:
  `MC_CMD_RSS_CONTEXT_ALLOC` and `_V2_IN` allocate exclusive, shared, or
  even-spreading RSS contexts and return an opaque `RSS_CONTEXT_ID`, with
  `0xffffffff` reserved as invalid. `MC_CMD_RSS_CONTEXT_FREE` frees it.
  `MC_CMD_RSS_CONTEXT_SET_KEY/GET_KEY` transfer the 40-byte Toeplitz key.
  `MC_CMD_RSS_CONTEXT_SET_TABLE/GET_TABLE` operate on the legacy fixed
  128-entry table. `MC_CMD_RSS_CONTEXT_WRITE_TABLE/READ_TABLE` operate on
  selectable-size tables with variable length arrays and MCDI2 larger maximums.
  `MC_CMD_RSS_CONTEXT_SET_FLAGS/GET_FLAGS` configure hash enable bits and the
  newer per-packet-type RSS mode nibbles.

## Control Flow and Protocol Flow

This header does not implement runtime control flow, but the constants encode
the control flow that the SFC driver follows:

- Firmware capability probing sends `MC_CMD_GET_CAPABILITIES` and branches on
  the response length before reading later-version offsets. For example,
  `ef10.c` reads flags2 and PIO size only when the output is at least V2, reads
  `VI_WINDOW_MODE` only when at least V3, and reads MAC statistics count only
  when at least V4. `ef100_nic.c` similarly checks for V7 before consuming
  flags3.
- Command marshalling is table-driven through `MCDI_SET_*`, `MCDI_DWORD`,
  `MCDI_WORD`, `MCDI_BYTE`, `MCDI_PTR`, and `MCDI_POPULATE_DWORD_*` helper
  macros that take the suffixes defined here. A command wrapper fills fixed-size
  buffers using the offsets in this header, calls `efx_mcdi_rpc()` or
  `efx_mcdi_rpc_quiet()`, checks `outlen`, and then stores decoded IDs/flags in
  NIC state.
- MCDI v2 flow in `mcdi.c` wraps extended requests with `MC_CMD_V2_EXTN`,
  places the extended command number and actual length into the v2 extension
  dword, and validates that responses either match the extended wrapper or fit
  the expected command/length path.
- SR-IOV and EVB setup allocates a vSwitch on an upstream port, then allocates
  vPorts with VLAN insertion/removal parameters, and then may allocate or query
  vAdaptors and assign EVB ports to PF/VF functions. `ef10_sriov.c` uses these
  layouts for VF vPort provisioning, fallback from two VLAN tags to one, and
  vPort teardown.
- PIO setup links a firmware-allocated PIO buffer handle to a TXQ instance and
  unlinks it during teardown. `ef10.c` has compile-time size checks for zero
  length link/unlink responses and reuses the larger link request buffer for
  unlinking.
- RSS setup allocates an RSS context for the current vPort, configures the
  128-entry indirection table and 40-byte Toeplitz key, optionally sets
  additional RSS modes when the capability bit is present, and frees the context
  during teardown. Selectable table commands are the newer path when firmware
  reports `RSS_SELECTABLE_TABLE_SIZE`.

## State and Persistence Behavior

The state described here is firmware-owned or firmware-persistent for the
duration of the resource lifetime, with opaque host handles stored by driver
state:

- Capability responses are snapshots of NIC firmware state and hardware
  configuration. The driver caches selected bits and resource values in NIC
  private data, such as datapath caps, caps2/caps3, PIO buffer size, VI stride,
  firmware IDs, MAC stats count, and RSS limits.
- vSwitches, vPorts, vAdaptors, EVB assignments, PIO-buffer links, Onload stack
  IDs, and RSS contexts persist inside the management controller until matching
  free/unlink commands or function reset/firmware cleanup. The protocol exposes
  these through opaque port, vPort, stack, PIO, and RSS context IDs.
- RSS context configuration persists in firmware across packet processing:
  context type, queue count, optional selectable indirection table allocation,
  Toeplitz key, table entries, and hash mode flags determine how subsequent
  filters and RX packets are spread across queues.
- Some command semantics intentionally depend on older firmware behavior.
  `RSS_CONTEXT_GET_FLAGS` can use caller-provided default flags because older
  firmware may not fill the flags field; `RSS_CONTEXT_SET_FLAGS` must not set
  mode nibbles unless `ADDITIONAL_RSS_MODES` is reported because older firmware
  rejects flags values above `0xff`.

## Dependencies and Integration Points

- Included by SFC driver code that uses MCDI protocol helpers, especially
  `drivers/net/ethernet/sfc/ef10.c`, `ef10_sriov.c`, `mcdi.c`,
  `mcdi_filters.c`, `ef100_nic.c`, and matching Siena code paths.
- Depends on the MCDI buffer accessor layer generated around these suffixes:
  `MCDI_DECLARE_BUF`, `MCDI_SET_DWORD`, `MCDI_POPULATE_DWORD_*`,
  `MCDI_DWORD`, `MCDI_WORD`, `MCDI_BYTE`, and `MCDI_PTR`. The header itself
  only supplies offsets, lengths, and bit numbers.
- Integrates with Linux netdev feature setup, SR-IOV VF provisioning, vPort
  filter programming, hardware timestamping, VLAN offloads, TSO/encapsulation
  offloads, RX queue creation, MAC statistics DMA sizing, PIO/CTPIO transmit
  paths, Onload acceleration resources, and RSS/ethtool indirection/hash
  configuration.
- Firmware compatibility is central: comments repeatedly mark fields as absent
  on older firmware and direct callers to check returned length. Production
  drivers must treat `TEST_RESERVED` as opaque and must not infer unsupported
  capabilities from unreported tail fields.

## Risks and Edge Cases

- ABI drift is high risk. Any changed offset, length, bit position, or enum
  value can silently misprogram firmware because host buffers are densely packed
  binary MCDI messages.
- Versioned capability parsing must remain length guarded. Reading V3/V4/V7/V9
  fields from shorter firmware responses can decode uninitialized stack bytes
  and enable unsupported features.
- Several fields have compatibility sentinels or fallbacks. PF assignment
  `INCOMPATIBLE_ASSIGNMENT` should be treated like not assigned by old drivers;
  missing V3 VI window mode should keep the legacy/default VI stride; missing
  MAC stats count should fall back to the older fixed statistic count.
- RSS mode flags are a compatibility trap. Additional mode nibbles are valid
  only when `ADDITIONAL_RSS_MODES` is present, while legacy `_EN` bits are the
  backwards-compatible representation.
- RSS table commands have two incompatible table models. The fixed
  `SET_TABLE/GET_TABLE` ABI is only for 128-entry tables; selectable-size
  firmware requires `WRITE_TABLE/READ_TABLE` index/value arrays and V9 min/max
  table-size limits.
- Resource lifetime leaks or double frees can leave firmware vSwitch, vPort,
  vAdaptor, PIO, Onload, or RSS resources allocated after driver teardown.
  Teardown paths must tolerate partial allocation failures and opaque invalid
  IDs.
- Privilege category mistakes can expose administrative operations to VFs or
  deny legal VF/Onload operations. `RDWR_A64_REGIONS` is explicitly admin-only.
- VLAN tag count and packed tag fields must match vSwitch/vPort restrictions;
  firmware returns errors when requested transparent insertion/removal is
  incompatible with the upstream vSwitch.

## Test Signals

- Build-time: compile the SFC driver with `BUILD_BUG_ON` checks around command
  lengths, especially PIO link/unlink, RSS key/table lengths, and capability
  output buffer sizes.
- Capability probing: exercise firmware responses at V2, V3, V4, V7, V8, and
  V9 lengths and verify the driver only consumes fields present in `outlen`,
  sets VI stride correctly for 8K/16K/64K modes, and preserves fallback defaults
  for older firmware.
- Feature gating: verify flags1/flags2/flags3 bits enable only matching
  netdev/driver features such as VLAN offloads, TSO variants, timestamping,
  CTPIO, RX queue buffer-size handling, WOL, RSS even spreading, selectable RSS
  tables, and extended-width EVQs.
- SR-IOV/EVB: create and remove vSwitches, vPorts, and vAdaptors for PF and VF
  paths, including VLAN-restricted vPorts, one-tag/two-tag fallback, MAC set/get
  or query behavior, EVB port assignment, and cleanup after intermediate
  firmware failures.
- PIO/Onload: allocate/link/unlink PIO buffers across TXQ instances and
  allocate/free Onload stack IDs, including failure injection and teardown with
  partially linked resources.
- RSS: allocate exclusive and shared contexts, skip shared context allocation
  for one-queue spread, program/read back 128-entry tables and 40-byte keys,
  set/get legacy enable bits and additional mode nibbles, test rejection when
  modes are sent without `ADDITIONAL_RSS_MODES`, and exercise selectable table
  read/write with boundary indices and MCDI2 maximum payload sizes.
- Negative protocol tests: short output buffers should produce `-EIO` or
  capability fallback, invalid opaque handles should fail cleanly, resource
  exhaustion in V2 RSS table-pool allocation should surface `ENOSPC`, and
  admin-only A64 region writes should be denied outside the proper privilege.

### subset-b-004641: lines 15706-17204

# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_pcol.h lines 15706-17204

## Chunk Scope

This chunk is the final range of the Siena copy of the Solarflare/Xilinx SFC
MCDI protocol header. It is generated ABI material rather than executable C:
the file defines Management Controller Diagnostic Interface command IDs,
privilege categories, request/response sizes, field offsets, bit positions,
array length helpers, and enum values. Driver code uses these constants through
the `MCDI_*` accessor macros when composing firmware RPC payloads and parsing
firmware responses.

The range starts with the tail of `MC_CMD_RSS_CONTEXT_GET_FLAGS` output flags,
then covers vPort MAC/VLAN management, EVB port query, clock and interrupt
commands, shmboot/offline BIST/PSU/fuse diagnostics, classic and V3 licensing,
parser-dispatcher configuration, port-mode and workaround queries, privilege
and VF link-state controls, tunnel encapsulation UDP port programming, VNIC
encapsulation rules, and final generic function/personality structures before
the header guard closes.

## Purpose and Responsibilities

- Publish the wire layout for late MCDI commands used by EF10/Medford-era and
  later SFC driver code while preserving the legacy Siena source-tree copy.
- Give host code stable symbolic names for command numbers such as
  `MC_CMD_GET_FUNCTION_INFO`, `MC_CMD_LICENSING_V3`,
  `MC_CMD_SET_TUNNEL_ENCAP_UDP_PORTS`, `MC_CMD_PRIVILEGE_MASK`, and
  `MC_CMD_VNIC_ENCAP_RULE_ADD`.
- Encode SR-IOV privilege requirements with `MC_CMD_0x*_PRIVILEGE_CTG`
  definitions, separating general commands from admin and insecure operations.
- Define variable-length payload calculations for arrays of MAC addresses,
  fuse bytes, license IDs, licensed-app arguments/results, parser-dispatcher
  values, and tunnel encapsulation entries.
- Preserve cross-version protocol compatibility: for example RSS context flags
  expose both old `_EN` bits and newer `_RSS_MODE` fields, licensing exposes
  both pre-V3 and V3 commands, and several responses provide MCDI2 larger
  maximum lengths.

## Important APIs, Types, and Constants

- RSS context flags:
  `MC_CMD_RSS_CONTEXT_GET_FLAGS_OUT_FLAGS_*` defines four legacy Toeplitz
  enable bits and six 4-bit mode fields for TCP/UDP/other over IPv4/IPv6. The
  comment establishes the compatibility rule: new drivers should trust the
  `_RSS_MODE` fields, while old enable bits remain consistent for fresh
  contexts and old-style SET operations.
- vPort MAC and VLAN operations:
  `MC_CMD_VPORT_ADD_MAC_ADDRESS`, `MC_CMD_VPORT_DEL_MAC_ADDRESS`, and
  `MC_CMD_VPORT_GET_MAC_ADDRESSES` operate on a 32-bit vPort handle and 6-byte
  MAC addresses. `GET_MAC_ADDRESSES_OUT` is variable length, with 41 legacy
  entries or 169 MCDI2 entries. `MC_CMD_VPORT_RECONFIGURE` can replace VLAN
  tags and/or up to four MAC addresses on an existing vPort and reports
  `RESET_DONE` if firmware reset the vPort user before applying changes.
- EVB, function identity, clocks, and interrupts:
  `MC_CMD_EVB_PORT_QUERY` returns vPort flags and available VLAN tag count.
  `MC_CMD_GET_CLOCK` returns system and DPCPU frequencies in MHz.
  `MC_CMD_TRIGGER_INTERRUPT` asks firmware to prod a BIU interrupt level
  relative to the function base. `MC_CMD_GET_FUNCTION_INFO` reports PF and VF
  indexes for the calling function.
- Admin, insecure, and diagnostic controls:
  `MC_CMD_SHMBOOT_OP` supports shmboot operations such as pushing Greenport
  slave data. `MC_CMD_ENABLE_OFFLINE_BIST` enters a destructive offline BIST
  mode where queues are torn down and the only exit is reboot.
  `MC_CMD_SET_PSU`, `MC_CMD_READ_FUSES`, and `MC_CMD_FUSE_DIAGS` are marked
  insecure and expose voltage rail programming, OTP fuse reads, and fuse
  mismatch/checksum diagnostics.
- Licensing:
  `MC_CMD_LICENSING` reports classic license key counts and self-test status.
  `MC_CMD_LICENSING_V3` reports V3 key counts, private diagnostic state,
  self-test status, and 64-bit licensed application/feature masks.
  `MC_CMD_LICENSING_GET_ID_V3` returns license type plus a variable-length
  unique license ID. `MC_CMD_GET_LICENSED_APP_STATE`,
  `MC_CMD_GET_LICENSED_V3_APP_STATE`, and
  `MC_CMD_GET_LICENSED_V3_FEATURE_STATES` query current application or feature
  state, with explicit notes that update-license operations or MC reboot can
  invalidate cached state.
- Licensed app operations:
  `MC_CMD_LICENSED_APP_OP` is the classic extensible app operation wrapper with
  validate and mask variants. `MC_CMD_LICENSED_V3_VALIDATE_APP` validates a V3
  app using a 48-byte challenge and returns a 96-byte ECDSA signature, expiry
  information, base NIC MAC address, and current vAdaptor MAC address.
  `MC_CMD_LICENSED_V3_MASK_FEATURES` is an admin command for masking licensed
  features on or off. `MC_CMD_LICENSING_V3_TEMPORARY` installs, clears, or
  polls a temporary V3 license that survives MC reboot but is erased by power
  cycle.
- Parser-dispatcher and port modes:
  `MC_CMD_SET_PARSER_DISP_CONFIG` and `MC_CMD_GET_PARSER_DISP_CONFIG` update
  or read settings keyed by type and entity, including TXQ multicast UDP
  destination lookup and vAdaptor self-TX suppression. `MC_CMD_GET_PORT_MODES`
  returns production/default/current port modes, and V2 adds engineering modes.
  `MC_CMD_OVERRIDE_PORT_MODE` stores an admin override in persistent DMEM for
  subsequent warm MC reboots, with cold reboot clearing the override.
- Workarounds and privileges:
  `MC_CMD_GET_WORKAROUNDS` returns implemented and enabled workaround bitmasks
  for hardware/firmware bug IDs. `MC_CMD_PRIVILEGE_MASK` reads or conditionally
  sets a function's privilege mask when `DO_CHANGE` is present, covering admin,
  link, Onload, PTP, filtering, spoofing, MAC-change, unrestricted VLAN,
  insecure, and TSA-unbound admin groups. `MC_CMD_PRIVILEGE_MODIFY` applies add
  and remove masks to groups of PCIe functions. `MC_CMD_LINK_STATE_MODE`
  reads/sets VF link mode as auto, forced up, forced down, or read-only.
- Tunnel encapsulation:
  `TUNNEL_ENCAP_UDP_PORT_ENTRY` packs a 16-bit UDP port and 16-bit protocol
  selector, with standard VXLAN (`0x12b5`) and Geneve (`0x17c1`) values.
  `MC_CMD_SET_TUNNEL_ENCAP_UDP_PORTS` programs up to 16 entries, can unload
  the parser configuration, and reports whether firmware is resetting
  functions as a consequence.
- VNIC encapsulation rules:
  `MC_CMD_VNIC_ENCAP_RULE_ADD` defines per-VNIC encapsulation detection rules
  for RX checksum validation and inner-packet parsing. Match bits cover
  ethertype, outer VLAN, destination IP, IP protocol, and destination port.
  Fields store network-order IPv4/IPv6 ethertype/IP/port data, optional outer
  VLAN VID, a strip-outer-VLAN action bit, and a MAE encapsulation type. The
  output handle is later passed to `MC_CMD_VNIC_ENCAP_RULE_REMOVE`.
- Final structure definitions:
  `FUNCTION_PERSONALITY` stores a 32-bit personality ID for EF100, virtio-net,
  virtio-blk, acceleration management, and acceleration user functions.
  `PCIE_FUNCTION` stores an 8-byte interface/PF/VF tuple with wildcard and
  null sentinels plus host/AP interface selectors.

## Control Flow and Protocol Flow

This header chunk has no C branches or call graph. Runtime control flow is
encoded as firmware command sequences invoked through `efx_mcdi_rpc()` and
related quiet variants.

- vPort MAC discovery/update flow builds an input payload with the vPort ID,
  sends `VPORT_GET_MAC_ADDRESSES` to learn current MACs, and bounds response
  parsing by both `outlen` and `MACADDR_COUNT`. Adding a MAC uses
  `VPORT_ADD_MAC_ADDRESS`; full replacement uses `VPORT_RECONFIGURE`, after
  which callers must handle possible function reset indicated by
  `RESET_DONE`.
- Function initialization flow commonly calls `GET_FUNCTION_INFO` early to
  determine PF/VF identity. The main SFC tree consumes this in `ef10.c`,
  `mcdi.c`, and `mcdi_functions.c` to populate PF/VF indexes and to handle
  firmware that may not support the command.
- Licensing flow starts with `LICENSING` or `LICENSING_V3` reporting installed
  key/app/feature state. `LICENSING_V3` can return `EAGAIN` while update
  processing is in progress. Individual app/feature state commands then query
  masks, and validation commands exchange challenge/response payloads. Temporary
  license installation is explicitly asynchronous: send SET, then poll STATUS
  until OK, IN_PROGRESS, or ERROR.
- Parser and tunnel flow programs parser-dispatcher state before traffic
  depends on it. `SET_TUNNEL_ENCAP_UDP_PORTS` builds an entries array and may
  trigger function resets; driver code must treat the `RESETTING` output flag
  as a synchronization signal rather than assuming the configuration is a
  local-only update.
- Privilege and VF link management flow addresses target PCIe functions by
  packed PF/VF fields. `PRIVILEGE_MASK` can be read-only or write depending on
  the MSB in `NEW_MASK`; `PRIVILEGE_MODIFY` applies bulk changes to groups.
  `LINK_STATE_MODE` uses `DO_NOT_CHANGE` for read-only queries and otherwise
  writes VF-visible link state policy.
- Workaround flow reads firmware-implemented and enabled masks. The main SFC
  tree uses this to toggle driver behavior for unsafe EVQ writes, broken EVQ
  timer writes, multicast filter chaining, and older firmware that lacks the
  command.
- VNIC encapsulation flow first discovers supported match combinations through
  the parser-dispatcher information command defined earlier in the header, then
  adds non-overlapping rules. Returned handles are the only remove keys, so the
  driver must persist them for cleanup.

## State and Persistence Behavior

- vPort MAC/VLAN configuration is firmware-owned state tied to vPort handles.
  `VPORT_RECONFIGURE` can reset the vPort's user function, so state changes may
  have broader device-visible effects than a local table update.
- Licensing state lives in firmware and NVRAM license partitions. V3 reports
  aggregate key/app/feature masks, but command comments make clear that cached
  app/feature states can be invalidated by license update operations or MC
  reboot. Temporary V3 licenses are stored in MC persistent data, survive MC
  reboot, and are erased on adapter power cycle or explicit clear.
- `OVERRIDE_PORT_MODE` stores override data in the persistent section of DMEM
  and activates it on next warm MC reboot. Cold reboot clears it, and the
  override does not change PF configuration, so invalid port/PF mappings remain
  a host/firmware integration risk.
- Fuse data and fuse diagnostics expose OTP and hardware-programmed state.
  Reads are bounded by requested offset/length and response maximums, while
  diagnostics summarize mismatched or unexpectedly clear bits across fuse
  areas.
- Privilege masks and VF link-state modes are firmware policy state for target
  PCIe functions. Admin functions may observe all privileges, while secure
  adapters can still reject insecure command groups regardless of mask bits.
- Tunnel encapsulation UDP port mappings and VNIC encapsulation rules configure
  parser/VNIC hardware state. Tunnel port programming is global enough to cause
  all functions to see a reset, whereas VNIC encapsulation rules are per-driver
  or per-VNIC and have finite table capacity.
- `FUNCTION_PERSONALITY` and `PCIE_FUNCTION` are reusable value encodings, not
  persistent state by themselves; they are embedded in other MCDI protocols for
  function allocation, discovery, and device personality selection.

## Dependencies and Integration Points

- `mcdi.h` is the immediate consumer layer: its `MCDI_DECLARE_BUF`,
  `MCDI_SET_DWORD`, `MCDI_POPULATE_DWORD_*`, `MCDI_DWORD`,
  `MCDI_QWORD`, `MCDI_PTR`, and `MCDI_ARRAY_*` helpers concatenate field names
  from this header with `_OFST`, `_LEN`, `_LBN`, and `_WIDTH`.
- The main SFC `ef10.c` consumes several definitions from this exact range:
  `GET_FUNCTION_INFO` for PF/VF identity, `LICENSING_V3` for licensed feature
  masks, `GET_CLOCK` for system clock frequency, `VPORT_GET_MAC_ADDRESSES` and
  `VPORT_ADD_MAC_ADDRESS` for vPort MAC handling, workaround bits, and
  `SET_TUNNEL_ENCAP_UDP_PORTS` for VXLAN/Geneve parser offload.
- `mcdi.c` consumes `GET_WORKAROUNDS` and `GET_FUNCTION_INFO`, including
  response length checks and tolerance for older firmware returning
  unsupported-command errors.
- `ef10_sriov.c` consumes `LINK_STATE_MODE` to set or query VF link state,
  using packed PF/VF bitfields and the `DO_NOT_CHANGE` read-only sentinel.
- The VNIC encapsulation rule commands refer to definitions outside this range,
  especially `MAE_MPORT_SELECTOR_ASSIGNED`, `MAE_MCDI_ENCAP_TYPE`, and
  `MC_CMD_GET_PARSER_DISP_INFO` supported-match queries defined earlier in the
  protocol header.
- Privilege categories such as `SRIOV_CTG_GENERAL`, `SRIOV_CTG_ADMIN`,
  `SRIOV_CTG_INSECURE`, and `SRIOV_CTG_ADMIN_TSA_UNBOUND` are defined earlier
  and are used by firmware-side authorization plus host tooling that reasons
  about command availability.
- The Siena subtree carries this protocol copy for compatibility, but not every
  late EF10/Medford/EF100 command is actively used by Siena-specific C files.
  Keeping the ABI in sync still matters because shared code and generated
  protocol tooling can include the Siena header copy.

## Risks and Edge Cases

- This is a firmware ABI. Any changed command number, length, offset, enum
  value, or bit position can create silent host/firmware disagreement and corrupt
  MCDI messages.
- Several response layouts are variable length and have different legacy MCDI
  versus MCDI2 maxima. Callers must validate `outlen`, count fields, and array
  calculations before copying MACs, fuse bytes, license IDs, parser values, or
  tunnel entries.
- Some comments document destructive behavior: `ENABLE_OFFLINE_BIST` tears down
  queues and requires reboot; `VPORT_RECONFIGURE` can reset a function;
  `SET_TUNNEL_ENCAP_UDP_PORTS` can reset all functions; port-mode override only
  activates after warm MC reboot. Treating these as ordinary configuration RPCs
  risks data-path disruption.
- Insecure commands are marked separately and may be rejected on secure
  adapters independent of privilege masks. Callers should not assume that
  `GRP_INSECURE` privilege is sufficient on secure hardware.
- Licensing V3 has asynchronous and invalidation cases. `REPORT_LICENSE` may
  return `EAGAIN`, temporary license SET needs status polling, and app/feature
  state can become stale after update or reboot.
- Network-byte-order fields in VNIC encapsulation rules and tunnel entries must
  be populated consistently. The 12-bit outer VLAN field has both a deprecated
  bit offset and an aligned word wrapper; using the wrong helper can shift the
  VID incorrectly.
- Encapsulation rule overlap is explicitly caller-managed. Firmware may choose
  a random matching rule when overlaps exist, duplicate matches return
  `EALREADY`, unsupported match combinations return `EOPNOTSUPP`, and full
  per-driver tables return `ENOSPC`.
- `PRIVILEGE_MASK` uses the MSB of `NEW_MASK` as the write-enable bit. A caller
  that forgets `DO_CHANGE` will only read, while a caller that accidentally sets
  it can alter privileges.
- `GET_WORKAROUNDS` must tolerate older firmware. The main driver already
  treats absence of the command as non-fatal, so tests should preserve that
  behavior when changing workaround handling.

## Test Signals

- Compile coverage is the primary signal for this generated header: all users
  of `MCDI_*` helper names must still find matching `_OFST`, `_LEN`, `_LBN`,
  and `_WIDTH` macros.
- Unit or static-build checks should cover representative MCDI payloads for
  `GET_FUNCTION_INFO`, `VPORT_GET_MAC_ADDRESSES`, `LICENSING_V3`,
  `LINK_STATE_MODE`, and `SET_TUNNEL_ENCAP_UDP_PORTS`, especially response
  length checks and variable array sizing.
- Runtime smoke tests on supported EF10/Medford hardware should include
  firmware RPC success/failure paths for function identity, clock read, license
  report, workaround query, vPort MAC enumeration, VF link-state query/set, and
  tunnel encapsulation programming where available.
- Negative tests should exercise older firmware or simulated unsupported MCDI
  results for `GET_WORKAROUNDS`, `GET_FUNCTION_INFO`, licensing update in
  progress, unsupported VNIC match flags, duplicate encapsulation rules, full
  rule tables, and secure-adapter rejection of insecure commands.
- Reset-sensitive tests should verify that callers recover when
  `VPORT_RECONFIGURE` reports `RESET_DONE` or tunnel UDP port programming
  reports `RESETTING`.
- ABI regression tests can compare generated offsets, lengths, and command IDs
  against firmware protocol sources, with particular attention to packed PF/VF
  fields, 64-bit app/feature masks, MCDI2 maximum response sizes, and final
  `PCIE_FUNCTION` tuple layout.
