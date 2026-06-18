# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_qm_arc_aux_regs.h

Purpose: generated register map for the auxiliary ARC control/status block inside `DCORE0_TPC0_QM`. It exports 284 `mmDCORE0_TPC0_QM_ARC_AUX_*` address constants from `0x4008100` to `0x4008920`.

Important APIs/types/functions: macro-only API spanning ARC run/halt request/ack, reset vector, debug mode, cluster/ARC IDs, wake events, DCCM address bases, CTI state, ARC reset request/status, scratchpads, cache/queue/DCCM controls, breakpoint and debug/status registers, error cause registers, queue base/producer/consumer/shadow fields, DCCM queue alert message, inflight counters, AXI ordering counters, and ARC upper DCCM enable.

Control flow: none in the header. External reset, firmware boot, security, and debug flows use these addresses to halt/run the ARC, set reset vectors, configure DCCM/queues, observe errors, or expose safe debug ranges.

State and persistence behavior: represents ARC microcontroller state associated with the TPC queue manager. State includes execution control, queue metadata, scratchpads, error latches, and counters. Values persist across normal operation until ARC reset, device reset, or explicit reprogramming.

Dependencies and integration points: included by `gaudi2_regs.h`; heavily referenced in `gaudi2_security.c` as register ranges and individual allowed registers. It integrates with `dcore0_tpc0_qm_regs.h` for QMAN queues and with TPC CFG QM kernel/tensor setup.

Risks: this is a sensitive firmware-control surface. Incorrect register access can halt firmware, corrupt DCCM queues, break command processing, or expose privileged debug state. Security tables must not overexpose ARC control registers.

Test signals: ARC boot/reset tests, queue-manager firmware liveness checks, security allowlist tests in `gaudi2_security.c`, debug halt/resume smoke tests, and generated address range validation against ARC auxiliary register specs.
