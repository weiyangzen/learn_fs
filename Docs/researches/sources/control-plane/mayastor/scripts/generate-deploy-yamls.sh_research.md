# sources/control-plane/mayastor/scripts/generate-deploy-yamls.sh

Purpose: Helm wrapper for generating Mayastor deployment YAMLs with profile-specific defaults.

Important APIs/types/functions: supports options for cores, output dir, pool node/device pairs, registry, tag, helm `--set`, helm values files, and namespace. Profiles `develop`, `release`, and `test` set defaults for CPU count, image tag, pull policy, huge pages, and MOAC debug.

Control flow: parses options, validates profile and helm availability, prepares a temp directory, builds comma-separated Helm values, updates chart dependencies, runs `helm template`, moves Mayastor templates into deploy output, moves Bitnami etcd templates into `deploy/etcd`, and trims trailing whitespace.

State/persistence: overwrites generated YAML output directories; temporary files are removed by trap.

Dependencies/integration: integrates repository Helm chart, profile values files, generated deploy directory, and optional pool placement values.

Risks: `--set "$helm_string"` and `-f "$helm_file"` are passed even when empty, depending on helm tolerance. Pool parsing is comma-based and unquoted namespace may break on unusual values.

Test signals: generated YAMLs under deploy and deploy/etcd should be valid Kubernetes manifests for the selected profile.
