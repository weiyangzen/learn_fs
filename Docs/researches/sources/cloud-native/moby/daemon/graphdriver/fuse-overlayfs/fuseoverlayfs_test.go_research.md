# sources/cloud-native/moby/daemon/graphdriver/fuse-overlayfs/fuseoverlayfs_test.go

Purpose: conformance and benchmark coverage for the fuse-overlayfs graphdriver.

Important APIs and control flow: `init` swaps chrooted untar/apply functions for direct archive helpers to speed tests and make failures easier to debug. Tests acquire a shared driver, validate empty/base/snapshot layer creation, read through 128 layers, and release the driver. Benchmarks measure `Exists`, `Get` on empty layers, diff workloads with different lower/upper file counts, diff/apply, deep-layer diff, and deep-layer read.

State, dependencies, and risks: tests require Linux, the `fuse-overlayfs` binary, FUSE support, and sufficient mount permissions. They do not include native diff tests because this driver relies on naive diff. The strongest signals are layer-chain visibility and generic graphdriver correctness; performance benchmarks expose FUSE and naive diff overhead.
