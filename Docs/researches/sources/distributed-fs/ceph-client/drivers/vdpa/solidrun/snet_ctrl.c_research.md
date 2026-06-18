<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_ctrl.c

Purpose: Implements the SolidRun DPU control-register protocol for destroying, suspending, resuming devices and reading VQ state.

Important APIs/functions: Public functions are `snet_ctrl_clear()`, `snet_destroy_dev()`, `snet_read_vq_state()`, `snet_suspend_dev()`, and `snet_resume_dev()`. Internal helpers poll opcode/control registers, send old config-v1 messages, send config-v2 no-payload messages, and read chunked payloads from the DPU.

Control flow: For config version 2 or newer, commands serialize under `snet->ctrl_lock`. Send paths wait for an empty control register, write control/opcode under `ctrl_spinlock`, wait for chunk-ready/error, clear chunk-ready, and wait until the DPU clears the opcode. Read paths write expected buffer size and opcode/VQ index, then loop over ready chunks until the requested word count is consumed or the DPU clears in-process. For old config version 1, only the opcode register is used and ACK is opcode clearing.

State and persistence: State is in DPU MMIO control registers and the caller-provided buffers. There is no disk persistence. Locking state is maintained in `struct snet`.

Dependencies and integration points: Uses offsets from `snet->psnet->cfg.ctrl_off`, MMIO accessors from `snet_vdpa.h`, and version negotiation performed by `snet_main.c`.

Risks: Protocol depends on 4-byte aligned buffers, timeouts, and correct chunk-size/error-bit interpretation. Control register writes are serialized with both mutex and spinlock because opcode/control pairs must appear atomically to the DPU. `snet_read_vq_state()` is unsupported on config version 1.

Test signals: Test destroy on reset, suspend/resume netlink migration paths, VQ state read for config v2, old config v1 ACK path, DPU error bits translating to negative errno, and timeout logging for stuck opcode/control registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_ctrl.c -->
