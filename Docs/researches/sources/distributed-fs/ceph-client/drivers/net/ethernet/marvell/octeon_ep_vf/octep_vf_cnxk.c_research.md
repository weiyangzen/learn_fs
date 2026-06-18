# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_cnxk.c

## Purpose
This file implements CNXK VF hardware operations for OCTEON endpoint VFs, including queue reset/setup, watermark programming, mailbox register binding, queue interrupt handling, enable/disable operations, register reinitialization, and debug register dumping.

## Important APIs, Types, And Functions
- Debug/reset: `cnxk_vf_dump_q_regs()`, `cnxk_vf_reset_iq()`, `cnxk_vf_reset_oq()`, and `octep_vf_reset_io_queues_cnxk()`.
- Config: `octep_vf_init_config_cnxk_vf()` discovers rings-per-VF, sets descriptor counts, buffer size, refill and interrupt thresholds, OQ watermark, and MSI-X count.
- Register setup: `octep_vf_setup_iq_regs_cnxk()` and `octep_vf_setup_oq_regs_cnxk()` program CNXK IQ/OQ CSRs; OQ setup includes `CNXK_VF_SDP_R_OUT_WMARK`.
- Interrupts: `octep_vf_ioq_intr_handler_cnxk()` handles queue interrupts and PF-to-VF mailbox notifications delivered with queue 0.
- Ops registration: `octep_vf_device_setup_cnxk()` fills the VF hardware ops vector.

## Control Flow
VF main setup selects this file for CN10KA/CNF10KA/CNF10KB/CN10KB VF device IDs. IQ setup waits for IDLE, sets 64-byte instruction mode and ESR, writes descriptor base/size, stores doorbell/count/interrupt register pointers, and initializes instruction count. OQ setup waits for IDLE, writes watermark, writes descriptor base/size with retry until the register reflects the DMA address, clears packet/control mode bits, programs buffer size and interrupt moderation, and stores credit/count register pointers. Open/stop use the registered ops to enable/disable queues and interrupts.

## State And Persistence
The file mutates in-memory VF config and per-queue MMIO pointers, plus hardware state for ring base/size, control bits, watermarks, interrupt thresholds/enables, queue enable bits, mailbox interrupt enable, and doorbell/count registers. State is runtime only and reset/recreated across open/stop or device reset.

## Dependencies And Integration Points
It depends on `octep_vf_regs_cnxk.h`, `octep_vf_main.h`, and `octep_vf_config.h`. It integrates through `struct octep_vf_hw_ops` with the generic VF main, Tx, Rx, and mailbox code. Its OQ watermark behavior corresponds to CNXK register definitions and differs from CN9K.

## Risks And Edge Cases
- IQ IDLE wait loops are unbounded; OQ base programming has a bounded retry but can return `-EFAULT` or `-EAGAIN` and abort queue setup.
- Mailbox delivery is coupled to queue 0 interrupt handling.
- Watermark programming is CNXK-specific; incorrect defaults can cause backpressure problems.
- `schedule_timeout_interruptible(1)` loops while enabling IQs rely on process context and can delay open under slow hardware.

## Test Signals
Probe CNXK VFs, verify OQ descriptor base retry success, validate watermark programming, run Tx/Rx traffic with interrupts, test mailbox link notifications, exercise open/stop/reopen, dump queue registers including `ERR_TYPE`, and test failure behavior when OQ setup cannot latch descriptor base.
