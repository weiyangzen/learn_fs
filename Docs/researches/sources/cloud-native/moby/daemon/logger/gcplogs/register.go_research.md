## sources/cloud-native/moby/daemon/logger/gcplogs/register.go

Purpose: Registers the Google Cloud Logging driver and validator with the daemon logger factory.

Important API: `init` registers `name` with `New` and registers `ValidateLogOpts`, panicking on errors.

Control flow and state: Import side effect mutates the global factory registry and validator map.

Dependencies and integration points: Activated by platform logdriver blank imports; enables `gcplogs` selection and option validation.

Risks: Init-time panics on duplicate registration. Driver availability depends on this blank import being included for the target platform.

Test signals: No direct tests in this subset.
