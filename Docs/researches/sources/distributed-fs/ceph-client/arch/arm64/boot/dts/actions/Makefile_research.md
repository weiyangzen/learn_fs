## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/actions/Makefile

### Purpose
Declares Actions Semi ARM64 DTB targets.

### Important APIs, Types, And Functions
Adds `s700-cubieboard7.dtb` and `s900-bubblegum-96.dtb` under `CONFIG_ARCH_ACTIONS`.

### Control Flow
When `ARCH_ACTIONS` is enabled, Kbuild builds the listed DTBs from matching DTS files.

### State, Persistence, And Dependencies
State is build metadata; outputs are DTB files. Depends on the referenced DTS sources and the platform Kconfig symbol.

### Integration Points
Participates in ARM64 `dtbs` and FIT image generation for Actions boards.

### Risks
Renamed or removed DTS files leave stale DTB rules. Config gating must match the platform symbol.

### Test Signals
Build `make ARCH=arm64 dtbs CONFIG_ARCH_ACTIONS=y` and validate both DTBs compile with `dtc`.
