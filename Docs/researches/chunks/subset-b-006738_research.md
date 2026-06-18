# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-io.json lines 10587-10668

## Scope And Purpose

This chunk is the final tail of the Snow Ridge X `uncore-io.json` PMU event table used by Linux `perf` under `tools/perf/pmu-events/arch/x86`. The source file is a JSON array of declarative event descriptors, not executable code. These descriptors let perf expose named uncore IO events and translate each `EventName` into the raw unit, event selector, mask, package scope, and counter constraints needed to program Snow Ridge X uncore PMUs.

The requested line range begins inside the already-open `UNC_M2P_VERT_RING_BL_IN_USE.UP_EVEN` object, starting at its `PublicDescription`, and then continues through the closing `]` of the top-level JSON array. Interpreting by event objects that intersect this range, the chunk covers the last 8 `M2PCIe` vertical-ring utilization descriptors in the file: 2 BL, 2 IV, and 4 TGC events. Seven of those objects are complete within the selected range; the first object is completed here but starts on line 10580 in the previous chunk.

All visible descriptors are package-scoped (`PerPkg: "1"`), experimental (`Experimental: "1"`), use programmable counters `0,1,2,3`, and belong to `Unit: "M2PCIe"`. The full file parses as one top-level JSON array with 924 event objects and this chunk supplies the final entries before the array terminator.

## Data Contract And Important Fields

There are no local functions, classes, or methods. The effective API is the PMU event metadata schema consumed by perf's pmu-events tooling:

- `EventName` is the user-facing symbolic alias. In this chunk the names are `UNC_M2P_VERT_RING_*_IN_USE.*` variants for BL, IV, and TGC vertical ring activity.
- `Unit` is `M2PCIe`, selecting the mesh-to-PCIe uncore PMU block rather than a core PMU or another uncore unit.
- `EventCode` identifies the hardware event family. `0xb2` is used for BL ring use, `0xb3` for IV ring use, and `0xb5` for TGC ring use.
- `UMask` selects the direction/parity subtype. Up/even uses `0x1`, up/odd uses `0x2`, down/even uses `0x4`, and down/odd uses `0x8` where the family supports even/odd split.
- `Counter` constrains scheduling to counters `0,1,2,3` on the M2PCIe PMU.
- `PerPkg` marks these as package-level uncore events, so interpretation and aggregation should be socket/package scoped.
- `Experimental` flags the events as less stable or less formally guaranteed than non-experimental aliases.
- `BriefDescription` and `PublicDescription` are the help text shown by list/documentation paths and are important for users interpreting ring-direction semantics.

## Event Families In This Chunk

The BL entries describe vertical BL ring cycles in use at the ring stop. The selected range completes `UNC_M2P_VERT_RING_BL_IN_USE.UP_EVEN` and includes the full `UNC_M2P_VERT_RING_BL_IN_USE.UP_ODD` object. Both share `EventCode: "0xb2"` and differ only by mask: `0x1` for up/even and `0x2` for up/odd. The public text says the count includes cycles where packets pass by or are sunk at this ring stop, but excludes packets being sent from the ring stop.

The IV entries are `UNC_M2P_VERT_RING_IV_IN_USE.DN` and `UNC_M2P_VERT_RING_IV_IN_USE.UP`, both using `EventCode: "0xb3"`. Unlike BL and TGC, this family exposes only direction-level masks in the visible tail: down is `0x4` and up is `0x1`. The description notes there is only one IV ring, so consumers wanting even or odd monitoring must combine up and down selections according to the surrounding ring topology guidance.

The TGC entries are a complete four-way direction/parity family under `EventCode: "0xb5"`: `DN_EVEN` (`0x4`), `DN_ODD` (`0x8`), `UP_EVEN` (`0x1`), and `UP_ODD` (`0x2`). Their descriptions follow the same vertical ring occupancy semantics as the BL events and explain the clockwise/counter-clockwise interpretation of up/down paths on the left and right sides of the ring.

## Control Flow And Integration

This JSON chunk has no direct runtime control flow. Its integration path is data-driven:

1. Perf's PMU event build tooling reads the Snow Ridge X JSON files and validates the top-level event array.
2. The generator converts each object into generated event tables or event-map data.
3. At runtime, perf selects the Snow Ridge X event map for matching hardware.
4. `perf list` and related help paths display the aliases and descriptions.
5. `perf stat` or similar commands resolve a selected alias to `Unit: M2PCIe`, the event code, the unit mask, package scope, and the allowed counter set before programming the uncore PMU.

The chunk is tightly coupled to earlier chunks because it is the tail of a single JSON array and begins mid-object. A processor must parse the full `uncore-io.json` file, or at least stitch adjacent chunks, rather than treating lines 10587-10668 as standalone JSON.

## State And Persistence Behavior

The file is static persisted metadata. It does not allocate memory, mutate state, or maintain counters itself. Runtime state lives in hardware counters after perf programs the selected uncore event.

The persistent state encoded here is semantic metadata: package scope through `PerPkg`, experimental status through `Experimental`, counter eligibility through `Counter`, and ring topology guidance through descriptions. Because the events are uncore and package-scoped, counts should not be interpreted as per-thread or per-core activity.

## Dependencies And External Contracts

The immediate dependency is perf's PMU event JSON schema, including support for string-encoded hexadecimal fields, comma-separated counter lists, optional descriptive fields, and package-level uncore metadata. The content depends on Intel Snow Ridge X M2PCIe uncore PMU definitions and on the kernel/perf uncore PMU naming that exposes a compatible `M2PCIe` unit.

The event aliases also depend on naming consistency with the rest of `uncore-io.json`. The dotted suffixes (`UP_EVEN`, `UP_ODD`, `DN_EVEN`, `DN_ODD`, `UP`, `DN`) are part of the public perf interface. Renaming them, changing masks, or moving them to another unit would be a user-visible behavioral change even though this is data-only source.

## Risks And Edge Cases

- The selected range starts at a `PublicDescription` line inside an object, so isolated JSON parsing of only these lines will fail. Full-file validation is the relevant test signal.
- Wrong `UMask` values are a high-risk metadata error: the file would remain syntactically valid but count the wrong ring direction or parity.
- The ring descriptions explain that up/down mapping reverses across ring sides and CBo halves. Documentation changes that simplify this text may make the counters easier to misuse.
- TGC public descriptions say "two rings in JKT" even though this file is for Snow Ridge X. This appears to be inherited vendor wording and should be checked against the source authority before changing.
- All entries are experimental, so downstream tests should verify parseability and event availability without assuming permanent semantic stability.
- Counter constraints are unit-specific. Ignoring `Counter: "0,1,2,3"` or `Unit: "M2PCIe"` could produce event scheduling failures or invalid PMU programming.

## Test Signals

Useful validation signals for this chunk and the final merged per-file report include:

- Parse the full `uncore-io.json` file as JSON and confirm it contains 924 top-level event objects and ends at line 10668.
- Confirm the final 8 objects are all `Unit: "M2PCIe"`, `PerPkg: "1"`, `Experimental: "1"`, and `Counter: "0,1,2,3"`.
- Verify the BL family uses `EventCode: "0xb2"` with `UP_EVEN` mask `0x1` and `UP_ODD` mask `0x2`.
- Verify the IV family uses `EventCode: "0xb3"` with `UP` mask `0x1` and `DN` mask `0x4`.
- Verify the TGC family uses `EventCode: "0xb5"` with masks `UP_EVEN=0x1`, `UP_ODD=0x2`, `DN_EVEN=0x4`, and `DN_ODD=0x8`.
- Run perf PMU event generation or schema checks to catch malformed JSON, missing required fields, duplicate aliases, or unsupported unit/counter metadata.
- On Snow Ridge X hardware with matching uncore PMUs, use `perf list` and short `perf stat` probes for representative aliases such as `UNC_M2P_VERT_RING_BL_IN_USE.UP_EVEN`, `UNC_M2P_VERT_RING_IV_IN_USE.DN`, and `UNC_M2P_VERT_RING_TGC_IN_USE.UP_ODD`.
