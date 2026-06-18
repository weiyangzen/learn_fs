<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles-negative/env_no_value/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles-negative/env_no_value/Dockerfile

## Purpose
Negative parser fixture that intentionally exercises Dockerfile rejection behavior or empty-input handling. The fixture has 3 lines and 2 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM busybox`; `ENV PATH`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 2 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is intentional invalid input: changing parser leniency can flip this fixture from error to success, weakening negative coverage.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles-negative/env_no_value/Dockerfile -->
