<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/fixtures/unix/container_config_1_24.json -->
# sources/cloud-native/moby/daemon/internal/runconfig/fixtures/unix/container_config_1_24.json

Purpose: fixture representing an API 1.24 Unix container create request.

Important APIs and types: JSON fields include command/entrypoint, exposed ports, host config resources, bind mounts, capabilities, DNS, links, logging, memory, network mode, port bindings, restart policy, volumes-from, labels, MAC address, networking config, stdin/TTY settings, and volumes.

Control flow: no executable flow; consumed by `TestDecodeCreateRequest`.

State and persistence: static test data preserving older API request shape.

Dependencies and integration: validates `runconfig.DecodeCreateRequest` compatibility with historical Unix Docker run options.

Risks: fixture may lag current API fields by design; tests assert only selected decoded values.

Test signals: confirms broad JSON unmarshalling remains compatible for Unix create requests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/fixtures/unix/container_config_1_24.json -->
