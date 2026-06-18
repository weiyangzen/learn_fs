
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-480.c

## Purpose
Implements VFE 480 ops for a newer RDI-focused generation with separate register offsets for full VFE and VFE-lite instances.

## Important APIs, Types, and Functions
Exports `vfe_ops_480`. Offset macros depend on `vfe_is_lite(vfe)`. Key helpers are `reg_update_rdi()`, bus IRQ mask helpers, `vfe_global_reset()`, `vfe_wm_start()`, `vfe_wm_stop()`, `vfe_wm_update()`, `vfe_reg_update()`, `vfe_enable_irq()`, `vfe_isr()`, and `vfe_isr_reg_update()`.

## Control Flow
Reset masks reset ack and writes hardware/register reset. WM start maps logical RDI to actual WM, configures frame increment, burst, image config, stride, packer, no frame drops, IRQ subsampling, and enables MIPI RAW WM. IRQ enable keeps masks for already reserved/on lines. ISR clears top status, handles reset ack, then on bus-top IRQ clears bus status, processes RDI register updates, and calls `vfe_buf_done()` for matching composite groups. Halt is delegated to generic output stop.

## State and Persistence
State is generic VFE v2 output state plus `vfe->reg_update`; actual full/lite differences are computed at access time. No persistent storage.

## Dependencies and Integration Points
Depends on generic VFE v2 helpers, `vfe_is_lite()`, PM-domain functions, vb2 queue helpers, and V4L2 pixel format state.

## Risks and Test Signals
`vfe_buf_done_480()` is a no-op in the ops table while the ISR directly calls generic `vfe_buf_done()`, so callers using the ops callback may not get completion. IRQ mask calculation loops over `MAX_VFE_OUTPUT_LINES` and must match resource line counts. Test full vs lite offsets, concurrent RDI lines, reset ack, reg-update completion, buffer completion path, and no stale IRQ masks after stop.
