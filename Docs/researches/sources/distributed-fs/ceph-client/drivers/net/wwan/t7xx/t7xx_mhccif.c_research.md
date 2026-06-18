# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_mhccif.c

This file implements the host side of the modem-host cross-core interrupt facility (MHCCIF). It masks/unmasks device-to-host software interrupts, acknowledges status bits, and routes the MHCCIF PCIe interrupt into modem and PM handling.

The key APIs are `t7xx_mhccif_init`, `t7xx_mhccif_read_sw_int_sts`, `t7xx_mhccif_mask_set`, `t7xx_mhccif_mask_clr`, `t7xx_mhccif_mask_get`, and `t7xx_mhccif_h2d_swint_trigger`. The primary handler pair is `t7xx_mhccif_isr_handler` and `t7xx_mhccif_isr_thread`; the top half only wakes the threaded handler, while the thread reads status, acknowledges suspend/resume/deep-sleep-lock interrupts, completes PM waiters, and invokes `t7xx_pci_mhccif_isr` for modem events.

State is mostly hardware register state under `base_addr.mhccif_rc_base`, plus completions in `t7xx_pci_dev`. Dependencies include `t7xx_reg.h` register offsets and bits, PCIe MAC interrupt registration, and modem/FSM logic. Risks include lost interrupts if status is acked before software observes all relevant bits, incorrect mask changes across suspend/resume, and completion wakeups for stale PM requests. Test signals include port-enumeration interrupts, exception interrupts, suspend/resume ACKs, deep sleep lock ACKs, and mask readback after init.
