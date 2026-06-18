# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/scc.go

Purpose: constructs an OpenShift `SecurityContextConstraints` object suitable for Rook-Ceph service accounts.

Important APIs/types/functions: `NewSecurityContextConstraints(name string, namespaces ...string) *secv1.SecurityContextConstraints`.

Control flow: the function returns a fully populated SCC with OpenShift API metadata, privileged containers enabled, hostPath volumes enabled, host IPC enabled, host networking and host ports disabled, allowed capabilities `MKNOD` and `SYS_ADMIN`, all capabilities dropped by default, permissive run-as-user and supplemental-group strategies, constrained SELinux and FSGroup strategies, and a fixed set of allowed volume types. It builds the `Users` slice by appending service-account subjects for every namespace: `rook-ceph-system`, `rook-ceph-default`, `rook-ceph-mgr`, `rook-ceph-osd`, `rook-ceph-rgw`, and `rook-ceph-nvmeof`.

State and persistence: no persistence. The returned SCC object is in-memory and can be submitted by callers to the Kubernetes/OpenShift API.

Dependencies/integration: depends on `github.com/openshift/api/security/v1`, Kubernetes core capabilities, and `metav1`. It is an OpenShift-specific integration point for running Rook Ceph components that need privileged storage access.

Risks: the SCC grants broad privileges, including privileged containers and hostPath. Host networking is false here, so workloads requiring host networking must be handled elsewhere. New Rook service accounts need to be added to the hard-coded user list. Namespace argument order controls user ordering.

Test signals: `scc_test.go` only confirms the SCC name and `AllowPrivilegedContainer`; broader security fields and generated users are not tested.
