# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/CompareUtils.java

Purpose: small comparator helpers for raw byte ranges and scalar offsets used by TFile/BCFile lookup code.

Important APIs/types/functions: `BytesComparator`, `Scalar`, `ScalarLong`, `ScalarComparator`, and `MemcmpRawComparator`.

Control flow: `BytesComparator` delegates byte-range comparison to a supplied Hadoop `RawComparator`. `ScalarComparator` orders by `magnitude()` using long subtraction sign. `MemcmpRawComparator` delegates to `WritableComparator.compareBytes` and deliberately rejects object comparison.

State and persistence: comparator instances only; no durable state.

Dependencies and integration: `BCFile.Reader.getBlockIndexNear()` uses scalar comparison with `Utils.lowerBound`; TFile key comparisons can use `BytesComparator`/`RawComparable`.

Risks: `ScalarComparator` computes `o1 - o2`, which can overflow for extreme longs. Tests should cover lower-bound ordering, raw byte lexicographic comparison, unsupported object comparison, and extreme scalar values.
