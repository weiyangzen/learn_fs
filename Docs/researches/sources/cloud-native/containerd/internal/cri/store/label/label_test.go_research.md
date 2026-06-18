# Research: sources/cloud-native/containerd/internal/cri/store/label/label_test.go

This SELinux-dependent test file validates label store reference counting and bad input handling. Both tests skip when SELinux is not enabled, because the underlying label parser and semantics depend on SELinux support.

`TestAddThenRemove` overrides the store's reserver and releaser to count calls and assert the label level. It reserves two labels with the same MCS level, verifies only one map entry with count two, releases both labels, and confirms the map is empty while reserver and releaser were each called exactly once. This proves the store reserves per level, not per full label string.

`TestJunkData` verifies empty labels are ignored, malformed labels fail reserve and do not call callbacks, releasing unknown labels is a no-op, and over-releasing after one reserve only calls releaser once and leaves no level entry. The tests guard against label leaks and double-release bugs. Gaps include concurrent reserve/release, different levels in one test, behavior when SELinux parser accepts labels without levels, and integration with container/sandbox stores.
