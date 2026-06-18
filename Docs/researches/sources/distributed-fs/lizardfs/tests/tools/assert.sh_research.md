<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/assert.sh -->
# sources/distributed-fs/lizardfs/tests/tools/assert.sh

Purpose: implements the shell assertion DSL used by the LizardFS system tests, generating assert, assertlocal, and expect variants from assertion templates and attaching source-location/backtrace diagnostics.

Important APIs, functions, and commands: template functions define program, file, equality, numeric, regex, AWK, diff, success/failure, and eventually assertions; a loop synthesizes `assert_*`, `assertlocal_*`, and `expect_*` wrappers with source context.

Control flow: Control flow routes each public assertion wrapper through a template with `FAIL_FUNCTION` set to assert, assertlocal, or expect semantics; eventually assertions call `wait_for`, while failures collect source context and stack traces before failing or continuing.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: environment/config variables such as `ASSERT_NAME`, `ASSERT_FILE`, `ASSERT_LINE`, `FAIL_FUNCTION`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load. Test signals: hard assertions, soft expectation accumulation, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/assert.sh -->
