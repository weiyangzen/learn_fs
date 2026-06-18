# sources/control-plane/rook/deploy/examples/nfs.yaml

Purpose: documents and configures a standard `CephNFS` example with one active NFS server and optional commented sections for Kerberos/SSSD and backing pool setup.

Important APIs/types/functions: `CephNFS/my-nfs` in `rook-ceph`, `spec.server.active`, placement, annotations, labels, resources, and `logLevel: NIV_INFO`. The commented examples show `CephBlockPool`, Kerberos config maps, keytab secrets, and SSSD integration.

Control flow: Rook observes the CephNFS CR and creates NFS-Ganesha deployment resources. Optional security material can be enabled by uncommenting and adapting the Kerberos/SSSD resources.

State and persistence: daemon desired state is stored in the CR; NFS metadata can use a Ceph pool such as `.nfs`.

Dependencies/integration: requires Rook Ceph cluster, NFS CRD/controller, and optional secrets/configmaps for Kerberos.

Risks: many fields are commented placeholders; partial uncommenting can create invalid security configuration. One active server is a simple availability profile.

Test signals: NFS pod readiness, Ganesha logs, CephNFS status, and successful client mount.
