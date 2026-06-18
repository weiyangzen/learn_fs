# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/uncore-memory.json

Purpose: defines 18 Meteor Lake uncore memory-controller events. The file covers free-running memory-controller read CAS, write CAS, and total request counters for MC0 and MC1, plus programmable iMC events for ACT, CAS, PRE, thermal warm/hot, read data, write data, and total data transfers.

Important APIs/types/functions: each object is a perf PMU event descriptor. Free-running entries use `Unit` `imc_free_running_0` or `imc_free_running_1`, fixed event code `0xff`, package scope, and specific counter indices for read/write/total request counts. Programmable entries use `Unit` `iMC`, counters `0,1,2,3,4`, event codes such as `0x22` for read CAS, `0x23` for write CAS, `0x3A` for read data, and `0x3C` for total data. Several entries include `PublicDescription` clarifying 32B/64B CAS and request merge semantics.

Control flow: build-time `jevents.py` turns the descriptors into perf aliases. Runtime perf chooses the correct uncore PMU unit, programs the event or reads the free-running counter, and reports package-level memory-controller activity. Users typically combine these events in `perf stat` to estimate bandwidth, command mix, page behavior, and thermal throttling signals.

State and persistence: no mutable source state. Free-running counters may already be advancing outside a perf session, while programmable iMC counters count only while configured. The file itself persists only event metadata. Counts are package-level because all rows set `PerPkg`.

Dependencies and integration points: depends on Meteor Lake kernel PMU support for `iMC` and `imc_free_running_*` units and the perf PMU event generation pipeline. It integrates with uncore interconnect events for traffic source analysis and with core pipeline/memory-stall events for correlating bandwidth pressure with frontend/backend stalls.

Risks: request counts and DRAM command counts are not equivalent to bytes; descriptions warn that partial/full-line writes and merged writes can make request count higher than DRAM bandwidth. Data transfer events increment in 32B chunks, so downstream metrics must multiply correctly. Free-running MC0 and MC1 counter indices are explicit and easy to transpose. Thermal warm/hot events are rank-level state indicators, not byte traffic.

Test signals: JSON validation, generated alias inspection, `perf list` checks for both free-running and programmable iMC events, and memory bandwidth smoke tests using read, write, and mixed workloads. Compare `UNC_M_RD_DATA`, `UNC_M_WR_DATA`, and `UNC_M_TOTAL_DATA` for arithmetic consistency, and compare MC0/MC1 free-running counters on systems where both controllers are active.
