# sources/distributed-fs/eos/mgm/proc/admin/IoCmd.hh

Purpose: Declares `IoCmd` and the traffic shaping report builder API used by EOS MGM IO administration.

Important APIs/types/functions: Forward declares `TrafficShapingRateRequest` and `TrafficShapingRateResponse`, and declares `BuildTrafficShapingRateReport()` for external report construction. `IoCmd` derives from `IProcCommand`, overrides `ProcessRequest()`, and declares helpers for stat, enable, report, namespace popularity, shaping dispatch, and older monitor shaping helpers (`MonitorSet`, `MonitorSetLs`, `MonitorSetRm`, `MonitorAdd`, `MonitorRm`).

Control flow: The command object's `.cc` dispatches generated `IoProto` submessages into these helpers. Shaping helper declarations split the larger implementation into `IoShapingCmd.cc` while keeping command state and access to `WantsJsonOutput()` in `IoCmd`.

State and persistence behavior: The header owns no persistent state. Runtime and persistent effects occur in `gOFS->mIoStats` and `gOFS->mTrafficShapingEngine`.

Dependencies and integration points: Includes `Namespace.hh`, `ProcCommand.hh`, and standard string. It is the common declaration shared by normal IO stats code, traffic shaping implementation, and any component that needs `BuildTrafficShapingRateReport()`.

Risks: Some monitor helper declarations appear legacy and are not implemented in the read file set, so stale declarations should be checked during refactors. Shaping implementation depends on generated proto names in method signatures, so proto evolution has high compile impact here.

Test signals: Build linkage for `IoCmd.cc` plus `IoShapingCmd.cc`, external use of `BuildTrafficShapingRateReport()`, dispatch into shaping, and absence of stale undefined helper references in linked targets.
