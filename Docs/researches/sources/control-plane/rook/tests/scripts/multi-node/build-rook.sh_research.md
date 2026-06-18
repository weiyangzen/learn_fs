<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multi-node/build-rook.sh -->
# sources/control-plane/rook/tests/scripts/multi-node/build-rook.sh

Purpose: multi-node Vagrant helper that builds a local Rook image, pushes it to a local registry, rewrites deployment templates, and deploys Rook to a Vagrant Kubernetes cluster.

Important APIs and control flow: it verifies it is in a git repo, configures kubeconfig from the `k8s-01` VM, ensures the user can run Docker, starts a local registry, purges existing Rook/Ceph resources and VM Ceph disks, runs `make`, tags/pushes the build image to `172.17.8.1:5000/rook/ceph:latest`, rewrites `operator.yaml`, and creates operator/cluster manifests.

State, persistence, and integration: mutates kubeconfig, Docker registry/images, Kubernetes resources, Vagrant VM disks, and deploy examples. Dependencies include Vagrant, Docker, kubectl, make, and Rook example manifests. Risks include broad deletion of Rook resources and CRDs, destructive disk zeroing on VMs, image selection by regex, and older manifest names. Test signals are successful node listing, image push, CRD availability, and cluster creation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multi-node/build-rook.sh -->
