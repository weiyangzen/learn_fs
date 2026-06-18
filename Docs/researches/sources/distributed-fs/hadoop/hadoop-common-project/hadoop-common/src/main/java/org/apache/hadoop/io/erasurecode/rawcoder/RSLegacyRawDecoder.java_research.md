# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSLegacyRawDecoder.java

Purpose: older pure-Java Reed-Solomon decoder based on HDFS-RAID style Vandermonde/Galois-field operations.

Important APIs/types/functions: `errSignature`, `primitivePower`; overrides public `decode()` for ByteBuffer and byte arrays to reorder data/parity; `doDecodeImpl()` overloads; `doDecode()` overloads; `adjustOrder()`; temporary buffer helpers.

Control flow: public decode reorders caller layout from data-first/parity-after to the parity-first layout expected by the legacy math. The internal decode identifies null inputs as erased/not-read positions, maps requested erased indexes to caller outputs, allocates temporary buffers for unrequested nulls, computes syndromes with `RSUtil.GF.substitute`, then solves a Vandermonde system to recover missing units.

State and persistence: object-scoped `errSignature` and `primitivePower`; temporary buffers are per call in the current code. No durable state.

Dependencies and integration: extends `RawErasureDecoder`, uses `CoderUtil`, `RSUtil`, `GaloisField`, and `ErasureCoderOptions`; produced by legacy RS factory.

Risks: can compute unrequested not-read units unnecessarily; comments flag HADOOP-11871. `allowChangeInputs()` is relevant indirectly via legacy encoder, while decoder mutates outputs/temp buffers. Tests should cover data and parity erasures, order adjustment, nulls matching erased indexes, too many erasures, and parity with modern RS/native coders where compatible.
