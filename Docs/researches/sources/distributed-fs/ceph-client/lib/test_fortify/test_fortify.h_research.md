
# sources/distributed-fs/ceph-client/lib/test_fortify/test_fortify.h

## Purpose

This shared header is the common harness for all fortify compile-time tests in the directory. Each small source defines a `TEST` macro before including it.

## Important APIs, Types, And Functions

It includes kernel, printk, slab, and string headers. It defines `__BUF_SMALL`, `__BUF_LARGE`, `struct fortify_object`, literal strings, shared global arrays (`small_src`, `large_src`, `small`, `large`), a global `instance`, and `size`. `do_fortify_tests()` initializes the buffers and struct field with `memset()` and then expands `TEST`.

## Control Flow And State

There is no module entry point here. The harness creates compiler-visible object sizes and initializations so each test expression is compiled in a consistent context. The global symbols are intentionally simple and fixed-size to make fortify diagnostics deterministic.

## Dependencies And Integration Points

It integrates with `test_fortify.sh` and the Makefile's per-source compile rules. The `TEST` macro contract is the extension point used by every C file in this directory.

## Risks And Test Signals

Changing buffer sizes, literal lengths, or the struct layout changes the expected overflow categories across every test. A valid signal is that each test expands to exactly one unsafe operation whose expected symbol is derivable from the source filename.
