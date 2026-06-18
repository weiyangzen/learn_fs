# sources/cloud-native/containerd/core/runtime/v2/task_manager.go

## Purpose
Registers and implements the runtime v2 task manager plugin. It creates bundles, activates mounts, starts shims, creates shim tasks, lists/gets/deletes tasks, exposes runtime plugin info, and validates runtime feature support.

## APIs, Flow, State, Dependencies, Risks, And Tests
`TaskConfig` carries platform strings. Plugin init parses platforms, exports supported log URI schemes, gets shim/mount/warning services, creates root/state dirs, reloads shims, emits platform warnings, and returns `TaskManager`. `NewTaskManager` is a direct constructor. `Create` builds a bundle, activates rootfs mounts with GC labels and shim-handled mount allowances, starts a shim, creates a `shimTask`, validates runtime features, calls task `Create`, and downgrades client version on `ErrNotImplemented`. Failure paths delete bundles, deactivate mounts, delete shim records, and try shim task cleanup. `Get`, `Tasks`, and `Delete` adapt shim map entries to runtime tasks. `PluginInfo` runs shim `-info`. `validateRuntimeFeatures` checks OCI idmap mounts against runtime feature output.

State includes root/state directories, active mount-manager entries, shim-manager namespace map, and bundle files. Dependencies include plugins, metadata services, mount manager, warning service, typeurl, OCI specs/features, runtime API, errdefs, and external shim binaries.

Risks include cleanup leaks on partial failures, mount activation races with duplicate task IDs, runc feature detection gaps, nil mount manager assumptions, and v2/v3 downgrade complexity. Test signals cover runtime path resolution, idmap feature validation, create/delete integration, mount activation/deactivation behavior, and plugin initialization metadata.
