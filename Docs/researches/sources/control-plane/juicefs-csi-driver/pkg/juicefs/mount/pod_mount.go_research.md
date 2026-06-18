## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/pod_mount.go

### Purpose
`pod_mount.go` implements the Kubernetes mount-pod backend. It creates or reuses managed JuiceFS mount pods, tracks bind-mount references as pod annotations, creates Secrets and Jobs for lifecycle operations, waits for mount readiness, cleans up pods/secrets, and optionally uses the kubelet API for faster local mount pod discovery.

### Important APIs, Types, And Functions
`PodMount` embeds `SafeFormatAndMount` and holds a `K8sClient` plus optional `KubeletClient`. Public interface methods are `JMount`, `GetMountRef`, `UmountTarget`, `JUmount`, `JCreateVolume`, `JDeleteVolume`, `AddRefOfMount`, and `CleanCache`. Important helpers include `waitUntilKubeletCanSeePod`, `listMountPodsOfUniqueId`, `genMountPodName`, `createOrAddRef`, `waitUntilMountReady`, `waitUntilJobCompleted`, `setUUIDAnnotation`, `setMountLabel`, `GetJfsVolUUID`, `getErrContainerLog`, `getNotCompleteCnLog`, `GetRef`, and `GenPodNameByUniqueId`.

### Control Flow
`JMount` hashes settings, assigns an upgrade UUID, locks by hash, finds/reuses a mount pod, labels the app pod, creates or adds a reference, optionally waits for kubelet visibility, waits for mount readiness, and stores the JuiceFS UUID annotation if needed. `createOrAddRef` mutates mount path and secret name, creates directories, creates/updates the Secret, starts fuse-pass serving when supported, creates the pod, or adds a reference to an existing pod. `JUmount` removes the target annotation, checks remaining refs, honors delayed deletion annotations, stops fuse-pass, attempts source unmount, deletes the pod, and deletes the related Secret best-effort.

### State, Persistence, And Dependencies
Persistent state lives in Kubernetes pods, annotations, labels, jobs, and secrets. Reference keys are derived from target paths and counted by matching key/value pairs. Local state includes FUSE fd servers and cached dev minor values. Dependencies include `builder`, `k8sclient`, `resource`, `passfd`, `config`, `common`, Kubernetes retry/errors/fields APIs, host `umount`, and local filesystem helpers.

### Integration Points
This is the main backend for CSI node mount operations in pod mode. It integrates with `PodBuilder` and `JobBuilder`, `resource` wait/patch helpers, kubelet pod listing, app pod labels, FUSE passfd upgrade flows, and clean-cache jobs.

### Risks
Concurrency is controlled by a per-hash lock, but Kubernetes object races still require retry-on-conflict patching. Annotation JSON patch paths depend on safe reference key formats. Kubelet list fallback must remain correct or mount pod reuse can miss pods. `createOrAddRef` mutates `jfsSetting.MountPath` and `SecretName`, which callers must treat as side effects. `waitUntilJobCompleted` treats NotFound as success, which is correct after TTL recycle but can mask premature deletion. Deleting a pod with no refs is sensitive because delayed delete and fuse-pass cleanup must happen in the right order.

### Test Signals
`pod_mount_test.go` covers adding refs, unmount reference deletion, pod deletion/no deletion cases, lazy unmount output handling, create-or-add-ref reuse/new-pod behavior, `JMount` error path, constructor output, and `GetRef`. Additional integration tests should cover kubelet fallback, delayed delete, job completion errors, fuse-pass server cleanup, and app pod scheduling inheritance.
