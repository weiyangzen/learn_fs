# sources/control-plane/mayastor/scripts/js-check.sh

Purpose: semistandard formatter/linter wrapper for gRPC JavaScript test files.

Important APIs/types/functions: filters incoming paths to those under `test/grpc/`, strips the prefix, and runs `npx semistandard --fix` in the test/grpc directory.

Control flow: loops arguments, accumulates relative grpc test paths, and only invokes semistandard if any are found.

State/persistence: modifies matching JS files in place because `--fix` is enabled.

Dependencies/integration: likely used by pre-commit/CI formatting workflows for JS tests.

Risks: unquoted variables and backticks can mishandle spaces. Auto-fixing in a check script can dirty the worktree unexpectedly.

Test signals: after running, selected gRPC JS tests should satisfy semistandard style.
