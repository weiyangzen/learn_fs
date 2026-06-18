# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_reg.h

This header is the T7xx hardware register and bitfield map. It defines MHCCIF base offsets and H2D/D2H channels, PCIe chip/ATR/PM/status/interrupt registers, device stages and link-kernel events, host events, EXT_INT IDs, and DPMAIF UL/DL/AO register offsets and masks.

The file has no functions, but it is the dependency root for PCIe MAC programming, MHCCIF, PCI PM, modem reset, DPMAIF TX/RX, and FSM boot-stage handling. Persistent behavior is hardware register state: writing these offsets changes interrupt delivery, address translation, ASPM/deep-sleep state, DPMAIF queues, BAT/PIT/DRB rings, and modem lifecycle status.

Risks are high because constants are hardware ABI. Notable concerns include duplicate `MISC_RESET_TYPE_PLDR` definition, similar mask names (`MKS` vs `MSK` typo in one DLQ timeout macro), bitfield width assumptions, and coupling to register translation math in PCIe MAC/PCI code. Test signals include register readback after init, ATR access, MHCCIF interrupt exchange, PM resource status polling, DPMAIF queue setup, and suspend/resume across all documented device stages.
