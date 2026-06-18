# sources/cloud-native/moby/daemon/logger/local/register.go

Purpose: registers the local logger with the daemon logger factory.

Important APIs/types/functions: `init` registers `Name`, `New`, and `ValidateLogOpt`.

Control flow/state/persistence: package-init side effect only.

Dependencies/integration: makes the `local` driver selectable and validates options.

Risks: registration must be imported by daemon setup.

Test signals: build/factory and local tests indirectly validate registration.
