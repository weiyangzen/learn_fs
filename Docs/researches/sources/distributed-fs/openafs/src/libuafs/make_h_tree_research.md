## sources/distributed-fs/openafs/src/libuafs/make_h_tree

Purpose: Generates a local `h/` include tree for libuafs userspace builds by mapping legacy `#include <h/foo.h>` references to stubs including `<sys/foo.h>`.

Important logic: Creates directory `h`, scans `*.c` files in each argument directory, extracts include names matching `h/<name>`, sorts and uniques them, and writes `h/<name>` containing `#include <sys/<name>>`.

Control flow: The script runs with `sh -e`, so command failures abort. For each source directory argument, it uses `cat`, `sed`, `sort`, and `uniq`, then writes one stub per discovered header.

State and persistence: Creates and populates `h/` in the current working directory. Existing `h` will make `mkdir h` fail under `-e`, so callers usually remove it first.

Dependencies and integration: Called by `Makefile.common` target `h` after removing any existing `h`. Supports compiling kernel-ish AFS sources in userspace without changing their include names.

Risks: Uses command substitution over unquoted header names, though extracted names exclude slash and quotes. It scans only `.c` files directly under each provided directory. It overwrites stubs with `>` and assumes no conflicting real files in `h/`.

Test signals: Given sample C files with `#include <h/socket.h>`, verify `h/socket.h` contains `#include <sys/socket.h>`. Check failure on pre-existing `h`, multi-directory duplicate handling, and no-output behavior for sources without matching includes.
