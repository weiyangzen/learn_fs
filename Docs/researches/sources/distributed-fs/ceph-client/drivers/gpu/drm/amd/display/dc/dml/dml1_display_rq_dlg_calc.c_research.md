# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dml1_display_rq_dlg_calc.c

## Purpose
`dml1_display_rq_dlg_calc.c` computes DCN1 requestor sizing parameters, DLG deadline registers, and TTU QoS/register values from DML pipe, SoC, and IP parameters.

## Important APIs, Types, And Functions
Public functions are `dml1_rq_dlg_get_rq_params()`, `dml1_extract_rq_regs()`, and `dml1_rq_dlg_get_dlg_params()`. Private helpers classify pixel formats, derive block sizes, compute prefetch ratios and swath needs, extract log2 register fields, split detile buffer storage, compute row heights, and build per-surface RQ parameters.

## Control Flow
RQ calculation derives luma/chroma bytes per element, block geometry, swath width/request counts, meta request geometry, DPTE request shape, row heights, row bytes, and group counts, then handles dual-plane chroma and detile-buffer splitting. Register extraction converts byte sizes and swath heights into encoded fields. DLG/TTU calculation clears outputs, computes refclk/pixel conversions, vblank deadline budgets, prefetch line budgets, VM/meta timing, prefetch ratios, nominal/vblank PTE and meta timings, line/request delivery times, cursor0 timing, QoS levels, and `min_ttu_vblank`.

## State, Persistence, And Dependencies
The file is stateless except for caller-owned output structs. It reads `display_mode_lib`, RQ/DLG params, DLG system params, e2e pipe params, SoC latencies, IP buffer sizes, and IP delay totals. It depends on DML math wrappers, logger helpers, and DML enum values.

## Integration Points
This is the DCN1 register preparation layer after higher-level DML has selected clocks, watermarks, and pipe configuration. Outputs map to requestor, DLG, and TTU programming structures.

## Risks
Power-of-two log math assumes valid nonzero inputs. Assertions guard many range failures but do not recover. DCN1-specific assumptions include hardcoded chunk sizes, limited 4:2:0 DCC support, cursor0-only timing, and a DEGVIDCN10-137 request-size workaround.

## Test Signals
Test linear/tiled, horizontal/vertical scan, 4K/64K/256K tiles, RGB/444/420 formats, DCC, VM, cstate, pstate, immediate flip, hsplit, cursor widths, small vblank modes, and register boundary assertions.
