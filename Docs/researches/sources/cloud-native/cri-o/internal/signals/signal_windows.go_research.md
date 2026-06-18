# sources/cloud-native/cri-o/internal/signals/signal_windows.go

Purpose: Windows-specific aliases for termination and hangup signals.

Important APIs/types/functions: `Term os.Signal = windows.SIGTERM` and `Hup os.Signal = windows.SIGHUP`.

Control flow: compiled on Windows by filename/build selection.

State and persistence behavior: package-level variables only.

Dependencies and integration points: imports `golang.org/x/sys/windows`; allows shared code to refer to `signals.Term` and `signals.Hup`.

Risks: Windows signal semantics differ from Unix and may not map perfectly to process-control expectations.

Test signals: compile-time platform coverage.
