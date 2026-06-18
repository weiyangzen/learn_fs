## sources/cloud-native/moby/daemon/logger/etwlogs/register.go

Purpose: Windows-only registration hook for the ETW logging driver.

Important API: `init` calls `logger.RegisterLogDriver(name, New)` and panics on error.

Control flow and state: Mutates the global logger factory during package initialization.

Dependencies and integration points: Activated by Windows log driver blank imports and exposes `etwlogs` as a selectable daemon logging driver.

Risks: Duplicate name registration or init failure panics. There is no option validator registered because the ETW driver has no driver-specific options in this file set.

Test signals: No direct tests in this subset.
