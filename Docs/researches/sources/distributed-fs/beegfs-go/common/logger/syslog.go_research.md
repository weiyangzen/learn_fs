# sources/distributed-fs/beegfs-go/common/logger/syslog.go

Purpose: implements a zap `WriteSyncer` that sends console-encoded zap log entries to syslog with severity mapping.

Important APIs are `SyslogWriteSyncer`, `NewSyslogWriteSyncer(priority syslog.Priority, tag string)`, `Write`, and `Sync`. The constructor opens a `log/syslog` writer. `Write` parses zap console output as timestamp, level, and message separated by tabs.

Control flow: if the encoded line has fewer than three tab-separated fields, it writes bytes unchanged to syslog. Otherwise it drops zap's timestamp, joins remaining fields into the syslog message, maps zap levels to syslog methods, and returns `len(p)` plus the syslog error. `Sync` is a no-op because `log/syslog` does not expose flushing.

State is the underlying `*syslog.Writer`. Dependencies include `log/syslog` and `strings`. Integration points are `logger.New` with `Type=Syslog` and zapcore's write path.

Risks: parsing is tightly coupled to zap console encoder output. `strings.Join(splitString[2:], "")` removes tab separators from structured fields, which can reduce readability. `log/syslog` is not portable to every platform. Performance is noted as lower than other destinations.

Test signals: no direct tests in this subset. Regression tests would need a fake syslog writer or an interface extraction.
