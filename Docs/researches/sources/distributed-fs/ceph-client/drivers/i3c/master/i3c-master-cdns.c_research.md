# sources/distributed-fs/ceph-client/drivers/i3c/master/i3c-master-cdns.c

Purpose: Cadence I3C master controller driver. It maps Cadence command/response FIFOs, retaining registers, IBI response/data FIFOs, hotjoin work, clock prescalers, and device slots to the I3C core.

Important APIs/types/functions: `struct cdns_i3c_master` owns core base, capabilities, free RR slots, IBI slots, transfer queue, sysclk, and device data. `struct cdns_i3c_cmd/xfer` model queued commands. Key functions implement CCC filtering, enable/disable, queue start/end/unqueue, CCC/I3C/I2C transfers, attach/reattach/detach, DAA, bus init/cleanup, IBI ops, IRQ demux, hotjoin work, probe, and remove.

Control flow: Probe validates DEV_ID, maps MMIO, enables clocks, disables interrupts, requests IRQ, reads capabilities, initializes IBI slots/thresholds, clears device slots, and registers. Bus init programs pure/mixed mode and prescalers, prepares master RR0, reads identity, sets master info, programs hotjoin/halts/MCS/data-hold controls, and enables hardware. DAA pre-fills inactive RRs, sends ENTDAA, adds active new devices, clears unused slots, sends DEFSLVS, updates SCL limits, and enables HJ/MR events.

State and persistence: Tracks capabilities, `free_rr_slots`, IBI slot ownership, `i3c_scl_lim`, and queued transfers. Hardware state includes CTRL, PRESCL, DEVS_CTRL, DEV_ID retaining registers, SIR_MAP, FIFOs, and interrupt masks.

Dependencies/integration: OF `cdns,i3c-master`, `pclk`, `sysclk`, MMIO/IRQ resources, I3C core ops, and generic IBI pools.

Risks: Error mapping is coarse. IBI overflow reporting has a FIXME. DAA depends on active-slot bits and cleanup of unused RRs. Prescaler math can fail with invalid clock/SCL combinations.

Test signals: Bad DEV_ID and clock failures; command timeout and FIFO flush; CCC error mapping; SDR length limit; I2C 10-bit support; hotjoin DAA; SIR_MAP rollback; IBI max payload handling; SCL limit updates; hotjoin work cancellation.
