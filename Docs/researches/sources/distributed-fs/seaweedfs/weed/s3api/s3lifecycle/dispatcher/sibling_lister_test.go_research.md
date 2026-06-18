# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dispatcher/sibling_lister_test.go

Purpose: tests `filerSiblingLister` with a fake filer implementing the small `ListEntries` and `LookupDirectoryEntry` surface used by the lister.

Important helpers/APIs: `fsListStream`, `fsFakeFiler`, `newFakeFiler`, `newLister`, and `versionEntry`. The fake models sorted list responses, `StartFromFileName` pagination, first-`Recv` not-found errors, one-shot injected transport errors, and tree-backed lookup.

Control flow and state: tests build an in-memory directory tree keyed by filer directory path. `Survivors` cases exercise version count capping and null bare-key lookup. `ListVersions` cases force missing containers, filtered invalid entries, a 1030-entry pagination boundary, and list errors. `LookupNullVersion` and `LookupVersion` cases drive regular files, explicit null ids, directory-key markers, plain directories, not-found collapse, and transport errors.

Dependencies/integration: imports filer protobufs, `s3_constants`, gRPC stream interfaces, and testify. It documents expectations the router and dispatcher rely on when determining sole survivors and version identities.

Risks: fake behavior must stay close to real filer semantics, especially not-found surfacing from stream `Recv` and exclusive `StartFromFileName`; drift could hide production bugs. The embedded client intentionally panics on unexpected method use.

Test signals: this is the signal source. It confirms safety for hard-delete races, directory marker handling, version filtering, pagination ordering, and non-NotFound error propagation.
