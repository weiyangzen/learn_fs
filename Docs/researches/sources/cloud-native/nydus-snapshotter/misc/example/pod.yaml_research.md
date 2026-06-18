# sources/cloud-native/nydus-snapshotter/misc/example/pod.yaml

Purpose: minimal CRI pod sandbox example with metadata, namespace, log dir, and empty Linux namespace options.

Control flow/state: this file is declarative or a small script used by local/CI examples. It configures runtime endpoints, mounted paths, plugin settings, or test workload behavior rather than implementing snapshotter library logic.

Dependencies/integration: consumed by Makefile targets, GitHub workflows, crictl/containerd/NRI, or optimizer test harnesses depending on path.

Risks/tests: examples can drift from current binary flags, socket paths, or containerd schema. Coverage is indirect through smoke, optimizer, and integration workflows rather than unit tests.
