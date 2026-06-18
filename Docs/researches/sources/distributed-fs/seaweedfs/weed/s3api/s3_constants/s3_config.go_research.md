# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/s3_config.go

Purpose: holds S3 configuration defaults for circuit breaker files, allowed legacy actions, limit type labels, and action-string concatenation.

Important APIs and values: `CircuitBreakerConfigDir`, `CircuitBreakerConfigFile`, `AllowedActions`, `LimitTypeCount`, `LimitTypeBytes`, `Separator`, and `Concat`.

Control flow: `Concat` joins arbitrary strings with `Separator` (`:`), matching legacy action encodings such as `Read:bucket/path`.

State and persistence: mutable package variables hold defaults. Config files are external to this file.

Dependencies and integration: used by identity/action parsing, S3 configuration, and circuit breaker setup.

Risks: `AllowedActions` omits newer retention/object-lock constants defined in `s3_actions.go`, so validation paths using it may reject newer coarse actions unless updated elsewhere.

Test signals: no direct tests in this subset.
