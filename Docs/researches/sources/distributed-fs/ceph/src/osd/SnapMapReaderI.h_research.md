# sources/distributed-fs/ceph/src/osd/SnapMapReaderI.h

## Purpose
`SnapMapReaderI.h` defines the scrub-facing read interface for snap-map data. It lets scrub code ask for the set of snaps associated with an object without depending on the full `SnapMapper` implementation or object-store transaction machinery.

## Important APIs, Types, And Functions
`Scrub::SnapMapReaderI` declares two pure virtual methods: `get_snaps()` and `get_snaps_check_consistency()`. Both return `tl::expected<std::set<snapid_t>, result_t>`. `result_t` distinguishes `success`, `backend_error`, `not_found`, and `inconsistent`, with `backend_error` carrying the raw errno. `snap_mapper_op_t` identifies fix operations as `add`, `update`, or `overwrite`. `snap_mapper_fix_t` packages a requested mapper repair with target object, desired snaps, and wrong snaps for logging.

## Control Flow
Scrub backends call `get_snaps()` when they only need the object-to-snaps entry and `get_snaps_check_consistency()` when they need to verify that object entries and snap mapping entries agree. If inconsistency is discovered, scrub can return or construct `snap_mapper_fix_t` records for the PG scrubber to apply through the real mapper and object-store transactions.

## State And Persistence Behavior
This header owns no state and performs no IO itself. It defines the error vocabulary for persistent snap mapper reads and repairs. The actual durable data lives in mapper omap keys managed by `SnapMapper`.

## Dependencies And Integration Points
Dependencies are intentionally small: scrub types, `tl::expected`, `hobject_t`, and `snapid_t` from Ceph headers. `SnapMapper` implements this interface, and scrub components consume it to decouple verification logic from PG internals.

## Risks And Test Signals
Risk is mostly semantic: callers must handle `inconsistent` differently from missing data or backend IO errors, and repair code must preserve enough wrong-snaps detail for diagnostics. Tests should mock or exercise implementations returning all result codes, especially consistency mismatches and backend errors.
