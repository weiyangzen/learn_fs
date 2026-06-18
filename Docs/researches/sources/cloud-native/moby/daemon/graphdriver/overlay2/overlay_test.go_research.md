# sources/cloud-native/moby/daemon/graphdriver/overlay2/overlay_test.go

Purpose: conformance and benchmark coverage for the overlay2 graphdriver.

Important APIs and control flow: `init` replaces chrooted archive functions with direct archive helpers for faster and more debuggable tests. `skipIfNaive` creates a temp dir and skips native-diff-specific tests when `useNaiveDiff` says the host is unsafe. Tests acquire a shared overlay2 driver, validate empty/base/snapshot creation, read through 128 layers, run diff/apply when native diff is available, skip `Changes` because naive change algorithm is not used there, and release the driver. Benchmarks cover common driver operations and deep-layer workloads.

State, dependencies, and risks: tests require Linux overlayfs support and sufficient mount privileges. Because native-diff capability is host-dependent, some tests skip on kernels/filesystems that force naive diff. The suite strongly signals graphdriver contract behavior but leaves some overlay2-specific storage-option and mount-shortening paths untested.
