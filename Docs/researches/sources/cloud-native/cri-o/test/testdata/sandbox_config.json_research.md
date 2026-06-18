<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/sandbox_config.json -->
# sources/cloud-native/cri-o/test/testdata/sandbox_config.json

Purpose: baseline CRI `PodSandboxConfig` fixture for CRI-O integration tests.

Important structure: metadata identifies pod name, UID, namespace, and attempt; hostname is `crictl_host`; DNS server is `8.8.8.8`; resource requests/limits are present for CPU and memory; labels/annotations include seccomp unconfined and a custom annotation. Linux config sets `cgroup_parent` to a systemd-like slice and uses pod namespace options plus SELinux label fields.

State and integration: static JSON request body for `RunPodSandbox`. It stores no state directly; CRI-O creates pod sandbox resources. Risks include seccomp annotation compatibility, cgroup parent format mismatch with cgroup manager, and CRI API field drift. Test signal is sandbox creation and metadata/resource propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/sandbox_config.json -->
