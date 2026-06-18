# sources/control-plane/rook/tests/framework/installer/ceph_manifests.go

Purpose: this file defines the `CephManifests` interface and the current-version `CephManifestsMaster` implementation that generates Rook/Ceph test manifests as strings.

Important APIs/types/functions: `CephManifests` includes methods for CRDs, operator, common RBAC, clusters, toolbox, block pools/storage/snapshot classes, CephFS/NFS/RBD mirror, object stores/users/buckets/notifications/topics, Ceph clients, filesystem subvolume groups, and COSI resources. `NewCephManifests` chooses master or previous-version implementations. `GetCephCluster` is the largest generator and conditions on PVC storage, mon count, crash pruner, multiple managers, messenger settings, encryption, compression, and OSD creation.

Control flow: static manifest files are loaded and namespace/image substitutions are applied for CRDs/operator/common/toolbox. Other resources are built through string concatenation or `renderTemplate`, using settings to determine namespace, cluster name, image, ports, TLS, Swift/Keystone, COSI names, and CSI provisioner names.

State and persistence behavior: no direct state mutation; the returned YAML becomes persistent Kubernetes state when applied by clients/installers.

Dependencies and integration points: depends on `TestCephSettings`, local `deploy/examples` manifests, previous-version manifest selection, COSI constants, Kubernetes/OpenShift platform detection, and installer helper templating.

Risks: string-built YAML has injection/formatting risk if test names contain special characters. Map iteration in `GetClient` creates nondeterministic caps order. Some comments are stale or duplicated. Changes in Rook CRD schema require coordinated updates here and in `ceph_manifests_previous.go`.

Test signals: manifest rendering should be exercised by end-to-end apply/reconcile tests. Unit-level signals would include namespace placeholder removal, valid YAML parsing, correct CSI driver names, and Swift/Keystone object store fields.
