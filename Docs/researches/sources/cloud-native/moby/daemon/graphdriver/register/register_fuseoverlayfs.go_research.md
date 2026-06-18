# sources/cloud-native/moby/daemon/graphdriver/register/register_fuseoverlayfs.go

Purpose: blank-import registration hook for the fuse-overlayfs graphdriver.

Important APIs and control flow: imports the `fuse-overlayfs` graphdriver package for side effects on Linux unless `exclude_graphdriver_fuseoverlayfs` is set. Its `init` registers `"fuse-overlayfs"` in the graphdriver registry.

State, dependencies, and risks: no direct runtime state. Build tags decide availability; runtime initialization still checks binary and kernel support. This hook is needed for Linux priority selection to consider fuse-overlayfs after overlay2. Test signal is successful build and driver selection/registration.
