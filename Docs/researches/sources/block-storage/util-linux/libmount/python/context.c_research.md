# File Research: sources/block-storage/util-linux/libmount/python/context.c

## Scope

Implements the Python `libmount.Context` type wrapping `struct libmnt_context`.

## Behavior

- Defines object lifecycle: allocation initializes fields, init creates a libmount context, dealloc releases context-associated Python user data and frees the C context.
- Constructor accepts source, target, fstype, options, mount flags, type/options patterns, filesystem object, fstab table, and option mode.
- Provides Python methods for enabling/disabling mount behavior flags, canonicalization, helpers, mtab updates, swap matching, fake/force/lazy/loop delete/read-only/sloppy/verbose/fork modes.
- Exposes setters/getters for source, target, fstype, options, mount flags, user mount flags, fstab, mtab, fs object, status, syscall errno, and option mode.
- Wraps mount workflow calls: apply fstab, prepare/do/finalize mount, prepare/do/finalize umount, high-level mount/umount, helper initialization/options, and umount target lookup.
- Exposes state queries such as fake/force/lazy/nohelpers/nocanonicalize/restricted/syscall_called/helper_executed/tab_applied/parent/child/fork.
- Registers `ContextType` into the module as `Context`.

## Dependencies And Risks

- Depends on `pylibmount.h`, `FsType`, `TableType`, conversion helpers, and libmount `mnt_context_*` APIs.
- Reference ownership is manually coordinated through libmount userdata slots for fs/fstab/mtab Python objects.
- Several wrappers map positive libmount status/error returns to Python exceptions; callers are expected to inspect `status` after mount/umount errors.
- The file contains fragile binding code paths: argument parsing and status/query wrappers must be audited carefully because mismatched `PyArg_Parse*` logic or return-value conventions can turn libmount errors into Python API bugs.
