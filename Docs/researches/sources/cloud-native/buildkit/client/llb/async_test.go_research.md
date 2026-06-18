# sources/cloud-native/buildkit/client/llb/async_test.go

Purpose: verifies lazy behavior of asynchronous state transforms.

Important APIs/types/functions: `TestAsyncNonBlocking` builds an image state, adds a blocking async transform, chains another run, releases the wait channel only before marshal, and inspects generated protobuf operations.

Control flow: after creating the async chain, the test confirms the callback has not run within 100ms. It then marshals, checks graph length and final pointer, and asserts command/cwd propagation through async result.

State and persistence: uses channels to observe callback execution; no external persistence.

Dependencies/integration points: LLB `Image`, `Dir`, `Async`, `Run`, `Shlex`, marshal, and test helpers `parseDef`/`last`.

Risks/test signals: catches eager async execution and metadata propagation regressions. It does not cover error caching or constraints-sensitive async behavior.
