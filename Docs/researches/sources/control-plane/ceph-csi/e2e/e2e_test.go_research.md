# sources/control-plane/ceph-csi/e2e/e2e_test.go

Purpose: is the e2e suite entry point. It registers command-line flags, initializes Kubernetes e2e framework configuration, detects OpenShift, and starts the Ginkgo suite.

Important APIs/types/functions: `init()` registers flags controlling deploy/test enablement for CephFS, RBD, NFS, NVMe-oF, fscrypt, NBD, helm/operator/upgrade modes, namespaces, filesystem, cluster ID, NFS driver name, and timeouts. `setDefaultKubeconfig()` defaults `KUBECONFIG` to `$HOME/.kube/config`. `TestE2E(t)` registers Gomega failure handling, detects OpenShift, sets fail-fast Ginkgo config, and runs specs. `handleFlags()` wires Kubernetes framework flags, parses flags, and derives dependent feature toggles.

Control flow: package initialization redirects log output to `GinkgoWriter`, registers local and framework flags, sets kubeconfig, parses flags, applies derived behavior (`testCephFS` enables NFS testing/deploy, `testNVMeoF` enables NVMe-oF deployment, operator mode rewrites `cephCSINamespace`), and logs deployment timeout. The test function runs in parallel at the Go test level but Ginkgo ordered contexts control suite internals.

State and persistence: mutates global flags and suite globals such as `deployCephFS`, `deployNFS`, `deployNVMeoF`, `testNFS`, `cephCSINamespace`, `rookNamespace`, `fileSystemName`, `clusterID`, and `isOpenShift`. It sets the process environment variable `KUBECONFIG` if absent.

Dependencies and integration points: uses Go `testing`, Ginkgo/Gomega, Kubernetes e2e `framework` and `config`, and local `detectOpenShift()`. Every e2e file depends on the globals initialized here.

Risks: `testCephFS` implicitly enables NFS tests and NFS deployment, which may surprise callers expecting only CephFS. `testing.Init()` and `flag.Parse()` in `init()` can make package composition brittle. `t.Parallel()` allows this suite to overlap with other Go tests if invoked together. Operator mode hard-codes the operator namespace.

Test signals: successful flag parsing, OpenShift detection, suite start, and correct skip/deploy behavior across flag combinations are the main signals. Fail-fast means the first failing spec aborts later coverage in a run.
