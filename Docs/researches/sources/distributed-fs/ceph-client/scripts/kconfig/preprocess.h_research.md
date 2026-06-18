# sources/distributed-fs/ceph-client/scripts/kconfig/preprocess.h

## Purpose
`preprocess.h` declares the Kconfig preprocessor interface used by the parser and scanner.

## Important APIs, Types, and Functions
`enum variable_flavor` defines `VAR_SIMPLE`, `VAR_RECURSIVE`, and `VAR_APPEND`, matching `:=`, `=`, and `+=`. The header forward-declares `struct gstr` and exposes `env_write_dep()`, `variable_add()`, `variable_all_del()`, `expand_dollar()`, and `expand_one_token()`.

## Control Flow
The header has no runtime control flow; it binds parser token actions and scanner token expansion to `preprocess.c`.

## State and Persistence
It exposes operations over process-global variable and environment-reference lists owned by `preprocess.c`.

## Dependencies and Integration Points
Included by `parser.y` and scanner/preprocessor consumers. It depends on the shared Kconfig string API only through a forward declaration.

## Risks and Edge Cases
Callers must free strings returned by `expand_dollar()` and `expand_one_token()`. Callers must also call `variable_all_del()` after parsing to avoid stale variables across parses in one process.

## Test Signals
The preprocessor pytest fixtures validate the public behavior behind this header.
