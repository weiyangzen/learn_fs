# sources/cloud-native/containerd/core/content/helpers_test.go

Purpose: unit tests for content helper copy and descriptor-data fast paths.

Important coverage: `TestCopy` validates no-offset copying, offset resume from seeker and unseekable sources, `ErrAlreadyExists` on commit, and repeated `ErrReset` success/failure paths using `fakeWriter`. `TestUseDescriptorData` covers matching data/digest/size, sha512, empty data, size mismatches, malformed or unsupported digests, and digest mismatch. `TestBlobReadSeeker_WithDescriptorData` and `TestReadBlob_WithDescriptorData` verify valid embedded data bypasses provider and invalid/mismatched data falls back or errors.

Control flow and state: tests use in-memory buffers, fake content provider, and fake reader-at implementation to assert whether the content provider was invoked.

Dependencies and integration: imports crypto hash registration for go-digest algorithms, errdefs, OCI descriptors, and testify.

Risks: does not cover `OpenWriter` retry timing, `CopyReaderAt`, `CopyReader`, `Exists`, or very large allocation behavior. Some fake reset closures capture `Status` by value, so they simulate only the intended buffer reset path.

Test signals: strong signal around descriptor `Data` trust rules and resumable `Copy` behavior.
