<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/metadata/annotations.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/bundle/metadata/annotations.yaml

Purpose: bundle metadata annotations consumed by OLM/catalog tooling.

Important APIs and flow: declares bundle media type, manifests and metadata directories, package name `beegfs-csi-driver-operator`, channel/default channel `stable`, operator-sdk metrics metadata, scorecard test metadata, and minimum OpenShift version `v4.11`.

State and persistence: packaged into bundle image metadata; no cluster object by itself.

Dependencies and integration points: read by operator registry, bundle validation, scorecard discovery, and Red Hat/OpenShift catalog tooling.

Risks and test signals: incorrect package/channel annotations make upgrades or catalog indexing fail. Test with `operator-sdk bundle validate` and `opm index add`.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/metadata/annotations.yaml -->
