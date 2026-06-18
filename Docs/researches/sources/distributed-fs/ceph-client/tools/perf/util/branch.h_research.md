# sources/distributed-fs/ceph-client/tools/perf/util/branch.h

## sources/distributed-fs/ceph-client/tools/perf/util/branch.h

Purpose: this header defines perf branch-stack data structures and declares branch classification helpers.

Important types: `struct branch_flags` overlays the raw 64-bit branch flags with bitfields for prediction, transaction, cycle count, type, speculation, extended type, privilege, and not-taken state. `struct branch_info` stores resolved map symbols and source lines. `struct branch_entry`/`branch_stack` mirror sampled branch stack records. `struct branch_type_stat` accumulates counts.

Control flow: the inline `perf_sample__branch_entries()` handles the two possible branch stack layouts depending on whether `PERF_SAMPLE_BRANCH_HW_INDEX` is present; it skips `nr` and optionally `hw_idx` before returning entries.

State and persistence: data is embedded in perf samples or caller-owned stats; the header itself owns no state.

Dependencies and integration: includes perf event UAPI, sample definitions, and map-symbol types. Used by branch reporting, scripting, and statistics code.

Risks: bitfield layout assumes the platform/compiler representation matches perf's little-endian UAPI expectations. `perf_sample__branch_entries()` relies on `sample->no_hw_idx` being set correctly by sample parsing.

Test signals: parse samples with and without hardware branch index, validate bitfield decoding against raw flag values, and verify branch stats on recordings with extended ABI types.
