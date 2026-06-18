# sources/cloud-native/moby/daemon/logger/logger_error.go

Purpose: centralizes rate-limited daemon logging for log driver write failures.

Important APIs/types/functions: package variable `logErrorLimiter` and function `logDriverError`.

Control flow/state/persistence: every call increments `logWritesFailedCount`; daemon error logging is limited to 333 events per second with burst 333 to avoid disk saturation.

Dependencies/integration: used by ring logger and other error paths. Depends on containerd log and x/time/rate.

Risks: rate limiting suppresses daemon log detail under sustained failures, so metrics are necessary for full visibility.

Test signals: no direct test in this subset, but ring tests exercise error paths indirectly.
