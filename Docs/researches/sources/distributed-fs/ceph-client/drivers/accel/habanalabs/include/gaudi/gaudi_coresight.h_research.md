## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_coresight.h

### Purpose
`gaudi_coresight.h` defines index enumerations for Gaudi debug and trace components exposed through the driver coresight/debug interface. The indices identify STM, ETF, funnel, BMON, and SPMU register blocks for MME, DMA, CPU, PCIe, PSOC, NIC, MMU, SRAM, and TPC units.

### Important APIs, Types, And Functions
The file exports five enums: `gaudi_debug_stm_regs_index` with 48 entries, `gaudi_debug_etf_regs_index` with 50 entries, `gaudi_debug_funnel_regs_index` with 78 entries, `gaudi_debug_bmon_regs_index` with 123 entries, and `gaudi_debug_spmu_regs_index` with 42 entries. Each enum starts at a `*_FIRST` entry and ends with a `*_LAST` sentinel equal to the final real unit index.

### Control Flow
No code executes in this header. `gaudi_coresight.c` uses these indices to select base registers and configure capture/trace units. The runtime control flow unlocks coresight components, programs source-specific registers, polls timeout/status bits, and enables or disables tracing based on the enum-provided block identity.

### State, Persistence, And Dependencies
The indices are stable identifiers for hardware debug blocks. Hardware trace state is held in the corresponding device registers and buffers, not in this header. The header depends on `gaudi_coresight.c` maintaining register arrays in the same order as these enums and on `gaudi_masks.h`/`gaudi_reg_map.h` for field masks and PSOC scratch-register aliases used during debug flows.

### Integration Points
The enums integrate with the driver debugfs/coresight control path in `gaudi_coresight.c`. They cover accelerator engines, memory fabric paths, PCIe/CPU/PSOC blocks, NICs, and all eight TPC EML units, enabling uniform handling of trace sources and performance monitors across Gaudi.

### Risks
Enum order is an implicit ABI between this header and register-address arrays. Reordering a value without updating arrays in `gaudi_coresight.c` would configure the wrong debug block. The presence of unusual ordering such as the SRAM funnel entries means "natural" sorting can be wrong. Missing `*_LAST` updates can leave valid units unconfigurable or expose out-of-range indexing.

### Test Signals
Exercise coresight/debug configuration for representative STM, ETF, funnel, BMON, and SPMU units. Validate first/last iteration bounds, timeout paths, enable/disable cycles, and register-array indexing. Hardware trace smoke tests should confirm that TPC7, NIC, PCIe, PSOC, DMA, and MME sources produce expected captures.
