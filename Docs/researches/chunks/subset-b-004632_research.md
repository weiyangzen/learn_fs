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
