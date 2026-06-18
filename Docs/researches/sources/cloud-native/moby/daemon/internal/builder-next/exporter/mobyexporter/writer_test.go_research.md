# sources/cloud-native/moby/daemon/internal/builder-next/exporter/mobyexporter/writer_test.go

## Purpose
Validates basic image config patching behavior for the Moby exporter writer helpers.

## APIs, Control Flow, and Integration
`TestPatchImageConfig` table-drives `patchImageConfig` with `{}`, `{"history":[]}`, `{"rootfs":{}}`, and `null`. It expects all object configs to succeed and a null config to return `null image config`. The test uses `gotest.tools/v3/assert`.

## State, Dependencies, and Risks
No external state is touched. The test confirms parsing and top-level object validation but does not verify actual generated `rootfs`, `history`, `created`, or inline cache fields. It is a smoke test rather than comprehensive config compatibility coverage.
