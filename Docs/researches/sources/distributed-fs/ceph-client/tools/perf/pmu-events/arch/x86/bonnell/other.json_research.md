# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/other.json

## Purpose

This file defines 55 miscellaneous Bonnell events, mostly external bus, snoop, interrupt masking, SpeedStep, thermal, and segment-register-load counters. It covers bus transaction classes, bus-ready/data-ready/lock/HIT/HITM signals, outstanding requests, snoop responses, interrupt masking cycles, hardware interrupt receipt, EIST transitions, and thermal trips.

## Important APIs, Types, And Data

The records use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. Families include `BUS_*`, `EXT_SNOOP`, `CYCLES_INT_MASKED`, `EIST_TRANS`, `HW_INT_RCV`, `SEGMENT_REG_LOADS`, `SNOOP_STALL_DRV`, and `THERMAL_TRIP`. Several bus events have `.THIS_AGENT`, `.ALL_AGENTS`, `.SELF`, or transaction-type suffixes.

## Control Flow

Generation converts each record into a generated Bonnell perf alias. Masks distinguish bus transaction classes and agent scope. At runtime, perf opens the corresponding core PMU event and counts bus or miscellaneous processor signals.

## State And Persistence Behavior

The JSON is static metadata. Runtime bus, snoop, interrupt, thermal, and power-transition counts are hardware state. Default sampling periods persist as generated event fields.

## Dependencies And Integration Points

This file integrates with Bonnell model mapping, `jevents.py`, generated PMU tables, and perf list/stat. It is relevant for platform-level diagnosis on older Atom systems where external bus and snoop events are important.

## Risks And Edge Cases

Agent scope suffixes are easy to misread: `.ALL_AGENTS`, `.THIS_AGENT`, and `.SELF` do not mean the same thing. Bus transaction masks are dense and similar, increasing maintenance risk. Some events depend heavily on platform topology and may be unavailable or low-value under virtualization. Thermal and EIST events are system-management signals rather than instruction-level performance counters.

## Test Signals

Validate JSON and generated aliases. Generation tests should confirm representative bus transaction, snoop, EIST, interrupt, and thermal aliases. Runtime validation can use I/O-heavy, memory-sharing, interrupt-heavy, and power-state-transition workloads on Bonnell hardware.
