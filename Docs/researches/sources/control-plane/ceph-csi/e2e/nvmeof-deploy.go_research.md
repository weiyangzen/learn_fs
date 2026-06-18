# sources/control-plane/ceph-csi/e2e/nvmeof-deploy.go

Purpose: deploys and configures the NVMe-oF CSI plugin for e2e tests, including OpenShift SCC handling, configmap creation, StorageClass generation with gateway listener information, and Ceph credentials.

Important APIs/types/functions: path/name globals describe NVMe-oF deploy/example YAMLs and secret/user names. `createORDeleteNVMeoFResources(action)` applies SCCs when OpenShift and then CSI driver, config, RBAC, provisioner, and nodeplugin YAML. `deployNVMeoFPlugin(f, deployTimeout)` creates the ConfigMap, applies resources, and waits for CSI readiness. `deleteNVMeoFPlugin()` reverses those steps. `createNVMeoFStorageClass(f, name, scOptions, parameters, policy)` loads the example StorageClass and injects secrets, clusterID, subsystem NQN, gateway address/listeners, binding mode, mount options, and reclaim policy. `deleteNVMeofStorageClass()` and `createNVMeoFCredentials()` manage storageclass and Ceph user Secret lifecycle.

Control flow: resource deployment builds a `ResourceDeployer` slice, optionally prepending SCC YAML with namespace replacement for OpenShift. StorageClass creation discovers cluster ID, gets gateway pod host/IP, writes `nvmeofGatewayAddress` and JSON `listeners`, creates a unique subsystem NQN from the framework namespace, applies caller parameter overrides with empty-value deletion, then polls StorageClass creation.

State and persistence: creates Ceph-CSI ConfigMap, NVMe-oF CSI Kubernetes resources, Ceph users, Kubernetes Secrets, and StorageClasses. The StorageClass persists gateway IP and listener JSON, so gateway pod recreation can stale it.

Dependencies and integration points: uses deployment resource abstractions, configmap helpers, `getNVMeofGateway()`, Ceph user/RBD secret helpers, RBD caps, Kubernetes storage APIs, and Gomega expectations. The NVMe-oF Ginkgo suite calls these during setup/teardown.

Risks: gateway pod IP is captured at StorageClass creation and may change if the gateway restarts. `deleteNVMeofStorageClass()` clears errors only when `IsNotFound` is true; other delete errors fail. NVMe-oF credentials reuse broad RBD caps with empty pool/namespace strings. OpenShift SCC string replacement assumes `:default:` markers in templates.

Test signals: CSI deployment and daemonset readiness, StorageClass creation with correct listener JSON, successful provisioning through the gateway, and cleanup of StorageClass/configmap/resources are the main signals.
