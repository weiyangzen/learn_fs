# sources/cloud-native/cri-o/internal/oci/finished.go

## Purpose
Linux non-32-bit implementation for deriving container finish time from the conmon exit file's inode metadata.

## Behavior and Integration
`getFinishedTime` asserts `os.FileInfo.Sys()` to `*syscall.Stat_t` and returns `time.Unix(st.Ctim.Sec, st.Ctim.Nsec)`. It is called by `updateContainerStatusFromExitFile` in `runtime_oci.go` to populate `ContainerState.Finished`.

## Risks and Tests
The code assumes Linux `ctime` is the desired finish marker and that `FileInfo.Sys()` has the expected type. The 32-bit variant handles type conversion separately. Runtime status tests indirectly cover exit-file reading but not architecture-specific stat behavior.
