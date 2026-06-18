# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gpu_state.h

## Purpose

`a6xx_gpu_state.h` is the static capture schema for A6xx GPU state and the shared metadata schema for A7xx generated snapshot tables. It contains register ranges, shader-memory blocks, cluster descriptors, DBGAHB descriptors, GMU/GPUCC ranges, indexed CP register descriptors, debugbus block tables, and printable name arrays used by `a6xx_gpu_state.c`.

## Important APIs, Types, And Tables

- `A6XX_NUM_CONTEXTS` and `A6XX_NUM_SHADER_BANKS` define A6xx dump dimensionality.
- `struct a6xx_cluster`, `struct a6xx_dbgahb_cluster`, `struct a6xx_registers`, `struct a6xx_shader_block`, `struct a6xx_indexed_registers`, and `struct a6xx_debugbus_block` describe local A6xx capture ranges.
- `a6xx_clusters`, `a6xx_dbgahb_clusters`, `a6xx_hlsq_reglist`, `a6xx_shader_blocks`, `a6xx_reglist`, AHB/VBIF/GBIF reglists, GMU reglists, GPUCC reglists, indexed reglists, and debugbus block arrays feed the capture loops.
- `struct gen7_sel_reg`, `struct gen7_cluster_registers`, `struct gen7_sptp_cluster_registers`, `struct gen7_shader_block`, and `struct gen7_reg_list` define the shape expected from generated A7xx snapshot headers.
- `a7xx_debugbus_blocks`, `a7xx_statetype_names`, `a7xx_pipe_names`, and `a7xx_cluster_names` let A7xx dumps print stable names from enum values.
- Forward declarations for `a6xx_get_cp_roq_size()` and `a7xx_get_cp_roq_size()` support runtime-sized indexed register dumps.

## Control Flow

The header supplies data, not active code. `a6xx_gpu_state.c` walks each range array in register-pair form, where each pair is inclusive start/end dword offset. `RANGE()` in the C file computes counts from these pairs. For A6xx, local arrays fully describe which normal registers, HLSQ/SP/TP blocks, shader banks, clusters, CP indexed regions, GMU regions, and debugbus blocks are dumped. For A7xx, generated snapshot files provide family-specific lists in the `gen7_*` structures declared here, while this header provides common debugbus lookup and enum-name tables.

## State And Persistence Behavior

All tables are `static const` and persist in kernel text/data for the module lifetime. They do not store captured values. Their pointers are saved as `handle` fields in `struct a6xx_gpu_state_obj`, letting printer functions recover names, register ranges, dimensions, selectors, and output formatting after capture.

## Dependencies And Integration Points

The header includes `a6xx.xml.h` for A6xx register and statetype constants and depends on A7xx enum types included earlier by `a6xx_gpu.h`. Generated A7xx snapshot headers must produce arrays compatible with the `gen7_*` structs. `a6xx_gpu_state.c` relies on the order and sentinel conventions: A6xx arrays use explicit `count`, while many A7xx arrays end with `UINT_MAX` or NULL `regs`.

## Risks And Edge Cases

- Register ranges are raw dword offsets. Wrong ranges can read reserved registers, miss critical fault data, or overflow crashdumper data space.
- A6xx register arrays use inclusive pairs and `ARRAY_SIZE`; an odd number of entries corrupts range walking.
- A7xx arrays use sentinel conventions. Missing `UINT_MAX` or NULL terminators can make capture walk past the table.
- Debugbus block IDs are global for A7xx but selected per generated family list. Invalid IDs index `a7xx_debugbus_blocks` incorrectly.
- Printable name arrays are enum-indexed. If generated enum values change without updating the arrays, dumps show wrong names or access outside intended entries.
- New GPU families require careful table additions plus corresponding family selection in `a6xx_gpu_state.c`; current code has `BUG_ON()` for unsupported A7xx family values.

## Test Signals

Good signals are devcoredumps with populated register, indexed-register, shader, cluster, DBGAHB, GMU, and debugbus sections matching the target family; no `WARN_ON(datasize > A6XX_CD_DATA_SIZE)` during crashdump; no missing or nonsensical A7xx names; and stable dumps across A6xx, A650/A660, A7xx generation 1/2/3, and targets with VBIF versus GBIF.
