<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/ioutils/writers_test.go -->
# sources/cloud-native/moby/pkg/ioutils/writers_test.go

Purpose: unit test for `NewWriteCloserWrapper`. It writes through to an in-memory buffer and verifies the close callback executes only once across repeated closes. State is a bytes buffer and counter. Dependencies are standard testing and bytes. Risks covered are double-close behavior; write-after-close behavior is not deeply exercised. Test signal is narrow and fast.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/ioutils/writers_test.go -->
