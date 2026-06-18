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
