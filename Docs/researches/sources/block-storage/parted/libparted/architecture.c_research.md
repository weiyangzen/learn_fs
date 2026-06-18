# File Research: sources/block-storage/parted/libparted/architecture.c

This file owns the global architecture dispatch pointer used by libparted.

Key behavior:
- Defines `const PedArchitecture* ped_architecture`.
- `ped_set_architecture()` initializes the global pointer exactly once.
- Compile-time platform selection:
  - `linux` selects `ped_linux_arch`.
  - `__BEOS__` selects `ped_beos_arch`.
  - All other builds select `ped_gnu_arch`.

Research notes:
- This is the runtime bridge between common code like `device.c` and the platform-specific operation tables.
- The function is idempotent but not synchronized; initialization assumes libparted setup is serialized.
