# sources/distributed-fs/ceph-client/tools/perf/util/arm64-frame-pointer-unwind-support.h

Purpose: declares the AArch64 frame-pointer leaf caller recovery helper.

Important APIs and types: forward declares `struct perf_sample` and `struct thread`, includes Linux integer types, and exports `u64 get_leaf_frame_caller_aarch64(struct perf_sample *sample, struct thread *thread, int user_idx)`.

Control flow: no executable control flow; the header gives architecture-specific callchain code a narrow entry point without exposing register or unwind internals.

State and persistence: no state is defined here.

Dependencies and integration points: consumed by callchain or unwind paths that need arm64-specific frame-pointer support. The implementation includes AArch64 UAPI perf register names.

Risks: the signature exposes only `user_idx`; callers must ensure that index is valid for the sample callchain. Include guard naming differs slightly from the file name but is conventional enough.

Test signals: compile coverage on arm64 and non-arm64 build combinations is the main signal; runtime behavior is covered through the `.c` helper.
