# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/thp_settings.c

Purpose: shared utility implementation for reading, writing, saving, restoring, and stacking transparent hugepage sysfs settings used by THP-related selftests.

Important APIs and functions: file helpers `read_file()`, `read_num()`, `write_num()`; THP wrappers `thp_read_string()`, `thp_write_string()`, `thp_read_num()`, `thp_write_num()`; state APIs `thp_read_settings()`, `thp_write_settings()`, `thp_save_settings()`, `thp_restore_settings()`, `thp_push_settings()`, `thp_pop_settings()`; supported-order detection and enabled checks.

Control flow and state: reads parse bracketed active values from `/sys/kernel/mm/transparent_hugepage`, including per-order directories and khugepaged tunables. Writes mirror the struct back to sysfs. Static state holds saved settings, a small stack, and optional read-ahead path.

Dependencies and risks: depends on `vm_util.h` `write_file()`, THP sysfs layout, and `thp_settings.h`. Parsing assumes fixed bracketed sysfs format; abrupt exits after writes can leave host THP settings changed.
