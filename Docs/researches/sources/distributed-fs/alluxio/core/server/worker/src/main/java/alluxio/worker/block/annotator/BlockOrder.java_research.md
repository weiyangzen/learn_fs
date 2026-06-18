# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/BlockOrder.java

Purpose: Small enum that standardizes natural and reverse ordering for block sorted fields.

Important APIs: Values are `NATURAL` and `REVERSE`; `reversed()` returns the opposite; `comparator()` returns a raw `Comparator<Comparable>` for sorted-field comparisons.

Control flow: Iterator implementations use the enum to pick ascending or descending per-directory iterators and to compare boundary blocks for tier alignment.

State and persistence: Stateless enum with no persistence.

Dependencies and integration: Used by `DefaultBlockIterator`, `EmulatingBlockIterator`, `AlignTask`, `PromoteTask`, `SwapRestoreTask`, and `TierManagementTaskProvider`.

Risks and test signals: Raw comparator typing can hide class-cast issues until runtime. Test reverse pairing, comparator direction, and illegal/default cases only through enum exhaustiveness.
