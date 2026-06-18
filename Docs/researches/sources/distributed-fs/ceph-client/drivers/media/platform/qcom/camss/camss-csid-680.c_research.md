# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-680.c

## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-680.c

Purpose: Implements CSID operations for Titan 680-style hardware with top wrapper routing, per-RDI register update tracking, buffer-done IRQ handling, and VFE notification.

Important APIs/types/functions: Exports `csid_ops_680`. Major helpers include `csid_reg_update()`, `csid_reg_update_clear()`, `__csid_configure_top()`, `__csid_configure_rx()`, `__csid_configure_rdi_stream()`, `csid_reset()`, `csid_isr()`, and `csid_subdev_reg_update()`.

Control flow/state: Stream configuration writes wrapper path routing, then for each enabled VC configures RDI data type, VC, DT_ID, payload-only decode, timestamp/byte-count/drop/crop/packing flags, IRQ subsampling, and RDI halt/resume. `csid->reg_update` stores outstanding RUP/AUP bits and is written to `CSID_REG_UPDATE_CMD`; RUP-done IRQs clear bits. Reset preserves registers, enables per-RDI RUP done, clears/enables buf-done IRQs, unmasks top IRQs, and waits for reset completion. ISR clears top, RX, buf-done, and per-RDI statuses, clears reg-update bits on RUP done, and calls `camss_buf_done()` for matching RDI buffer-done bits.

Dependencies/integration: Requires common CAMSS `csid_wrapper_base`, VFE parent ops, common CSID link setup, and VFE buffer completion path.

Risks/test signals: Risks include wrapper routing mistakes, RDI offset differences for lite vs full blocks, reg-update bit leaks, and false buf-done port mapping. Test all enabled VC masks, lite/full variants, stream disable, VFE buffer completion, reset with IRQ masks, and reg-update clear/set through `camss_reg_update()`.
