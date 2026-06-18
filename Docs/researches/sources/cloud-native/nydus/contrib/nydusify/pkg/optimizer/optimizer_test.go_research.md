# sources/cloud-native/nydus/contrib/nydusify/pkg/optimizer/optimizer_test.go

Purpose: unit tests for optimizer helpers and external builder argument construction.

Important fixtures/APIs: fake optimizer shell script helpers, `makeDesc`, `packToTar`, `getOriginalBlobLayers`, `isSignalKilled`, `Build`, `hosts`, `remoter`, and uncompressed tar packing.

Control flow and state: tests create fake executable scripts that record arguments and write output JSON. They verify localfs vs remote backend flags, invalid JSON errors, and documented panics for missing/empty blob lists. Tar tests inspect directory and file entries. Remoter tests validate reference handling.

Dependencies and integration points: temporary shell executables, OCI descriptors/digests, parser image structs, Nydus utility media types, gzip/tar readers, filesystem temp dirs, and Docker reference validation through `remoter`.

Risks and test signals: tests explicitly capture panic behavior for empty output JSON, indicating a known robustness gap. Full `Optimize` and remote push sequencing are not covered with mocks here.
