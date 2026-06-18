## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas-debug.c

### Purpose
`vas-debug.c` exposes PowerNV VAS instance/window state through debugfs.

### Important APIs, Types, And Functions
Functions include `cop_to_str()`, `info_show()`, `hvwc_show()`, `print_reg()`, `vas_init_dbgdir()`, `vas_instance_init_dbgdir()`, `vas_window_init_dbgdir()`, and `vas_window_free_dbgdir()`.

### Control Flow
VAS instance creation calls `vas_instance_init_dbgdir()`, which lazily creates the root `vas` debugfs directory and then a per-instance directory. Window allocation calls `vas_window_init_dbgdir()` to create `w<id>/info` and `w<id>/hvwc`. The seq-file show callbacks lock `vas_mutex`, verify the window remains mapped, and print metadata or HV window-context registers.

### State, Persistence, And Dependencies
State is the root debugfs dentry, per-instance names/directories, and per-window debug names/directories. Output reflects live MMIO register state, not persisted software state.

### Integration Points
It depends on `vas.h` register offset macros and `read_hvwc_reg()`, and is called from VAS instance/window lifecycle code.

### Risks
Debugfs reads race window close unless `vas_mutex` is respected. A failed debugfs or name allocation silently skips observability. Register reads require mapped HVWC context.

### Test Signals
Opening and closing VAS windows, reading debugfs `info` and `hvwc`, and concurrent close/read stress are useful signals.
