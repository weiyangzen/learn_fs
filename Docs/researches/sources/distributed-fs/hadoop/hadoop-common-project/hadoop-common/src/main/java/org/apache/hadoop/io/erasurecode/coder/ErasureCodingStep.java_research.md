# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureCodingStep.java

Purpose: operation-level interface describing one encoding or decoding step over chunks.

Important APIs and control flow: exposes input/output `ECBlock[]`, `performCoding(ECChunk[],ECChunk[])`, and `finish()`. Current framework comments state only one step is supported, but the abstraction anticipates multi-step codecs.

State and persistence: interface only. Implementations may hold raw coder resources and block arrays.

Dependencies and integration: returned by `ErasureCoder.calculateCoding()` and consumed by callers that read/write chunks for selected blocks.

Risks and test signals: tests should verify chunk array lengths align with block arrays and that `finish()` releases or finalizes resources when implementations require it.
