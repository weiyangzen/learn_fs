# sources/distributed-fs/eos/mgm/monitoring/MonitoringConfig.hh

Purpose: defines configuration keys, defaults, bounds, and parsing helpers for the MGM Prometheus monitoring endpoint.

Important APIs and constants: keys are `monitoring.prometheus.enabled`, `monitoring.prometheus.port`, and `monitoring.prometheus.cache_ttl_seconds`. Defaults are port `9987`, cache TTL `1` second, and maximum cache TTL `60` seconds. `ParseUint32Config` parses a non-empty unsigned 64-bit string and rejects values above `uint32_t` max. `ParsePortConfig` parses a non-zero `uint16_t` port through `ParseUint32Config`. `IsValidCacheTtl` accepts TTL values up to the configured maximum.

Control flow and state behavior: this is header-only parsing logic with no state. Callers read string config values, parse them into numeric types, validate TTL, and apply defaults outside the helper when parsing fails or config is absent.

Dependencies and integration points: depends on `common/ParseUtils.hh`, integer limits, and strings. Used by MGM monitoring configuration and `PrometheusExporter` setup; `CachedCollectable` consumes the resulting TTL after conversion to chrono duration.

Risks and test signals: empty values are invalid rather than defaulted inside the parser, so callers must implement default behavior consistently. The port parser rejects zero and values above 65535. TTL validation only checks the upper bound, so zero is valid and later disables caching when converted to the collectable TTL. Tests should cover empty strings, non-numeric strings, max uint32 boundaries, port 0, port 65535/65536, TTL 0, TTL 60, and TTL 61.
