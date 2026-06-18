<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/gc.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/gc.go

- Purpose: Exposes garbage collection for unreferenced storage data.
- Important behavior: Calls `m.GarbageCollect()` and reports errors.
- Control flow and state: Mutates storage by removing unreferenced data directories or driver state that the library considers garbage.
- Dependencies and integration: Relies on store GC implementations, especially container/layer/image stores.
- Risks: GC is destructive and correctness depends on metadata references being current.
- Test signals: Integration tests that leave orphan data and verify cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/gc.go -->
