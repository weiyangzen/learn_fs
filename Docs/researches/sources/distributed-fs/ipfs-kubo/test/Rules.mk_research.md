# sources/distributed-fs/ipfs-kubo/test/Rules.mk

Purpose: includes the test subtree make rules into the repository make system.

Important APIs and control flow: includes `mk/header.mk`, sets `dir` to `test/bin`, `test/sharness`, and `test/unit` in turn and includes each `Rules.mk`, then includes `mk/footer.mk`.

State and persistence: no direct writes; participates in make target graph construction.

Dependencies and integration: relies on surrounding make variables, `mk/header.mk`, `mk/footer.mk`, and child Rules files.

Risks and test signals: simple include file with no standalone tests. Missing child files or unexpected `dir` variable behavior would break make parsing.
