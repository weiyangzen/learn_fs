<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/object-external.yaml -->
# sources/control-plane/rook/deploy/examples/external/object-external.yaml

Purpose: defines a Rook `CephObjectStore` that points at an external RGW endpoint.
Important APIs/types/functions: `CephObjectStore` `external-store`, namespace `rook-ceph`, `spec.gateway.port: 80`, and `externalRgwEndpoints` with IP/optional hostname.
Control flow: Rook represents an external RGW service without deploying local gateways; bucket provisioning and object clients use the configured endpoint. State is the object store CR and external RGW service/bucket state. Dependencies are an accessible RGW endpoint, imported RGW admin credentials when bucket provisioning is used, and object bucket provisioner. Risks: placeholder IP must be replaced, only one endpoint is shown, TLS/hostname are omitted, and endpoint must belong to the intended Ceph cluster. Test signals: CephObjectStore ready, bucket StorageClass can create OBCs, and S3 operations reach the external endpoint.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/object-external.yaml -->
