# sources/distributed-fs/ceph-client/tools/include/nolibc/getopt.h

## Purpose
Implements a compact POSIX-like `getopt` parser for nolibc command-line tools.

## APIs, Types, and Functions
Defines weak data symbols `optarg`, `optind`, `opterr`, and `optopt`, plus `getopt(int argc, char * const argv[], const char *optstring)`. It forward-declares `stderr` and `fprintf` to report invalid options.

## Control Flow, State, and Persistence
`getopt()` tracks the current argv index and character offset in static parser state, handles clustered short options, required option arguments, `--` termination, and error reporting. Persistent state is the standard getopt globals plus internal scan position.

## Dependencies and Integration
Depends on nolibc stdio for diagnostics and conventional argv layout from `crt.h`. It integrates with small tools that parse short options without pulling in libc.

## Risks and Test Signals
Risks include limited GNU-extension support, global parser state not being thread-safe, and behavior differences around optional arguments or argument permutation. Test signals are clustered options, missing arguments, `--`, invalid-option reporting, optind reset behavior, and silent mode with leading `:` or `opterr=0`.
