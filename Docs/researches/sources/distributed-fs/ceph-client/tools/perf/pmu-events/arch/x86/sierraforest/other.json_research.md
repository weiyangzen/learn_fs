# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/other.json

## Purpose

This two-entry Sierra Forest table holds miscellaneous core events that do not fit the cache, memory, frontend, floating-point, or pipeline buckets. It includes a deprecated last-branch-record insert alias and an offcore response event for streaming writes.

## Important APIs, Types, and Data

Entries use standard event fields: `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and optional `Deprecated`, `PublicDescription`, `MSRIndex`, and `MSRValue`. `LBR_INSERTS.ANY` uses event `0xe4`, mask `0x1`, is marked deprecated, and aliases `MISC_RETIRED.LBR_INSERTS`. `OCR.STREAMING_WR.ANY_RESPONSE` uses event `0xB7`, mask `0x1`, offcore MSRs `0x1a6,0x1a7`, and filter value `0x10800`.

## Control Flow

Perf resolves these aliases like other core events. The LBR alias counts only when LBRs are enabled/configured, and should generally be reached through its non-deprecated replacement. The streaming-write OCR event requires offcore MSR programming before the counter can count responses.

## State and Persistence Behavior

The file persists compatibility and miscellaneous aliases. Runtime state includes normal core counter state, LBR facility configuration for `LBR_INSERTS.ANY`, and temporary offcore MSR filter state for streaming writes. The deprecated marker is persistent user-facing metadata and should steer new metric formulas away from the old name.

## Dependencies and Integration Points

This file integrates with perf's LBR support, offcore response support, generated pmu-events tables, and any metrics or workflows that track streaming store traffic. It also ties to `pipeline.json`, where `MISC_RETIRED.LBR_INSERTS` is the preferred alias for the same LBR behavior.

## Risks

Using the deprecated LBR alias in new metrics can preserve stale naming. LBR counting depends on LBR enablement, so zero counts may indicate configuration rather than absence of branches. The streaming-write offcore filter has the same risk as other OCR events: an incorrect `MSRValue` silently changes the response class. Offcore MSR resources can conflict with other OCR events in the same group.

## Test Signals

Tests should confirm the deprecated alias appears with metadata and that `MISC_RETIRED.LBR_INSERTS` remains available. Runtime tests should enable LBRs and verify insert counts move on branch-heavy workloads. Streaming-write tests should use non-temporal store workloads and verify offcore MSR programming for `0x10800`.
