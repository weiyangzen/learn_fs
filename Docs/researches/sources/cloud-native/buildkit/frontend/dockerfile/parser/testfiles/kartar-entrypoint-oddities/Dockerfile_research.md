<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/kartar-entrypoint-oddities/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/kartar-entrypoint-oddities/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 7 lines and 7 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM ubuntu:14.04`; `LABEL maintainer James Turnbull "james@example.com"`; `ENV REFRESHED_AT 2014-06-01`; `RUN apt-get update`; `RUN apt-get --no-install-recommends install -y redis-server redis-tools`; `EXPOSE 6379`; `ENTRYPOINT [ "/usr/bin/redis-server" ]`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 7 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/kartar-entrypoint-oddities/Dockerfile -->
