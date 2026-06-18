## sources/cloud-native/moby/daemon/logdrivers_windows.go

Purpose: Registers Windows daemon logging drivers by blank-importing their packages for init-time factory registration.

Important imports: Registers `awslogs`, `etwlogs`, `fluentd`, `gcplogs`, `gelf`, `jsonfilelog`, `loggerutils/cache`, `splunk`, and `syslog`.

Control flow and state: Behavior is entirely side-effect imports. Windows includes ETW logs and omits journald/local from this list.

Dependencies and integration points: Bridges platform build selection to `logger` factory availability. Each driver package must successfully register at init time.

Risks: Registration availability differences are platform API behavior. Duplicate registration panics in any driver init would affect daemon startup.

Test signals: No direct tests for this aggregation file in the subset.
