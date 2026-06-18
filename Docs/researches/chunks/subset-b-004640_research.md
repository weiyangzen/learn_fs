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
