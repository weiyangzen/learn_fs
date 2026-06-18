# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/uncore-interconnect.json lines 11954-13859

## Scope

This chunk covers the tail of the Cascade Lake X `uncore-interconnect.json` PMU event table. The range starts inside the `UNC_M3UPI_VN0_CREDITS_USED.NCS` object and continues through the closing `]` of the top-level JSON array. The adjacent preceding lines show that the partial opening object is:

- `UNC_M3UPI_VN0_CREDITS_USED.NCS`, `EventCode` `0x5C`, `UMask` `0x20`, `Counter` `0,1,2`, `Unit` `M3UPI`.

The rest of the chunk contains complete static JSON event records for the `M3UPI`, `M2M`, `UPI`, and `UBOX` uncore units. There are no functions, classes, branches, or local runtime variables in this source file; its behavior is data-driven through perf's PMU event generation and lookup pipeline.

## Purpose

The purpose of this chunk is to expose Cascade Lake X uncore interconnect monitoring events to perf. These records let perf users refer to symbolic event names instead of raw event selectors and unit masks when measuring Ultra Path Interconnect behavior, M3UPI credit pressure, and UBOX package-level events.

The covered event records fall into four broad areas:

- `M3UPI` credit use and credit starvation for VN0 and VN1 message channels.
- One deprecated `M2M` compatibility alias redirecting users from `UNC_NoUnit_TxC_BL.DRS_UPI` to `UNC_M2M_TxC_BL.DRS_UPI`.
- `UPI` link, flow-control, receive-path, transmit-path, power-state, FLIT, header-match, queue, and credit-return events.
- `UBOX` fixed clockticks, legacy event-message receipt, lock/PHOLD cycles, DRNG RACU activity, and outstanding RACU register requests.

All records in this chunk are package-scoped through `"PerPkg": "1"`. Most are marked `"Experimental": "1"`, especially the detailed flow-control, header-match, queue, and UBOX entries. Some records are explicitly `"Deprecated": "1"` and exist to preserve legacy names while pointing users toward newer aliases.

## Important Data Shape and APIs

Each entry is a JSON object in the perf PMU event schema consumed by `tools/perf/pmu-events/jevents.py` during perf table generation. Important fields in this chunk are:

- `EventName`: The symbolic alias source. Perf's generated tables normally expose lower-case aliases derived from these names, such as `unc_upi_txl_flits.all_data`.
- `EventCode`: The raw event selector programmed into the uncore PMU.
- `UMask`: The unit mask that distinguishes subevents under shared selectors, such as message classes, slots, virtual networks, and opcode-match variants.
- `Counter`: The valid counter set. `M3UPI` events use counters `0,1,2`; most `UPI` events use `0,1,2,3`; most `UBOX` programmable events use `0,1`; `UNC_U_CLOCKTICKS` uses the fixed counter.
- `Unit`: The uncore block used for PMU routing. This chunk uses `M3UPI`, `M2M`, `UPI`, and `UBOX`.
- `PerPkg`: Marks the events as package-scoped uncore events in generated metadata.
- `BriefDescription`: The short user-facing description.
- `PublicDescription`: Longer help text where present. Many low-level experimental records omit this field and rely only on the brief description or event name.
- `Deprecated`: Preserves old event aliases while steering users toward current event names.
- `Experimental`: Marks events whose interface or support quality should be treated more cautiously by users and tooling.

The JSON records do not define code-level APIs themselves, but their field names are an API contract with perf's generator and generated lookup code. At build time, `jevents.py` parses these fields into generated PMU event tables. At runtime, perf's PMU event lookup helpers use those generated tables to support `perf list`, `perf stat -e <event>`, metric resolution, and detailed event descriptions.

## Event Families

### M3UPI VN0 and VN1 Credit Events

Lines 11954-12198 finish the M3UPI credit section. The chunk begins inside `UNC_M3UPI_VN0_CREDITS_USED.NCS`; the remaining `VN0_CREDITS_USED` entries cover `REQ`, `RSP`, `SNP`, and `WB`, all with `EventCode` `0x5C` and counters `0,1,2`.

The `UNC_M3UPI_VN0_NO_CREDITS.*` family uses `EventCode` `0x5E` and reports cycles where VN0 credits were unavailable. The masks split the condition by message class:

- `REQ` on AD: `UMask` `0x1`.
- `SNP` on AD: `UMask` `0x2`.
- `RSP` on AD: `UMask` `0x4`.
- `WB` on BL: `UMask` `0x8`.
- `NCB`/data-response wording in the brief text: `UMask` `0x10`.
- `NCS`/non-coherent broadcast wording in the brief text: `UMask` `0x20`.

The `UNC_M3UPI_VN1_CREDITS_USED.*` family uses `EventCode` `0x5D`, and the `UNC_M3UPI_VN1_NO_CREDITS.*` family uses `EventCode` `0x5F`. Both mirror the same message-class masks. The long descriptions explain the core interpretation: requests prefer shared VNA credits and fall back to reserved VN0/VN1 pools to avoid deadlock. The credit-used events count fallback use, while no-credit events count cycles where the relevant reserved pool was unavailable.

These events are diagnostic signals for remote-socket traffic and backpressure. A high VN0/VN1 credit-used count suggests falling back from VNA; high no-credit cycles suggest more severe flow-control pressure.

### Deprecated M2M Alias

Lines 12200-12210 define `UNC_NoUnit_TxC_BL.DRS_UPI`, a deprecated `M2M` record with `EventCode` `0x40`, `UMask` `0x4`, and counters `0,1,2,3`. Its brief description points to `UNC_M2M_TxC_BL.DRS_UPI`.

This is compatibility data. The record should remain parseable and discoverable for users with old event names, but new documentation and tests should prefer the replacement alias.

### UPI Clock, Direct Attempts, Flow Queue, and M3 Blocking

Lines 12212-12466 start the main `UPI` tail section:

- `UNC_UPI_CLOCKTICKS` counts UPI fixed-frequency link clock ticks with `EventCode` `0x1`. Its long description states that the clock is one eighth of the UPI GT/s link speed, making it a natural denominator for UPI rates and occupancy-like interpretations.
- `UNC_UPI_DIRECT_ATTEMPTS.D2C` and `.D2U` use `EventCode` `0x12` to count data-response packets attempting to bypass the CHA and go direct to core or direct to UPI. `D2K` is deprecated in favor of `D2U`.
- `UNC_UPI_FLOWQ_NO_VNA_CRD.*` uses `EventCode` `0x18` and masks for AD, AK, and BL VNA credit conditions, such as `AD_VNA_EQ0`, `AK_VNA_EQ3`, and `BL_VNA_EQ0`.
- `UNC_UPI_L1_POWER_CYCLES` uses `EventCode` `0x21` to count cycles where both link directions are in the L1 shutdown power state.
- `UNC_UPI_M3_BYP_BLOCKED.*` uses `EventCode` `0x14` for bypass blocking reasons, including BGF credit, VNA threshold conditions, BL VNA empty, and global valid blocking.
- `UNC_UPI_M3_CRD_RETURN_BLOCKED` uses `EventCode` `0x16`.
- `UNC_UPI_M3_RXQ_BLOCKED.*` uses `EventCode` `0x15` for receive-queue blocking reasons, including BGF credit, flow queue thresholds, BL VNA empty, and global valid blocking.

These are low-level link-flow-control records. Most lack `PublicDescription`, so event names and masks carry much of the semantic detail. That increases the value of preserving exact names and avoiding accidental alias churn.

### UPI Power-State Handshake and M3 Slot Requests

Lines 12470-12554 define more UPI link-state and request-routing events:

- `UNC_UPI_PHY_INIT_CYCLES` counts cycles where the PHY is outside normal L0/L0c/L0p/L1 states.
- `UNC_UPI_POWER_L1_NACK` and `UNC_UPI_POWER_L1_REQ` count L1 transition NACK and ACK/REQ handshakes with `EventCode` `0x23` and `0x22`.
- `UNC_UPI_REQ_SLOT2_FROM_M3.*` uses `EventCode` `0x46` and masks `VNA` `0x1`, `VN0` `0x2`, `VN1` `0x4`, and `ACK` `0x8`.
- `UNC_UPI_RxL0P_POWER_CYCLES` and `UNC_UPI_RxL0_POWER_CYCLES` report receive-side low-power and full-power link-layer cycles.

The power-state descriptions emphasize that UPI power states are per link and per direction. Consumers comparing Rx and Tx power events must not assume one event covers both directions unless the description explicitly says so, as `UNC_UPI_L1_POWER_CYCLES` does.

### UPI Receive-Path Header, FLIT, Queue, and Credit Events

Lines 12558-13119 define receive-path (`RxL`) events:

- `UNC_UPI_RxL_BASIC_HDR_MATCH.*` uses `EventCode` `0x5` and masks for message classes and opcode-specific matching. Message-class aliases include `NCB`, `NCS`, `REQ`, `RSP_DATA`, `RSP_NODATA`, `SNP`, and `WB`; opcode variants add a high mask bit such as `0x108`, `0x109`, `0x10c`, `0x10d`, `0x10e`, or `0x10f`.
- `UNC_UPI_RxL_BYPASSED.SLOT0`, `.SLOT1`, and `.SLOT2` use `EventCode` `0x31` and count FLITs that bypassed slot-specific receive buffers, which is the intended low-latency common path.
- `UNC_UPI_RxL_CREDITS_CONSUMED_VNA`, `_VN0`, and `_VN1` use event codes `0x38`, `0x39`, and `0x3A` to count RxQ credit consumption by virtual network.
- `UNC_UPI_RxL_FLITS.*` uses `EventCode` `0x3` to count received data, null, idle, LLCRD, LLCTRL, non-data, protocol header, and slot-selected FLITs.
- Deprecated `UNC_UPI_RxL_FLITS.NULL` and `.PROT_HDR` point to `.ALL_NULL` and `.PROTHDR`.
- Deprecated `UNC_UPI_RxL_HDR_MATCH.*` entries point to `UNC_UPI_RxL_BASIC_HDR_MATCH.*`.
- `UNC_UPI_RxL_INSERTS.SLOT*` and `UNC_UPI_RxL_OCCUPANCY.SLOT*` use event codes `0x30` and `0x32` to measure RxQ allocations and accumulated occupancy by slot.
- `UNC_UPI_RxL_SLOT_BYPASS.*` uses `EventCode` `0x33` for cross-slot bypass routing signals such as `S0_RXQ1` and `S2_RXQ1`.

The FLIT families combine type masks with slot masks. For example, `DATA` notes that data FLITs consume all slots, but the counted value depends on enabled slot mask bits. Users and tests should treat these as bitmask-composable hardware encodings, not as independent mutually exclusive counters.

### UPI Transmit-Path Power, Header, FLIT, Queue, and Credit Events

Lines 13123-13732 define transmit-path (`TxL`) records:

- `UNC_UPI_TxL0P_CLK_ACTIVE.*` uses `EventCode` `0x2A` for active clock subcomponents during L0p, including `CFG_CTL`, `RXQ`, `RXQ_BYPASS`, `RXQ_CRED`, `TXQ`, `RETRY`, `DFX`, and `SPARE`.
- `UNC_UPI_TxL0P_POWER_CYCLES`, `_LL_ENTER`, and `_M3_EXIT` use event codes `0x27`, `0x28`, and `0x29`.
- `UNC_UPI_TxL0_POWER_CYCLES` uses `EventCode` `0x26`.
- `UNC_UPI_TxL_BASIC_HDR_MATCH.*` mirrors the receive-side header-match family but uses `EventCode` `0x4` for transmit-path matching.
- `UNC_UPI_TxL_BYPASSED` uses `EventCode` `0x41` to count FLITs that bypass the transmit buffer and pass directly to the UPI link.
- `UNC_UPI_TxL_FLITS.*` uses `EventCode` `0x2` to count transmitted data, null, idle, LLCRD, LLCTRL, non-data, protocol-header, and slot-selected FLITs.
- Deprecated `UNC_UPI_TxL_FLITS.NULL` and `.PROT_HDR` point to `.ALL_NULL` and `.PROTHDR`.
- Deprecated `UNC_UPI_TxL_HDR_MATCH.*` entries point to `UNC_UPI_TxL_BASIC_HDR_MATCH.*` where an equivalent exists. Several deprecated entries, such as `DATA_HDR`, `DUAL_SLOT_HDR`, `LOC`, `NON_DATA_HDR`, `REM`, and `SGL_SLOT_HDR`, have no replacement text beyond "This event is deprecated."
- `UNC_UPI_TxL_INSERTS` and `UNC_UPI_TxL_OCCUPANCY` use event codes `0x40` and `0x42` for transmit flit-buffer allocations and accumulated occupancy.
- `UNC_UPI_VNA_CREDIT_RETURN_BLOCKED_VN01` and `UNC_UPI_VNA_CREDIT_RETURN_OCCUPANCY` use event codes `0x45` and `0x44` to track VNA credit-return blockage and pending-return occupancy.

The transmit queue descriptions parallel the receive queue descriptions: bypass is the normal fast path, while inserts and occupancy indicate buffering, typically due to L0p or link-layer retry conditions. Occupancy values are accumulated queue-depth signals and need a denominator such as clockticks or a not-empty event from nearby data to become averages.

### UBOX Clock, Messages, Locks, PHOLD, DRNG, and RACU

Lines 13736-13859 close the file with `UBOX` entries:

- `UNC_U_CLOCKTICKS` uses `Counter` `FIXED` and `EventCode` `0xff` for UBOX clockticks.
- `UNC_U_EVENT_MSG.*` uses `EventCode` `0x42` with masks for `VLW_RCVD`, `MSI_RCVD`, `IPI_RCVD`, `DOORBELL_RCVD`, and `INT_PRIO`. The long descriptions describe Virtual Logical Wire legacy messages and, for subevents, inter-processor interrupts or message-signaled interrupts.
- `UNC_U_LOCK_CYCLES` uses `EventCode` `0x44` and counts starts of IDI lock or split-lock sequences.
- `UNC_U_PHOLD_CYCLES.ASSERT_TO_ACK` uses `EventCode` `0x45`, `UMask` `0x1`.
- `UNC_U_RACU_DRNG.*` uses `EventCode` `0x4C` with masks for `RDRAND`, `RDSEED`, and `PFTCH_BUF_EMPTY`.
- `UNC_U_RACU_REQUESTS` uses `EventCode` `0x46` and counts outstanding register requests within the message-channel tracker.

These records are the package-control tail of the interconnect file. The final `]` at line 13859 closes the entire JSON array, so syntax errors in this range invalidate the whole Cascade Lake X interconnect event topic.

## Control Flow and Integration

This chunk has no executable control flow. The practical control flow is supplied by perf's data pipeline:

1. The x86 PMU event build selects the `arch/x86/cascadelakex` model directory for matching Cascade Lake X CPU models.
2. `jevents.py` reads topic files such as `uncore-interconnect.json` as JSON arrays.
3. Each object is converted into generated PMU event metadata. `EventCode` and `UMask` become raw event terms, `EventName` becomes the alias, descriptions become help text, `Unit` selects the uncore PMU family, `PerPkg` marks package scope, and `Deprecated`/`Experimental` become generated metadata flags.
4. The generated event tables are compiled into perf.
5. Runtime perf lookup APIs and user commands resolve names such as `UNC_UPI_RxL_FLITS.ALL_DATA` or `UNC_U_CLOCKTICKS` against the generated Cascade Lake X table.

The file integrates with kernel uncore PMU drivers indirectly: perf can only schedule these aliases if the running kernel exposes compatible uncore PMUs and if the event's counter restrictions match the hardware PMU layout.

## State and Persistence

There is no mutable software state in this chunk. Its persistent state is the source-controlled mapping from symbolic event names to uncore PMU encodings and descriptions.

The main persistence contracts are:

- `EventName` stability matters because users, scripts, documentation, and metric expressions may reference aliases by name.
- `EventCode` and `UMask` correctness determines which hardware signal perf programs. A wrong value can produce plausible but incorrect performance data.
- `Unit` controls PMU routing. A typo can make an event appear under the wrong generated PMU or disappear from the expected uncore PMU.
- `Counter` constraints describe legal hardware counters and affect scheduling expectations.
- `Deprecated` entries preserve compatibility while guiding users toward newer names.
- `Experimental` metadata warns consumers that some entries may be less stable or less fully documented.
- The closing array bracket persists structural validity for the whole file.

Because this is a static event database, changes take effect only after regenerating or rebuilding perf's PMU event tables.

## Dependencies

This chunk depends on:

- Valid JSON syntax for the whole `uncore-interconnect.json` array.
- The perf PMU event JSON schema and field spellings recognized by `jevents.py`.
- The Cascade Lake X x86 model mapping that selects the `cascadelakex` directory.
- Generated PMU event table code and lookup helpers used by `perf list`, `perf stat`, and metric parsing.
- Kernel uncore PMU support for Cascade Lake X units corresponding to `M3UPI`, `M2M`, `UPI`, and `UBOX`.
- Hardware documentation matching the listed event selectors, masks, counter constraints, and package-scoped semantics.

There are no direct code imports, includes, or local helper functions in the JSON file. The important dependency is the schema-level contract between static data and perf's generator.

## Risks

- The chunk starts mid-object. A chunk-only reader could miss that the first visible fields belong to `UNC_M3UPI_VN0_CREDITS_USED.NCS`, not a standalone object.
- The range ends the top-level JSON array. Any missing comma, brace, or closing bracket here breaks parsing for the entire Cascade Lake X uncore interconnect topic.
- Many records are experimental and have terse descriptions. Users may need platform documentation to interpret low-level flow-control names such as `FLOWQ_AD_VNA_BTW_2_THRESH` or `GV_BLOCK`.
- Deprecated aliases must remain syntactically valid. Removing or renaming them can break older perf scripts even if newer aliases exist.
- Header-match families use closely related masks for class and opcode matching. Accidental mask changes can silently turn a class match into an opcode-filtered match or vice versa.
- Rx and Tx families are intentionally similar but use different event selectors (`RxL_BASIC_HDR_MATCH` uses `0x5`, `TxL_BASIC_HDR_MATCH` uses `0x4`; Rx FLITs use `0x3`, Tx FLITs use `0x2`). Copying between families is error-prone.
- Some descriptions have legacy or inconsistent wording, such as QPI references inside UPI VN1 descriptions and brief-description mismatches around NCB/NCS/WB. Those strings may confuse users even when raw encodings are correct.
- Occupancy-style events are accumulated over cycles, not simple transaction counts. Tooling or documentation that treats them as raw event counts can produce misleading conclusions.
- `Counter` differs by unit: M3UPI uses three counters, UPI uses four, UBOX mostly uses two, and `UNC_U_CLOCKTICKS` is fixed. Incorrect scheduling assumptions can produce event-open failures or bad multiplexing behavior.

## Test and Validation Signals

Useful validation signals for this chunk include:

- Parse the full source file with a strict JSON parser, for example `python3 -m json.tool sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/uncore-interconnect.json`.
- Regenerate or build perf PMU event tables and confirm the Cascade Lake X table contains representative aliases from each unit: `UNC_M3UPI_VN1_NO_CREDITS.REQ`, `UNC_NoUnit_TxC_BL.DRS_UPI`, `UNC_UPI_CLOCKTICKS`, `UNC_UPI_RxL_FLITS.ALL_DATA`, `UNC_UPI_TxL_FLITS.ALL_DATA`, and `UNC_U_CLOCKTICKS`.
- Check sample generated encodings: `UNC_UPI_RxL_BASIC_HDR_MATCH.REQ_OPC` should carry `event=0x5,umask=0x108`; `UNC_UPI_TxL_BASIC_HDR_MATCH.REQ_OPC` should carry `event=0x4,umask=0x108`; `UNC_U_EVENT_MSG.MSI_RCVD` should carry `event=0x42,umask=0x2`.
- Run perf PMU event table tests, especially generated event lookup tests under `tools/perf/tests/pmu-events.c` in a full perf tree.
- Inspect `perf list --details` output for deprecated aliases and ensure replacement text is visible where present.
- On Cascade Lake X hardware with compatible kernel uncore PMUs, run low-impact `perf stat -a -e` checks for representative UPI and UBOX aliases and confirm event resolution, counter scheduling, and package-level aggregation.
- For behavioral validation, compare bypass, insert, and occupancy families under workloads that vary UPI traffic and link power state; bypass should represent the fast path, while insert/occupancy should rise when queues are used.
