# sources/compression/lz4/tests/test_install.sh

## Purpose
This shell test checks that uppercase and lowercase Make install variables produce identical installation and uninstallation results. It covers variables such as `PREFIX`, `LIBDIR`, `BINDIR`, and man/pkg-config paths.

## Important Control Flow
The script selects `make` or `gmake` based on `uname`, then for `install` and `uninstall` loops over a variable list. For each variable it installs into two separate `DESTDIR` roots using uppercase and lowercase forms, compares the trees with `diff -r`, and after uninstall asserts the lowercase tree contains no files.

## State, Dependencies, and Integration
It depends on an external `lz4_root` environment variable, Make/gmake, `diff`, `find`, `tr`, and shell command substitution. Temporary roots are under the current directory as `tmp-lower-*` and `tmp-upper-*`.

## Risks and Test Signals
The test provides packaging compatibility signals for Makefile variable aliases. It is sensitive to missing `lz4_root`, platform-specific make selection, and install side effects. It compares entire trees, so benign metadata/order differences are not an issue but generated content differences fail.
