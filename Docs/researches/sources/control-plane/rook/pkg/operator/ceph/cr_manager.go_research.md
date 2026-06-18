# sources/control-plane/rook/pkg/operator/ceph/cr_manager.go

## Purpose
`cr_manager.go` wires Rook Ceph custom-resource controllers into a controller-runtime manager. It is the registration point for the main Ceph cluster controller, child resource controllers, CSI, object/file/pool controllers, and the maintenance/disruption controller.

## Important APIs, Types, and Functions
`resourcesSchemeFuncs` registers client-go and Ceph API schemes. `AddToManagerFuncs` lists child controller `Add` functions for node daemons, pools, object users, realms/zones, object stores, filesystems, NFS, RBD, clients, NVMe-oF, mirroring, the operator config controller, CSI, bucket/topic/notification, subvolume groups, rados namespaces, COSI, and object accounts. `AddToManagerFuncsMaintenance` currently contains `clusterdisruption.Add`. `Operator.addToManager` registers cluster, child, and maintenance controllers. `Operator.startCRDManager` builds and starts the controller-runtime manager.

## Control Flow, State, and Persistence
Startup creates a new runtime scheme, configures metrics binding from `ROOK_OPERATOR_METRICS_BIND_ADDRESS`, optionally restricts cache namespaces using `NamespaceToWatch`, creates a manager from in-cluster/rest config, builds a `controllerconfig.Context`, registers controllers, and blocks in `mgr.Start(context)`. Errors are sent to `mgrErrorCh`; no persistent state is written by this file directly.

## Dependencies and Integration Points
The file integrates all Ceph operator packages with controller-runtime manager/cache/config APIs, `clusterd.Context`, operator config, and maintenance context. `controllerconfig.LockingBool` is prepared for disruption reconciliation coordination.

## Risks
Controller order is implicit in list order and can affect watches or shared resources. A failure in any child registration aborts the whole manager. Namespace cache restriction must match all watched resources. The package global `EnableMachineDisruptionBudget` is declared here but not used in this file.

## Test Signals
Signals come mainly from individual controller tests and operator startup integration tests. Registration failures, scheme omissions, and namespace cache behavior are the critical cases to test around this file.
