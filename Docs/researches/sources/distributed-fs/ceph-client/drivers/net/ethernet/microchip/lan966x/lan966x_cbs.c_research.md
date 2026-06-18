# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_cbs.c

Purpose: translates Linux TC CBS queue offload requests into LAN966x queue scheduler element configuration.

Important APIs and functions: `lan966x_cbs_add` validates `tc_cbs_qopt_offload`, computes committed information rate and burst size, enables AVB/frame mode on the queue scheduler element, and writes `QSYS_CIR_CFG`. `lan966x_cbs_del` disables frame mode and clears CIR rate/burst.

Control flow: add rejects non-positive idleslope, non-negative sendslope, and invalid credit ranges. It computes the scheduler element index as `SE_IDX_QUEUE + chip_port * NUM_PRIO_QUEUES + queue`, converts rate to 100 kbps units and burst to 4 KB units, clamps zero to one, verifies field widths, then programs QSYS registers. Delete uses the same index and clears the rate/burst.

State and persistence: no local state is kept. Hardware CBS state persists in QSYS scheduler registers until deletion, port reset, or driver teardown.

Dependencies and integration points: called from the driver TC setup path declared in `lan966x_main.h`. Depends on Linux `tc_cbs_qopt_offload` semantics and LAN966x QSYS scheduler register macros.

Risks and test signals: arithmetic overflow or integer truncation can misprogram rates/bursts. Unsupported parameters are rejected with `-EINVAL`, so TC tests should cover bad slopes, credit boundaries, field-limit overflow, add/delete on all queues, and traffic shaping behavior.
