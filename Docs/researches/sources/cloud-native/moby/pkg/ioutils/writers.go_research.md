<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/ioutils/writers.go -->
# sources/cloud-native/moby/pkg/ioutils/writers.go

Purpose: writer equivalent of `NewReadCloserWrapper`, adding a custom close callback to any `io.Writer`. Important API is `NewWriteCloserWrapper`; `writeCloserWrapper.Close` uses atomic state to invoke the closer once and warn on repeated closes. State is the wrapped writer and closed flag. Dependencies include `io` and atomics. Risks are low, mainly repeated close behavior and logging side effects. Test signal is `writers_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/ioutils/writers.go -->
