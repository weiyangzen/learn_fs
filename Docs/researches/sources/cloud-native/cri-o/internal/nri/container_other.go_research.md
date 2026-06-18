# sources/cloud-native/cri-o/internal/nri/container_other.go

Purpose: non-Linux container conversion fallback for NRI. `linuxContainerToNRI` returns nil so `nri.Container.Linux` is unset on non-Linux builds. There is no state, persistence, or external control flow. Dependencies are only NRI adaptation types for the return signature. Risks are plugins expecting Linux data on non-Linux platforms and reduced feature parity. Test signals are compile-time build tag coverage.
