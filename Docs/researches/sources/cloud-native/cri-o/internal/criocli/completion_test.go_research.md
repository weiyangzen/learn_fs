# sources/cloud-native/cri-o/internal/criocli/completion_test.go

Purpose: exposes unexported zsh completion quoting for external-package tests.

Important APIs/types/functions: `ZshQuoteCmd(name, usage string)` returns `zshQuoteCmd(name, usage)`.

Control flow: no logic beyond delegation.

State and persistence behavior: none.

Dependencies/integration points: compiled in the `criocli` package test context so `criocli_test.go` can call the helper from package `criocli_test`.

Risks: exporting test-only internals can hide API drift if the helper changes and tests are not updated.

Test signals: enables zsh quoting table tests.
