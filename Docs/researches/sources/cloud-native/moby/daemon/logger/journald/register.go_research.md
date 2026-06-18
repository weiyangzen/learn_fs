# sources/cloud-native/moby/daemon/logger/journald/register.go

Purpose: registers the journald driver with the logger factory on Linux builds.

Important APIs/types/functions: `init` calls `logger.RegisterLogDriver(name, New)` and `logger.RegisterLogOptValidator(name, validateLogOpt)`.

Control flow/state/persistence: package initialization only. Registration makes the driver available by name and wires option validation.

Dependencies/integration: depends on logger factory APIs outside this subset.

Risks: Linux-only build tag means non-Linux builds cannot select this driver. Registration side effects rely on package import.

Test signals: build and factory tests indirectly validate registration.
