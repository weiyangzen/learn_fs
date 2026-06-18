# sources/distributed-fs/openafs/src/butm/error_macros.h

Purpose: tiny local error-exit helper header used by tape module code and tests to centralize `code = value; goto label` patterns.

Important APIs: `ERROR_EXIT(evalue)` sets local variable `code` and jumps to `error_exit`; `ABORT_EXIT(evalue)` sets `code` and jumps to `abort_exit`.

Control flow and dependencies: these macros require a local `code` variable and the corresponding label to exist in the including function. They are intentionally statement-like via `do { ... } while (0)`.

Risks and tests: macro use hides non-local control flow and can overwrite prior error values during cleanup if used carelessly. Compile coverage comes from `file_tm.c`, `test_ftm.c`, and butc code that include similarly named local headers.
