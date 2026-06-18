<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles-negative/only_comments/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles-negative/only_comments/Dockerfile

## Purpose
Negative parser fixture that intentionally exercises Dockerfile rejection behavior or empty-input handling. The fixture has 3 lines and 0 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: empty/comment-only Dockerfile input.

## Control Flow
The fixture has no executable Dockerfile instructions; parser tests use it to verify empty/comment-only inputs fail with the expected no-instructions path.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is intentional invalid input: changing parser leniency can flip this fixture from error to success, weakening negative coverage.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles-negative/only_comments/Dockerfile -->
