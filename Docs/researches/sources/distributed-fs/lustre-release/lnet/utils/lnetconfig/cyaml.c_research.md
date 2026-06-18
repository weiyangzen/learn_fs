# sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/cyaml.c

## Purpose
Implements a small cYAML tree wrapper around libyaml for Lustre LNet configuration tools. It parses block-style YAML into an n-tree, supports lookup/traversal/free, builds trees programmatically, dumps/prints YAML, and creates structured error output.

## Important APIs And Functions
Public APIs include `cYAML_load()`, `cYAML_build_tree()`, `cYAML_print_tree()`, `cYAML_print_tree2file()`, `cYAML_dump()`, `cYAML_free_tree()`, lookup helpers, constructors, insertion helpers, `cYAML_clean_usr_data()`, and `cYAML_build_error()`. Internal parser state uses `cYAML_tree_node`, token handler dispatch, and a list-stack of `cYAML_ll` nodes.

## Control Flow
`cYAML_build_tree()` initializes a libyaml parser from a path, memory block, or stdin. `cYAML_parser_to_tree()` scans tokens, dispatches handlers, and builds nodes with stack-managed parent/child state. It supports block mappings and block sequences while rejecting flow collections, aliases, anchors, tags, and directives. Scalars are typed as null, bool, number, or string. Dump/print walks the tree and appends formatted YAML to a dynamically grown buffer.

## State And Persistence
Trees and dump buffers are heap allocated and caller-owned. Optional `cy_user_data` is caller-managed and can be cleaned with a callback. No global mutable parser state exists.

## Dependencies And Integration Points
Uses libyaml, libc, math, `liblnetconfig.h`, libcfs user-space list helpers, and `cyaml.h`. Built into `liblnetconfig.la`.

## Risks
`ensure()` reallocates on every non-null append due to an always-true size comparison, which is inefficient. `cYAML_dump(NULL)` leaks its initially allocated buffer. `print_string()` temporarily mutates multiline string contents. Unsupported but valid YAML constructs fail. Some `strdup()` results are unchecked.

## Test Signals
Parse nested maps/sequences, scalar typing including hex and booleans, unsupported flow YAML, malformed input, file-open errors, error-tree generation, lookup differences, sequence iteration, user-data cleanup, dump round trips, and allocation failures where possible.
