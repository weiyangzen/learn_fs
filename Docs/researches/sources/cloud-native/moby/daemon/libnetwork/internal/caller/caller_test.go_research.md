# Research: sources/cloud-native/moby/daemon/libnetwork/internal/caller/caller_test.go

Purpose: verifies `caller.Name` stack-level behavior. Important fixtures are helper functions `fun1` through `fun6` and `TestCaller`.

Control flow: `fun1` returns `Name(0)` and should resolve to `fun1`; `fun2` returns `Name(1)` and should resolve to `TestCaller`; `fun3`/`fun4` validate an indirect `Name(0)` call; `fun5`/`fun6` validate an indirect `Name(1)` call. Failures use fatal assertions with the unexpected name.

State/dependencies: no external state or persistence. Dependencies are the runtime call stack and testing package. The test protects the hard-coded frame offset in `Name`. Risks not covered include compiler inlining effects, method receivers, anonymous functions, and out-of-range stack levels returning `unknown`.
