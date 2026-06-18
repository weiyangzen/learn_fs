<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/wakeup-mask.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/wakeup-mask.c

### Purpose
Synchronizes Samsung wake-disable register bits with Linux IRQ wake-enable state.

### Important APIs, Types, And Functions
`samsung_sync_wakemask(void __iomem *reg, const struct samsung_wakeup_mask *mask, int count)` reads a wake mask register, updates bits based on whether mapped IRQs are wake-enabled, ignores `NO_WAKEUP_IRQ` sentinels as always-disabled hardware wake bits, and writes the result back.

### Control Flow
SoC PM prepare code calls this before sleep. The function iterates the mapping table, tests IRQ wake state, clears disable bits for enabled wake IRQs, and sets disable bits otherwise.

### State, Persistence, And Dependencies
State is the SoC wake mask register. Dependencies include IRQ wake state tracking and raw MMIO accessors.

### Integration Points
`pm-s3c64xx.c` maps RTC, touch, MMC, modem, and HSI wake bits through this helper.

### Risks
The register uses disable-bit polarity, so inverted logic would mask desired wake sources. Stale IRQ wake state can either prevent wake or allow unwanted wakeups.

### Test Signals
Per-IRQ wake enable/disable tests and suspend wake-source matrix tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/wakeup-mask.c -->
