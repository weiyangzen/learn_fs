# sources/cloud-native/cri-o/cmd/crio/daemon_unsupported.go

Purpose: non-Linux no-op implementation of CRI-O daemon readiness notification.

Important APIs and control flow: `notifySystem` has the same signature as Linux and does nothing.

State and persistence: no state or side effects.

Dependencies and integration: selected by `//go:build !linux` to let `main.go` compile on unsupported platforms without systemd dependencies.

Risks: non-Linux builds receive no external readiness signal. This is expected for portability.

Test signals: cross-compilation jobs, such as FreeBSD build validation, catch missing symbol regressions.
