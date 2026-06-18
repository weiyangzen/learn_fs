## sources/cloud-native/moby/daemon/builder/dockerfile/metrics.go

**Purpose:** Defines and registers Prometheus-style metrics for classic builder invocations and failure reasons.

**Important APIs:** Package vars `buildsTriggered` and `buildsFailed`; constants for failure labels such as syntax, empty Dockerfile, unsupported command, target unreachable, unknown instruction, and canceled build; `init` registers a `builder` metrics namespace.

**Control flow:** Init creates counters, preinitializes labeled counters for all known reasons, and registers the namespace.

**State and persistence:** Metrics live in process memory and are exported through the daemon metrics registry.

**Dependencies and integration:** Used by `BuildManager.Build`, parser error handling, target errors, and cancellation paths.

**Risks:** Missing labels make dashboards sparse or inconsistent. Metrics registration in init affects package import behavior and tests.

**Test signals:** No direct tests in this subset; compile-time use and metrics endpoint integration are the main signals.
