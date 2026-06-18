# sources/distributed-fs/ceph-client/drivers/tty/mips_ejtag_fdc.c

## Purpose
`mips_ejtag_fdc.c` implements tty, console, early-console, and optional KGDB support for MIPS EJTAG Fast Debug Channels. It exposes up to 16 per-CPU debug channels as raw ttys, encodes byte streams into FDC words, drains RX from hardware, writes TX asynchronously from a CPU-pinned kthread, and supports IRQ or polling operation.

## Important APIs, Types, And Functions
- Register macros define FDC access, configuration, status, RX, and per-channel TX registers plus FIFO and interrupt thresholds.
- `struct fdc_word`, `mips_ejtag_fdc_encode`, and `mips_ejtag_fdc_decode` implement compact byte packing into 32-bit FDC words.
- `struct mips_ejtag_fdc_tty_port` stores tty-port state, RX buffer/lock, circular TX state, and empty completion.
- `struct mips_ejtag_fdc_tty` stores CPU, register mapping, ports, waitqueue, writer thread, FIFO sizes, IRQ/polling state, and optional sysrq state.
- Console helpers support normal and early FDC consoles.
- `mips_ejtag_fdc_put`, `mips_ejtag_fdc_put_chan`, `mips_ejtag_fdc_handle`, `mips_ejtag_fdc_isr`, and `mips_ejtag_fdc_tty_timer` are the core data paths.
- Probe and CPU hotplug hooks are `mips_ejtag_fdc_tty_probe`, `mips_ejtag_fdc_tty_cpu_down`, and `mips_ejtag_fdc_tty_cpu_up`.

## Control Flow And State
Console initialization probes CDMM type `0xfd` and registers the `fdc` console. Device probe maps registers, reads FIFO sizing, disables interrupts, allocates a 16-minor raw tty driver for the CPU, initializes ports and locks, caches console register pointers, starts a writer kthread pinned to the FDC CPU, then either enables RX interrupts or starts a pinned polling timer.

TTY writes enter a per-port circular buffer, update aggregate `xmit_total`, and wake the writer. The kthread waits for data and TX FIFO space, enables TX-not-full interrupts when needed, selects non-empty channels round-robin, encodes up to four bytes, writes the per-channel TX register, updates buffer pointers, and wakes tty writers.

RX handling is shared by IRQ and timer paths. It drains RX words, decodes bytes, handles optional KGDB Ctrl-C and console sysrq sequences, inserts bytes into active tty flip buffers, and wakes the writer when TX FIFO space returns.

## State And Persistence Behavior
Runtime state includes mapped FDC registers, tty ports, TX circular buffers, RX buffers allocated while ports are active, interrupt configuration, polling timer state, and cached per-CPU console register pointers. No host storage is used; hardware registers persist until CPU down/remove or reconfiguration.

## Dependencies And Integration Points
The driver depends on MIPS CDMM discovery, CP0 FDC interrupt cause bits, Linux tty/console/kgdb/sysrq APIs, kthreads, timers, raw spinlocks, and per-CPU IRQ constraints. It registers as a built-in MIPS CDMM driver.

## Risks And Edge Cases
The FDC interrupt may be shared and non-maskable per device, requiring `IRQF_NO_THREAD` and raw locks. Console writes busy-wait for FIFO space with local interrupts disabled. Polling and writer threads must stay on the correct CPU because channels are per-CPU. TX shutdown waits for pending data to drain, so a stuck FIFO can delay close.

## Test Signals
Validate console and early console output, `ttyFDC*` registration, RX/TX on multiple channels with round-robin fairness, polling fallback without IRQ, CPU down/up restart, sysrq/KGDB paths, and clean close/remove with no live timer or kthread.
