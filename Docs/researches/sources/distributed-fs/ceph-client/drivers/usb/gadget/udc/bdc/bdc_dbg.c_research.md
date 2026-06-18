<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_dbg.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_dbg.c

## Purpose
This optional verbose-debug file dumps BDC controller registers, endpoint status registers, the status report ring, and endpoint buffer descriptor lists.

## Important APIs, Types, And Functions
`bdc_dbg_regs()` prints BDC configuration, capability, port, and device context registers. `bdc_dump_epsts()` prints EP status registers 0 through 7. `bdc_dbg_srr()` iterates all status report ring entries and prints their DMA address and four descriptor words. `bdc_dbg_bd_list()` walks each BD table for an endpoint and prints global/local indexes, virtual and DMA addresses, and descriptor words.

## Control Flow
These functions are called from core initialization, endpoint queuing/dequeue paths, and command stop paths when verbose gadget debugging is built. They do not influence transfer flow except for MMIO reads and logging.

## State And Persistence
No state is owned here. The functions observe `struct bdc`, `struct srr`, and `struct bd_list` state plus hardware registers.

## Dependencies And Integration Points
This file depends on `CONFIG_USB_GADGET_VERBOSE` being selected by the Makefile. The fallback inline no-op implementations live in `bdc_dbg.h`, letting the rest of the driver call debug helpers unconditionally.

## Risks
Full descriptor-ring dumps can be noisy and expensive under verbose logging. The functions assume descriptor arrays are allocated and valid at call time; calling after endpoint memory has been freed would be unsafe. One format string for `dvcsb` appears malformed (`0x%x08`), which affects readability but not behavior.

## Test Signals
Build with verbose gadget logging, then inspect logs during probe, endpoint queue/dequeue, stop endpoint, and status report processing. Confirm no debug helper is linked when verbose logging is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_dbg.c -->
