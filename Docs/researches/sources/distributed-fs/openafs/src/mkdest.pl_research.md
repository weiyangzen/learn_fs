# sources/distributed-fs/openafs/src/mkdest.pl

Purpose: interactive Perl helper for creating an AFS platform build tree with symlinks back to the source tree.

Important APIs/types/functions: top-level script asks for confirmation, creates `dest` and `obj`, and recursively processes source directories through `dodir`. `lastcomp` derives a source component relative to `$srcdir`.

Control flow: after user confirms `y`, it creates build directories, enters `obj`, then `dodir` traverses `$srcdir`. For each directory it creates `DEST` and `SRC` symlinks, symlinks non-directory files to `SRC/<name>`, skips `.`/`..`/`RCS`, creates matching subdirectories, and recurses.

State and persistence: creates filesystem directories and symbolic links in the current working directory. Does not modify source files.

Dependencies/integration: uses Perl built-ins and shell `ln -s` through `system`. It assumes `$ENV{PWD}` reflects the target platform tree.

Risks and test signals: unquoted `system` strings and simplistic path parsing can misbehave with spaces or shell metacharacters. It is interactive and old-style Perl. Correct output is a mirrored object tree with `SRC` and `DEST` links.
