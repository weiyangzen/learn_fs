## sources/cloud-native/moby/daemon/logger/gelf/register.go

Purpose: Registers the GELF log driver and option validator with the global logger factory.

Important API: `init` calls `logger.RegisterLogDriver(name, New)` and `logger.RegisterLogOptValidator(name, ValidateLogOpt)`.

Control flow and state: Import side effect mutates process-global factory state and panics if registration fails.

Dependencies and integration points: Activated by platform logdriver blank imports, enabling `gelf` as a daemon logging driver.

Risks: Duplicate name registration or missing blank import changes driver availability.

Test signals: Indirectly covered by GELF tests and logdriver platform imports.
