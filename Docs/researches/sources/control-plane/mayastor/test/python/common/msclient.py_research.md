# sources/control-plane/mayastor/test/python/common/msclient.py

## Purpose
Wrapper around the `io-engine-client` CLI for tests that inspect Mayastor controller state through command-line output.

## Important APIs, Types, And Functions
Defines `MayastorClient.__call__`, `with_url`, `with_json_output`, `with_default_output`, `with_verbose`, and `get_msclient`. Calls include `-o <output>`, optional `-q`, `-v`, and backend URL arguments.

## Control Flow
`get_msclient` locates the binary under `mayastor_target_dir()`. Invoking the client constructs an argv list, executes it via `subprocess.check_output(shell=False)`, decodes UTF-8 output, and parses JSON when requested.

## State And Persistence
The client stores mutable configuration such as URL and output mode. The CLI may mutate Mayastor state depending on commands, but this wrapper itself persists nothing.

## Dependencies And Integration Points
Depends on `SRCDIR`/`IO_ENGINE_DIR` through `mayastor_target_dir`, `subprocess`, and JSON output conventions. Used by CLI controller tests to inspect NVMe controller list/stats.

## Risks
Missing build artifacts cause immediate `FileNotFoundError`. Mutating builder methods return `self`, so reuse across tests can leak output mode or URL settings if not scoped carefully.

## Test Signals
JSON CLI output matching gRPC-created controllers validates the CLI, controller reporting, and target URL routing.
