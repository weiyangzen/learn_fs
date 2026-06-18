# sources/control-plane/juicefs-csi-driver/pkg/config/config_test.go

Purpose: validates config file parsing and mount pod patch generation/matching.

Important tests: `TestLoadConfig` writes YAML and asserts parsed images, labels, annotations, PVC selector, resources, probes, termination grace, env, volumes, devices, and cache dirs. `TestGenMountPodPatch` covers empty config, selectors, ordered merge, template replacement, duplicate/internal volume filtering, mount options, node selector, and DNS. Other tests cover `SupportFusePass`, template idempotence, and selector matching with/without node context.

State/persistence: writes a temporary `/tmp/test-config.yaml` and mutates `GlobalConfig`, then resets it. Most tests use local `Config` instances.

Dependencies/integration: uses `testify/assert` and Kubernetes core/meta/resource APIs. It protects behavior consumed by `setting.go` and pod builders.

Risks/gaps: no direct coverage for `LoadFromConfigMap`, `StartConfigReloader`, fsnotify symlink handling, invalid full config loads, `ENABLE_NODE_SELECTOR`, or concurrent reloads.

Test signal: strong for patch parse/merge behavior; weak for live config delivery.
