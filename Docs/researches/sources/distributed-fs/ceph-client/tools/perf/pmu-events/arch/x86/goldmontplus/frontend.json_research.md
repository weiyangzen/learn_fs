## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/frontend.json

**Purpose:** Goldmont Plus frontend topic with eight aliases for BACLEAR conditions, predecode restrictions, instruction-cache accesses/hits/misses, and micro-sequencer decoded entries. It exposes fetch/decode disruption and instruction-cache health.

**Schema and important records:** Uses standard event fields without PEBS-specific metadata. `BACLEARS.ALL`, `.COND`, and `.RETURN` classify branch-address-clear recovery; `DECODE_RESTRICTION.PREDECODE_WRONG` tracks decode restriction from predecode mistakes; `ICACHE.ACCESSES`, `.HIT`, and `.MISSES` count I-cache behavior; `MS_DECODED.MS_ENTRY` tracks micro-sequencer decoding.

**Control flow and integration:** `jevents.py` emits the file as a frontend topic for the Goldmont Plus model. Runtime consumers can select aliases directly or use them as components in frontend-bound analysis.

**State and persistence:** No mutable state. The JSON persists symbolic names, encodings, and descriptions in generated C tables.

**Dependencies:** Depends on Goldmont Plus frontend PMU encodings and integrates with pipeline-level `UOPS_NOT_DELIVERED.ANY`, fetch-stall events in `other.json`, and virtual-memory ITLB events.

**Risks:** Frontend events often have overlapping interpretations. Inaccurate descriptions can lead users to double-count or misattribute stalls between I-cache, ITLB, decode, and branch-recovery sources.

**Test signals:** JSON parse and jevents generation. On target hardware, compare `ICACHE.ACCESSES`, `ICACHE.HIT`, and `ICACHE.MISSES` for plausible relationships, and use `perf list frontend` to ensure topic grouping is correct.
