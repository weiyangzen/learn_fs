# sources/distributed-fs/ceph-client/drivers/sbus/char/uctrl.c

Purpose: implements a misc-device driver for the Tadpole TS102 microcontroller interface on Sparcbook 3 systems. It can query microcontroller event and external status and exposes a placeholder ioctl interface.

Important APIs/types/functions: register layouts `struct uctrl_regs` and `struct ts102_regs` describe mapped MMIO. `struct uctrl_txn` describes a microcontroller command transaction, and `struct uctrl_status` caches selected status fields. `enum uctrl_opcode` lists many supported microcontroller commands. Core functions are `uctrl_do_txn()`, `uctrl_get_event_status()`, `uctrl_get_external_status()`, `uctrl_open()`, `uctrl_probe()`, and `uctrl_remove()`. Macros `WRITEUCTLDATA` and `READUCTLDATA` poll FIFO status and access data registers.

Control flow: probe allocates global driver state, maps registers, requests the IRQ, registers `/dev/uctrl`, enables RX-not-empty interrupt bits, logs device info, and performs initial event/external status reads. Opening the device re-reads event and external status under a mutex. Transactions write the opcode and input bytes to the controller FIFO, read an ACK, then read requested output bytes. The interrupt handler currently just returns handled, and ioctl accepts no commands.

State and persistence: global singleton state includes mapped registers, IRQ number, a pending field, and cached status. Hardware state is the TS102 microcontroller FIFO/status/interrupt registers. No persistent storage is changed.

Dependencies and integration: depends on SPARC OF platform probing for node name `uctrl`, SBUS read/write helpers, misc minor `UCTRL_MINOR`, IRQ registration, and the Tadpole hardware protocol.

Risks and test signals: `global_driver` is dereferenced in open without checking probe success or removal races. The read macro's polling condition appears inverted for "receive not empty" and may read before data is ready or after timeout. Debug logging is compiled on unconditionally through `#define DEBUG 1`. The IRQ handler ignores device state, and ioctl is effectively unimplemented despite a large opcode list. Test probe failure cleanup, open after remove prevention, event/external status transaction timing, FIFO timeout behavior, IRQ delivery, misc registration failure, and safe behavior when userland issues unsupported ioctls.
