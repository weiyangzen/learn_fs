## sources/cloud-native/moby/integration/capabilities/capabilities_linux_test.go

Purpose: verifies `no-new-privileges=true` interacts correctly with file capabilities. It builds an image where `/bin/cat` has `CAP_DAC_OVERRIDE` and a non-root user attempts to read a root-only file.

Control flow creates a fake build context with a Dockerfile, builds the image through the API, then runs two subtests. One requests `CAP_DAC_OVERRIDE` and expects stdout `hello`; the other drops the capability and expects an operation-not-permitted stderr. Both runs set user `test` and security option `no-new-privileges=true`, wait for exit, and read logs via `stdcopy`.

State includes a built test image, container capability sets, file capability metadata, and logs. Dependencies include Linux base image, `libcap2-bin`, internal container helpers, fakecontext, and API log demultiplexing. Risks are package install/network behavior during build, capability semantics across kernels, and exact error text. Test signals are trimmed stdout/stderr matching the expected strings.
