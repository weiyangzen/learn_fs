<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/config/config-v1.17.0.toml -->
# sources/cloud-native/cri-o/test/testdata/config/config-v1.17.0.toml

Purpose: historical CRI-O v1.17-style full configuration fixture for config migration, parsing, and default compatibility tests.

Important structure: covers `[crio]`, API socket and stream server settings, runtime defaults, conmon/cgroup/SELinux/seccomp/AppArmor/runtime handler settings, image transport/pause/signature policy options, CNI network paths, and metrics. Most storage values are comments, while active defaults include `log_dir`, `version_file`, `listen`, `default_runtime = "runc"`, `cgroup_manager = "cgroupfs"`, default capabilities, runtime root, pause image, and CNI plugin dirs.

State and integration: static TOML input that represents old config shape and comments. It persists no runtime state, but tests may copy it into temporary CRI-O config paths. Risks include deprecated fields (`default_mounts`, old namespace lifecycle names) and old Kubernetes pause image/runtime defaults. Test signal is parser/migration acceptance of legacy config.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/config/config-v1.17.0.toml -->
