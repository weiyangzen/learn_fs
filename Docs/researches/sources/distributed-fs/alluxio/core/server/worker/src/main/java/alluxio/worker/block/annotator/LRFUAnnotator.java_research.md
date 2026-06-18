# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/LRFUAnnotator.java

Purpose: Implements LRFU block ranking, combining recency and frequency through an attenuated combined recency-frequency score.

Important APIs: `updateSortedField` increments a logical clock for one access; `updateSortedFields` refreshes a batch at the same clock for offline ordering; `isOnlineSorter` returns false; nested `LRFUSortedField` compares by CRF value.

Control flow: On an update, a missing field starts with CRF 1. Existing fields decay by `pow(1 / attenuation, interval * step)` and add 1 for the new access. Offline batch update uses the current clock without incrementing per block.

State and persistence: Stores an `AtomicLong` logical clock. Sort fields store clock and CRF in memory only.

Dependencies and integration: Reads `WORKER_BLOCK_ANNOTATOR_LRFU_STEP_FACTOR` and `WORKER_BLOCK_ANNOTATOR_LRFU_ATTENUATION_FACTOR`. Used by `DefaultBlockIterator` as an offline annotator requiring lazy total-order refresh.

Risks and test signals: Bad step or attenuation configuration can skew ordering. Equality and hash code ignore clock and use only CRF, relying on `SortedBlockSet` change indexes for tie-breaking. Tests should cover decay math, batch refresh stability, equal CRF ties, and low/high factor boundaries.
