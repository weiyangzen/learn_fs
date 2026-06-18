<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-memory.c -->
## sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-memory.c

### Purpose
`malta-memory.c` provides Malta firmware memory initialization hooks and a CDMM physical base.

### Important APIs, Types, And Functions
`fw_meminit()` sets `free_init_pages_eva` when EVA is enabled. `free_init_pages_eva_malta()` frees unused kernel init pages using `__pa_symbol()`. `mips_cdmm_phys_base()` returns `0x1fc10000`. `physical_memsize` is a global filled by the DT shim.

### Control Flow
During PROM initialization, `fw_meminit()` chooses the EVA-specific free-init callback or leaves it null. CDMM users later call `mips_cdmm_phys_base()` for a fixed typically-unused address.

### State, Persistence, And Dependencies
Persistent state is `physical_memsize` and optional `free_init_pages_eva` function pointer. Dependencies include memblock/init memory helpers, EVA configuration, MAAR/CDMM headers, and firmware setup.

### Integration Points
`malta-init.c` calls `fw_meminit()`. `malta-dtshim.c` updates `physical_memsize`. Core MIPS CDMM code consumes `mips_cdmm_phys_base()`.

### Risks
The EVA free path relies on `__pa_symbol()` because kernel virtual addresses may not map normally. The CDMM base is a convention and could conflict with unusual memory maps.

### Test Signals
Boot Malta EVA and non-EVA kernels, verify init memory is freed correctly, and test CDMM device discovery or absence at the fixed physical base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-memory.c -->
