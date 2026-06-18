## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/other.json

**Purpose:** Grand Ridge miscellaneous topic with two events: last-branch-record insertions and OCR streaming write responses.

**Schema and important records:** Standard event fields plus `Deprecated` on `LBR_INSERTS.ANY`, and `MSRIndex`/`MSRValue` on `OCR.STREAMING_WR.ANY_RESPONSE`. The LBR event is compatibility-sensitive, while the OCR event tracks streaming write requests with any offcore response.

**Control flow and integration:** `jevents.py` emits both into Grand Ridge's `other` topic. The OCR record uses MSR selector conversion; the deprecated marker persists into generated metadata.

**State and persistence:** Static metadata only. Runtime LBR insertion and streaming write counts are held in PMU counters for the perf session.

**Dependencies:** Depends on Grand Ridge LBR/OCR event encodings and offcore MSR mapping. Related pipeline file has `MISC_RETIRED.LBR_INSERTS`, so users may see both old and newer naming.

**Risks:** Deprecated aliases can confuse users if preferred replacements are not clear. OCR streaming write selector errors are hard to catch because any-response counts may look plausible under memory traffic.

**Test signals:** JSON/build validation; `perf list other` should show deprecation handling. Runtime streaming/non-temporal store tests can exercise `OCR.STREAMING_WR.ANY_RESPONSE`.
