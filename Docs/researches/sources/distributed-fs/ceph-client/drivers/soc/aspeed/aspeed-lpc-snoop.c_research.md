# sources/distributed-fs/ceph-client/drivers/soc/aspeed/aspeed-lpc-snoop.c

## Purpose
This driver captures host writes to configured LPC I/O ports, commonly BIOS port 0x80 progress codes, and exposes captured bytes through per-channel miscdevices.

## Important APIs, Types, And Functions
State is split across `struct aspeed_lpc_snoop`, `struct aspeed_lpc_snoop_channel`, and static channel configs. File operations provide blocking/nonblocking `read`, `poll`, and no seek. IRQ handling is in `aspeed_lpc_snoop_irq()`. Setup helpers include `aspeed_lpc_enable_snoop()` and `aspeed_lpc_disable_snoop()`.

## Control Flow
Probe validates the parent LPC compatible, obtains the syscon regmap and clock, requests the shared IRQ, reads `snoop-ports` DT entries, and enables one or two channels. Each enabled channel allocates a 2048-byte kfifo, registers a miscdevice, programs the snoop port, enables channel interrupts, and optionally sets HICRB enable bits on newer SoCs. IRQ reads pending status, acknowledges it, reads the snooped data byte, pushes it into the channel FIFO discarding oldest on overflow, and wakes readers.

## State, Persistence, And Dependencies
Runtime state includes channel enabled flags, kfifo contents, wait queues, and LPC hardware registers. Dependencies include regmap/syscon, clocks, IRQs, miscdevice, kfifo, poll, and DT `snoop-ports`.

## Integration Points
Userspace reads `/dev/aspeed-lpc-snoop0` and `/dev/aspeed-lpc-snoop1`. The driver binds as a child of ASPEED LPC syscon and uses model data to decide HICRB support.

## Risks
The remove path comments that concurrent reader safety could improve; misc deregistration and FIFO free can race with open readers. FIFO overflow discards old data by design. If no `snoop-ports` entries exist, probe returns `-ENODEV`. Shared IRQ handling returns `IRQ_NONE` when no snoop bit is set.

## Test Signals
Generate LPC writes to configured ports, read blocking and nonblocking devices, poll readiness, verify FIFO discard on overflow, test one-channel and two-channel DTs, remove with open files, and compare AST2400 versus AST2500/2600 HICRB behavior.
