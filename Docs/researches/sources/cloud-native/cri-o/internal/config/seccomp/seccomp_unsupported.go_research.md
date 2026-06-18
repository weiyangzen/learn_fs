# sources/cloud-native/cri-o/internal/config/seccomp/seccomp_unsupported.go

Purpose: provides no-op seccomp implementation when the `seccomp && linux && cgo` build constraints are not met.

Important APIs/types/functions: stub `Config`, `Notifier`, `Notification`, `New`, `Setup`, notifier path/profile methods, `NewNotifier`, notifier methods, notification accessors, `IsDisabled`, `Profile`, and `DefaultProfile`.

Control flow: `New` returns disabled config. `Setup` always returns nil notifier, empty reference, and nil error. Profile load/default methods are no-ops. Notifier and notification methods return zero values.

State and persistence behavior: no profile or notifier state is persisted; `enabled` is false.

Dependencies/integration points: keeps the same API surface for builds without seccomp support so container setup code can compile and degrade to unconfined behavior.

Risks: custom seccomp expectations are silently ignored by `Setup` in unsupported builds, unlike the enabled implementation’s more nuanced disabled-seccomp checks.

Test signals: no direct tests for unsupported build behavior in this subset.
