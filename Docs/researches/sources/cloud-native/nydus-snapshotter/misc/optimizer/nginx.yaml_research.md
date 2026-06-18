# sources/cloud-native/nydus-snapshotter/misc/optimizer/nginx.yaml

Purpose: CRI container spec for nginx optimizer test that mounts a script directory and reads a file list.

Control flow/state: this file is declarative or a small script used by local/CI examples. It configures runtime endpoints, mounted paths, plugin settings, or test workload behavior rather than implementing snapshotter library logic.

Dependencies/integration: consumed by Makefile targets, GitHub workflows, crictl/containerd/NRI, or optimizer test harnesses depending on path.

Risks/tests: examples can drift from current binary flags, socket paths, or containerd schema. Coverage is indirect through smoke, optimizer, and integration workflows rather than unit tests.
