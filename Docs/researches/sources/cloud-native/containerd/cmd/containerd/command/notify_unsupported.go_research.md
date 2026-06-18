# sources/cloud-native/containerd/cmd/containerd/command/notify_unsupported.go

Purpose: supplies no-op notification functions on non-Linux platforms.

Important APIs/functions: `notifyReady()` and `notifyStopping()` return nil.

Control flow: keeps daemon startup and shutdown platform-neutral by allowing unconditional calls.

State and persistence: none.

Dependencies/integration: selected by `!linux`; pairs with Windows and other non-Linux signal/service files.

Risks: readiness/stopping notification is intentionally unsupported outside Linux/systemd.

Test signals: no local tests; behavior is trivial.
