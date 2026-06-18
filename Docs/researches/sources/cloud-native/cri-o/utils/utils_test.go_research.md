<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/utils_test.go -->
# sources/cloud-native/cri-o/utils/utils_test.go

Purpose: Ginkgo specs for the general `utils` package.

Important coverage: tests `StatusToExitCode`, `CopyDetachable` success, custom keys, nil reader/writer, reader/writer errors, and detach sequence; goroutine stack writing success and invalid path failure; `GetUserInfo` with missing/empty/existing user data; `GeneratePasswd` and `GenerateGroup` for existing/non-existing users and groups; and `ParseDuration` for unit-suffixed, integer seconds, negative values, zero, floating unit values, invalid float seconds, invalid text, and empty input.

State and integration: creates temporary etc/passwd and etc/group fixtures via helper functions and writes generated files in temporary directories. Risks include not covering `EnsureSaneLogPath`, label options, sync, terminal resizing, secure join symlink attacks, or Linux systemd helpers. Test signal is strong for identity and duration utilities.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/utils_test.go -->
