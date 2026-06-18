# sources/distributed-fs/ceph-client/drivers/i3c/master/adi-i3c-master.c

Purpose: Analog Devices AXI I3C master controller driver. It adapts ADI command/response/data/DAA/IBI/device-character registers to the I3C master core.

Important APIs/types/functions: `struct adi_i3c_master` owns core base, retaining-register slots, IBI slots, transfer queue, MMIO, clocks, SCL limit, and DAA staging. `struct adi_i3c_cmd/xfer` model queued commands. Key functions cover FIFO I/O, CCC filtering, transfer queue start/end/unqueue, CCC and private transfers, I2C transfers, attach/reattach/detach, DAA, IRQ demux, IBI lifecycle, probe, and remove.

Control flow: Probe maps registers, enables clocks, validates AXI major version, disables core/IRQs, requests IRQ, initializes slots and queues, enables command-response IRQ, and registers the master. Transfers preload TX FIFO, push command FIFO entries, wait for IRQ completion, and reset/unqueue on timeout. DAA precomputes free addresses, enables DAA IRQ handling, sends ENTDAA, services address requests in IRQ, adds discovered devices, syncs device-character metadata, sends DEFSLVS, and updates SCL limits.

State and persistence: Tracks `free_rr_slots`, per-device master data (`id`, `ibi`, pool), `ibi.slots[]`, current/queued transfers, and DAA address/index. Hardware state includes command/data FIFOs, IRQ masks, `REG_DEV_CHAR`, `REG_IBI_CONFIG`, and speed grade.

Dependencies/integration: ADI AXI common version register, clocks, MMIO/IRQ, I3C core ops, `internals.h` FIFO helpers, generic IBI pools, and OF `adi,i3c-master-v1`.

Risks: Unsupported-version path should be reviewed because the error probe call is not obviously returned. IBI handling appears MDB-focused rather than general payload copying. DAA index is IRQ-driven. Command FIFO room may limit submission.

Test signals: CCC get/set errors, SDR transfers with repeated starts, I2C 10-bit rejection, multi-device DAA, IBI enable/disable and slot exhaustion, DAA IRQ mask restoration, and remove shutdown.
