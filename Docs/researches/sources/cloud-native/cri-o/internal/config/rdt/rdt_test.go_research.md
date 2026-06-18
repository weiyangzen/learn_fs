# sources/cloud-native/cri-o/internal/config/rdt/rdt_test.go

Purpose: tests RDT YAML config file loading independently of host RDT enablement.

Important APIs/types/functions: `tempFileWithData` writes temporary test files; examples call unexported `loadConfigFile`.

Control flow: tests assert an error for a nonexistent file, an error for invalid config structure, and success for a minimal valid config containing a default partition, `l3Allocation`, and default class.

State and persistence behavior: writes temporary files through the CRI-O test framework and reads them through `loadConfigFile`.

Dependencies/integration points: uses Ginkgo/Gomega and the package-level test framework variable `t`. It validates the parser feeding `Config.Load`.

Risks: does not exercise `rdt.Initialize`, `rdt.SetConfig`, supported/disabled transitions, or annotation class enforcement.

Test signals: focused parser coverage.
