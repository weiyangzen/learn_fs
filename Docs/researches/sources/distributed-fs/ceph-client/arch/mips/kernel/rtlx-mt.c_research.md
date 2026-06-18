# sources/distributed-fs/ceph-client/arch/mips/kernel/rtlx-mt.c

## Purpose
Initializes RTLX support for MIPS MT/APRP systems by registering character devices, wiring VPE notifications, and handling inter-VPE software interrupts.

## Important APIs, Types, and Functions
- `rtlx_module_init()` creates `/dev/rtlx*` character devices and registers the RTLX interrupt path.
- `rtlx_module_exit()` destroys devices and unregisters the char major.
- `rtlx_interrupt()` acknowledges/reenables the RTLX software interrupt and wakes all channel queues.
- `_interrupt_sp()` signals the service processor VPE by setting C_SW0 in VPE1 cause.
- `rtlx_dispatch()` dispatches pending RTLX software interrupts through `do_IRQ()`.

## Control Flow
Module init rejects non-MIPS-MT CPUs and systems without reserved AP/SP TCs, registers a dynamic char major using `rtlx_fops`, initializes waitqueues/mutexes/open counters for each RTLX channel, creates devices, registers VPE start/stop notifications, assigns `aprp_hook` on vectored-interrupt CPUs, and requests the RTLX IRQ. The IRQ handler temporarily disables VPEs, enables the software interrupt status bit, restores VPE state, and wakes reader/writer queues. Writes call `_interrupt_sp()` from `rtlx.c` to notify the SP.

## State and Persistence
Runtime state includes char major, device nodes, waitqueues in `channel_wqs`, `rtlx_notify`, `aprp_hook`, and VPE interrupt cause/status bits. No persistent storage.

## Dependencies and Integration Points
Depends on MIPS MT/VPE APIs, `mt_class`, `rtlx_fops` from `rtlx.c`, `aprp_cpu_index()`, Linux IRQ/device/char-dev APIs, and vectored interrupt support.

## Risks
Failure cleanup must destroy already created devices and unregister the char major. `request_irq()` currently passes `rtlx` as dev_id, which may be NULL before shared memory is initialized; this must remain compatible with IRQ free semantics. Non-vectored interrupt CPUs are rejected after devices are created, so cleanup path matters.

## Test Signals
On supported MIPS MT systems, `/dev/rtlx0..` should appear, SP notifications should wake reads/writes, and unloading should remove devices. Unsupported systems should return `-ENODEV` with clear warnings.
