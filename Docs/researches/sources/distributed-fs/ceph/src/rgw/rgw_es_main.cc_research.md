# sources/distributed-fs/ceph/src/rgw/rgw_es_main.cc

## Purpose
Provides a small utility executable that compiles an RGW Elasticsearch query expression and prints its JSON representation.

## Important APIs, types, and functions
`main()` initializes Ceph global context, reads the expression from `argv[1]` or defaults to `age >= 30`, constructs `ESQueryCompiler`, sets field aliases, generic entity type map, and custom metadata type map, then calls `compile()` and emits JSON via `JSONFormatter`.

## Control flow
Initialization happens first, then compiler setup, compile validation, error print/`EINVAL` return on failure, or JSON serialization on success.

## State and persistence
No persistent state is modified. The process only reads command-line args and prints to stdout/stderr.

## Dependencies and integration points
Uses Ceph global init/argparse/json helpers and `rgw_es_query.h`. The utility helps test/debug ES query parsing outside the main RGW daemon.

## Risks and test signals
Risks include uncaught exceptions from compiler/global init, default expression hiding missing args, and alias/type-map drift from production code. Tests should run valid/invalid expressions, alias fields, custom metadata fields, date/int typing, and compare emitted JSON with expected query trees.
