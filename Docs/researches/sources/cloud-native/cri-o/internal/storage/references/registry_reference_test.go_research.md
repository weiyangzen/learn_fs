# sources/cloud-native/cri-o/internal/storage/references/registry_reference_test.go

Purpose: Ginkgo/Gomega tests for the registry-reference value type and its public parsing/accessor behavior.

Important APIs/types/functions: exercises `ParseRegistryImageReferenceFromOutOfProcessData`, `RegistryImageReferenceFromRaw`, `StringForOutOfProcessConsumptionOnly`, `Raw`, `Registry`, and `fmt.Formatter` conformance.

Control flow: tests parse valid short and fully qualified names, loop invalid inputs, assert panic paths for nil/name-only raw references and uninitialized values, then check formatting and registry-domain results.

State and persistence: no persistent state; the tests only construct in-memory references. They verify canonical strings that downstream metadata/status paths rely on.

Dependencies/integration: imports containers/image `reference` for raw-construction checks and the CRI-O `references` package under test. Uses the shared CRI-O test framework suite from `suite_test.go`.

Risks: tests cover tag-only and registry extraction but not tag+digest stripping; adding a regression test for digest precedence would protect the constructor's ambiguity handling. Panic-based API contracts are tested but still fragile for callers.

Test signals: strong signal that the type intentionally implements `fmt.Formatter` but not `fmt.Stringer`, preserving logging support while discouraging casual string conversion.
