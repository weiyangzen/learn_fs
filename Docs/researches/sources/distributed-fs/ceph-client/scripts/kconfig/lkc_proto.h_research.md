# sources/distributed-fs/ceph-client/scripts/kconfig/lkc_proto.h

## Purpose

`lkc_proto.h` centralizes function prototypes for config persistence, symbol manipulation, and expression printing that are consumed through `lkc.h`.

## Important APIs, Types, and Functions

It declares `conf_parse()`, `conf_read()`, `conf_read_simple()`, `conf_write_defconfig()`, `conf_write()`, `conf_write_autoconf()`, dirty/message callbacks, `conf_errors()`, symbol lookup/search/value setters, choice setters, string validation, changeability checks, menu lookup helpers, `sym_get_string_value()`, `prop_get_type_name()`, and `expr_print()`.

## Control Flow

No executable flow exists in the header. It defines the callable surface used by command-line and UI frontends to parse Kconfig, read/write configuration, search symbols, and mutate user selections.

## State and Persistence Behavior

The declared functions operate on the global kconfig symbol/menu/expression state and the `.config`/generated-file state owned by `confdata.c`.

## Dependencies and Integration Points

It requires types from `expr.h` and `stdarg.h`. It is included by `lkc.h`, making it a central integration point between parser, symbol, expression, persistence, and frontend implementations.

## Risks and Edge Cases

Prototype drift breaks all tools at compile time. Several setters return `bool` for success/failure and frontends must honor those results to avoid displaying invalid state as accepted. `conf_parse()` is declared here but implemented outside this subset.

## Test Signals

Compile coverage, frontend load/save/edit paths, regex symbol search, and invalid string/tristate setter behavior are the useful signals.
