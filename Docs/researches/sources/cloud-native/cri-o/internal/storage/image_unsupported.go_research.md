# sources/cloud-native/cri-o/internal/storage/image_unsupported.go

Purpose: non-Linux implementation of image-pull cgroup movement.

Important APIs/types/functions: `moveSelfToCgroup(cgroup string) error`.

Control flow: immediately returns an unsupported error containing `runtime.GOOS`.

State and persistence behavior: no cgroup or filesystem changes.

Dependencies and integration points: selected by `//go:build !linux`; lets image service compile on non-Linux while making new-cgroup pull mode fail explicitly.

Risks: callers using `CgroupPull.UseNewCgroup` on unsupported platforms receive an error instead of silently ignoring the request.

Test signals: compile-time platform coverage only.
