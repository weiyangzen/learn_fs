# sources/cloud-native/moby/daemon/graphdriver/overlay2/overlay_unsupported.go

Purpose: unsupported-platform package stub for overlay2.

Important APIs and control flow: under build tag `!linux`, it only declares package `overlay2`; no driver registration or implementation is compiled.

State, dependencies, and risks: no runtime state. The integration point is platform build selection: overlay2 is Linux-only, so non-Linux graphdriver priority lists cannot select it. Build success is the primary signal.
