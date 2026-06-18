## sources/distributed-fs/ceph-client/arch/mips/kernel/spram.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/spram.c` probes and configures MIPS instruction and data scratchpad RAM for CPUs that expose SPRAM tags through cache tag operations and ErrCtl access mode.

### Important APIs, Types, And Functions
Important helpers are `bis_c0_errctl()`, `ispram_store_tag()`, `ispram_load_tag()`, `dspram_store_tag()`, `dspram_load_tag()`, `probe_spram()`, and `spram_config()`. The code uses tag constants such as `SPRAM_TAG0_ENABLE`, `SPRAM_TAG0_PA_MASK`, and `SPRAM_TAG1_SIZE_MASK`.

### Control Flow
`spram_config()` checks CPU type and Config bits for instruction/data SPRAM. For each present SPRAM type, `probe_spram()` walks up to eight tag pairs, derives size from tag1, aligns the requested base, writes a new physical base with enable bit to tag0, rereads the tag, and logs the resulting physical address and size. DSPRAM is additionally tested by writing and reading a CKSEG1 pattern.

### State, Persistence, And Dependencies
State is hardware tag state for ISPRAM/DSPRAM and CP0 ErrCtl. The configured physical base persists for the running kernel until reset or reprogramming. Dependencies include CP0 tag registers, cache `Index_Load_Tag_*` and `Index_Store_Tag_*` operations, hazard barriers, `asm/r4kcache.h`, and CPU-type/config feature bits.

### Integration Points
This is called from MIPS platform setup paths when scratchpad RAM needs configuration. It interacts with cache/TLB address spaces and platform-specific physical map assumptions, with comments noting Malta-specific base addresses.

### Risks
Incorrect tag semantics or base alignment can misconfigure scratchpad memory. The probe loop has an arbitrary bound to avoid runaway on unsupported implementations. DSPRAM read/write testing touches physical memory via CKSEG1 and can reveal bus or mapping problems. CPU-specific assumptions are narrow.

### Test Signals
Boot CPUs with ISP/DSP Config bits, confirm log output for expected SPRAM regions, validate DSPRAM pattern writes, test unsupported CPUs for no-op behavior, and check hazard-sensitive regressions after cache/tag changes.
