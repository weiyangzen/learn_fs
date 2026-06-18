<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/rwx/rwx-nginx-deployment.yaml -->
# sources/control-plane/longhorn/examples/rwx/rwx-nginx-deployment.yaml

Purpose: ReadWriteMany Longhorn example with three pods sharing an RWX PVC.

Important APIs/types/functions: Service `rwx-test`, PVC `rwx-test` with `ReadWriteMany`, Deployment with three replicas and Recreate strategy, an Ubuntu writer container appending dates to `/data/index.html`, and an nginx container serving the same data.

Control flow: Longhorn creates an RWX/share-manager backed volume, all replicas mount the shared filesystem, writer updates content, and nginx serves it.

State and persistence: shared file data persists in the Longhorn RWX volume.

Dependencies/integration points: depends on Longhorn RWX/NFS share manager, multi-attach support, and pod scheduling across nodes.

Risks/test signals: concurrent writes are simplistic and may hide real application locking needs. Test signals are three pods running, shared updates visible from all pods, share manager health, and service HTTP responses.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/rwx/rwx-nginx-deployment.yaml -->
