# sources/distributed-fs/ceph-client/lib/xz/xz_lzma2.h

## Purpose
Defines LZMA/LZMA2 decoder constants and inline state helpers used by `xz_dec_lzma2.c`.

## APIs and control flow
The header provides range-coder constants, position-state and literal-coder limits, `enum lzma_state`, transition helpers for literal/match/long-repeat/short-repeat states, match length geometry, distance-slot and alignment constants, `PROBS_TOTAL`, `REPS`, and `lzma_get_dist_state`. The inline helpers implement the LZMA finite-state transitions but no standalone runtime loop.

## State, dependencies, and integration
It declares constants only; runtime state lives in `struct lzma_dec` in the C file. Values must match the LZMA format and probability-array layout assumptions.

## Risks and test signals
Changing constants or transitions can corrupt probability indexing or output. Any change requires full LZMA2 vector coverage, match/distance boundary tests, invalid-distance tests, and memory-safety instrumentation around probability arrays.
