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
