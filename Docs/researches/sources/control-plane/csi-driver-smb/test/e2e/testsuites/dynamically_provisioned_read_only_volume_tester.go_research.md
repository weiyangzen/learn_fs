# sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_read_only_volume_tester.go

## Purpose
This testsuite verifies that read-only SMB volume mounts prevent writes and expose an expected error in pod logs.

## Important APIs, Types, And Functions
`DynamicallyProvisionedReadOnlyVolumeTest` carries a dynamic driver, pod details, and storage-class parameters. `Run` provisions volumes and checks failure behavior.

## Control Flow
For each pod, it selects the expected log substring: `"Read-only file system"` for Linux or `"FileOpenFailure"` for Windows. It sets up dynamic volumes, creates the pod, waits for failure, then reads pod logs and asserts that the selected substring is present.

## State, Persistence, And Dependencies
State includes the Kubernetes resources and pod log stream. Dependencies include Gomega string matching, framework error handling, and shared provisioning helpers.

## Integration Points
Specs must configure a pod command that attempts a write to a read-only mount. This runner integrates with the shared `TestPod.WaitForFailure` condition and Kubernetes pod log retrieval.

## Risks And Test Signals
The expected error text is platform-specific and could change with base image or shell behavior. The signal is a failed pod plus matching log text; a mount failure with different wording may fail the test even if read-only behavior is correct.
