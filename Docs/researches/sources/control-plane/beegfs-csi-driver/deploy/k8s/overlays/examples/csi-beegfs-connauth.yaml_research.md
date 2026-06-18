<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/csi-beegfs-connauth.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/csi-beegfs-connauth.yaml

Purpose: example connAuth mapping file for BeeGFS file systems that require connection authentication.

Important APIs and flow: declares a YAML list of `sysMgmtdHost`, `connAuth`, and `encoding` entries, matching the driver's `ConnAuthConfig` shape. One example uses `encoding: raw`; the other uses a folded base64 secret. At runtime the deployment parser associates each secret value with a BeeGFS management host and merges it with plugin configuration outside the public CRD schema.

State and persistence: this is secret material intended to be transformed into Kubernetes Secret data or an equivalent mounted file, not persisted in the `BeegfsDriver` CR spec.

Dependencies and integration points: integrates with BeeGFS authentication, overlay secret generation, and the driver's redaction-aware `MarshalJSON` behavior for connAuth values.

Risks and test signals: raw values are sensitive, and base64 is encoding rather than encryption. Wrong `sysMgmtdHost` keys lead to unauthenticated mounts. Test with authenticated BeeGFS mounts and verify logs redact the value as `******`.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/csi-beegfs-connauth.yaml -->
