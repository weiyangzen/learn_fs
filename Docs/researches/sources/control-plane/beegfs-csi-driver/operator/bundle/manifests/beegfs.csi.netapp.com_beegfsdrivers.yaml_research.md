<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs.csi.netapp.com_beegfsdrivers.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs.csi.netapp.com_beegfsdrivers.yaml

Purpose: generated CustomResourceDefinition for namespaced `BeegfsDriver` objects.

Important APIs and flow: defines group `beegfs.csi.netapp.com`, version `v1`, kind/list/plural names, served/storage status, and status subresource. The OpenAPI schema exposes image overrides, resource overrides, `logLevel` with min 0/max 5, controller/node `NodeAffinity`, plugin config hierarchy, string-only `beegfsClientConf`, required `sysMgmtdHost` in file-system configs, required `nodeList` in node configs, and `status.conditions`. Metadata name is constrained to `^csi-beegfs-cr$`, enforcing a singleton resource name.

State and persistence: stores desired operator state in CR specs and observed readiness in status conditions. Secret auth/cert values are absent from the public CRD schema.

Dependencies and integration points: generated from Go API types by controller-gen v0.16.5 and consumed by the CSV/operator manager.

Risks and test signals: schema drift from Go types breaks OLM/API behavior. Test with `make manifests`, CRD apply, schema validation failures for invalid logLevel/name, and status updates.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs.csi.netapp.com_beegfsdrivers.yaml -->
