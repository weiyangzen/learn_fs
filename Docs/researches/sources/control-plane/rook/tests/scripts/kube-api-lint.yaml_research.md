<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/kube-api-lint.yaml -->
# sources/control-plane/rook/tests/scripts/kube-api-lint.yaml

Purpose: kube-api-linter configuration for validating Kubernetes API conventions in Rook code.

Important structure: the file configures linters and exceptions used by CI. It is a policy artifact rather than executable code, shaping which Kubernetes API patterns are accepted or ignored during lint runs.

State, persistence, and integration: no runtime state is created; CI tools read it when linting API types. Dependencies include kube-api-linter and its expected YAML schema. Risks include stale exceptions masking real API quality issues or config schema drift across linter versions. Test signals are kube-api-linter pass/fail results in CI.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/kube-api-lint.yaml -->
