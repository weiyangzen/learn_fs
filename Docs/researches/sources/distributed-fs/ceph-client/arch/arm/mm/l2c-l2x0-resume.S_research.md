## sources/distributed-fs/ceph-client/arch/arm/mm/l2c-l2x0-resume.S

### Purpose
Assembly helper for secure-world early resume of L2C-310/L2X0 cache controller settings before normal CPU state restoration.

### Important APIs, Types, And Functions
Exports `l2c310_early_resume`. It reads `l2x0_saved_regs` via PC-relative offset and programs L2X0/L310 registers: auxiliary control, tag/data latency, address filters, prefetch control, power control, and enable.

### Control Flow
On entry it resolves saved-register storage, returns immediately if the controller base is zero, conditionally restores revision-dependent prefetch and power controls, returns if L2 is already enabled, then restores latency/filter/auxiliary registers and enables the controller.

### State, Dependencies, And Integration
State lives in `l2x0_saved_regs` maintained by L2X0 platform code. Depends on secure-world MMIO access and cache-l2x0 register offsets. Integrates with platform suspend/resume firmware paths.

### Risks And Test Signals
Risks include running outside secure world, invalid saved base address, wrong revision checks, and enabling L2 with stale latency/filter settings. Test suspend/resume on L2C-310 platforms, secure firmware path selection, and cache data integrity after resume.
