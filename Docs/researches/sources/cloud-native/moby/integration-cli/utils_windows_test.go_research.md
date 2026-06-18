## sources/cloud-native/moby/integration-cli/utils_windows_test.go

Purpose: Windows implementation of `getLongPathName`, expanding short 8.3-style path components such as `ADMIN~1` to long names using Windows APIs.

Control flow converts the input string to UTF-16, calls `windows.GetLongPathName` with an initial buffer, reallocates if the return length exceeds the buffer, and converts the result back to a Go string. State is only the path queried from the Windows filesystem. Dependencies are `golang.org/x/sys/windows`.

Risks include UTF-16 conversion failures, race with filesystem changes, and buffer-size handling. Test signals are returned long paths or propagated errors for callers that normalize Windows filesystem output.
