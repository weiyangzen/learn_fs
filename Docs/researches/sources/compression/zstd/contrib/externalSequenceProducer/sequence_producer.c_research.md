# sources/compression/zstd/contrib/externalSequenceProducer/sequence_producer.c

Purpose: simple demonstration match finder implementing `ZSTD_sequenceProducer_F` for the external sequence producer API.

Important behavior: uses a 1024-entry hash table with match length search size 4. For each input position, it hashes the current bytes with `ZSTD_hashPtr`, checks the previous index in the table, counts match length with `ZSTD_count`, emits a `ZSTD_Sequence` when the match meets `ZSTD_MINMATCH_MIN` and the offset fits the provided `windowSize`, advances by match length, and finally emits a terminal literal-only sequence. Dict inputs, capacity, compression level, and producer state are ignored.

State, dependencies, and integration: state is a stack hash table per call. It depends on `zstd_compress_internal.h` internals and the local header, so it is tied to static/internal API compatibility.

Risks and test signals: it does not honor `outSeqsCapacity`, so unusual small capacities could overflow. It ignores dictionaries and is intentionally naive; round-trip validation in `main.c` and contrib build coverage are the key signals.
