## sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/store.go

Purpose: converts global CLI flags into SOCI store options.

Important APIs/types/functions: `ContentStoreOptions`.

Control flow: reads content-store type, containerd address, and root flags, then returns `store.WithType`, `store.WithContainerdAddress`, and `store.WithSnapshotterRoot`.

State and persistence: no direct state; returned options determine later DB/content-store paths and connections.

Dependencies and integration: used by create, convert, push, index, ztoc, prefetch, and rebuild commands when opening `store.NewContentStore`.

Risks and test signals: this helper does not trim `unix://` prefixes unlike `NewClient`; downstream store must handle address shape. No direct tests here.
