## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_tbf.c

Purpose: this file offloads tc Token Bucket Filter shaping to LAN966x hierarchical scheduler elements. It supports both root/port shaping and per-queue shaping depending on the qdisc parent handle.

Important APIs and functions: `lan966x_tbf_add()` validates the parent, maps it to a scheduler element, converts Linux rate and burst parameters to hardware units, enables frame-mode shaping, and programs committed information rate/burst registers. `lan966x_tbf_del()` resolves the same scheduler element, disables shaping mode, and clears CIR/burst.

Control flow: a root qdisc maps to `SE_IDX_PORT + chip_port`; a class/queue parent maps to `SE_IDX_QUEUE + chip_port * NUM_PRIO_QUEUES + queue`. Non-root queue indices are extracted with `TC_H_MIN(parent) - 1` and rejected when outside `NUM_PRIO_QUEUES`. Rate bytes/s are converted to kbps-like units through bytes-to-bits and a hardware 100 kbps unit, rounded up and clamped away from zero. Burst is converted to 4 KiB units, rounded up and clamped away from zero. Field-width checks reject values too large for QSYS fields.

State and persistence: no software state is persisted. Hardware state lives in `QSYS_SE_CFG(se_idx)` and `QSYS_CIR_CFG(se_idx)` until destroyed or overwritten. Delete returns success after clearing the hardware state even if the previous configuration is unknown.

Dependencies and integration: called from `lan966x_tc_setup_qdisc_tbf()` in `lan966x_tc.c`; depends on scheduler index constants and QSYS register macros from `lan966x_main.h`/`lan966x_regs.h`.

Risks: parent-handle interpretation must match tc queue numbering. Hardware unit conversion can materially differ from requested rates, especially at low rates where values round up to one unit. Only CIR/CBS are programmed; unsupported TBF semantics are not represented here. Test signals include root and per-queue TBF add/delete, rejection of invalid queue parents and oversized rates/bursts, observed egress throughput around rounding boundaries, and interaction with CBS/ETS/TAPRIO scheduler state.
