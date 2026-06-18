# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/RawComparable.java

Purpose: public evolving interface for objects that expose a byte-array range to a Hadoop `RawComparator`.

Important APIs/types/functions: `buffer()`, `offset()`, and `size()`.

Control flow: no implementation logic; adapters such as `ByteArray` provide backing data and range metadata, while external comparators define semantics.

State and persistence: interface only.

Dependencies and integration: used by `CompareUtils.BytesComparator` and TFile key/range comparison helpers.

Risks: implementors expose mutable backing buffers, and semantic compatibility depends on using the correct `RawComparator`. Tests should cover implementations with slices and ensure comparator consumers honor offset/size rather than whole arrays.
