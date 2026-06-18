## sources/cloud-native/moby/daemon/internal/layer/filestore_test.go

Purpose: Tests filesystem metadata store edge cases.

Important helpers/tests: `randomLayerID` creates deterministic test digests. `newFileMetadataStore` creates temp roots. `TestCommitFailure` creates a file where the algorithm directory should be and expects `ENOTDIR`. `TestStartTransactionFailure` creates a file at `tmp`, expects transaction start failure, then removes it and verifies a transaction can be canceled. `TestGetOrphan` creates committed metadata, then renames the layer directory to a `-removing` name and expects orphan discovery. `TestIsValidID` covers valid 64-character lower-hex IDs, `-init`, too short/long, uppercase, non-hex, empty, and suffix-only strings.

Control flow and state: Tests mutate on-disk metadata directly to simulate failure and cleanup states.

Dependencies and integration: Uses `stringid.GenerateRandomID`, OpenContainers digest, syscall errors, and temp directories.

Risks covered: Atomic transaction parent conflicts, orphan layer cleanup discovery, and mount ID validation. Gaps include descriptor JSON, tar-split reader/writer, metadata getters, `List`, and `Remove`.

Persistence: Strong focus on layerdb disk layout.
