## sources/distributed-fs/ipfs-kubo/thirdparty/unit/unit_test.go

Purpose: verifies the binary size constants in `thirdparty/unit`.

Important APIs/types/functions: `TestByteSizeUnit` asserts `KB` through `EB` equal repeated powers of 1024. It does not test `Information.String`.

State and persistence: no state; pure unit test.

Dependencies and integration points: uses Go `testing` only.

Risks and test signals: catches accidental constant drift but leaves formatter boundary behavior untested, including exact-unit and truncation cases.
