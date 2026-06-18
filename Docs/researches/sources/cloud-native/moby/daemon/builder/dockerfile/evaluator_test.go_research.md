## sources/cloud-native/moby/daemon/builder/dockerfile/evaluator_test.go

**Purpose:** Verifies that parsed Dockerfile commands are dispatched successfully through the evaluator jump table.

**Important APIs:** `TestDispatch` uses `dispatchTestCase` entries and `TestMain` setup to run command dispatch scenarios.

**Control flow:** Test cases parse or construct commands, pass them through `dispatch`, and assert expected errors/state.

**State and persistence:** Uses in-memory dispatch state and mocks.

**Dependencies and integration:** Protects evaluator-to-dispatcher wiring rather than real daemon side effects.

**Risks:** It does not replace instruction-specific tests; errors in backend integration, container lifecycle, or image persistence can pass these tests.

**Test signals:** Useful compile/runtime signal that supported command types are recognized and unsupported paths fail predictably.
