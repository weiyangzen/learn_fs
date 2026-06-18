# sources/cloud-native/moby/daemon/graphdriver/driver_windows.go

Purpose: Windows graphdriver priority declaration.

Important APIs and control flow: defines `priority = "windowsfilter"`, causing automatic graphdriver selection on Windows to prefer the HCS-backed Windows filter driver.

State, dependencies, and risks: there is no direct runtime state. Correct behavior depends on the Windows filter package registering `windowsfilter` and `InitFilter` succeeding on a supported filesystem. Test signal is Windows build and driver integration coverage.
