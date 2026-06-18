# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/supern_2.h

Purpose: Defines the AMD Supernet II/Supernet III FORMAC+ MAC, PLC/ELM physical-layer, descriptor, register, bitfield, command, status, timing, and BIST constants used by the `skfp` FDDI adapter driver. It is the hardware ABI map for the lower-level MAC/PHY code.

Important APIs/types/functions: This header exports no functions, but defines descriptor unions `rx_descr`, `tx_descr`, `tx_pointer`, and `struct tx_queue`; FORMAC register offsets such as `FM_ST1U`, `FM_ST2U`, `FM_MDREG1`, `FM_MDREG2`, `FM_MDREG3`, queue pointer registers, address-filter registers, and command registers; descriptor masks such as `RD_S_MSVALID`, `RX_FS_LLC`, `TD_C_MORE`, and `TD_C_XDONE`; PLC registers such as `PL_CNTRL_A`, `PL_CNTRL_B`, `PL_STATUS_A`, `PL_INTR_EVENT`; PLC state and interrupt masks; timing defaults `TP_C_MIN`, `TP_T_OUT`, `TP_LC_LENGTH`, `TP_NS_MAX`; and conversion macros `MSTOBCLK()` and `MSTOTVX()`.

Control flow: There is no executable control flow. Runtime code uses these symbolic constants to pack/unpack DMA descriptors, drive FORMAC commands, interpret MAC/PLC interrupts, configure receive queues and frame filtering, and program physical connection timers.

State and persistence behavior: The header owns no runtime state. Its constants describe persistent hardware-visible state in device registers, descriptor rings, PLC state machines, address filter CAMs, and MAC counters. Endianness-dependent bitfield layouts in the descriptor unions mirror how 32-bit status/control words appear in memory.

Dependencies and integration points: Used by `hwmtm.c`, `hwt.c`, `pcmplc.c`, MAC code, and board I/O helpers via `ADDR()`, `FM_A()`, and `PLC()`. It depends on compile-time feature switches such as `PCI`, `SUPERNET_3`, `MOT_ELM`, `LITTLE_ENDIAN`, and `TAG_MODE`. Its register constants also align with `targethw.h`, `skfbi.h`, `fplus.h`, and `fplustm.h`.

Risks: Bit positions and register offsets are correctness-critical; a wrong value can corrupt DMA ownership, miss interrupts, or misprogram physical-layer signaling. The descriptor bitfields depend on compiler bitfield layout and endian guards, so most code also uses explicit masks. Several Supernet III notes document changed or reserved meanings, making mixed-chip support risky. Interrupt event registers that clear on read require callers to use these definitions in the right order.

Test signals: Build coverage for both Supernet II/III and endian configurations; descriptor ring init and DMA completion tests; MAC receive status decoding for LLC/SMT/MAC/error frames; PLC interrupt decoding for PCM code, break, enabled, LEM, and elasticity errors; hardware bring-up that verifies BIST signatures and address-filter behavior.
