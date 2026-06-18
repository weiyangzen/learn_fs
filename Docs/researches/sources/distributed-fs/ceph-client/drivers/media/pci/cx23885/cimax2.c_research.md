# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cimax2.c

Implements CIMax2 SP2 CI support for NetUP-style cx23885 DVB-S2 CI boards. It maps DVB CA EN50221 attribute/control operations to I2C configuration and MC417 GPIO bus cycles.

Important APIs include CAM memory/control accessors, `netup_ci_slot_reset`, `netup_ci_slot_ts_ctl`, `netup_ci_slot_status`, `netup_poll_ci_slot_status`, `netup_ci_init`, and `netup_ci_exit`. Init selects I2C address by port, writes CIMax config, powers slots, registers a CA slot, initializes work, and schedules status polling. IRQ handling schedules work from GPIO0/GPIO1; work handles FR/DA IRQs and polls insertion/removal.

State includes `netup_ci_state`, current CI flag, IRQ mode, cached slot status, poll timeout, and `port->port_priv`. Risks are I2C failures, MC417 ACK timeout, work not explicitly canceled on exit, and timing-sensitive CAM cycles. Test signals are CAM IO, slot reset, TS enable, insertion/removal IRQs, poll-open IRQ mode, and unload after CA use.
