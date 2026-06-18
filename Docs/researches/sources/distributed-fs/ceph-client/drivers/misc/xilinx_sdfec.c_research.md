# sources/distributed-fs/ceph-client/drivers/misc/xilinx_sdfec.c

## Purpose
Platform misc character driver for Xilinx SD-FEC16 IP. It maps registers, enables clocks, parses DT stream/FEC configuration, exposes `/dev/xsdfecN`, and lets userspace control start/stop, Turbo/LDPC programming, IRQs, polling, and error counters.

## Important APIs, Types, And Functions
- `struct xsdfec_dev` owns the miscdevice, clocks, MMIO base, cached config, wait queue, state, IRQ flag, and ISR/ECC counters.
- `xsdfec_dev_ioctl()` dispatches the SDFEC UAPI commands.
- `xsdfec_reg0_write()` through `xsdfec_reg3_write()` and `xsdfec_table_write()` program LDPC code metadata and SC/LA/QC tables.
- `xsdfec_irq_thread()` masks, reads, clears, counts, updates state, wakes poll waiters, and unmasks interrupts.
- `xsdfec_parse_of()`, `xsdfec_clk_init()`, `xsdfec_probe()`, and `xsdfec_remove()` handle platform integration for `xlnx,sd-fec-1.1`.

## Control Flow
Probe allocates state, enables clocks, maps MMIO, gets an optional IRQ, parses required DT properties, syncs hardware config, registers a threaded IRQ, allocates an ID, and registers a misc device. Userspace drives the device through ioctl. Start checks hardware FEC mode before enabling AXI stream interfaces. Stop clears input stream enables. LDPC additions validate mode, started state, write protection, register ranges, and table bounds before writing hardware.

## State And Persistence
State is hardware register contents plus cached `xsdfec_config`, `enum xsdfec_state`, poll flags, and error counters. Stats persist until `XSDFEC_CLEAR_STATS` or removal. Device IDs are IDA allocated. No on-disk state is written.

## Dependencies And Integration Points
Uses platform/OF, common clocks, miscdevice, wait queues, threaded IRQs, MMIO accessors, user-copy helpers, `pin_user_pages_fast()`, and `<uapi/misc/xilinx_sdfec.h>`.

## Risks And Edge Cases
Pinned user table writes require strict depth/offset arithmetic. IRQ mask-register semantics must match hardware. The source snapshot contains apparent duplicated/extra lines and braces around config/table/clock paths and duplicate `XSDFEC_GET_TURBO` handling, which would be compile or cleanup risks if active. Optional clock handling should be checked against the kernel clock API.

## Test Signals
Build with the SDFEC config enabled. Runtime checks: `/dev/xsdfecN` creation, ioctl start/stop/config/stats, LDPC validation failures, poll wakeups after injected IRQ/ECC events, and probe unwind for clock/IRQ failures.
