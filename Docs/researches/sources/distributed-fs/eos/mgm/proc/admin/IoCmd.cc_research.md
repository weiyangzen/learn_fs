# sources/distributed-fs/eos/mgm/proc/admin/IoCmd.cc

Purpose: Implements the protobuf-backed `io` command for IO statistics, collection toggles, namespace popularity reports, namespace report reads, and dispatch into traffic shaping.

Important APIs/types/functions: `IoCmd::ProcessRequest()` dispatches `IoProto` oneof cases. `StatSubcmd()` calls `mIoStats->PrintOut()` with summary/detail/top/domain/app/sample/time options. `EnableSubcmd()` starts/stops IO collection, popularity collection, report store, namespace reporting, or UDP targets. `ReportSubcmd()` prints a namespace report for root. `NsSubcmd()` translates proto options into legacy flag strings for `PrintNsPopularity()`. `ShapingSubcommand()` is implemented in `IoShapingCmd.cc`.

Control flow: Stat defaults to summary output if no detail selectors are enabled and converts monitoring output to JSON when requested. Enable/disable branches are selected by `switchx()` and secondary booleans for reports/namespace/popularity/UDP. Report requires root. Namespace popularity builds compact flags for ranking, hotfiles, week scope, and count before rendering.

State and persistence behavior: IO collection/report/popularity state is managed by `gOFS->mIoStats`. UDP targets are added/removed from the IO stats subsystem. This file mostly toggles runtime services and reads report state; traffic shaping persistence is in `IoShapingCmd.cc` and its engine.

Dependencies and integration points: Depends on `Iostat`, `XrdMgmOfs`, `ProcInterface`, generated `Io.pb.h`, ZMQ headers, and the `IoCmd.hh` shaping declaration. Integrates older `Iostat` formatting with protobuf console requests.

Risks: Most enable/disable actions do not check root, so authorization must be enforced by higher-level routing if intended. Output messages can concatenate when enabling reports and namespace reporting together. `ReportSubcmd()` guards `mIoStats` but still returns success with empty output if it is null. Legacy flag string construction in `NsSubcmd()` is compact but not type-safe.

Test signals: Dispatch for every subcommand, stat default summary behavior, JSON conversion, enable/disable idempotency errors, UDP target add/remove, popularity requiring collection start, root-only report, namespace option flag mapping, count enum handling, and shaping dispatch into `IoShapingCmd.cc`.
