# sources/cloud-native/nydus/contrib/nydusify/pkg/metrics/metrics.go

Purpose: defines nydusify conversion metrics and a one-time registration/export hook.

Important APIs/types/functions: `Exporter`, metric key constants, global counter vectors, `Register`, `Export`, `ConversionDuration`, `ConversionSuccessCount`, `ConversionFailureCount`, `StoreCacheDuration`, and `sinceInSeconds`.

Control flow: `Register` uses `sync.Once` to create a new Prometheus registry, register all counter vectors, and store the exporter. Recorder functions add elapsed seconds or increment counters with labels. `Export` calls the registered exporter when present.

State and persistence: metrics live in global Prometheus counter vectors and a global `Registry`. Registration is one-shot per process unless tests reset internals. The exporter determines persistence, commonly the file exporter.

Dependencies and integration points: Prometheus client_golang, conversion and cache workflows that record timings/counts, and file/exporter implementations.

Risks and test signals: `sync.Once` prevents reconfiguration after first register. Labels include source references and failure reasons, which may increase cardinality. Duration is represented as a counter rather than histogram/summary, limiting distribution analysis.
