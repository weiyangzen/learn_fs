## sources/cloud-native/soci-snapshotter/cmd/soci/commands/ztoc/get-file.go

Purpose: implements `soci ztoc get-file`, extracting one file from a local image layer using a zTOC.

Important APIs/types/functions: `getFileCommand`, `getZtoc`, and `getLayer`.

Control flow: require zTOC digest and file path args, connect to containerd, fetch/unmarshal zTOC from selected SOCI store, open artifacts DB, find original layer digest, open layer `ReaderAt` from containerd content store, extract file via zTOC, and write to output path or stdout.

State and persistence: read-only except optional output file write.

Dependencies and integration: zTOC package, artifacts DB, selected store for zTOC, containerd content for layer data.

Risks and test signals: `os.WriteFile` errors and permissions use mode `0`, and output write error is ignored. No direct tests here.
