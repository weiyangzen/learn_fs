## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/other.json

**Purpose:** Panther Lake miscellaneous event topic with five records that do not fit the cache, frontend, memory, or floating-point buckets. It covers hardware/page-fault assists, streaming-write OCR responses, atom BTB clears, and core uncore-request backpressure.

**Schema and important records:** `ASSISTS.HARDWARE` and `ASSISTS.PAGE_FAULT` are core events on `EventCode: 0xc1` with different umasks. `OCR.STREAMING_WR.ANY_RESPONSE` is a core offcore/OCR event using `EventCode: 0x2A,0x2B`, `MSRIndex: 0x1a6,0x1a7`, and `MSRValue: 0x10800`. `PREDICTION.BTCLEAR` is an atom branch-prediction event on event `0xe8`. `XQ.FULL` is a core cycle event with `CounterMask: 1` for cycles where uncore cannot accept further requests.

**Control flow and integration:** Perf's PMU event build places these records under the Panther Lake `other` topic. Runtime handling is mixed: assists and BTCLEAR are ordinary event-code/umask counters, `OCR.STREAMING_WR.ANY_RESPONSE` requires OCR MSR selector programming, and `XQ.FULL` uses counter-mask cycle counting. These events provide supporting diagnostics for hardware assists, streaming-store traffic, BTB behavior, and uncore queue pressure.

**State and persistence:** Static event metadata. Generated perf tables persist the raw selector fields and sample periods. Runtime state consists of programmed counters, OCR MSR state for streaming writes, and per-session counts.

**Dependencies:** Depends on Panther Lake core/atom PMU encodings and OCR support. `XQ.FULL` complements cache and memory offcore events by indicating uncore request acceptance pressure. Assist events overlap conceptually with floating-point assist events but intentionally count broader hardware and page-fault assist categories.

**Risks:** The small file can be overlooked by topic-based validation, leaving miscellaneous but useful events missing from generated tables. `ASSISTS.HARDWARE` has a broad definition and should not be compared directly with narrow FP assists. `OCR.STREAMING_WR.ANY_RESPONSE` has the same OCR selector risk as cache/memory OCR records. `XQ.FULL` requires `CounterMask` retention to remain a cycle-presence event.

**Test signals:** Validate all five records appear under `perf list other` for Panther Lake. Runtime smoke tests should check ordinary assist counters, atom BTCLEAR availability, OCR streaming-write selector programming, and `XQ.FULL` movement under memory/uncore pressure. Schema tests should retain `CounterMask` and OCR `MSRIndex`/`MSRValue` fields.
