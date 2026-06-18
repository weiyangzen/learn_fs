<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/config.go -->
# sources/cloud-native/moby/daemon/internal/runconfig/config.go

Purpose: decodes container create requests from JSON, fills daemon-side defaults, and validates platform-specific options.

Important APIs and types: `DecodeCreateRequest`, `decodeCreateRequest`, `validateCreateRequest`, and `loadJSON`.

Control flow: `DecodeCreateRequest` decodes then validates. `decodeCreateRequest` reads JSON into `container.CreateRequest`, rejects missing `Config`, initializes nil maps/configs for volumes, host config, port bindings, networking config, and endpoints, and defaults non-Windows empty network mode to `default`. `validateCreateRequest` delegates to network mode, isolation, QoS, resources, privileged, and readonly-rootfs validators. `loadJSON` wraps decoder errors as invalid JSON and rejects extra JSON values using `dec.More`.

State and persistence: no persistence; mutates returned request defaults in memory.

Dependencies and integration: used by daemon API create-container path. Depends on API container/network types and sysinfo.

Risks: `dec.More` is not a full trailing-token check outside arrays/objects, so extra JSON detection may be incomplete. Defaults preserve backward-compatible API behavior and are platform-sensitive. Validation split across platform files must stay in sync.

Test signals: `config_test.go` covers fixture decoding, isolation validation, and Windows privileged validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/config.go -->
