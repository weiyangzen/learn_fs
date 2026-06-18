# sources/cloud-native/moby/daemon/graphdriver/fsdiff.go

Purpose: generic diff implementation that wraps a `ProtoDriver` to satisfy full `graphdriver.Driver` when the backend exposes mounted directories but not native diffs.

Important APIs and control flow: `NewNaiveDiffDriver` returns a `NaiveDiffDriver` with ID mapping. `Diff` mounts the target layer, and for base layers tars the whole filesystem; otherwise it mounts parent, computes `archive.ChangesDirs`, exports changes with ID mapping, and wraps the tar reader so close releases mounts. It sleeps until the next second after close to avoid mtime precision races. `Changes` mounts layer and optional parent and delegates to `archive.ChangesDirs`. `ApplyDiff` mounts the target, applies an uncompressed layer through `ApplyUncompressedLayer` with ID mapping and best-effort xattr option, and logs timing. `DiffSize` computes changes then sums changed sizes.

State, dependencies, and risks: state is backend mounts and `BestEffortXattrs`. Dependencies include `go-archive`, chrootarchive, compression, logging, and user mappings. Risks include expensive full-tree comparisons, mtime second-granularity workaround slowing builds, and subtle behavior when xattrs cannot be restored. Concrete drivers use this as fallback or primary diff implementation.
