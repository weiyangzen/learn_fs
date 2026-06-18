
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-680.c

## Purpose
Implements VFE 680 ops for very new CAMSS hardware where RDI streaming uses write clients and external CAMSS register-update plumbing, with no meaningful local global reset or top-level IRQ processing in this driver.

## Important APIs, Types, and Functions
Exports `vfe_ops_680`. Important functions are `vfe_global_reset()`, `vfe_disable_irq()`, `vfe_wm_start()`, `vfe_wm_stop()`, `vfe_wm_update()`, `vfe_reg_update()`, and `vfe_reg_update_clear()`. Register macros switch between full VFE and VFE-lite offsets and define bus write-client image config, MMU prefetch, frame-drop, IRQ subsample, and diagnostics.

## Control Flow
`vfe_global_reset()` simply completes `reset_complete` because this hardware has no local global reset path. WM start maps logical RDI to actual WM, programs image dimensions/stride, packer, frame increment, MMU prefetch, no-drop/no-subsample settings, disables local IRQs for RDI mode, and enables the write client. Buffer address updates write the current image address. Register updates call `camss_reg_update()` with clear=false/true instead of local VFE update registers.

## State and Persistence
State is generic VFE v2 output and queue state plus volatile hardware registers. There is no local IRQ state for RDI completion in this file; external CAMSS paths are expected to drive update behavior.

## Dependencies and Integration Points
Depends on `vfe_is_lite()`, CAMSS top-level `camss_reg_update()`, generic VFE v2 queue/output helpers, PM-domain helpers, and V4L2 pixel format state.

## Risks and Test Signals
The ISR is a stub returning handled and local IRQs are disabled in RDI mode, so integration with external interrupt/update handling is mandatory. `RDI_WM()` is documented as RDI-only and would be wrong for stats/AWB/BHIST clients. Test external register-update completion, full/lite offsets, MMU prefetch configuration, write-client enable/disable, address updates, and streaming without local IRQ completions.
