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
