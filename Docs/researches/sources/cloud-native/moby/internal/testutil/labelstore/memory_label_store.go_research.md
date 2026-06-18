<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/labelstore/memory_label_store.go -->
# sources/cloud-native/moby/internal/testutil/labelstore/memory_label_store.go

Purpose: implements a thread-safe in-memory label store keyed by OCI digests for tests. Important APIs are `InMemory.Get`, `Set`, and `Update`. Control flow locks a mutex, clones maps on reads/writes to avoid caller mutation, replaces labels on `Set`, and merges updates on `Update` while returning the new map. State is a process-local digest-to-label map. Dependencies include `maps.Clone`, `sync`, and `go-digest`. Risks are low; absence of persistence is intentional, but tests depending on insertion order should avoid map ordering. Test signal is for consumers that need deterministic label-store behavior without backing storage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/labelstore/memory_label_store.go -->
