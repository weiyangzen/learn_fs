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
