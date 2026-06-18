<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/bmips_5xxx_init.S -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/bmips_5xxx_init.S

### Purpose
This BMIPS5000 assembly file initializes secondary Broadcom BMIPS 5xxx cores by sizing and clearing caches, enabling cache modes, programming Broadcom CP0 configuration, and clearing branch predictor state.

### Important APIs, Types, And Functions
Important symbols are `size_i_cache`, `size_d_cache`, `enable_ID`, `l1_init`, `set_other_config`, `set_branch_pred`, `set_luc`, `set_cwf_tse`, `set_clock_ratio`, `set_zephyr`, `set_llmb`, `core_init`, `clear_jump_target_buffer`, and public `bmips_5xxx_init`.

### Control Flow
The entry saves `ra` and `a0`, calls L1 cache initialization, core configuration, and branch target buffer reset, clears CP0 Cause, restores `a0`, and returns. Cache initialization sizes I/D caches from Config1, runs uncached while setting K0 cache mode, invalidates tags, then resumes cached execution. Core init programs Zephyr, low-latency memory bus, branch prediction, link-uncached, CWF/TSE, clock ratio, and cache error behavior.

### State, Persistence, And Dependencies
State is CP0 Config, Broadcom Config0/Mode, cache tag/data registers, ZSC L2 registers, Cause, and predictor structures. Dependencies include BMIPS CP0 encodings, cacheop macros, and `CONFIG_CPU_BMIPS5000`.

### Integration Points
`bmips_vec.S` invokes this path during BMIPS5200 warm boot/secondary startup. SMP BMIPS code and platform reset vectors rely on these settings before entering C.

### Risks
This code executes before normal kernel services and uses raw CP0/ZSC accesses. Wrong cache sizing or mode transitions can hang secondary cores or corrupt memory. Some `.word` CP0 operations are opaque and hardware-specific.

### Test Signals
BMIPS5000/BMIPS5200 SMP boot, secondary CPU online/offline cycles, suspend/resume warm restart, cache coherency stress, and branch predictor reset validation are high-value tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/bmips_5xxx_init.S -->
