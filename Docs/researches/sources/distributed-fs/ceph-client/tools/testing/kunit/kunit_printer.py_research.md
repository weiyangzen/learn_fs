<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_printer.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_printer.py

## Purpose

`kunit_printer.py` is the small output abstraction used by the KUnit Python tooling. It wraps a text stream with optional printing, terminal-aware ANSI coloring, and timestamped status output so parser, runner, and test code can share formatting behavior without each caller probing stdout directly.

## Important APIs, Types, and Functions

The main API is `Printer(print=True, output=sys.stdout)`. Its `print()` method writes a message only when printing is enabled, `print_with_timestamp()` prefixes the current local time as `HH:MM:SS`, and `red()`, `yellow()`, and `green()` conditionally wrap text in bold ANSI color escapes. `_color()` centralizes the `isatty()`-gated escape behavior, while `color_len()` returns the escape overhead by coloring an empty string. The module exports `stdout` for normal console output and `null_printer` for silent consumers.

## Control Flow

Construction decides whether color is possible: disabled printers never color, enabled printers color only if the output object reports `isatty()`. Printing then flows through `Printer.print()` so callers can pass a real or mock printer without branching. Color helpers are pure string transforms when color is enabled and no-ops otherwise.

## State and Persistence Behavior

State is limited to `_output`, `_print`, and `_use_color` on each `Printer` instance. The module has no persistent files or process-global counters beyond the two singleton printer instances. Timestamps are generated at call time and are not retained.

## Dependencies and Integration Points

It depends only on `datetime`, `sys`, and Python typing. It integrates with KUnit parser and tool tests, where `Printer.print` is mocked to assert user-visible summaries and error text. The `stdout` singleton is passed into parser calls in `kunit_tool_test.py`.

## Risks and Edge Cases

The constructor parameter named `print` shadows the builtin inside the method scope, though the method still calls the builtin from its own scope. Any output object used here must implement `isatty()` if color decisions are needed. `color_len()` is tied to the current color implementation and can return zero when color is disabled.

## Test Signals

Useful signals are parser tests that mock `Printer.print`, terminal versus non-terminal runner tests, and direct checks that disabled printers suppress writes and color escapes. Color behavior should be validated with fake output objects returning both `True` and `False` from `isatty()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_printer.py -->
