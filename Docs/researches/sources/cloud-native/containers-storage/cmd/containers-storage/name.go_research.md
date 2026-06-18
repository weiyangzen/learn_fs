<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/name.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/name.go

- Purpose: Gets, adds, removes, or replaces names for storage objects.
- Important functions: `getNames`, `addNames`, `removeNames`, and `setNames`.
- Control flow: Resolve object, apply name operation, persist through storage API, and print resulting names.
- State and persistence: Mutates object name indexes in store metadata.
- Dependencies and integration: Uses storage name update semantics and duplicate-name checks.
- Risks: Name collisions can remove or reassign references; scripts should prefer IDs for stable addressing.
- Test signals: Lookup by new/removed names and duplicate-name rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/name.go -->
