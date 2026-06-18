# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/ByteArray.java

Purpose: lightweight adapter exposing a byte-array region as `RawComparable`.

Important APIs/types/functions: constructors from `BytesWritable`, whole `byte[]`, and `byte[]` slice; `buffer()`, `offset()`, and `size()`.

Control flow: slice constructor validates offset/length using bitwise bounds check, then stores references. Accessors return raw backing buffer and range metadata without copying.

State and persistence: immutable wrapper fields, but the underlying byte array remains mutable by external owners.

Dependencies and integration: used with `CompareUtils.BytesComparator` and Hadoop `RawComparator` workflows in TFile code.

Risks: no defensive copy, so comparisons can change if the backing array is mutated. Tests should cover bounds validation, `BytesWritable` length handling, whole/sliced wrappers, and comparator integration.
