<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/checkpoint-restore-cri-test.sh -->
# sources/cloud-native/containerd/contrib/checkpoint/checkpoint-restore-cri-test.sh

## Purpose
End-to-end CRI checkpoint/restore test using crictl and containerd.

## Important APIs, Types, And Functions
Shell functions `cleanup`, `test_from_archive`, and `test_from_oci`.

## Control Flow
Builds `checkcriu`, validates tools, starts isolated containerd socket, creates pod/container fixtures, mutates rootfs, checkpoints, restores from archive and OCI image paths, verifies logs/files, and reports PASS/FAIL.

## State And Persistence
Creates temp directories, containerd sockets/logs, CRI pods/containers, checkpoint archives/images, and may kill containerd during cleanup.

## Dependencies And Integration Points
bash, go, CRIU, crictl, jq, ctr/containerd, testdata JSON, ghcr.io image.

## Risks And Test Signals
Requires root and host checkpoint support; cleanup is destructive to test containerd processes. Strong integration test signal. Source size reviewed: 229 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/checkpoint-restore-cri-test.sh -->
