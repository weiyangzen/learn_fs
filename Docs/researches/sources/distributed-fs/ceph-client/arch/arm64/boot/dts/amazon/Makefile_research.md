## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amazon/Makefile

### Purpose
Declares Amazon Annapurna Labs Alpine ARM64 DTB targets.

### Important APIs, Types, And Functions
Adds `alpine-v2-evp.dtb` and `alpine-v3-evp.dtb` under `CONFIG_ARCH_ALPINE`.

### Control Flow
Kbuild builds the two evaluation platform DTBs when Alpine platform support is enabled.

### State, Persistence, And Dependencies
Build metadata only; depends on matching DTS files and Alpine platform Kconfig.

### Integration Points
Includes Amazon Alpine boards in ARM64 DTB builds and boot packaging.

### Risks
Board coverage is limited to listed EVP variants; new DTS files require explicit target additions.

### Test Signals
Build with `ARCH_ALPINE`, run `dtc` validation, and boot-test Alpine v2/v3 DTBs where hardware or emulation is available.
