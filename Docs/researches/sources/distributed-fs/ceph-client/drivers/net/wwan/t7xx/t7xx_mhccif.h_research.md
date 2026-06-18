# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_mhccif.h

This header exposes MHCCIF register-control helpers and defines `D2H_SW_INT_MASK`, the set of modem-originated software interrupts handled by the T7xx driver. The mask includes exception stages, port enumeration, PM ACKs, and asynchronous MD/AP handshake bits.

Its functions are thin register operations around mask set/clear/get, status read, initialization, and host-to-device software interrupt triggering. Integration points include `t7xx_pci.c` for PM, `t7xx_modem_ops.c` for exception/handshake routing, and `t7xx_state_monitor.c` for FSM events. The header has no persistent state, but it defines the interrupt contract that controls persistent modem lifecycle state. Risks are missing a new bit in `D2H_SW_INT_MASK` or triggering the wrong H2D channel. Tests should verify mask programming, status filtering, and all H2D/D2H channels used by reset, exception, port enumeration, and PM.
