# sources/cloud-native/containerd/cmd/ctr/commands/namespaces/namespaces_linux.go

Purpose: provides Linux namespace delete options.

Important APIs/functions: `deleteOpts()` returns `opts.WithNamespaceCgroupDeletion` when `--cgroup` is set.

Control flow: called by namespace remove command to translate CLI flag into service option.

State and persistence: can cause namespace cgroup deletion through runtime opts.

Dependencies/integration: runtime opts package and namespace delete option type.

Risks: only meaningful when the namespace cgroup exists and deletion is supported by the service/runtime.

Test signals: no local tests.
