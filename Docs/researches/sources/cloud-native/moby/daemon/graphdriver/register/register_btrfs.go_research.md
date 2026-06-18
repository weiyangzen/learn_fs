# sources/cloud-native/moby/daemon/graphdriver/register/register_btrfs.go

Purpose: blank-import registration hook for the Btrfs graphdriver.

Important APIs and control flow: imports `github.com/moby/moby/v2/daemon/graphdriver/btrfs` for side effects under Linux when the `exclude_graphdriver_btrfs` build tag is not set. The imported package `init` registers `"btrfs"` with the central graphdriver registry.

State, dependencies, and risks: no direct runtime state. Build tags control whether Btrfs registration is compiled in. The file is part of the daemon's graphdriver plugin registration mechanism; omitting it or setting the exclusion tag makes Btrfs unavailable even on suitable filesystems. Build/initialization coverage is the signal.
