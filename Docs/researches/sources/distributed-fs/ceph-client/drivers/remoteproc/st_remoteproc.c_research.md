# sources/distributed-fs/ceph-client/drivers/remoteproc/st_remoteproc.c

## Purpose
Platform driver for ST ST40/ST231 remote processors. It controls clocks, reset lines, boot address programming through syscon, optional mailbox-based virtqueue signaling, reserved-memory carveouts, and ELF firmware loading through the remoteproc core.

## Important APIs, Types, And Functions
Defines `struct st_rproc_config` for SoC reset and boot-mask differences and `struct st_rproc` for resets, clock, boot syscon, and mailbox channels. `st_rproc_ops` supplies `kick`, `start`, `stop`, `parse_fw`, and default ELF callbacks. Probe/remove are `st_rproc_probe()` and `st_rproc_remove()`.

## Control Flow
Probe allocates an rproc, selects match data, parses reset controls, clock frequency, and boot syscon, prepares the clock, detects current reset state, marks already-enabled hardware running, otherwise sets clock rate, optionally requests four mailbox channels, and registers the rproc. Firmware parsing enumerates reserved memory: normal regions become ioremap-backed carveouts and `vdev0buffer` becomes a reserved-memory DMA pool, then ELF resource-table loading runs.

Start writes masked boot address bits, enables the clock, deasserts software reset, and deasserts power reset when present. Stop asserts resets and disables the clock. Mailbox callbacks route vq0/vq1 events to `rproc_vq_interrupt()`, and `kick()` sends the virtqueue ID on the TX channel.

## State And Persistence Behavior
Private state persists in `rproc->priv`. Clock preparation lasts until remove; clock enable is runtime. Reserved memory entries are added during firmware parse and cleaned by core. Mailbox channels are held from probe to remove. Already-running hardware is represented by incrementing `power` and setting `RPROC_RUNNING`.

## Dependencies And Integration Points
Depends on compatibles `st,st40-rproc` and `st,st231-rproc`, reset controller names, `clock-frequency`, `st,syscfg`, optional `mbox-names`, reserved memory, regmap/syscon, mailbox, and remoteproc ELF helpers. It integrates with virtio/rpmsg through mailbox kicks.

## Risks
The start error path after power-reset failure should be reviewed for exact reset unwinding. Mailbox support is optional, but rpmsg firmware needs valid TX/RX channels. Already-running detection uses reset status and does not use the detached attach flow. Reserved-memory classification depends on the `vdev0buffer` naming convention.

## Test Signals
Test ST40/ST231 match data, missing/deferred resets/clocks, boot-address mask programming, already-running probe, start/stop reset sequencing, reserved-memory parsing, optional no-mailbox operation, vq0/vq1 mailbox interrupts, and rpmsg `kick()` traffic.
