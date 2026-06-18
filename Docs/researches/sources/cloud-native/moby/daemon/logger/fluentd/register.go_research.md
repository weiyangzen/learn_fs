## sources/cloud-native/moby/daemon/logger/fluentd/register.go

Purpose: Registers the Fluentd log driver and its option validator with the global logger factory.

Important API: `init` calls `logger.RegisterLogDriver(name, New)` and `logger.RegisterLogOptValidator(name, ValidateLogOpt)`.

Control flow and state: Registration occurs as an import side effect and panics on failure.

Dependencies and integration points: Activated by platform log driver blank imports, enabling user selection of `fluentd` and validation of `fluentd-*` options.

Risks: Duplicate registration or mismatched `name` causes init-time panic or driver lookup failure.

Test signals: Indirectly covered by Fluentd tests and daemon logdriver imports.
