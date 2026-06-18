# sources/cloud-native/overlayfs-tools/fsck.c

Purpose: command-line front end for `fsck.overlay`, responsible for option parsing, opening layer directories, basic safety checks, running scan/fix, and producing fsck-style exit codes.

Important APIs/types/functions: global `struct ovl_fs ofs`, `flags`, `status`; `ovl_open_dirs`, `ovl_clean_dirs`, `ovl_basic_check_layer`, `ovl_basic_check_workdir`, `ovl_basic_check`, `parse_options`, `fsck_exit`, and `main`.

Control flow: parses `-o lowerdir=...,upperdir=...,workdir=...` plus repair policy flags `-p`, `-n`, `-y`, opens all layer directories with fd-limit adjustment, checks whether any layer is mounted, validates xattr/read-only/workdir constraints, calls `ovl_scan_fix`, cleans fds/path allocations, then maps status bits to fsck return values.

State and persistence: may modify filesystem metadata through `ovl_scan_fix` unless `-n` or mounted-blocking prevents it. Global flags and status drive repair policy and exit code.

Dependencies/integration: uses mount parsing from `mount.c`, filesystem constants from `overlayfs.h`, scanning from `check.c`, xattr helpers from `lib.c`, and diagnostics from `common.c`.

Risks: option conflicts are fatal. Workdir/upperdir subdir checks use substring matching, which can false-positive on path prefixes. Fsck refuses mounted overlays unless no-change mode is used.

Test signals: fixture tests should cover option parsing, lower-only validation, mounted refusal, xattr unsupported layers, read-only layers, and exit status combinations.
