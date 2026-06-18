# sources/distributed-fs/ceph-client/arch/mips/include/asm/prom.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/prom.h

### Purpose
`prom.h` declares MIPS firmware/device-tree setup hooks and machine-name accessors. It supports Open Firmware/device-tree boot when `CONFIG_USE_OF` is enabled and provides no-op initialization otherwise.

### Important APIs, Types, And Functions
Exports include `device_tree_init`, forward `struct boot_param_header`, `__dt_setup_arch`, `__dt_register_buses`, `mips_get_machine_name`, and `mips_set_machine_name`.

### Control Flow
Early boot calls `device_tree_init` and architecture setup to consume the boot parameter header and register buses. Non-OF builds compile `device_tree_init` to an empty inline, leaving platform-specific boot paths to supply machine data.

### State, Persistence, Dependencies, And Integration
State includes the boot firmware's DT blob, registered platform buses, and an in-kernel machine-name string. Dependencies under OF include bug, I/O, type, and bootinfo headers. Integration is early architecture setup, platform device enumeration, and user-visible machine identity.

### Risks
DT pointers are early-boot memory and must remain valid until unflattened. Bus registration names must match platform driver expectations. Non-OF builds can silently skip DT setup, so call sites must not assume devices appear.

### Test Signals
Boot OF and non-OF MIPS configs, verify `/proc/device-tree` or platform devices, check machine name reporting, and build both branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/prom.h -->
