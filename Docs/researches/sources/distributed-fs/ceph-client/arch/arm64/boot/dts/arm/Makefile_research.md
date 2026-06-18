<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/arm/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/arm/Makefile

### Purpose
This Makefile registers Arm reference, model, and development-platform DTBs for ARM64 builds.

### Important APIs, Types, And Functions
It exports 19 DTB targets under `CONFIG_ARCH_VEXPRESS`, including Foundation models, Juno variants, RTSM/FVP models, Corstone1000, Morello, and Zena CSS. The file is pure Kbuild metadata.

### Control Flow
When the Versatile Express architecture option is enabled, Kbuild compiles all listed model/platform DTS files during `make dtbs`.

### State, Persistence, And Dependencies
Generated DTBs are build artifacts. The file depends on same-directory DTS sources, DTC, and Kconfig selection of `CONFIG_ARCH_VEXPRESS`.

### Integration Points
These DTBs support Arm reference platforms used heavily for validation and CI. They integrate with generic Arm platform, PSCI, GIC, SCMI, and model-specific device descriptions.

### Risks
Because these DTBs are often used in CI and emulator flows, target breakage can block broad arm64 test coverage. Some variants encode subtle PSCI/GIC/SCMI differences that must not be collapsed accidentally.

### Test Signals
Build the DTBs with `CONFIG_ARCH_VEXPRESS=y`, run DTC/dt-schema checks, and boot smoke-test FVP/Juno/Corstone/Morello targets where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/arm/Makefile -->
