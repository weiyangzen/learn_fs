# sources/cloud-native/cri-o/internal/signals/signal_unix.go

Purpose: Unix-specific signal aliases for termination and hangup.

Important APIs/types/functions: `Term os.Signal = unix.SIGTERM` and `Hup os.Signal = unix.SIGHUP`.

Control flow: selected for non-Windows builds by `//go:build !windows`.

State and persistence behavior: package-level variables only.

Dependencies and integration points: imports `golang.org/x/sys/unix`; supports Unix signal handling in shared CRI-O code.

Risks: Unix-only constants must not leak into Windows builds except through this abstraction.

Test signals: compile-time platform selection.
