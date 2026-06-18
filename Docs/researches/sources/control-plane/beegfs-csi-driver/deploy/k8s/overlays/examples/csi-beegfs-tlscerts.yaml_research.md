<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/csi-beegfs-tlscerts.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/csi-beegfs-tlscerts.yaml

Purpose: example TLS certificate mapping for BeeGFS management endpoints that require certificate material.

Important APIs and flow: declares a list of `sysMgmtdHost` to PEM `tlsCert` entries, matching the driver's `TLSCertConfig` type. The examples cover a hostname and an IP address key. Runtime parsing associates the PEM certificate with a BeeGFS file system identity and injects it into the driver's connection configuration.

State and persistence: certificate data should be stored as a Secret or mounted config file. It is intentionally not exposed as a JSON field in `BeegfsConfig` and is redacted in log marshaling.

Dependencies and integration points: depends on BeeGFS TLS support, valid PEM formatting, overlay wiring, and exact host identity matching.

Risks and test signals: placeholder PEM blocks must be replaced; malformed certificates or host mismatches cause connection failures. Test by mounting a TLS-enabled file system and confirming logs redact certificate content.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/csi-beegfs-tlscerts.yaml -->
