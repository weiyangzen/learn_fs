## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/prometheusrules.yaml

Purpose: renders a Prometheus Operator `PrometheusRule` resource for Ceph alerts when monitoring rule creation is enabled.

Important template behavior: gated by `.Values.monitoring` and `.Values.monitoring.createPrometheusRules`. It labels the rule for rook-prometheus, applies optional labels/annotations, selects `prometheus/localrules.yaml` by default or `prometheus/externalrules.yaml` when `cephClusterSpec.external.enable` is true, parses the file with `fromYaml`, then iterates groups/rules. For each rule it determines a name from alert or record, applies `monitoring.prometheusRuleOverrides` via `mergeOverwrite`, drops disabled rules, and omits empty groups.

Control flow: dynamic render-time rule loading and override merging.

State and persistence: creates PrometheusRule CRs, usually in release namespace or `rulesNamespaceOverride`.

Dependencies and integration points: depends on packaged rule files, Prometheus Operator CRD, Helm functions, and values schema. Risks: override names must exactly match alert/record names; malformed overrides can produce invalid Prometheus rules; external-mode detection depends on values shape. Test signals should include Helm render and promtool validation for default and override cases.
