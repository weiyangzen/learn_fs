<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/images.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/images.go

- Purpose: Lists images and supports digest-based image lookup.
- Important functions: `images` and `imagesByDigest`; `imagesQuiet` controls terse output.
- Control flow: Enumerate images, output JSON or human list, optionally filter/lookup by digest.
- State and persistence: Read-only.
- Dependencies and integration: Uses storage image enumeration and digest metadata.
- Risks: Quiet output may omit information needed for disambiguation.
- Test signals: CLI output after image creation and digest assignment.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/images.go -->
