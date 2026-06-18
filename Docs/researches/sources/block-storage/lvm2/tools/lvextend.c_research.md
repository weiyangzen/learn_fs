# File Research: sources/block-storage/lvm2/tools/lvextend.c

This file is a minimal command wrapper for `lvextend`.

Function:
- `lvextend()` directly calls `lvresize_cmd(cmd, argc, argv)`.

Role:
- `lvextend` shares implementation with the general LV resize command path.
- All option parsing, validation, allocation, filesystem resize handling, and metadata updates are handled by `lvresize_cmd()` elsewhere.
