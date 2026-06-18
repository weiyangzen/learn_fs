<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/test.d/template -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/test.d/template

## Purpose
This file is a skeleton for new ftrace `.tc` shell test cases.

## Important APIs, Types, And Functions
It documents required metadata lines `# description:` and `# requires:` and the result helpers `exit_pass`, `exit_fail`, `exit_unsupported`, `exit_unresolved`, `exit_untested`, and `exit_xfail`.

## Control Flow
The template exits `0` by default. Real tests are sourced by `ftracetest` under `set -e` from the tracefs directory after requirements are checked.

## State And Persistence
The template has no state. Real tests may mutate tracefs and should rely on harness cleanup helpers.

## Dependencies And Integration Points
It integrates with `ftracetest` metadata parsing and `test.d/functions` helper API.

## Risks
Leaving the template unchanged as a `.tc` would create a meaningless passing test. Requirement strings need correct `:tracer` or `:README` suffixes to avoid false skips/failures.

## Test Signals
For a real test derived from it, a correct description appears in harness output and the chosen exit helper maps to the intended result code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/test.d/template -->
