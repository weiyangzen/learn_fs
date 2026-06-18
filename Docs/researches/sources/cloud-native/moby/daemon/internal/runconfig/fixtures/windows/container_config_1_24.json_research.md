<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/fixtures/windows/container_config_1_24.json -->
# sources/cloud-native/moby/daemon/internal/runconfig/fixtures/windows/container_config_1_24.json

Purpose: fixture representing an API 1.24 Windows container create request.

Important APIs and types: JSON mirrors the Unix fixture but uses Windows image/entrypoint and Windows-style bind/volume paths.

Control flow: no executable flow; consumed by `TestDecodeCreateRequest`.

State and persistence: static compatibility test data.

Dependencies and integration: validates `runconfig.DecodeCreateRequest` compatibility with historical Windows create request payloads.

Risks: contains fields that may be ignored or invalid for modern Windows behavior; the decoding test only checks a subset.

Test signals: confirms Windows fixture decodes with expected image, entrypoint, and memory values.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/fixtures/windows/container_config_1_24.json -->
