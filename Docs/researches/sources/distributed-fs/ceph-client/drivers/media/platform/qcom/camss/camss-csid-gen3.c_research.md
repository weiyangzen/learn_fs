# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen3.c

## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen3.c

Purpose: Implements Titan Gen3 CSID operations, including wrapper routing, RDI configuration, RUP/AUP register updates, buffer-done forwarding to VFE, reset, and IRQ handling for newer Qualcomm CAMSS SoCs.

Important APIs/types/functions: Exports `csid_ops_gen3`. Helpers include `__csid_configure_wrapper()`, `__csid_configure_rx()`, `__csid_configure_rdi_stream()`, `__csid_ctrl_rdi()`, `csid_subdev_reg_update()`, `csid_isr()`, and `csid_reset()`. Register macros handle lite vs full and CSID 690 offset differences.

Control flow/state: Stream enable configures the wrapper for full CSIDs, then each enabled VC gets RDI payload-only decode, timestamp, pixel store, crop/drop, MIPI packing, IRQ subsampling, RX lane/PHY settings, and RDI start command. `csid->reg_update` tracks RUP/AUP bits written to `CSID_RUP_AUP_CMD`; RUP done IRQ clears bits. Reset enables top and per-enabled-RDI buf-done IRQ masks, sets reset mode/location, issues HW+IRQ reset, and waits for completion. ISR clears top/RX/buf-done/per-RDI statuses, forwards buf-done to `camss_buf_done()`, clears IRQ command, and completes reset.

Dependencies/integration: Depends on common CSID entity/link/power code, CAMSS resource version checks (`CAMSS_8775P`, `CAMSS_8300`), VFE downstream buffer handling, and `camss-csid-gen3.h`.

Risks/test signals: Risks include incorrect buf-done RDI offset per SoC/lite variant, no real testgen support despite a no-op configure hook, and reg-update command bits not being written on clear. Test supported Gen3 SoCs, lite/full paths, multi-VC buf-done, RUP/AUP update flow, reset timeout, and stream disable.
