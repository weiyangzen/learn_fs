# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/page_frag/Makefile

## Purpose

This Makefile builds the `page_frag_test.ko` kernel module used to test page fragment cache behavior.

## Important APIs, Types, and Functions

It defines `PAGE_FRAG_TEST_DIR`, `KDIR`, verbosity variable `Q`, `MODULES = page_frag_test.ko`, and `obj-m += page_frag_test.o`. Targets are `all` and `clean`, both delegating to the kernel build system with `make -C $(KDIR) M=$(PAGE_FRAG_TEST_DIR)`.

## Control Flow

`all` builds external modules from the page_frag test directory. `clean` runs the kernel module clean target for the same directory. `KDIR` defaults to the kernel tree root relative to the selftests directory or to `$(O)` when an out-of-tree output directory is provided.

## State and Persistence Behavior

The Makefile creates kernel module build artifacts in the module directory or configured output tree and removes them on `clean`. It does not run the module.

## Dependencies and Integration Points

It depends on a configured kernel build tree and kbuild external module support. It integrates `page_frag_test.c` into the mm selftest build flow as a loadable module.

## Risks and Edge Cases

Incorrect `KDIR` or `O` settings cause build failures. Module build products are generated files outside the source logic. Verbosity is controlled by `V=1`.

## Test Signals

Successful `make` produces `page_frag_test.ko`; successful `clean` removes module artifacts.
