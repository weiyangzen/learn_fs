## sources/cloud-native/moby/daemon/internal/layer/filestore.go

Purpose: Provides filesystem metadata persistence for layer store state, including read-only layer metadata, tar-split data, writable mount metadata, and orphan cleanup discovery.

Important APIs/types: `fileMetadataStore`, `fileMetadataTransaction`, `newFSMetadataStore`, path helpers, `StartTransaction`, transaction setters (`SetSize`, `SetParent`, `SetDiffID`, `SetCacheID`, `SetDescriptor`, `TarSplitWriter`, `Commit`, `Cancel`), getters (`GetSize`, `GetParent`, `GetDiffID`, `GetCacheID`, `GetDescriptor`, `TarSplitReader`), mount metadata setters/getters, `getOrphan`, `List`, `Remove`, `RemoveMount`, and `isValidID`.

Control flow: Transactions write into `root/tmp` using `atomicwriter.WriteSet` and commit atomically to `root/<algorithm>/<encoded>`. Layer metadata files are simple text or JSON sidecars: `size`, `parent`, `diff`, `cache-id`, `descriptor.json`, and `tar-split.json.gz`. Tar-split writer can gzip input. Mount metadata lives under `root/mounts/<mount>/`. `List` enumerates valid layer digest directories and mount directories. `getOrphan` finds directories ending `-removing`, validates the encoded digest prefix, reads cache ID, and returns lightweight `roLayer` values for cleanup. `Remove` removes only matching `-removing` metadata folders for a given chain/cache pair.

State and persistence: All state is durable files under layerdb. The store itself has no lock; callers coordinate.

Dependencies and integration: Used by `layer_store.go` for restore, register, release, mount save, tar reconstruction, and cleanup. Depends on gzip, JSON, distribution descriptors, atomic writer, and digest parsing.

Risks: Metadata corruption causes restore failures. `isValidID` constrains mount/init IDs to 64 lower-hex chars with optional `-init`, which may reject unexpected graphdriver IDs. `TarSplitWriter` close wrapper ignores the gzip close error ordering by returning only file close after calling `wc.Close`.

Test signals: `filestore_test.go` covers transaction failure, orphan detection, and mount/init ID validation.
