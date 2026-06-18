<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resstats.h -->
# sources/distributed-fs/coda/coda-src/resolution/resstats.h

Purpose: declares resolution statistics structures and histogram bucket macros.

Important APIs/types: `fileresstats`, `dirresstats`, and `conflictstats` count outcomes. `logshiphisto` tracks shipped log sizes and maximum entries. `logsize`, `varlhisto`, and `logstats` track recoverable log size, allocation/free counts, wraparounds, and admin growth. `resstats` aggregates these per volume and provides update/print hooks. Macros `Lsize` and `VarlHisto` expose nested log stats.

State/persistence: declares global `ResStatsList`; per-volume objects are expected to live with volume-log state.

Dependencies/integration: uses `olist` and is consumed throughout resolution and recoverable log code.

Risks/test signals: bucket macros are deeply nested and hard to audit for boundary correctness. Some counters distinguish file, directory, conflict, and log behavior but are only as accurate as call sites. Unit tests should hit bucket boundaries around powers of two and verify aggregation updates do not drop user-resolver counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resstats.h -->
