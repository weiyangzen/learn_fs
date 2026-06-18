# sources/distributed-fs/ipfs-kubo/test/cli/tracing_test.go

Purpose: integration test for OpenTelemetry trace export from the Kubo daemon to an OTLP collector.

Important APIs and data: `otelCollectorConfigYAML` defines an OpenTelemetry Collector config with OTLP gRPC receiver and file exporter to `/traces/traces.json`. `TestTracing` uses `testutils.RequiresDocker`, Docker CLI, host networking, node environment variables, and daemon startup.

Control flow: the test skips unless Docker tests are enabled. It writes collector config and an empty writable `traces.json` into the node directory, runs `docker run --rm --detach` with volume mounts and `--net host`, registers cleanup to stop the named container, sets `OTEL_TRACES_EXPORTER=otlp`, `OTEL_EXPORTER_OTLP_PROTOCOL=grpc`, and `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317`, starts the daemon, and waits up to five minutes until `traces.json` contains `go-ipfs`.

State and persistence: trace output is written to the node directory by the collector container. The Docker container is named `ipfs-test-otel-collector` and should be stopped during cleanup.

Dependencies and integration points: requires Docker, host networking, the `otel/opentelemetry-collector-contrib:0.52.0` image, file permissions compatible with container writes, OpenTelemetry environment variable handling, and daemon instrumentation.

Risks and test signals: fixed container name can collide with stale/running containers. Host networking and image pulls can fail in CI. The five-minute wait is long but necessary for collector startup. Failure means traces were not exported, collector did not write the file, or instrumentation service name changed.
