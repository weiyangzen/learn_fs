<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/tf2/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/tf2/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 23 lines and 20 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM ubuntu:12.04`; `EXPOSE 27015`; `EXPOSE 27005`; `EXPOSE 26901`; `EXPOSE 27020`; `RUN apt-get update && apt-get install libc6-dev-i386 curl unzip -y`; `RUN mkdir -p /steam`; `RUN curl http://media.steampowered.com/client/steamcmd_linux.tar.gz | tar vxz -C /steam`; `ADD ./script /steam/script`; `RUN /steam/steamcmd.sh +runscript /steam/script`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 20 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/tf2/Dockerfile -->
