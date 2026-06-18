# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/uncore-interconnect.json lines 1-3919

## Chunk Scope

This chunk covers the beginning of the HaswellX uncore interconnect PMU event table through line 3919 of a 4392-line JSON array. The visible records define perf event metadata for units `IRP`, `QPI`, `R3QPI`, and the first part of `SBOX`; the next chunk continues from the `UNC_S_RxR_CRD_STARVED.IV` object that starts at line 3919.

The file is declarative data, not executable code. Its API surface is the schema expected by Linux perf's PMU event loader: each object names a hardware event and provides fields such as `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, and sometimes `PublicDescription`.

## Purpose

The chunk maps Intel Haswell-EX/HaswellX uncore interconnect counters into perf-readable event aliases. These aliases let perf users request semantically named metrics instead of programming raw uncore event select and umask values. The covered interconnect domains expose:

- `IRP`: I/O request path transactions, snoop responses, coherent operations, ingress and egress queue occupancy, cache occupancy, and credit stalls.
- `QPI`: QPI link-layer clocks, link power states, CRC errors, direct-to-core spawning, receive/transmit flit counts, Rx/Tx queue occupancy, stalls, and R3 egress credit pools.
- `R3QPI`: R3 ring/QPI bridge clocks, CBox/HA/R2/QPI credit-empty signals, ring use, ingress allocation/occupancy, VN0/VN1/VNA credit use and reject behavior, and SBox credit interactions.
- `SBOX`: ring-stop and SBox metrics for AD/AK/BL/IV ring use, bounces, sink starvation, ingress bypass, and ingress starvation through `UNC_S_RxR_CRD_STARVED.IFV`.

## Schema And Important Fields

The important data contract is stable across the records:

- `EventName` is the public perf alias and the primary identifier. It uses hierarchical names such as `UNC_Q_RxL_FLITS_G1.DRS` or `UNC_R3_VN1_CREDITS_USED.HOM`.
- `EventCode` is the raw uncore event selector. Some clock aliases omit it, for example `UNC_I_CLOCKTICKS` and `UNC_S_CLOCKTICKS`.
- `UMask` refines an event into a subevent or filter. Base events such as some occupancy and clock counters may omit it.
- `Counter` constrains which programmable counters can count the event. `IRP` records use `0,1`; `QPI` records mostly use `0,1,2,3`; `R3QPI` mixes `0,1,2`, `0,1`, and single-counter occupancy records such as `UNC_R3_RxR_OCCUPANCY_VN1.*` with counter `0`; `SBOX` records use `0,1,2,3`.
- `Unit` binds aliases to a perf PMU unit. Consumers must keep identical event names on different units distinct by unit context.
- `PerPkg: "1"` marks the events as package-scoped uncore measurements.
- `BriefDescription` and `PublicDescription` are user-facing help text, but in this file they contain typos and some label drift. The raw mapping should be driven by `EventName`, `EventCode`, `UMask`, `Counter`, and `Unit`.

## Event Families

### IRP

The IRP section starts with cache and clock visibility, then moves through coherent operation classes and transaction queues:

- `UNC_I_CACHE_TOTAL_OCCUPANCY.{ANY,SOURCE}` accumulates outstanding read/write occupancy, with `SOURCE` filtered through `IRP_PmonFilter.OrderingQ`.
- `UNC_I_COHERENT_OPS.*` distinguishes CLFLUSH, CRd, DRd, PCI hints/read-current/ItoM, RFO, and WbMtoI operations.
- `UNC_I_MISC0.*` and `UNC_I_MISC1.*` cover fast-path behavior, secondary cache inserts, prefetch timeouts, data throttling, invalid/valid secondary transfers, lost forwards, and slow transfers in MESI states.
- `UNC_I_RxR_*` covers AK and BL ingress allocations, occupancy, and full cycles for DRS, NCB, and NCS queues.
- `UNC_I_SNOOP_RESP.*` and `UNC_I_TRANSACTIONS.*` classify snoop hits/misses and inbound transaction types. The transaction descriptions explicitly mention OR-reduction by request type and optional source-port qualification.
- `UNC_I_TxR_*` covers outbound request/data insertion and credit-stall cycles on AD and BL egress paths.

### QPI

The QPI section is the largest in the chunk. It models both link-layer traffic and the interface into R3:

- `UNC_Q_CLOCKTICKS` counts QPI qfclk cycles; descriptions state qfclk runs at one quarter of QPI GT/s and HaswellX does not support dynamic link speeds.
- `UNC_Q_DIRECT2CORE.*` exposes direct-to-core spawn success and mutually exclusive failure modes for DRS packets: egress-credit failure, route-back-table miss/invalid combinations, and successful RBT hits.
- Link power records distinguish L0/L0p/L1 cycles on Rx and Tx directions. Descriptions warn that link power states are per link and per direction.
- `UNC_Q_RxL_*` records cover receive-side bypass, CRC errors, VN0/VN1/VNA credit consumption, cycles-not-empty, inserts, occupancy, flit classes, and VN0/VN1 stalls.
- `UNC_Q_TxL_*` mirrors the transmit side with bypass, CRC no-credit states, cycles-not-empty, group 0/1/2 flit transmission, inserts, and occupancy.
- Flit group descriptions document interpretation: a flit is 80 bits, full-width L0 uses four 20-bit fits, L0p halves fit width, and data bandwidth must be derived from data flits rather than total flits.
- `UNC_Q_TxR_*_CREDIT_{ACQUIRED,OCCUPANCY}` records expose AD/AK/BL egress credits toward R3 for HOM, NDR, SNP, DRS, NCB, and NCS classes, split by VN0, VN1, and sometimes shared VN.
- `UNC_Q_VNA_CREDIT_RETURNS` and `UNC_Q_VNA_CREDIT_RETURN_OCCUPANCY` track VNA credits pending return on the Rx side.

### R3QPI

The R3QPI section models the bridge between QPI, CBoxes, HA/R2, and SBox/ring resources:

- `UNC_R3_CLOCKTICKS` counts uclk-domain clocks and notes slight divergence from UBox clocks due to enable/freeze delays.
- `UNC_R3_C_HI_AD_CREDITS_EMPTY.*` and `UNC_R3_C_LO_AD_CREDITS_EMPTY.*` map AD-ring credit-empty states to high and low CBox ranges. HaswellX CBox grouping appears in aliases like `CBO14_16` and `CBO_15_17`.
- `UNC_R3_HA_R2_BL_CREDITS_EMPTY.*`, `UNC_R3_QPI0_*_CREDITS_EMPTY.*`, and `UNC_R3_QPI1_*_CREDITS_EMPTY.*` expose credit starvation toward HA, R2, and QPI ports across AD/BL rings and virtual networks.
- `UNC_R3_RING_{AD,AK,BL,IV}_USED.*` counts ring use by direction and polarity. The AD/AK/BL families split clockwise/counter-clockwise and even/odd polarity; IV has fewer filters in this chunk.
- `UNC_R3_RxR_*` covers ingress cycles-not-empty, allocations, and VN1 occupancy by message class (`DRS`, `HOM`, `NCB`, `NCS`, `NDR`, `SNP`).
- `UNC_R3_SBO{0,1}_{CREDITS_ACQUIRED,CREDIT_OCCUPANCY}.*` and `UNC_R3_STALL_NO_SBO_CREDIT.*` connect R3 behavior to SBox AD/BL credits.
- `UNC_R3_TxR_NACK.*` tracks up/down NACKs for AD, AK, and BL rings.
- `UNC_R3_VN0_*`, `UNC_R3_VN1_*`, and `UNC_R3_VNA_*` record credit use and reject paths. Descriptions describe VNA as the shared high-performance pool and VN0/VN1 as reserved pools for forward progress/deadlock avoidance.

### SBOX Portion

The SBox records visible in this chunk begin at `UNC_S_BOUNCE_CONTROL` and continue through `UNC_S_RxR_CRD_STARVED.IFV`:

- `UNC_S_CLOCKTICKS` and `UNC_S_FAST_ASSERTED` provide basic SBox clock/distress-signal visibility.
- `UNC_S_RING_AD_USED.*`, `UNC_S_RING_AK_USED.*`, and `UNC_S_RING_BL_USED.*` use `DOWN`, `DOWN_EVEN`, `DOWN_ODD`, `UP`, `UP_EVEN`, and `UP_ODD` filters. Descriptions explain that HaswellX has clockwise and counter-clockwise rings and that `UP`/`DN` map differently on left and right sides of the ring.
- `UNC_S_RING_BOUNCES.*` and `UNC_S_RING_SINK_STARVED.*` cover AD cache, AK core, BL core, and IV core sink/bounce behavior.
- `UNC_S_RING_IV_USED.{DN,UP}` describes the IV ring as a single ring in HaswellX, with combined filters needed to distinguish even and odd polarity.
- `UNC_S_RxR_BUSY_STARVED.*` distinguishes starvation caused by bounceable/credited message activity, while `UNC_S_RxR_CRD_STARVED.*` distinguishes lack-of-credit starvation.
- `UNC_S_RxR_BYPASS.*` records SBox ingress bypass for AD, AK, BL, and IV traffic.

## Control Flow And Integration

At runtime, perf's pmu-events generator/loader reads this JSON as architecture-specific metadata under `tools/perf/pmu-events/arch/x86/haswellx`. The effective control flow is data-driven:

1. Parse the JSON array into event records.
2. Index records by `Unit` and `EventName`.
3. Expose aliases in perf for HaswellX-compatible uncore PMUs.
4. When a user selects an alias, program the corresponding unit, counter constraints, event selector, umask, package scope, and any supported filter registers.
5. Present `BriefDescription`/`PublicDescription` in event listings and help output.

There are no functions or in-file calls. Cross-file integration is by naming convention and schema compatibility with neighboring HaswellX PMU JSON files and with perf's shared PMU event parsing code.

## State And Persistence

This chunk persists a static hardware event catalog in source control. It does not hold runtime state. Runtime state lives in hardware counters, uncore PMU registers, and perf session output. The event records influence measurement state indirectly by specifying which event select and umask values perf programs into package-scoped uncore counters.

Occupancy records accumulate queue depth over cycles; pairing them with allocation or not-empty records is necessary to derive average occupancy or average lifetime. Credit use/reject records are cumulative event counts; they do not persist credit pool state themselves.

## Dependencies

The data depends on:

- Intel HaswellX uncore PMU programming semantics for IRP, QPI, R3QPI, and SBOX units.
- Perf's pmu-events JSON schema and generator expectations.
- Consistent `Unit` naming between JSON metadata and perf's uncore PMU discovery.
- Counter availability matching the `Counter` field.
- Optional filter support for events whose descriptions mention source-port or message-class filtering.

## Risks And Irregularities

- Descriptive text is not fully reliable. Examples include typos such as `PCIDCAHin5t`, `waitng`, and `IFV`/`IVF`, generic descriptions for debug events, and some apparently swapped brief descriptions in QPI stall records.
- Several records omit `PublicDescription`; consumers must handle absent long descriptions.
- Clock events may omit `EventCode` or `UMask`; validators should not require those fields for every event.
- Some aliases represent aggregate umasks, such as direction/polarity combinations. Counting multiple aliases together can double count if the user does not understand combined masks.
- Occupancy and cycles-not-empty events are useful only when interpreted with the right denominator. Raw counts are accumulators, not standalone latency metrics.
- QPI flit counters distinguish total flits from data flits; using total flits as data bandwidth would overstate payload bandwidth.
- The chunk boundary cuts immediately before the complete `UNC_S_RxR_CRD_STARVED.IV` record. The merge lane must combine this report with the next chunk to avoid treating `UNC_S_RxR_CRD_STARVED` as complete at `IFV`.

## Test Signals

Useful validation signals for this chunk and the merged file:

- `jq` parses the full JSON array successfully; this file currently contains 446 event objects in total.
- Event records in this chunk use expected units only: `IRP`, `QPI`, `R3QPI`, and `SBOX`.
- `EventName` values are unique within their unit after parsing.
- Records with `UMask` retain hexadecimal string form, and records without `UMask` remain accepted by the perf schema.
- Counter strings are preserved exactly, especially single-counter R3 occupancy records and mixed `R3QPI` counter sets.
- Perf event-listing tests on a HaswellX target, or parser tests using generated pmu-events tables, should show aliases such as `UNC_I_TRANSACTIONS.READS`, `UNC_Q_RxL_FLITS_G1.DRS`, `UNC_R3_VNA_CREDITS_REJECT.SNP`, and `UNC_S_RING_AD_USED.UP_EVEN`.
- Cross-chunk merge validation should confirm that SBox families beginning in this chunk are completed by later records for RxR inserts, RxR occupancy, TxR inserts/occupancy, and TxR starvation.
