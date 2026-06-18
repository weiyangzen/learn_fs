# sources/distributed-fs/ceph-client/drivers/acpi/debugfs.c

## Purpose
Creates the top-level ACPI debugfs directory used by ACPI debug and diagnostic code.

## Important APIs, Types, And Functions
Exports `struct dentry *acpi_debugfs_dir` with `EXPORT_SYMBOL_GPL`. `acpi_debugfs_init()` creates the `"acpi"` directory at debugfs root using `debugfs_create_dir()`.

## Control Flow
`acpi_debugfs_init()` is called from ACPI core initialization in `bus.c` after ACPI scan and EC setup. It assigns the returned dentry to the exported global. There is no teardown path here.

## State And Persistence
The only state is the global debugfs dentry pointer. Debugfs contents are volatile and exist only while debugfs is mounted and the kernel is running.

## Dependencies And Integration Points
Depends on `CONFIG_DEBUG_FS` infrastructure through `linux/debugfs.h` and ACPI internal init ordering. Other ACPI components can create files beneath `acpi_debugfs_dir`.

## Risks
Callers must tolerate debugfs being unavailable or directory creation returning an error-like dentry depending on debugfs configuration. Because the symbol is global, consumers should avoid assuming init has run before ACPI core setup.

## Test Signals
On debugfs-enabled systems, `/sys/kernel/debug/acpi` should exist after ACPI initialization. Consumers creating child files under `acpi_debugfs_dir` provide indirect coverage.
