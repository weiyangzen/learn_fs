# sources/control-plane/rook/pkg/daemon/multus/config.yaml

Purpose: human-readable Go template used by `ValidationTestConfig.ToYAML()` to emit a documented Multus validation config file.

Important APIs/types/functions: embedded as `ConfigYaml` in `config.go` and rendered with a `ValidationTestConfig`. It references scalar fields such as `.Namespace`, `.PublicNetwork`, `.ClusterNetwork`, `.ResourceTimeout`, `.FlakyThreshold`, `.HostCheckOnly`, and `.NginxImage`, then iterates `.NodeTypes`, placement selectors, and tolerations.

Control flow: the template outputs comments explaining each parameter and renders node type entries from the config map. Tolerations are emitted via `$toleration.ToJSON`, relying on the custom method in `TolerationType`.

State and persistence behavior: it is a static embedded template; rendered YAML can be persisted by users as CLI/tool configuration, but this file itself has no runtime state.

Dependencies and integration points: tightly coupled to `ValidationTestConfig` field names and Go template execution in `loadTemplate()`. The comments describe operational expectations for Rook-Ceph clusters, CSI daemon counts, and host-check-only mode.

Risks: map iteration order for `NodeTypes`, node selectors, and tolerations from Go maps may make rendered output order nondeterministic for map-backed fields. Template indentation must remain valid YAML for empty maps/slices. Documentation comments can drift from validation logic if fields or defaults change.

Test signals: `TestValidationTestConfig_YAML` confirms rendered YAML contains comments and round-trips into an equivalent config for representative empty, default, and full configs.
