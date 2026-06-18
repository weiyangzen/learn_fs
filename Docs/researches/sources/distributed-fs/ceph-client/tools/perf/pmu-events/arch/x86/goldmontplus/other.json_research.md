## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/other.json

**Purpose:** Goldmont Plus miscellaneous topic with five events for aggregate fetch stalls, ITLB-fill-related fetch stalls, and hardware interrupt delivery/masking behavior.

**Schema and important records:** Standard `pmu_event` fields. `FETCH_STALL.ALL` and `FETCH_STALL.ITLB_FILL_PENDING_CYCLES` count frontend fetch stall cycles. `HW_INTERRUPTS.RECEIVED`, `.MASKED`, and `.PENDING_AND_MASKED` account for interrupt activity that may perturb workload measurements.

**Control flow and integration:** `jevents.py` emits these into the Goldmont Plus event table under the `other` topic. Runtime perf event lookup treats them like the other core aliases.

**State and persistence:** Static metadata only; interrupt and stall counts live in hardware counters during a perf session.

**Dependencies:** Integrates with frontend and virtual-memory topics because fetch stalls can be caused by I-cache or ITLB behavior. Interrupt aliases depend on hardware PMU support for counting interrupt masking/receipt events.

**Risks:** The `other` topic is easy for users and tests to skip even though interrupts can explain noisy profiles. Fetch-stall aliases may be misinterpreted if compared directly with instruction-cache fill pending cycles from `cache.json`.

**Test signals:** JSON parse/build; `perf list other` or raw alias dump should include all five names. Runtime smoke tests can generate interrupt load and compare interrupt counters with expected activity.
