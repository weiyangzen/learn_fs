# sources/control-plane/ceph-csi/examples/nfs/volumeattributesclass.yaml

Purpose: example `VolumeAttributesClass` for changing NFS volume parameters.

Important fields and flow: VAC `updated-parameters` uses driver `nfs.csi.ceph.com` and sets `server` to an alternative NFS endpoint.

State, dependencies, and integration: Kubernetes applies this to PVCs that reference the class, and Ceph-CSI uses controller/node modify secret refs from the StorageClass to update attachment behavior.

Risks and test signals: requires Kubernetes VAC support and a valid replacement server. Tests validate updated publish behavior after reattachment.
