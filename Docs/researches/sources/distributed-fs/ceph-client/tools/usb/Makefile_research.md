# sources/distributed-fs/ceph-client/tools/usb/Makefile

## Purpose

`tools/usb/Makefile` builds and installs the main Linux USB user-space tools in this tree: `testusb` and `ffs-test`.

## Important APIs, Types, and Targets

Important variables are `bindir`, `srctree`, `CFLAGS`, `LDFLAGS`, `ALL_TARGETS`, and `ALL_PROGRAMS`. Targets include `all`, per-program links for `$(OUTPUT)testusb` and `$(OUTPUT)ffs-test`, `clean`, `install`, and `FORCE`.

## Control Flow and Data Flow

The Makefile locates `srctree` when unset, disables built-in rules with `MAKEFLAGS += -r`, exports build variables, includes `tools/build/Makefile.include`, recursively builds object aggregates in `testusb` and `ffs-test` subdirectories, then links final binaries with pthread support.

## State and Persistence Behavior

Build artifacts are written under `$(OUTPUT)` when set, otherwise the current directory. `install` copies binaries into `$(DESTDIR)$(bindir)`. `clean` removes programs and object/dependency/cmd files.

## Dependencies and Integration Points

It depends on the kernel tools build framework, compiler/linker variables, pthread, `tools/include`, and subdirectory build descriptions. It is invoked by kernel tools build targets and manual `make` in `tools/usb`.

## Risks and Edge Cases

Incorrect `srctree` or `OUTPUT` breaks include paths and artifact placement. The `clean` find expression depends on operator precedence and may be surprising. Link flags are globally appended with `-lpthread`. Installing requires destination permissions.

## Test Signals

Build tests should run `make -C tools/usb`, verify both binaries exist under `OUTPUT`, run `make clean`, and test `DESTDIR` installation layout.
