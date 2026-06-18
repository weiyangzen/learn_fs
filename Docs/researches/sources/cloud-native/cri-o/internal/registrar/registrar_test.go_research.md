# sources/cloud-native/cri-o/internal/registrar/registrar_test.go

Purpose: verifies registrar name/key reservation semantics and suite setup.

Important APIs/types/functions: `TestRegistrar`, test framework setup, and specs for `Reserve`, `Release`, `GetNames`, `Delete`, `Get`, and `GetAll`.

Control flow: each test starts with a fresh registrar containing `testName -> testKey`. Specs then add names, repeat operations, or delete state and assert errors/contents.

State and persistence behavior: in-memory only. The suite uses global framework state but recreates the registrar per test.

Dependencies and integration points: depends on Ginkgo/Gomega and CRI-O's test framework.

Risks: duplicate `GetNames` describe blocks cover similar assertions. Tests do not exercise concurrent use or mutation of returned slices.

Test signals: confirms reserved-name conflicts return `ErrNameReserved`, missing key/name return `ErrNoSuchKey` and `ErrNameNotReserved`, and delete removes reverse mappings.
