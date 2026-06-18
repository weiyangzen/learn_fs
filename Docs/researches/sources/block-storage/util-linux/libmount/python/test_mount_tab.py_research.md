# File Research: sources/block-storage/util-linux/libmount/python/test_mount_tab.py

Command-line smoke test harness for the Python `Table` and `Fs` bindings.

Key responsibilities:
- Parses mount table files with optional comment support.
- Installs a parser error callback.
- Iterates and prints filesystem records.
- Tests lookup by source, target, pair, mountpoint, and mounted-state checks.
- Tests copying an `Fs` object.

Important behavior:
- `create_table()` constructs an empty table, enables comments, sets `errcb`, and calls `parse_file()`.
- `--parse` prints intro/trailing comments and all entries via `next_fs()`.
- `--copy-fs` finds `/`, prints it, copies it, and prints the copy.
- `--find-forward` and `--find-backward` pass explicit iterator direction constants.

Dependencies:
- Depends on `pylibmount.Table`, `pylibmount.Fs`, parser callbacks, and real mount table files such as `/proc/self/mountinfo`.

Notable risks:
- Uses `mnt.Tab` in `test_is_mounted()`, but the binding type is registered as `Table`.
- Uses `ft.iter(...)`, but `functools` has no `iter` attribute; intended Python built-in `iter()` is used elsewhere.
- `test_find()` leaves `fs` undefined for unsupported lookup names.
