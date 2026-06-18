# sources/cloud-native/moby/daemon/graphdriver/register/register_overlay2.go

Purpose: blank-import registration hook for the overlay2 graphdriver.

Important APIs and control flow: imports `overlay2` for side effects on Linux unless `exclude_graphdriver_overlay2` is set. The overlay2 package `init` registers the `"overlay2"` driver.

State, dependencies, and risks: no direct state. This file connects the default Linux priority list to the actual driver implementation. Excluding it or breaking its import would make automatic selection skip overlay2 and fall back to later drivers. Build and initialization are the primary signals.
