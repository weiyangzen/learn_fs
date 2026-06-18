## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amd/Makefile

### Purpose
Declares AMD-related ARM64 DTB targets for Pensando Elba and AMD Seattle platforms.

### Important APIs, Types, And Functions
Adds `elba-asic.dtb` under `CONFIG_ARCH_PENSANDO` and `amd-overdrive-rev-b0.dtb`/`amd-overdrive-rev-b1.dtb` under `CONFIG_ARCH_SEATTLE`.

### Control Flow
Kbuild builds DTBs according to the selected platform symbols.

### State, Persistence, And Dependencies
Build metadata only; depends on the DTS files for Elba ASIC and AMD Overdrive revisions.

### Integration Points
Feeds ARM64 `dtbs` with AMD/Pensando platform device trees.

### Risks
Separate config gates mean platform symbol drift can silently omit targets. Hardware revisions must map to correct DTB names.

### Test Signals
Build DTBs with `ARCH_PENSANDO` and `ARCH_SEATTLE`, validate `dtc` output, and boot-test on matching board revisions.
