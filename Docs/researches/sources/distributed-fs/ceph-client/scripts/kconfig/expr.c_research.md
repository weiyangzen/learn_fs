# sources/distributed-fs/ceph-client/scripts/kconfig/expr.c

## Purpose

`expr.c` implements kconfig's expression graph: allocation/interning, equality and simplification, dependency transformation, value calculation, cache invalidation, and printable forms for diagnostics and help text.

## Important APIs, Types, and Functions

Allocation APIs are `expr_alloc_symbol()`, `expr_alloc_one()`, `expr_alloc_two()`, `expr_alloc_comp()`, `expr_alloc_and()`, and `expr_alloc_or()`, all backed by `expr_lookup()` and `expr_hashtable`. Simplification and dependency APIs include `expr_eq()`, `expr_eliminate_eq()`, `expr_eliminate_dups()`, `expr_transform()`, `expr_contains_symbol()`, `expr_depends_symbol()`, and `expr_trans_compare()`. Evaluation and output APIs include `expr_calc_value()`, `expr_invalidate_all()`, `expr_print()`, `expr_fprint()`, `expr_gstr_print()`, and `expr_gstr_print_revdep()`.

## Control Flow

Expressions are immutable-ish interned nodes keyed by type and child pointers. Parser/menu code constructs raw trees, `expr_transform()` rewrites boolean comparisons and pushes negations through compound expressions, and `expr_eliminate_dups()` repeatedly joins redundant operands until no transformation occurred. `expr_calc_value()` lazily evaluates tristate logic or relational comparisons, using cached `val` until invalidated. Printing recurses with precedence tracking so generated text is both compact and correctly parenthesized.

## State and Persistence Behavior

The file owns `expr_hashtable` and cached expression values. There is no file persistence, but cached values are semantic state; callers must use `expr_invalidate_all()` after user/default values change. `trans_count` is a process-global simplification counter used during transformations and temporarily restored by equality checks.

## Dependencies and Integration Points

It integrates with `symbol.c` via `sym_calc_value()` and `sym_get_string_value()`, with `menu.c` for dependency propagation and automatic submenu creation, and with UI/help code through `expr_gstr_print*()`. It relies on `hash.h`, `xalloc.h`, `internal.h`, and the types declared in `expr.h`.

## Risks and Edge Cases

The intern table makes pointer identity meaningful for equality and hash lookup. Because nodes are reused, callers should treat expressions as persistent trees and rebuild rather than mutate fields. Cached values can go stale if invalidation is missed. Numeric comparison falls back to string comparison when parsing fails, which is correct for mixed string cases but can surprise callers expecting strict numeric validation. The simplifier has special tristate/boolean assumptions; incorrect symbol typing can change dependency results.

## Test Signals

Useful tests cover boolean and tristate simplifications, De Morgan rewrites, duplicate elimination, choice dependency comparisons, relational comparisons for signed/unsigned/string values, cache invalidation after `conf_read_simple()`, and printed expression precedence.
