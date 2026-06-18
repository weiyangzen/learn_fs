## sources/cloud-native/moby/integration-cli/docker_utils_test.go

Purpose: shared integration-CLI utility layer for Docker command execution, inspect helpers, file IO, daemon time, environment construction, sleeping containers, goroutine polling, error decoding, polling composition, and special image loading.

Important functions include `dockerCmdWithError`, `inspectField`, `inspectMountPoint`, `daemonTime`, `daemonUnixTime`, `appendBaseEnv`, `runSleepingContainer`, `getGoroutineNumber`, `waitForStableGoroutineCount`, `pollCheck`, `reducedCheck`, `sumAsIntegers`, and `loadSpecialImage`. Control flow is mostly helper wrapping: run CLI/API commands, parse JSON or text, poll until comparisons pass, and fail tests on unexpected errors.

State touches daemon image/container stores, host container storage files, temp tar/image paths, and API `Info` fields. Dependencies include `cli`, `client`, `daemon`, `archive`, `specialimage`, `icmd`, and `poll`. Risks are deprecated helpers preserving old behavior, direct host storage reads, fragile text parsing of `docker info`, and poll timeouts hiding slow convergence. Test signals are helper-level assertions, returned IDs/fields, stable goroutine counts, decoded error messages, and loaded image refs.
