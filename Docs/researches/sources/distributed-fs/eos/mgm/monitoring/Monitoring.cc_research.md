# sources/distributed-fs/eos/mgm/monitoring/Monitoring.cc

Purpose: centralizes logging helpers for the MGM Prometheus endpoint lifecycle and monitoring configuration errors.

Important APIs and functions: `LogPrometheusEndpointStarting`, `LogPrometheusEndpointStarted`, `LogPrometheusEndpointStopped`, `LogPrometheusEndpointStartFailed`, and `LogMonitoringConfigError` emit structured EOS log lines with bind address, cache TTL, and error text as applicable.

Control flow and state behavior: there is no local state. Callers invoke these helpers around endpoint start/stop/configuration paths. Success paths log at notice level; start/config failures log at error level.

Dependencies and integration points: depends on `Monitoring.hh` and `common/Logging.hh`. The functions are intended for `PrometheusExporter` or MGM configuration code to keep log messages consistent.

Risks and test signals: errors are interpolated into structured log strings, so callers should pass already-sanitized single-line messages if log parsers are sensitive. Tests can assert that endpoint lifecycle paths call the right helper by using logging test sinks or integration logs.
