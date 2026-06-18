# sources/cloud-native/soci-snapshotter/integration/ztoc_test.go

Purpose: integration tests for the `soci ztoc` CLI. It verifies listing, info output, file extraction, shared-layer filtering, invalid inputs, and eStargz layer handling against real SOCI indexes and containerd/SOCI content stores.

Important APIs/types/functions: local JSON mirror types `Info` and `FileInfo` model `soci ztoc info` output. Tests include `TestSociZtocList`, `TestSociZtocInfo`, `TestSociZtocGetFile`, and `TestSociZtocWithEstargzLayers`. Helpers include `verifyZtocListing`, `dedupeZtocBlobs`, and `verifyInfoOutput`.

Control flow: tests start a snapshotter shell, reboot services, prepare SOCI indexes, then run `soci ztoc list` with all combinations of no filter, ztoc digest, image ref, and both filters. Info tests call `soci ztoc info`, unmarshal JSON, load the original ztoc from the content-store blob path, and compare fields. Get-file tests locate sample regular files per span, compare CLI output against contents extracted from the original gzip tar, and cover output-file mode. eStargz tests convert an image, push it through a registry, build a SOCI index, verify extraction from concatenated gzip members, push/pull the SOCI artifact, and assert FUSE mounting.

State and persistence: tests pull and convert images, write temporary output files, create registry-backed image references, push SOCI artifacts, remove images, and read blobs from containerd and SOCI content stores. eStargz coverage specifically persists converted OCI layers in the registry and validates later lazy-pull mounting.

Dependencies/integration points: integrates `soci` CLI, `nerdctl`, local registry helpers, `ztoc.Unmarshal`, OCI descriptors, digest parsing, gzip/tar readers, SOCI index annotations, content-store utilities, and containerd platforms. Uses Go 1.21 `slices` utilities for matching/deduplication.

Risks: tests depend on deterministic CLI table columns being discoverable by substring, prepared image sets containing regular files across spans, and exact JSON field order matching ztoc file metadata. `verifyZtocListing` checks length before deduping shared ztocs, so duplicate descriptor behavior must remain aligned with expected output semantics. Get-file stdout trimming assumes the CLI appends one newline.

Test signals: positive cases verify digest, size, layer annotations, info fields, file contents, eStargz extraction, push/pull path, and FUSE mount count. Negative cases cover invalid digest strings, missing ztocs, missing files, and unexpected ztoc filters.
