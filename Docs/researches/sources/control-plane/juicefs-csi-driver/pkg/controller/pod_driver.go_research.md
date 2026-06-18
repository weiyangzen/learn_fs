# sources/control-plane/juicefs-csi-driver/pkg/controller/pod_driver.go

Purpose: node mount-pod lifecycle state machine. It handles ready, pending, error, complete, and deleting mount pods; manages reference annotations; recreates replacement pods; recovers corrupt bind mounts; cleans mount paths/cache; and aborts stuck FUSE connections.

Important APIs/types: `PodDriver`, `Result`, `podStatus`, `Run`, `checkAnnotations`, status handlers, `recover`, `recoverTarget`, `CleanUpCache`, `applyConfigPatch`, `checkMountPodStuck`, `DoAbortFuse`, and `newMountPod`.

Control flow/state: `Run` refetches the pod, updates an in-memory unique-ID index, removes stale refs, then dispatches by status. Ready pods wait for mount readiness and recover targets from mountinfo. Deleted pods clean up or create replacements when refs remain. Pending/error pods may remove resource requests and recreate. Complete pods may create replacements and delete old pods.

Persistence/integration: changes Kubernetes Pods, Secrets, finalizers, annotations, and Jobs; performs host unmount/bind mount operations; manages FUSE fd handoff state; saves/deletes FUSE dev minor metadata; and triggers cache cleanup through mount utilities. Depends on config setting reconstruction, pod builders, passfd, resource utilities, mountinfo, and `k8sclient`.

Risks: high-risk node code with real unmounts, bind mounts, pod deletion/recreation, and goroutines. Local pod snapshots can remove annotations if stale. `applyConfigPatch` mutates the passed pod metadata/spec. Some cleanup errors are logged and ignored to preserve progress. Direct tests for this state machine are absent in this subset.

Test signals: indirect only through config and mountinfo tests; lifecycle branches need dedicated controller/driver tests for stronger confidence.
