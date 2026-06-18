<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/check.go -->
# sources/cloud-native/containers-storage/check.go

- Purpose: Implements storage integrity checking and repair across layers, images, containers, and low-level graph-driver layers.
- Important APIs/types: Exported error aliases, `CheckOptions`, `CheckMost`, `CheckEverything`, `CheckReport`, `RepairOptions`, `RepairEverything`, `(*store).Check`, and `(*store).Repair`. Internal comparison types include `checkIgnore`, `checkFileInfo`, and `checkDirectory`.
- Control flow: `Check` derives ignore rules from graph/pull options, walks layer stores to validate big data, diff digests/sizes, mountability, and optional mounted contents, then walks image stores to validate big data and layer references, walks containers to validate data/image/layer references, flags old unreferenced layers, and compares graph-driver layer listing for unaccounted layers.
- State and persistence: Mostly read-only, but it mounts layers for inspection and uses graph-driver get/put. `Repair` mutates storage by deleting damaged containers/images/layers, unmounting layers, and removing unaccounted driver layers.
- Dependencies and integration: Relies on storage driver APIs, archive/tar diff generation, id mappings, lock-protected store readers, logrus, and shared error types.
- Risks: Expensive full-store operation; content comparison must correctly handle whiteouts, hard links, idmapped ownership, and configured ignore modes. Repair deletes data and must preserve order so child layers are removed before parents.
- Test signals: Unit tests cover directory comparison; integration tests should exercise damaged data, missing layers, and repair behavior across drivers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/check.go -->
