## sources/distributed-fs/ceph-client/arch/mips/ralink/bootrom.c

### Purpose
This debugfs helper exposes the Ralink boot ROM contents through a read-only `bootrom` debugfs file.

### Important APIs, Types, And Functions
`membase` points at `KSEG1ADDR(BOOTROM_OFFSET)`. `bootrom_show()` writes `BOOTROM_SIZE` bytes to the seq file. `DEFINE_SHOW_ATTRIBUTE(bootrom)` generates file operations. `bootrom_setup()` creates the debugfs file at postcore init.

### Control Flow
When debugfs support includes this object, `postcore_initcall()` creates `/sys/kernel/debug/bootrom`. Reads stream the fixed boot ROM range.

### State, Persistence, And Dependencies
State is a fixed uncached KSEG1 pointer and the debugfs dentry. Dependencies include debugfs, seq_file, and Ralink physical memory map.

### Integration Points
Selected by `CONFIG_DEBUG_FS` in the Ralink Makefile, useful for platform bring-up and ROM inspection.

### Risks
The file exposes raw boot ROM contents to users with debugfs access. It assumes the boot ROM physical range is valid on all selected Ralink SoCs.

### Test Signals
With debugfs mounted, reading `bootrom` should return exactly 0x8000 bytes and not fault on supported hardware.
