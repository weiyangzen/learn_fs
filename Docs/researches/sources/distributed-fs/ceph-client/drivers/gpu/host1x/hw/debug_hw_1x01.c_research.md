<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/debug_hw_1x01.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/debug_hw_1x01.c

## Purpose

`debug_hw_1x01.c` implements register-specific debug output for pre-HW6 host1x generations. It reports channel CDMA state, command FIFO contents through sync-register peek controls, and MLOCK ownership.

## Important APIs, Types, And Functions

- `host1x_debug_show_channel_cdma()`: reads DMASTART/DMAEND/DMAPUT/DMAGET/DMACTRL plus CBREAD/CBSTAT, prints active/waiting status, and dumps queued gathers.
- `host1x_debug_show_channel_fifo()`: uses `CFPEEK_CTRL`, pointer, setup, and read registers to decode command FIFO entries.
- `host1x_debug_show_mlocks()`: reads each MLOCK owner register and reports channel, CPU, or unlocked state.

## Control Flow

The CDMA path first checks DMASTOP or missing pushbuffer mapping and returns inactive if true. Otherwise it interprets CBSTAT as either host wait-on-syncpoint, wait-on-syncpoint-base, or active class/offset. FIFO dumping enables peek for the channel, walks read pointer to write pointer with wrap, decodes opcodes, and disables peek afterward.

## State And Persistence Behavior

The file reads hardware registers and temporarily programs CFPEEK control. It does not mutate persistent CDMA/job state.

## Dependencies And Integration Points

It relies on old sync/channel register macros and the shared command decoder from `debug_hw.c`. It is included for `HOST1X_HW < 6`.

## Risks And Test Signals

Peek control must be disabled after use; stale peek state can affect later diagnostics. Field widths differ across old generations, so generated headers must be correct. Test by reading debugfs while channels are idle, waiting, active, and with MLOCKs held.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/debug_hw_1x01.c -->
