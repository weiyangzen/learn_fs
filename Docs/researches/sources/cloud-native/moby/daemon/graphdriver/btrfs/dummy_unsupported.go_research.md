# sources/cloud-native/moby/daemon/graphdriver/btrfs/dummy_unsupported.go

Purpose: unsupported-platform package stub for the Btrfs graphdriver.

Important APIs and control flow: the file has build tags `!linux || !cgo` and declares package `btrfs` without registering a driver or defining runtime behavior. This lets imports/builds of the package succeed on non-Linux or non-cgo builds while excluding the ioctl-backed implementation.

State, dependencies, and risks: there is no runtime state. The integration point is build selection: without Linux+cgo, `graphdriver.Register("btrfs", Init)` never runs, so automatic graphdriver selection cannot pick Btrfs. This is intentional, but tests or docs expecting Btrfs availability must account for build tags. No direct tests are needed beyond cross-platform build success.
