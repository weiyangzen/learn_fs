# sources/cloud-native/cri-o/server/metrics/metrics.go

Purpose: defines CRI-O's Prometheus metrics singleton, collector registration, metric mutation helpers, and HTTP/HTTPS/unix-socket serving.

Important APIs and functions: `New`, `Instance`, `Start`, `createEndpoint`, `startEndpoint`, `SinceInMicroseconds`, `SinceInSeconds`, `GetSizeBucket`, and many `Metric...` mutators for operations, image pulls, OOM, seccomp notifier, resource stages, monitor exits, and default runtime.

Control flow: `New` builds all Prometheus collectors and stores them in the package singleton. `Start` validates configs, creates a `/metrics` mux, starts TCP and optional Unix endpoints, and removes unused sockets first. `createEndpoint` registers only configured collectors. `startEndpoint` launches a goroutine serving HTTP or TLS and shuts down when the shared stop channel closes.

State and persistence: process-global `instance` holds collector objects. Prometheus default registry is mutated by `prometheus.Register`; failed duplicate registration aborts endpoint creation. Metrics values are in-memory counters/gauges/summaries. TLS cert generation may create or update cert/key files.

Dependencies and integration: uses Prometheus client libraries, CRI-O config TLS settings, cert reloader, process defunct counter, storage image references, and collector identifiers.

Risks: singleton/global Prometheus registry behavior can create duplicate-registration problems in repeated tests or multiple server instances. Some metric methods ignore unused parameters (`image`, `name`) and only increment aggregate counters. The unix socket endpoint uses the same handler and stop channel as TCP. TLS startup fatal-logs from the goroutine on cert errors.

Test signals: `metrics_test.go` covers only timing helper behavior. Runtime integration in `server.go` starts metrics when enabled, but collector registration and endpoint lifecycle have limited direct coverage in this subset.
