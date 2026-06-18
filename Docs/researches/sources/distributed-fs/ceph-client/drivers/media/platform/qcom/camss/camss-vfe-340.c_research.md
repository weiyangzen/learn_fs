
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-340.c

## Purpose
Implements TFE/VFE 340 ops, a compact top/bus register model for RDI streaming with subgroup-to-line mapping and bus write-client interrupts.

## Important APIs, Types, and Functions
Exports `vfe_ops_340`. It defines `enum tfe_iface`, `enum tfe_subgroups`, mapping arrays, `__line_to_iface()`, `__iface_to_line()`, `__subgroup_to_line()`, `vfe_global_reset()`, `vfe_isr()`, `vfe_enable_irq()`, `vfe_wm_start()`, `vfe_wm_update()`, `vfe_reg_update()`, and `vfe_reg_update_clear()`.

## Control Flow
Reset enables reset-done IRQ and writes core reset. Stream setup through generic v2 calls WM start, which programs image config, frame increment, PLAIN64 packer, no frame drop, IRQ subsampling, enables IRQ masks, and enables the write client. ISR clears top status, handles reset done, then if bus write IRQ fired it clears bus status, clears register-update bits by interface, completes buffers by subgroup-to-line mapping, and logs configuration/input/image-size violations. Overflow status is separately read, cleared, and logged per WM.

## State and Persistence
State is generic VFE line/output state plus `vfe->reg_update`. Hardware client state is volatile. No persistent storage.

## Dependencies and Integration Points
Uses generic `vfe_enable_v2()`, `vfe_disable()`, `vfe_buf_done()`, `vfe_queue_buffer_v2()`, PM-domain helpers, and V4L2 active pixel format data.

## Risks and Test Signals
Invalid line/interface mappings fall back to RDI0 or `VFE_LINE_NONE`, so bad caller state may become wrong-stream programming. Buffer done for PIX-related subgroups is mapped even though this implementation is mainly RDI. Test RDI0-2 WM mapping, bus violation logs, overflow logs, register-update clear, reset done, and frame stride/height programming.
