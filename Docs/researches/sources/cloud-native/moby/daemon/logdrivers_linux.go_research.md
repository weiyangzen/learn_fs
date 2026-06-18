## sources/cloud-native/moby/daemon/logdrivers_linux.go

Purpose: Registers Linux daemon logging drivers by blank-importing their packages for init-time factory registration.

Important imports: Registers `awslogs`, `fluentd`, `gcplogs`, `gelf`, `journald`, `jsonfilelog`, `local`, `loggerutils/cache`, `splunk`, and `syslog`.

Control flow and state: All behavior occurs through imported package `init` functions, which call `logger.RegisterLogDriver` and often `RegisterLogOptValidator`.

Dependencies and integration points: This file connects build tags/platform selection to the global logger factory. Linux includes journald and omits Windows ETW.

Risks: Removing or build-tagging an import changes available daemon log drivers. Init panics in driver registration would fail daemon startup.

Test signals: Driver-specific tests validate many imported packages; this registration aggregator has no direct tests here.
