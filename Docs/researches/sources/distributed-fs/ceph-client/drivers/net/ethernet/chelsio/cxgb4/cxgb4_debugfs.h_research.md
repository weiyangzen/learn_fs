# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_debugfs.h

## Purpose

`cxgb4_debugfs.h` declares the small shared interface for the `cxgb4` debugfs implementation. It provides the debugfs entry descriptor, the reusable `seq_tab` table abstraction, a hex conversion helper, and the public functions used by adapter setup and other driver modules to register debugfs files or open adapter memory views.

## Important APIs And Types

- `struct t4_debugfs_entry` describes one debugfs file: name, file operations, mode, and a small `data` byte that is added to the adapter pointer as `i_private`. The data byte is used to distinguish mailbox number, trace index, CIM queue id, or memory index.
- `struct seq_tab` stores a reusable table backing buffer for `seq_file` output. It contains a row formatter callback, row count, row width, header flag, and flexible-array row data.
- `hex2val()` converts a hexadecimal character to its numeric value using `isdigit()` and `tolower()`. Callers are expected to validate with `isxdigit()` first.
- `seq_open_tab()` allocates and initializes a `seq_tab` private buffer for table-style debugfs files.
- `t4_setup_debugfs()` creates the adapter's debugfs files.
- `add_debugfs_files()` registers an array of `struct t4_debugfs_entry` under an adapter debugfs root.
- `mem_open()` prepares memory-like debugfs file reads and flushes firmware cache state in the implementation.

## Control Flow

Driver setup calls `t4_setup_debugfs(adap)`. That implementation builds arrays of `struct t4_debugfs_entry` and calls `add_debugfs_files()`. Each entry's `data` byte becomes an offset from the adapter pointer in `debugfs_create_file()`, allowing one `file_operations` implementation to serve multiple mailbox, trace, or queue files.

Table-style debugfs implementations call `seq_open_tab()` from their open routines, fill `seq_tab->data` with hardware state, then rely on shared seq operations in the `.c` file to iterate rows and call the provided `show()` callback.

## State And Persistence

This header defines no global state. `struct seq_tab` instances are per-open seq private allocations and are freed by `seq_release_private()`. `struct t4_debugfs_entry` arrays are usually static in the implementation and describe registration metadata only.

## Dependencies And Integration Points

- Includes `<linux/export.h>` and relies on Linux VFS/debugfs/seq_file types supplied through surrounding includes.
- `struct adapter` is referenced but not defined here; consumers include this header in contexts where the main `cxgb4` adapter type is visible.
- `hex2val()` depends on ctype helpers being available to the translation unit.
- The functions declared here are implemented in `cxgb4_debugfs.c` and used by the main driver setup path and any module that contributes debugfs files.

## Risks And Edge Cases

- `hex2val()` does not reject non-hex characters. It must only be called after validation, as `rss_key_write()` does.
- The `data` field is only `unsigned char`, so it is suitable for small selectors but not large offsets.
- Pointer arithmetic on `(void *)adap + data` is a GNU C extension used by this driver; new users should preserve the local convention and keep offsets small and intentional.
- `seq_tab` row width and row count must match the amount of data filled by the open routine. A mismatch can produce misformatted output or out-of-bounds interpretation.

## Test Signals

- Compile-test all translation units including this header with debugfs enabled.
- Exercise at least one `seq_open_tab()` user per table shape to confirm header flag, row count, and width behavior.
- Validate `hex2val()` callers reject invalid characters before conversion.
- Confirm newly added `t4_debugfs_entry` users pass correct file modes and selector values.
