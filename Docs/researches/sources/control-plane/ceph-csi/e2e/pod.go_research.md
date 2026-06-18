# sources/control-plane/ceph-csi/e2e/pod.go

## Purpose
`pod.go` is the Ceph-CSI e2e suite's pod and nodeplugin helper layer. It loads pod templates, creates and deletes application pods, waits for daemonset and pod readiness, executes shell commands inside pods or CSI daemonset containers, validates RWOP and SELinux/read-affinity behavior, and verifies Ceph metadata tied to pod/node lifecycle.

## Important APIs, Types, And Functions
The file defines error-string constants for generic command failure and old/new Kubernetes ReadWriteOncePod conflict messages, plus `noError` as the nil expected-error sentinel.

Pod selection and execution helpers include `getDaemonSetLabelSelector`, `waitForDaemonSets`, `findPodAndContainerName`, `getCommandInPodOpts`, `execCommandInDaemonsetPod`, `getDaemonsetPodOnNode`, `listPods`, `execWithRetry`, `execCommandInPod`, `execCommandInContainer`, `execCommandInContainerByPodName`, `execCommandInToolBoxPod`, and `execCommandInPodAndAllowFail`.

Lifecycle helpers include `loadApp`, `createApp`, `createAppErr`, `waitForPodInRunningState`, `getPod`, `deletePod`, `deletePodWithLabel`, and `waitForPVCVolumeAttachmentsCleanup`.

Validation helpers include `calculateSHA512sum`, `appendToFileInContainer`, `getKernelVersionFromDaemonset`, `recreateCSIPods`, `validateRWOPPodCreation`, `verifySeLinuxMountOption`, `verifyReadAffinity`, `verifyMetadataRemoved`, `getAppAndPVC`, `verifyClientAddressMetadataExists`, and `verifyUserIdMappingMetadata`.

## Control Flow
The readiness functions poll Kubernetes resources until the desired condition appears or timeout expires. `waitForDaemonSets` repeatedly gets a daemonset and compares desired versus ready pod counts. `waitForPodInRunningState` polls a pod phase, accepts `Running`, treats completed phases as errors, and can treat expected event substrings as success when testing negative scheduling cases such as RWOP conflicts.

Execution flows resolve a target pod/container from selectors, build `e2epod.ExecOptions`, and run through `execWithRetry`, which retries only retryable API errors before returning captured stdout, stderr, and error. Higher-level command helpers log stderr but generally leave failure interpretation to callers.

Template and lifecycle flows unmarshal pod YAML, force `PullIfNotPresent` on all containers, create pods, wait for running state, and delete pods while polling for `NotFound`. CSI pod recreation deletes selected pods with kubectl and waits for both daemonset and deployment recovery.

Feature validations create PVC/app pairs, inspect Kubernetes and Ceph state, then clean up. SELinux validation modifies the bound PV mount options, starts an app, locates the nodeplugin pod on the app's node, and searches nodeplugin logs. Read-affinity validation creates an app, maps the PVC to an RBD image, reads `/sys/devices/rbd/*/config_info` from a CSI container, and validates `read_from_replica` and CRUSH location values. Metadata validation reads RBD image metadata or CephFS subvolume metadata for client address or user ID keys, deletes the pod, then waits for metadata removal.

## State, Persistence, And Dependencies
Most state is cluster state: pods, daemonsets, deployments, PVCs/PVs, VolumeAttachments, nodeplugin logs, and Ceph image/subvolume metadata. Local state is transient poll variables, command output, and loaded pod objects. Dependencies include Kubernetes core/apps/storage APIs, `wait.PollUntilContextTimeout`, e2e framework pod exec/log helpers, local constants for namespaces, labels, container names, topology values, Ceph metadata keys, and many helpers from adjacent files such as PVC helpers, deployment readiness, Ceph RBD/CephFS metadata access, image lookup, and kubectl retry wrappers.

## Integration Points
This file is central glue for RBD, CephFS, and NVMe-oF e2e tests. Other specs use it to run application pods against PVCs, execute verification commands in toolbox or nodeplugin pods, restart CSI components, validate Kubernetes scheduling errors, and assert that CSI node operations leave expected Ceph-side metadata. It also underpins `nvmeof_helper.go`, which uses `loadApp`, `createApp`, `deletePod`, and `waitForPodInRunningState`.

## Risks
`listPods` reads `podList.Items` before checking whether `List` returned an error, so a nil `podList` on error would panic. `waitForPVToBeDeleted` in the PVC file has a similar logging-before-error-check pattern; callers that combine these helpers should watch for API error paths. `calculateSHA512sum` uses `strings.Split(sha512sumOut, "")[0]`, which splits into characters rather than fields and will not return the checksum token; this looks like a concrete bug and should likely be `strings.Fields`. Several helpers assume selectors find at least one pod and that the first container is a useful default. `verifyReadAffinity` parses `key:value` pairs with fixed two-element indexing, so malformed `config_info` content can panic. Cleanup after validation failures is best-effort and may leak PVCs or pods if failures occur before the final cleanup call.

## Test Signals
High-value tests include selector resolution with empty, errored, and multi-container pod lists; exec retry behavior on retryable and permanent errors; pod readiness with expected RWOP event strings for both old and new Kubernetes messages; deletion polling on API errors and `NotFound`; checksum parsing against real `sha512sum` output; VolumeAttachment cleanup for bound, unbound, and deleted PVCs; SELinux mount-option log matching; read-affinity config parsing; and metadata removal for both RBD and CephFS after pod deletion.
