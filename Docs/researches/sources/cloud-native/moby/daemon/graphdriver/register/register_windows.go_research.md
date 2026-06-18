# sources/cloud-native/moby/daemon/graphdriver/register/register_windows.go

Purpose: blank-import registration hook for the Windows graphdriver.

Important APIs and control flow: under Windows builds, imports the `windows` graphdriver package for side effects so it registers `"windowsfilter"`.

State, dependencies, and risks: no direct runtime state. This is the bridge between the Windows priority list and the HCS-backed implementation. Correctness depends on Windows-only build selection and successful `InitFilter` at runtime. Build and Windows integration tests are the signal.
