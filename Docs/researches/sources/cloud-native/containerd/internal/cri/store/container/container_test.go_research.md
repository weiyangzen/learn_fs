# Research: sources/cloud-native/containerd/internal/cri/store/container/container_test.go

This test file validates the container store and container construction options. `TestContainerStore` builds several containers with fake status and SELinux-like process labels, adds them to a `Store`, retrieves them by generated truncated IDs, lists them, updates cached stats, checks duplicate add errors, deletes them by truncated IDs, and verifies deleted containers return `errdefs.ErrNotFound`.

When SELinux is enabled, the test overrides the label store's reserver/releaser callbacks to assert MCS levels are reserved once per level and released after the last container using that level is removed. The stats update section verifies `UpdateContainerStats` mutates the stored container values and `List` reflects those cached samples.

`TestWithContainerIO` checks that `WithContainerIO` attaches a `ContainerIO` pointer while a container without the option has nil IO. The tests exercise store locking indirectly but not with concurrency. Covered risks include truncation-index lookup, duplicate ID handling, stats cache mutation, stop-channel behavior from fake exited status, and label reference behavior. Gaps include checkpoint-backed `WithStatus`, IO close side effects on delete, stats collector callbacks, and real containerd client handles.
