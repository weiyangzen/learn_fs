<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/tests/scorecard/config.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/bundle/tests/scorecard/config.yaml

Purpose: Operator SDK scorecard configuration for validating the BeeGFS CSI operator bundle.

Important APIs and flow: defines scorecard v1alpha3 `Configuration` with one parallel stage running `basic-check-spec`, `olm-bundle-validation`, `olm-crds-have-validation`, `olm-crds-have-resources`, `olm-spec-descriptors`, and `olm-status-descriptors` using `quay.io/operator-framework/scorecard-test:v1.19.1`.

State and persistence: no runtime state beyond test execution artifacts produced by scorecard.

Dependencies and integration points: referenced by bundle annotations under `tests/scorecard/` and run by operator-sdk scorecard tooling.

Risks and test signals: image/tool version is old relative to current generated manifests and may diverge from installed operator-sdk. Test by running scorecard and checking all basic/OLM suites pass.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/tests/scorecard/config.yaml -->
