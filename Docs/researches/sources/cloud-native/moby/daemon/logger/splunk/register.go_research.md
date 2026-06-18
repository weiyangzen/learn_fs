# sources/cloud-native/moby/daemon/logger/splunk/register.go

Purpose: registers the Splunk log driver.

Important APIs/types/functions: `init` registers `driverName`, `New`, and `ValidateLogOpt`.

Control flow/state/persistence: package-init side effect only.

Dependencies/integration: makes the Splunk driver selectable by daemon configuration.

Risks: registration relies on package import. Option validation must stay aligned with `splunk.go`.

Test signals: Splunk tests and factory builds indirectly validate registration.
