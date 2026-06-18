# sources/cloud-native/moby/dockerversion/useragent_test.go

## Purpose
Tests Docker daemon User-Agent formatting and upstream client sanitization.

## Important APIs and Types
Contains `TestDockerUserAgent`, table-testing `DockerUserAgent` and `WithUpstreamUserAgent`.

## Control Flow, State, and Persistence
Each case builds a context and optional metadata slice, then checks the exact generated string against `getDaemonUserAgent()` plus appended metadata or `UpstreamClient(...)`.

## Dependencies, Integration Points, Risks, and Test Signals
Uses `pkg/useragent.VersionInfo` and `gotest.tools` assertions. It verifies parentheses, semicolon, and backslash escaping, and confirms CR/LF injection bytes are stripped. The test relies on the cached daemon UA from the same process, so it avoids fixed kernel/OS expectations while preserving exact formatting for the dynamic prefix.
