# sources/cloud-native/buildkit/client/llb/meta_test.go

Purpose: tests working directory normalization for relative and absolute `Dir` updates.

Important APIs/types/functions: `TestRelativeWd` chains `Scratch().Dir(...)` calls and uses `getDirHelper` to retrieve the current directory.

Control flow: asserts `foo` becomes `/foo`, `bar` appends, `..` resolves upward, absolute `/baz` replaces, and excessive `../../..` clamps to `/`.

State and persistence: no persistence; state metadata only.

Dependencies/integration points: `Scratch`, `State.Dir`, `State.GetDir`, and internal `getDir`.

Risks/test signals: protects path normalization semantics. It does not cover environment list ordering/deletion, shlex errors, user, network, security, ulimit, or resource metadata.
