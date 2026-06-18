# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/altera-ci.c

Supports the Altera FPGA CI module on NetUP Dual DVB-T/C RF CI cards and interposes hardware PID filtering into DVB demux feed callbacks. Public exports are `altera_ci_init`, `altera_ci_release`, `altera_ci_irq`, and `altera_ci_tuner_reset`.

Important state types are `fpga_internal` for shared FPGA state, `altera_ci_state` for DVB CA slots, `netup_hw_pid_filter` for demux callback replacement, and a global `fpga_inode` list keyed by device/demux. Init registers CA, installs PID feed hooks, enables TS output/IRQs, and schedules status work. Feed start/stop updates PID registers and calls original callbacks; PID `0x2000` toggles full-TS behavior.

State is volatile and includes shared mutex-protected FPGA registers plus unprotected global list lifetime. Risks are list concurrency, release ordering, callback restoration, NULL demux lookup paths, and board-specific PID semantics. Test signals are dual CI slots, CAM insertion/removal, individual PID and full-TS feeds, tuner reset, IRQ work, and module unload.
