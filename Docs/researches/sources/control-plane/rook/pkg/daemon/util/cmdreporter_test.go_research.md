# sources/control-plane/rook/pkg/daemon/util/cmdreporter_test.go

Purpose: tests command reporter serialization, constructor validation, execution capture, and ConfigMap safety behavior.

Important APIs/types/functions: `TestCommandMarshallingUnmarshalling()` covers command JSON helpers. `TestNew()` covers `NewCmdReporter()`. `TestRunner_Run()` uses a helper process to exercise `Run()`, `runCommand()`, and `saveToConfigMap()`. `mockExecCommand()` and `TestCmdReporterHelperProcess()` implement the fake command process.

Control flow: tests replace package variable `execCommand` with `mockExecCommand`, which re-invokes the test binary with `GO_WANT_HELPER_PROCESS=1`. Environment variables control fake stdout, stderr, retcode, and printed command. The tests verify generated ConfigMap data and app-label conflict behavior with fake Kubernetes clients.

State and persistence behavior: uses in-memory fake Kubernetes clientsets. Environment variables and package-level `execCommand` are mutated and restored around tests.

Dependencies and integration points: uses `client-go` fake clientset, `testify/assert`, OS process re-exec testing pattern, and Rook `k8sutil.AppAttr` constants.

Risks: tests assume Unix-like process exit behavior and environment variable isolation. Existing ConfigMaps in tests always initialize `Labels` and `Data`, so nil-map edge cases in production are not covered. Stderr teeing to stdout is not explicitly asserted.

Test signals: good coverage for expected command and ConfigMap workflow, including nonzero retcodes as successful reporter runs and app-label protection.
