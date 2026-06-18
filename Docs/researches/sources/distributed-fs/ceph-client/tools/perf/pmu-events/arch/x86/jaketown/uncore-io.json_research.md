# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/uncore-io.json

## Purpose

`uncore-io.json` defines 36 Jaketown uncore IO PMU events for the `R2PCIe` unit. These events expose PCIe/ring bridge behavior: IIO credit accounting, ring channel usage, receive ring pressure, egress fullness/not-empty cycles, and NACKs. The file complements `uncore-interconnect.json`, which contains the analogous `R3QPI` bridge events for QPI-facing traffic.

The public API is the set of `UNC_R2_*` event aliases. They let perf users diagnose IO-facing interconnect pressure, PCIe credit starvation, and ring AD/AK/BL traffic directionality.

## Important API Surface and Data Shape

The file is a JSON array of 36 unique event objects with these keys: `BriefDescription`, `Counter`, `EventCode`, `EventName`, `PerPkg`, `PublicDescription`, `UMask`, and `Unit`.

All records use `Unit: "R2PCIe"` and `PerPkg: "1"`. Event families are:

- `UNC_R2_CLOCKTICKS`: uncore clock cycles for the R2PCIe domain, using counters `0,1,2,3`.
- `UNC_R2_IIO_CREDITS_ACQUIRED`, `UNC_R2_IIO_CREDITS_REJECT`, and `UNC_R2_IIO_CREDITS_USED`: DRS, NCB, and NCS credit accounting using event codes `0x33`, `0x34`, and `0x32`.
- `UNC_R2_RING_AD_USED`, `UNC_R2_RING_AK_USED`, and `UNC_R2_RING_BL_USED`: clockwise/counter-clockwise and even/odd ring channel usage variants using event codes `0x7`, `0x8`, and `0x9`.
- `UNC_R2_RING_IV_USED.ANY`: IV ring usage.
- `UNC_R2_RxR_AK_BOUNCES` and `UNC_R2_RxR_CYCLES_NE` variants for receive-ring activity.
- `UNC_R2_TxR_CYCLES_FULL`, `UNC_R2_TxR_CYCLES_NE`, and `UNC_R2_TxR_NACKS`: AD/AK/BL egress pressure and NACK indicators.

Most events allow counters `0,1`; ring usage and clock events generally allow `0,1,2,3`; the TxR cycle events are restricted to counter `0`.

## Control Flow

The file has no executable control flow. Its external flow is:

1. The perf pmu-events generation tooling reads the Jaketown JSON catalog.
2. The R2PCIe records are emitted into generated event tables with event code, umask, unit, and counter metadata.
3. Runtime perf CPU-model matching selects the Jaketown table.
4. `perf list` exposes `UNC_R2_*` names, and `perf stat -e` resolves a selected name to an R2PCIe uncore PMU configuration.
5. The uncore PMU driver enforces availability and counter restrictions on the target hardware.

The records are ordered by hardware topic: clock, credits, ring channel usage, receive-ring state, then transmit-ring pressure.

## State and Persistence Behavior

The only persistent state is the checked-in JSON event mapping. It defines stable perf aliases and hardware encodings. There is no local mutation, caching, or generated output in this source file.

All events are package scoped (`PerPkg: "1"`), so measurements represent package-level uncore IO domains. This is important for interpretation on multi-socket systems and for tools that aggregate counts.

## Dependencies and Integration Points

This file depends on:

- perf's expected PMU JSON schema and generated table pipeline.
- Jaketown R2PCIe hardware event encodings.
- The runtime uncore PMU implementation that recognizes R2PCIe units.
- Related R3QPI and QPI definitions in `uncore-interconnect.json`, because cross-unit diagnostics often compare IO-facing and QPI-facing ring pressure.

Its most important integration point is the `Unit` string. If `R2PCIe` does not match the generated/runtime PMU naming convention, all aliases in this file become undiscoverable or unprogrammable even if the event codes are correct.

## Risks and Edge Cases

- Two records omit `UMask` (`UNC_R2_CLOCKTICKS` and possibly another simple selector), so schema validation must allow intentional mask absence.
- TxR full/not-empty records use only counter `0`; scheduling them like the broader ring events would be incorrect.
- The credit events distinguish DRS, NCB, and NCS by unit mask. Copy/paste mistakes in those masks would produce plausible but wrong measurements.
- `PerPkg` package scope can surprise users expecting per-core IO attribution.
- Names are public perf aliases. Renaming `UNC_R2_*` entries breaks user scripts and dashboards.

## Test Signals

- `jq` should parse the file as 36 objects with 36 unique `EventName` values.
- Every record should have `Unit == "R2PCIe"` and `PerPkg == "1"`.
- Counter lists should be checked by family: clock/ring events permit `0,1,2,3`, credit and NACK events mostly `0,1`, and TxR cycle pressure events `0`.
- Generated pmu-events tables should build without warnings.
- On supported hardware, `perf list` should show `UNC_R2_CLOCKTICKS`, a credit event, a ring event, and a TxR pressure event.
- A runtime smoke test can use `perf stat -e UNC_R2_CLOCKTICKS` plus one restricted counter event to catch parser or unit-name regressions.
