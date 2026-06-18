## sources/cloud-native/moby/integration-cli/test_vars_unix_test.go

Purpose: Unix build constants for integration CLI tests. It sets `isUnixCli = true` and `expectedFileChmod = "-rw-r--r--"`.

Control flow and state are compile-time only. The constants feed shared tests that branch on CLI platform or compare formatted permissions. Dependencies are Go build tags (`!windows`) and package `main`.

Risks are limited to permission-format assumptions and ensuring Windows builds use the companion file instead. Test signals are indirect through shared file permission and CLI-platform assertions.
