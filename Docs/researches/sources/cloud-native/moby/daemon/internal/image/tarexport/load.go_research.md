## sources/cloud-native/moby/daemon/internal/image/tarexport/load.go

Purpose: Implements Docker image archive load/import from a tar stream into image store, layer store, and reference store.

Important APIs/functions: `(*tarexporter).Load`, `untar`, `setParentID`, `loadLayer`, `setLoadedTag`, `safePath`, `parentLink`, `validatedParentLinks`, and `checkValidParent`.

Control flow: `Load` creates a temp directory, untars input with context-aware reads, opens `manifest.json`, rejects missing/null/invalid manifests, iterates manifest entries, reads config safely inside temp root, validates image JSON and host OS, applies optional platform matcher, checks manifest layer count against RootFS DiffIDs, then for each layer either reuses an existing chain layer or loads it from the archive. `loadLayer` opens the layer file sequentially, optionally wraps it in a progress reader, decompresses it, and registers it with descriptor support when available. After layers are present, `Load` creates the image, tags repo tags, records load events, validates parent links across the loaded set, and writes either loaded image names or IDs.

State and persistence: Writes layer data into `layer.Store`, image config into `image.Store`, tag mappings into `refstore.Store`, and emits image events. Temporary extraction state is removed at return.

Dependencies and integration: Uses chroot archive extraction, symlink-safe path resolution, compression, progress/stream formatting, distribution descriptors for foreign layers, tracing, and platform matching configured in `tarexport.go`.

Risks: Archive safety depends on `safePath` and `chrootarchive.Untar`. Load is all-or-partial; earlier layers/images/tags may remain if a later entry fails. Only loaded-set parent links are restored. Existing layer reuse trusts `lss.Get` and then checks DiffID.

Test signals: No dedicated load tests in this subset; behavior is coupled to image/layer store tests and external integration.
