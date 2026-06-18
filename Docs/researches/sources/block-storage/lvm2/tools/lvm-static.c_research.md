# File Research: sources/block-storage/lvm2/tools/lvm-static.c

This file provides the entry point for the statically linked LVM binary.

Functions:
- `main()` calls `init_is_static(1)` to mark the process as static, then delegates all command-line handling to `lvm2_main(argc, argv)`.
- `lvm_shell()` is provided as a stub returning `0`, with unused parameters marked, presumably because the static build does not provide interactive shell support here.

Role:
- This is not command logic; it is build/entry-point glue for the static executable.
- It includes `tools.h` and `lvm2cmdline.h`, then relies on the shared LVM command-line dispatcher.
- Licensing differs from most command files in this group: this file states GPL v2, while the other listed LVM command files state LGPL v2.1.
