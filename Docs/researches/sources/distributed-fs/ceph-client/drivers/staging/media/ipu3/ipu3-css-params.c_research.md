# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css-params.c

## Purpose
`ipu3-css-params.c` converts V4L2/user IPU3 parameter payloads into firmware ABI structures consumed by the IPU3 CSS pipeline while streaming. It builds accelerator (`acc`) parameters, late-bound VMEM0/DMEM0 parameter blocks, output-system scaler/formatter state, 3A operation schedules, and default GDC warp tables. The file is the bridge between user controls in `ipu3_uapi_params`, firmware binary memory-offset metadata, and the device-visible parameter buffers queued by `ipu3-css.c`.

## Important APIs, Types, and Functions
- Exported functions are `imgu_css_cfg_acc()`, `imgu_css_cfg_vmem0()`, `imgu_css_cfg_dmem0()`, and `imgu_css_cfg_gdc_table()`.
- Local calculation structures carry scaler, frame, stripe, and process-line state.
- OSYS helpers compute fixed-point scaler LUTs, actual scaled dimensions, formatter frame parameters, stripe offsets, padding, cropping, and block/chunk dimensions.
- 3A helpers generate shading, AF, AWB, and AWB FR operation lists for transfer/process/read handshakes.
- `imgu_css_cfg_copy()` uses firmware offset metadata to locate ABI substructures and copy user, old, or default-generated values.

## Control Flow
`imgu_css_set_parameters()` allocates/reuses pool entries and calls these functions. `imgu_css_cfg_acc()` recalculates geometry-sensitive stripe state, then for each accelerator block chooses user values when `use` flags are set, previous ABI values when available, or defaults from tables/literals. It patches derived fields such as frame width, grid ends, stripe-specific grid placement, BDS factors, ANR frame size, and operation lists.

VMEM0/DMEM0 configuration zeroes the firmware-declared memory block, then copies or initializes linearization, TNR3, and XNR3 sub-parameters. GDC table generation writes a unity warp table for luma and chroma blocks, including per-block input offsets.

## State and Persistence Behavior
The file does not own persistent state. It fills new DMA-backed pool entries and receives old entries so omitted user sections preserve previous values. Defaults are only generated when there is no previous state.

## Dependencies and Integration Points
It depends on `ipu3-css.h`, `ipu3-css-fw.h`, `ipu3-tables.h`, firmware ABI definitions, and UAPI parameter layouts. It integrates with the CSS parameter queue by producing ABI blocks that `ipu3-css.c` references from `imgu_abi_parameter_set_info`.

## Risks
- Stripe/scaler/grid arithmetic is alignment-sensitive and can corrupt output or hang firmware if wrong.
- Several split-grid paths reference stripe 1, so they depend on valid firmware stripe counts and earlier format constraints.
- Invalid user grid sizes or out-of-frame statistics regions return `-EINVAL`.
- Firmware metadata/ABI drift returns `-EPROTO` or risks writing the wrong offset.
- `imgu_css_cfg_vmem0()` only fills one indexed XNR3 default element after assigning `i = IPU3_UAPI_ISP_TNR3_VMEM_LEN`, which is a notable review target.

## Test Signals
Exercise default parameters, partial updates preserving old state, invalid grids, one- and two-stripe binaries, VF scaling around threshold ratios, statistics grids fully left/right/across overlap, and hardware runs that watch firmware warning/assert events and stripe-boundary image correctness.
