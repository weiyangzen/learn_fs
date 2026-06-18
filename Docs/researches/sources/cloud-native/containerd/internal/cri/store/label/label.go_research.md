# Research: sources/cloud-native/containerd/internal/cri/store/label/label.go

This file implements a small SELinux process label reservation store. `Store` tracks MLS/MCS levels in a map from level string to reference count, with injectable `Releaser` and `Reserver` callbacks defaulting to `selinux.ReleaseLabel` and `selinux.ReserveLabel`.

`Reserve` parses the label with `selinux.NewContext`, extracts the `level` component, ignores empty levels, calls the reserver only when the level is not already tracked, and increments the count. `Release` parses the label, ignores invalid labels and empty levels, looks up the count, and either calls the releaser and deletes the level when count is one, deletes corrupt nonpositive counts, or decrements counts above one.

State is process-local reference counts plus external SELinux reservation/release side effects. The store is shared by sandbox and container stores in `NewCRIService`, preventing duplicate reservation of the same MCS level while multiple objects use it. Risks include invalid labels causing reserve errors but release no-ops, empty level labels being ignored, correctness depending on all add/delete paths balancing reserve/release, and injected callbacks used in tests. Tests under SELinux cover reference counting, bad input, unknown release, and over-release behavior.
