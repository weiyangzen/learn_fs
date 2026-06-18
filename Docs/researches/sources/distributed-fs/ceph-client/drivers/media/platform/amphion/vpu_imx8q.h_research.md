<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_imx8q.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_imx8q.h

Purpose: declares i.MX8Q register offsets, MediaIP limits, IRQ-pin constants, the firmware `vpu_rpc_system_config` layout, and platform-specific function prototypes.

Important APIs/types: register macros cover SCB, decoder, encoder, HIF/SIF/MCX, block control, cache, and pixel interface bases. `struct vpu_rpc_system_config` mirrors the firmware-visible system topology for Malone/Windsor cores, command/message IRQs, timers, cache, heap, UART, and trace configuration.

Control/state behavior: no code executes here; it is the ABI and register map used by `vpu_imx8q.c`, `vpu_malone.c`, and Windsor code.

Dependencies and integration: included by platform and firmware iface files. Its constants determine how parent register base plus per-core offsets are written into shared memory.

Risks and test signals: incorrect offsets break firmware boot or stream-buffer register access. Build coverage plus boot tests on i.MX8QXP/i.MX8QM and firmware system-config inspection are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_imx8q.h -->
