<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/crypto6.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/crypto6.json

## Purpose
Defines the IBM z17 CPU Measurement Counter Facility crypto counter-set aliases for perf. The file extends the traditional s390 crypto counters with ECC activity counters and lets users name PRNG, SHA, DEA, AES, and ECC function, cycle, and blocked-work counters instead of supplying raw event numbers.

## APIs, Types, and Functions
This is a JSON array of 20 PMU event records. Each record uses `Unit: CPU-M-CF`, decimal `EventCode` values 64 through 83, `EventName`, `BriefDescription`, and `PublicDescription`. `jevents.py` converts `CPU-M-CF` to the Linux `cpum_cf` PMU name, lowercases event names for generated aliases, and emits `event=<code>` strings in generated `pmu-events.c`.

## Control Flow, State, and Persistence
There is no runtime control flow in the file. At build time the perf PMU event generator traverses the z17 directory selected by `arch/s390/mapfile.csv`, parses the array, and persists the records as compiled C string tables. At runtime perf matches an IBM 9175/9176 z17 CPU, exposes these aliases through `perf list`, and passes the selected event code to the kernel `cpum_cf` PMU.

## Dependencies and Integration
Depends on the s390 mapfile z17 entry, `tools/perf/pmu-events/jevents.py`, `pmu-events.h`, and the kernel s390 CPU-M-CF driver. It complements z17 `extended.json`, `pai_crypto.json`, and `pai_ext.json`; the same event names are used by users and may be referenced by metrics if added later.

## Risks and Test Signals
Risks are incorrect event-code numbering, mismatched z17 facility availability, and naming drift from IBM documentation. ECC counters are z17-specific additions relative to older `crypto.json` tables, so backporting or sharing this file with older CPU models would expose unsupported aliases. Test signals include `jq` schema validation, perf jevents generation, `perf list` on z17, and checking `perf stat -e cpum_cf/<alias>/` or the generated alias against kernel PMU acceptance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/crypto6.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/extended.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/extended.json

## Purpose
Defines the z17 extended CPU-M-CF event aliases used for cache/TLB sourcing, transactional execution, multithreading diagnostics, branch prediction, decimal/vector/deflate operations, and NNPA integrated-accelerator activity. It is the main z17 counter-facility event table beyond basic and crypto counters.

## APIs, Types, and Functions
The file contains 77 event records with `Unit: CPU-M-CF`, decimal `EventCode`, `EventName`, and descriptions. Important groups include TLB2 events (`DTLB2_*`, `ITLB2_*`, `TLB2_*`), transaction events (`TX_C_TEND`, `TX_NC_TEND`, `TX_*_TABORT`), data/instruction directory-write sourcing (`DCW_*`, `IDCW_*`, `ICW_*`), SMT accounting (`CYCLES_*THRD`, `INST_*THRD`, `MT_DIAG_CYCLES_*`), and accelerator counters (`DFLT_*`, `NNPA_*`). `jevents.py` maps these records to `cpum_cf` aliases and encodes the event code as the PMU config.

## Control Flow, State, and Persistence
Build-time flow is declarative: the JSON is parsed into generated `pmu-events.c` tables for z17. Runtime flow depends on perf CPU matching; once z17 is selected, these names become available for `perf stat` and metric expressions. The file itself stores no state, but its names form a persistent ABI-like catalog for users, scripts, and sibling z17 metrics.

## Dependencies and Integration
Integrates with `arch/s390/mapfile.csv` entries for IBM 9175/9176 and with `transaction.json`, whose z17 metric expressions reference many symbols from this file. It also relies on the kernel `cpum_cf` PMU supporting the listed extended set counters and on perf's event parser accepting the generated aliases.

## Risks and Test Signals
The largest risk is cross-file consistency: if a metric references `DCW_REQ`, `L1C_TLB2_MISSES`, or transaction abort counters absent from this table, `has_event()` guards may mask the error by returning zero. Counter semantics are hardware-specific and several names are similar, so wrong codes would produce plausible but misleading performance data. Test signals are successful jevents generation, `perf list` coverage for all 77 names, metric validation for z17 `transaction.json`, and hardware smoke tests for representative TLB, cache-sourcing, transaction, NNPA, and MT diagnostic counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/extended.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/pai_crypto.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/pai_crypto.json

## Purpose
Defines z17 Processor Activity Instrumentation crypto-function events for perf. It provides fine-grained aliases for s390 cryptographic instructions and function variants, including symmetric cipher operations, hashing, message authentication, ECC operations, random number generation, digital signatures, and key wrapping.

## APIs, Types, and Functions
The JSON array has 173 records using `Unit: PAI-CRYPTO`, decimal `EventCode` values starting at 4096, `EventName`, and descriptions. The first alias is `CRYPTO_ALL`, followed by families such as `KM*`, `KMC*`, `KMA_GCM*`, `KMF*`, `KMCTR*`, `KMO*`, `KIMD*`, `KLMD*`, `KMAC*`, `PCC*`, `PRNO*`, `KDSA*`, and `PCKMO*`. `jevents.py` maps `PAI-CRYPTO` to the Linux `pai_crypto` PMU name and emits the codes as event configs.

## Control Flow, State, and Persistence
The file is a static build input. During perf build, every record becomes a generated PMU event. At runtime the aliases are available only when the selected z17 PMU table is active and the kernel exposes the `pai_crypto` PMU. Counts are hardware-maintained PAI counters, not software state in perf.

## Dependencies and Integration
Depends on z17 mapfile selection, the `PAI-CRYPTO` unit mapping in `jevents.py`, and kernel support for the s390 `pai_crypto` PMU. It complements `crypto6.json`: `crypto6.json` exposes aggregate CPU-M-CF coprocessor activity, while this file exposes per-instruction/per-function PAI categories.

## Risks and Test Signals
Risks include off-by-one code mapping across the long contiguous block, retaining IBM-reserved aliases (`IBM_RESERVED_155`, `IBM_RESERVED_156`) as user-visible events, and confusion between encrypted-key and clear-key variants. Because these are specialized hardware counters, build tests only prove syntax and generation, not semantic correctness. Useful signals are JSON parsing, generated alias inspection, `perf list pai_crypto`, and hardware `perf stat` runs for representative KM/KIMD/KDSA/PCKMO events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/pai_crypto.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/pai_ext.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/pai_ext.json

## Purpose
Defines z17 Processor Activity Instrumentation extension events for NNPA and integrated accelerator operations. The aliases expose neural-network processing activity such as arithmetic, activation, pooling, convolution, matrix multiplication, tensor/frame-size classes, and exception/normalization operations.

## APIs, Types, and Functions
The file contains 37 PMU event records with `Unit: PAI-EXT`, event codes 6144 through 6180, and descriptive names. `jevents.py` maps `PAI-EXT` to `pai_ext`. The catalog starts with `NNPA_ALL`, covers operation-level counters (`NNPA_ADD`, `NNPA_MUL`, `NNPA_CONVOLUTION`, `NNPA_MATMUL_OP`), workload-shape counters (`NNPA_SMALLBATCH`, `NNPA_LARGEDIM`, `NNPA_1MFRAME`, `NNPA_2GFRAME`), and newer operations such as `NNPA_GELU`, `NNPA_LAYERNORM`, `NNPA_SQRT`, and `NNPA_REDUCE`.

## Control Flow, State, and Persistence
Build-time parsing produces generated perf event aliases. Runtime selection follows z17 CPU matching and availability of the kernel `pai_ext` PMU. The JSON records are static metadata; the live state is entirely in hardware PAI counters read through perf.

## Dependencies and Integration
Depends on z17 model matching, `jevents.py` unit conversion, and kernel PAI extension support. It relates to `extended.json`, which contains CPU-M-CF NNPA counters for invocations, completions, lock waits, and accelerator locality; this file provides the PAI operation breakdown.

## Risks and Test Signals
Risks are mismatched code assignments, hardware/firmware availability differences for newer NNPA operations, and vague descriptions for workload-shape counters labeled only as counter numbers. Test signals are successful JSON generation, `perf list pai_ext`, alias-to-code inspection in generated `pmu-events.c`, and z17 hardware runs for `NNPA_ALL` plus a few individual operation counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/pai_ext.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/transaction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/transaction.json

## Purpose
Defines derived z17 perf metrics over CPU-M-CF event aliases. The metrics summarize transaction activity, CPI, problem-state ratio, L1 miss pressure, cache/memory sourcing percentages, finite-cache CPI components, and estimated TLB cost.

## APIs, Types, and Functions
This file contains 14 metric records rather than raw events. Each record uses `MetricName`, `MetricExpr`, and `BriefDescription`. Expressions use perf metric syntax with arithmetic, references to event aliases from `basic.json` and z17 `extended.json`, and guards such as `if has_event(TX_C_TEND) else 0`.

## Control Flow, State, and Persistence
At build time `jevents.py` parses `MetricExpr` through `metric.ParsePerfJson()` and stores the simplified metric formula in generated tables. At runtime perf resolves referenced event aliases, opens the required counters, computes formulas after sampling, and reports zero for guarded metrics when the leading event is unavailable.

## Dependencies and Integration
Depends heavily on event names from z17 `extended.json` (`TX_*`, `DCW_*`, `ICW_*`, `L1C_TLB2_MISSES`, `DTLB2_*`, `ITLB2_*`) and basic CPU-M-CF names such as `CPU_CYCLES`, `INSTRUCTIONS`, `L1I_DIR_WRITES`, and `L1D_DIR_WRITES`. It also depends on perf metric expression parsing, `has_event()`, division handling, and event scheduling constraints.

## Risks and Test Signals
Risks include division by zero when denominators such as `INSTRUCTIONS` or L1 directory writes are zero, guard conditions that check only one representative event while the expression needs many, and metric drift if referenced aliases are renamed. Good test signals are metric parser tests, `perf list --details` showing the formulas, `perf stat -M transaction,cpi,...` on z17, and negative tests on non-z17 systems confirming guarded metrics do not fail alias resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/transaction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z196/basic.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z196/basic.json

## Purpose
Defines the basic IBM z196 CPU-M-CF perf aliases for cycles, instructions, L1 instruction/data directory writes, L1 penalty cycles, and their problem-state variants.

## APIs, Types, and Functions
The file has 12 records using `Unit: CPU-M-CF`, event codes 0-5 and 32-37, names such as `CPU_CYCLES`, `INSTRUCTIONS`, `L1I_DIR_WRITES`, and `PROBLEM_STATE_INSTRUCTIONS`, plus brief/public descriptions. `jevents.py` maps these to the `cpum_cf` PMU and generates standard perf aliases.

## Control Flow, State, and Persistence
The JSON is parsed during perf build for the z196 table selected by the s390 mapfile IBM 2817/2818 pattern. At runtime perf exposes the aliases for matching machines and reads kernel `cpum_cf` counters. No mutable state is stored in the JSON.

## Dependencies and Integration
These names are foundational for z196 metrics and for user scripts that rely on stable s390 CPU-M-CF aliases. They share the same schema and event-code layout as zEC12 `basic.json`, which indicates continuity across generations.

## Risks and Test Signals
Risks are low but include wrong problem-state code ranges and mismatch with kernel counter-set authorization. Test signals include JSON syntax checks, generated `pmu-events.c` inspection, `perf list` on z196, and smoke tests for `CPU_CYCLES` and `INSTRUCTIONS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z196/basic.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z196/crypto.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z196/crypto.json

## Purpose
Defines z196 CPU-M-CF crypto counter aliases for aggregate PRNG, SHA, DEA, and AES function, cycle, blocked-function, and blocked-cycle accounting.

## APIs, Types, and Functions
The file contains 16 records with `Unit: CPU-M-CF`, event codes 64 through 79, `EventName`, `BriefDescription`, and `PublicDescription`. It follows a four-counter pattern per crypto class: functions issued, cycles busy, functions blocked by another CPU, and blocked cycles.

## Control Flow, State, and Persistence
Perf builds the records into z196 PMU event tables via `jevents.py`. Runtime behavior is alias lookup and `cpum_cf` counter programming on matched z196 CPUs. The JSON file itself has no execution or persistence beyond generated tables.

## Dependencies and Integration
Depends on z196 mapfile selection, `CPU-M-CF` unit conversion, and kernel support for the crypto activity counter set. The same event-code block is reused by zEC12 and extended by z17 `crypto6.json` with ECC counters.

## Risks and Test Signals
Risks include exposing counters when crypto counter-set authorization is absent, and semantic ambiguity where PRNG descriptions mention shared DEA/AES/SHA coprocessors. Test signals are successful event generation, `perf list` visibility, and hardware readings for each of the four counter families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z196/crypto.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z196/extended.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z196/extended.json

## Purpose
Defines z196 extended CPU-M-CF aliases for cache sourcing and translation activity. The table covers L1 directory writes sourced from L2/L3/L4/local memory, first-level TLB misses/writes, huge-page TLB writes, and second-level translation-table writes.

## APIs, Types, and Functions
The JSON array has 24 `CPU-M-CF` records. Important names include `L1D_L2_SOURCED_WRITES`, `L1I_L2_SOURCED_WRITES`, `DTLB1_MISSES`, `ITLB1_MISSES`, `L2C_STORES_SENT`, `L1D_*_L3_SOURCED_WRITES`, `L1*_ONBOOK_L4_SOURCED_WRITES`, `L1*_OFFBOOK_L4_SOURCED_WRITES`, `DTLB1_HPAGE_WRITES`, and `TLB2_*_WRITES`.

## Control Flow, State, and Persistence
The file is consumed at perf build time and materialized into the generated z196 PMU event table. At runtime perf maps names to event codes for the `cpum_cf` PMU. Counter values are hardware state; the JSON does not persist runtime values.

## Dependencies and Integration
Depends on IBM z196 CPU matching in `arch/s390/mapfile.csv`, `jevents.py`, and kernel support for the extended counter set. It forms the generation-specific event catalog that later zEC12/z17 tables expand and rename around newer cache topology terms.

## Risks and Test Signals
Risks include topology-specific naming mistakes (`onbook`, `offbook`, `onchip`, `offchip`) and incorrect code reuse across CPU generations. Test signals are generated-table validation, `perf list` on z196 hardware, and comparing alias names/codes against IBM counter-set documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z196/extended.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_zec12/basic.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_zec12/basic.json

## Purpose
Defines the basic zEC12 CPU-M-CF perf aliases for core execution and L1 cache accounting, mirroring the z196 basic event layout.

## APIs, Types, and Functions
The file has 12 records with `Unit: CPU-M-CF`, event codes 0-5 and 32-37, and names for cycles, instructions, L1 I/D directory writes, L1 I/D penalty cycles, and problem-state versions. `jevents.py` converts these records into `cpum_cf` aliases.

## Control Flow, State, and Persistence
At build time the perf event generator includes this file in the zEC12 generated event table selected for IBM 2827/2828 models. At runtime perf resolves the aliases and asks the kernel CPU-M-CF PMU to count the selected hardware events.

## Dependencies and Integration
Depends on the s390 mapfile, perf PMU event generation, and kernel `cpum_cf` support. The names are used by zEC12 metrics such as `transaction.json` and are intentionally stable across z196 and later s390 tables.

## Risks and Test Signals
Risks are primarily source-of-truth drift from the hardware manual and missing counter authorization on target systems. Test signals include JSON generation, `perf list`, and `perf stat` for `CPU_CYCLES`, `INSTRUCTIONS`, and problem-state counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_zec12/basic.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_zec12/crypto.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_zec12/crypto.json

## Purpose
Defines zEC12 CPU-M-CF crypto aliases for PRNG, SHA, DEA, and AES activity. It preserves the z196 crypto event layout for the zEC12 PMU table.

## APIs, Types, and Functions
The JSON contains 16 `CPU-M-CF` records with event codes 64-79. Each crypto family has counters for total functions, busy cycles, blocked functions, and blocked cycles. `jevents.py` turns the records into lower-case perf aliases on `cpum_cf`.

## Control Flow, State, and Persistence
The table is parsed only during perf build. Runtime state resides in CPU-M-CF hardware counters and is read through perf when users select these aliases.

## Dependencies and Integration
Depends on zEC12 model matching, the `CPU-M-CF` unit mapping, and kernel support for the crypto counter set. It sits beside zEC12 `basic.json`, `extended.json`, and `transaction.json`.

## Risks and Test Signals
Risks are incorrect code assignment, unsupported counter-set access on a given LPAR, and confusion between function counts and cycle counts. Test signals are valid JSON generation, generated alias checks, `perf list`, and representative hardware `perf stat` runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_zec12/crypto.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_zec12/extended.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_zec12/extended.json

## Purpose
Defines zEC12 extended CPU-M-CF aliases for TLB, cache sourcing, and transactional-execution counters. It expands z196-style cache/TLB events with zEC12 L2I/L2D sourcing, intervention variants, and transaction begin/end/abort counters.

## APIs, Types, and Functions
The file contains 35 records with `Unit: CPU-M-CF`. It includes first-level TLB misses/writes, huge-page and second-level TLB writes, L1 data/instruction sourcing from L2I/L2D/local memory/L3/L4, invalid/intervention variants, and transaction counters `TX_NC_TEND`, `TX_C_TEND`, `TX_NC_TABORT`, `TX_C_TABORT_NO_SPECIAL`, and `TX_C_TABORT_SPECIAL`.

## Control Flow, State, and Persistence
The JSON is static input to `jevents.py`, which emits zEC12 generated event tables. Runtime perf flow is alias resolution followed by `cpum_cf` event programming. No file-level mutable state exists.

## Dependencies and Integration
Depends on zEC12 CPU matching and kernel extended counter support. `transaction.json` in the same directory references the transaction aliases from this file, while basic metrics rely on sibling `basic.json`.

## Risks and Test Signals
Risks include metrics silently becoming wrong if any transaction alias is renamed, topology naming differences between z196/zEC12/z17, and invalid/intervention suffix confusion. Test signals include successful metric parsing, `perf list` coverage, and `perf stat -M transaction` plus direct transaction alias tests on zEC12 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_zec12/extended.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_zec12/transaction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_zec12/transaction.json

## Purpose
Defines a single zEC12 derived metric named `transaction` that reports total transactional-execution activity.

## APIs, Types, and Functions
The metric record has `BriefDescription`, `MetricName: transaction`, and a `MetricExpr` summing `TX_C_TEND`, `TX_NC_TEND`, `TX_NC_TABORT`, `TX_C_TABORT_SPECIAL`, and `TX_C_TABORT_NO_SPECIAL`.

## Control Flow, State, and Persistence
At build time perf parses the metric expression and stores it in generated tables. At runtime perf schedules the referenced counters from zEC12 `extended.json`, collects counts, and reports their sum. There is no `has_event()` guard in this older metric, so all referenced event aliases must resolve.

## Dependencies and Integration
Depends directly on zEC12 `extended.json` transaction aliases and on perf metric expression parsing. It also depends on the kernel being able to schedule the required CPU-M-CF counters together or in a valid multiplexed configuration.

## Risks and Test Signals
Risks include hard failure on systems where one transaction event is unavailable, counter scheduling constraints, and division-free but still semantically broad aggregation of committed and aborted transactions. Test signals are metric parser success, `perf list -M transaction`, and hardware `perf stat -M transaction` on zEC12.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_zec12/transaction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/arch-std-events.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/arch-std-events.json

## Purpose
Provides a synthetic architecture-standard event used by perf PMU event generator tests. It lets test CPU JSON files reference a common `L3_CACHE_RD` event through `ArchStdEvent` without duplicating event metadata.

## APIs, Types, and Functions
The file contains one event record with `EventCode: 0x40`, `EventName: L3_CACHE_RD`, `BriefDescription`, and `PublicDescription`. In the pmu-events schema, architecture-standard JSONs are looked up by `EventName` when another file uses `ArchStdEvent`.

## Control Flow, State, and Persistence
During jevents test generation, the parser loads architecture root standard events, resolves `ArchStdEvent: L3_CACHE_RD` from child files, and emits the resolved event as if it were present locally. There is no runtime state beyond generated test tables.

## Dependencies and Integration
Integrates with `arch/test/test_soc/cpu/cache.json`, which contains only an `ArchStdEvent` reference. It exercises the standard-event dereference path described in the pmu-events README and covered by perf PMU event tests.

## Risks and Test Signals
Risks are narrow: if lookup-by-name changes, the cache fixture fails or emits incomplete events. Test signals are the perf `pmu-events` unit tests, generated table inspection for `L3_CACHE_RD`, and ensuring the child cache fixture inherits description and event code correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/arch-std-events.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/cpu/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/cpu/branch.json

## Purpose
Defines two synthetic branch-prediction events for the perf test architecture. The file exists to test normal per-topic event parsing for CPU PMU JSONs.

## APIs, Types, and Functions
The array contains `bp_l1_btb_correct` with event code `0x8a` and `bp_l2_btb_correct` with event code `0x8b`, each with a brief description. There is no `Unit`, so `jevents.py` maps them to the default core PMU marker.

## Control Flow, State, and Persistence
At build/test generation time the records become generated test PMU aliases. Runtime semantics are not tied to real hardware; the file is fixture data for parser and lookup tests.

## Dependencies and Integration
Depends on the `arch/test` map/test setup and the default-unit behavior in `jevents.py`. It integrates with perf tests that compare generated events from `pmu-events.c` against expected fixture output.

## Risks and Test Signals
Risks include accidental treatment as a real hardware table, default PMU mapping regressions, and event-name case handling. Test signals are `tools/perf/tests/pmu-events.c` expectations, generated alias strings, and successful JSON traversal of the test SOC CPU directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/cpu/branch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/cpu/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/cpu/cache.json

## Purpose
Tests the `ArchStdEvent` dereference mechanism for perf PMU event JSONs by importing the synthetic standard `L3_CACHE_RD` event.

## APIs, Types, and Functions
The file contains one object with `ArchStdEvent: L3_CACHE_RD`. It intentionally omits `EventName`, `EventCode`, and descriptions so the generator must resolve them from `arch/test/arch-std-events.json`.

## Control Flow, State, and Persistence
During generation, `jevents.py` detects `ArchStdEvent`, looks up the standard event by name, and substitutes/merges the referenced metadata into the generated output. The fixture has no independent runtime state or hardware behavior.

## Dependencies and Integration
Depends directly on `arch/test/arch-std-events.json` and the architecture-standard lookup path described in the pmu-events README. It is part of the test SOC CPU fixture set consumed by perf PMU event tests.

## Risks and Test Signals
Risks are missing or duplicate standard-event names and regressions where local fields no longer inherit correctly. Test signals include generated output containing event code `0x40` and description text from the standard event, plus PMU event unit tests that validate standard-event expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/cpu/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/cpu/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/cpu/metrics.json

## Purpose
Provides synthetic perf metric fixtures for expression parsing, metric dependency resolution, grouping, escaped event names, helper functions, cycles in metric references, and bandwidth-style formulas.

## APIs, Types, and Functions
The file contains 15 metric records with `MetricName`, `MetricExpr`, and optional `MetricGroup`. It defines simple reciprocal metrics (`CPI` as `1 / IPC`), direct event formulas (`IPC`), complex SMT arithmetic, escaped event names like `l1d\\-loads\\-misses`, derived cache metrics using `max()` and `d_ratio()`, cyclic references (`M1` and `M2`), self-reference (`M3`), and `L1D_Cache_Fill_BW` using `duration_time`.

## Control Flow, State, and Persistence
At generation time `jevents.py` parses each expression with the perf metric parser and writes generated metric metadata. At runtime in tests, perf resolves metric references and event names to exercise dependency handling. The cyclic metrics are deliberate fixtures for validation paths rather than usable production formulas.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/metric.py`, `metric_test.py`, and the PMU event test harness. It also relies on known fixed event rewrites in `jevents.py` for names such as `inst_retired.any` and `cpu_clk_unhalted.thread`.

## Risks and Test Signals
Risks include accidentally accepting cyclic metrics in production paths, breaking escaped hyphen parsing, or changing helper-function semantics without updating fixtures. Test signals are metric parser unit tests, generated output comparisons, and explicit failures or diagnostics for cyclic/self-referential metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/cpu/metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/cpu/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/cpu/other.json

## Purpose
Defines synthetic core PMU events that exercise optional event fields such as unit masks, counter constraints, and sample-after values.

## APIs, Types, and Functions
The file has three records: `SEGMENT_REG_LOADS.ANY`, `DISPATCH_BLOCKED.ANY`, and `EIST_TRANS`. Fields include `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `EventName`, and `BriefDescription`. With no `Unit`, these target the default core PMU path.

## Control Flow, State, and Persistence
The fixture is parsed into generated event metadata during perf test builds. `jevents.py` combines `EventCode` and `UMask`, preserves counter and sampling fields, and exposes the generated aliases to tests. There is no real runtime hardware dependency.

## Dependencies and Integration
Depends on parser support for x86-like fields (`UMask`, `Counter`, `SampleAfterValue`) even inside the test architecture. It integrates with generated PMU event comparison tests that verify field formatting.

## Risks and Test Signals
Risks include regressions in optional field serialization, especially zero-valued `UMask: 0x0`, and case/dot handling in event names. Test signals are generated event string comparisons and `perf list` test fixtures showing the expected encoded fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/cpu/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/cpu/uncore.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/cpu/uncore.json

## Purpose
Provides synthetic uncore PMU event fixtures for unit-to-PMU conversion, uncore field encoding, hyphenated event names, and vendor-specific unit names.

## APIs, Types, and Functions
The file contains seven events across units `hisi_sccl,ddrc`, `CBO`, `hisi_sccl,l3c`, `imc_free_running`, and `imc`. Fields include `EventCode`, `UMask`, `Counter`, `CounterMask`, `Invert`, `EdgeDetect`, `PublicDescription`, and `Unit`. `jevents.py` maps `CBO` to `uncore_cbox`, preserves Hisilicon comma units, and maps unknown units like `imc` to `uncore_imc`.

## Control Flow, State, and Persistence
Generation reads these records and emits uncore PMU aliases with unit-specific PMU names. The entries are fixtures, so runtime behavior is focused on parser/test expectations rather than real uncore hardware.

## Dependencies and Integration
Depends on `unit_to_pmu()` mapping in `jevents.py` and PMU event tests that verify generated PMU names and event encodings. The hyphenated `event-hyphen` and `event-two-hyph` names exercise name sanitization and lookup behavior.

## Risks and Test Signals
Risks include breaking special unit mappings, mishandling comma-containing unit names, and formatting optional fields incorrectly. Test signals are generated table comparisons for `uncore_cbox`, `hisi_sccl,*`, `uncore_imc*`, and encoded fields such as `cmask`, `inv`, and `edge`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/cpu/uncore.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/sys/uncore.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/sys/uncore.json

## Purpose
Defines synthetic system uncore PMU fixtures for alternate config fields, compatibility matching, node-type filtering, and sys PMU unit names.

## APIs, Types, and Functions
The file has three records: `sys_ddr_pmu.write_cycles` with `EventCode`, `sys_ccn_pmu.read_cycles` with `ConfigCode`, and `sys_cmn_pmu.hnf_cache_miss` with `EventidCode` plus `NodeType`. All include `Unit` and `Compat`; the compatibility values cover a plain string, a hex-like value, and a regex-style pattern.

## Control Flow, State, and Persistence
During generation `jevents.py` chooses the event encoding field in priority order: `ConfigCode` becomes `config=...`, `EventidCode` becomes `eventid=...`, otherwise `EventCode` becomes `event=...`. Runtime tests can then verify generated sys-PMU aliases and compatibility metadata. The JSON itself stores no mutable state.

## Dependencies and Integration
Depends on parser support for `ConfigCode`, `EventidCode`, `NodeType`, `Compat`, and sys PMU `Unit` names. It integrates with PMU event tests that check system PMU handling separately from core CPU fixtures.

## Risks and Test Signals
Risks include wrong precedence between event/config/eventid fields, dropped `NodeType`, and broken compatibility-pattern serialization. Test signals are generated output comparisons for `config=0x2c`, `eventid=0x1`, `event=0x2b`, retained `Compat`, and retained `NodeType`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/sys/uncore.json -->
