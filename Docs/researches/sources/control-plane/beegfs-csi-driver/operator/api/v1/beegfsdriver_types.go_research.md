<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/api/v1/beegfsdriver_types.go -->
# sources/control-plane/beegfs-csi-driver/operator/api/v1/beegfsdriver_types.go

Purpose: source of truth for the `beegfs.csi.netapp.com/v1` operator API, CRD schema annotations, status conditions, plugin config structures, and secret redaction behavior.

Important APIs and flow: defines `BeegfsDriverSpec`, `BeegfsDriverStatus`, `BeegfsDriver`, `BeegfsDriverList`, image/resource override types, `BeegfsConfig`, `PluginConfig`, `PluginConfigFromFile`, `ConnAuthConfig`, and `TLSCertConfig`. `init()` registers CR types. `NewBeegfsConfig` initializes the client-conf map. Custom `MarshalJSON` methods redact `ConnAuth` and `TLSCert` when logs encode config structs.

State and persistence: CR spec persists image/resource overrides, `logLevel`, node affinities, and non-secret plugin config. Status persists Kubernetes conditions for controller/node readiness. ConnAuth and TLS cert fields are deliberately not unmarshaled from CR JSON.

Dependencies and integration points: imports Kubernetes core/v1 and metav1 types, controller-gen/operator-sdk annotations, and JSON encoding.

Risks and test signals: schema comments feed CSV/GUI output, so wording changes are user visible. Test with `make generate`, `make manifests`, API serialization tests, and log redaction checks.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/api/v1/beegfsdriver_types.go -->
