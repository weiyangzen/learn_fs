# sources/distributed-fs/ceph-client/drivers/usb/musb/musb_io.h

## Purpose

`musb_io.h` defines the platform-abstracted register and FIFO I/O interface for the MUSB core. It lets common host/gadget code call generic MUSB register helpers while platform glue supplies address translation and special read/write implementations. The source was read as a complete 49-line file.

## Important APIs, Types, and Functions

The key type is `struct musb_io`, with callbacks for `ep_offset`, `ep_select`, `fifo_offset`, `read_fifo`, `write_fifo`, `busctl_offset`, `get_toggle`, and `set_toggle`. It declares global function pointers `musb_readb`, `musb_writeb`, `musb_clearb`, `musb_readw`, `musb_writew`, `musb_clearw`, plus `musb_readl` and `musb_writel`. The `musb_ep_select` macro routes endpoint selection through `musb->io.ep_select`.

## Control Flow

There is no independent control flow. Common code selects endpoints and accesses registers through these callbacks/function pointers, allowing standard flat-register controllers and indexed or remapped controllers such as sunxi to share host/gadget logic.

## State and Persistence Behavior

The header owns no storage except declared function pointers defined elsewhere. Runtime state is the platform-provided `musb->io` callback table and global register accessor pointers.

## Dependencies and Integration Points

It depends on Linux I/O accessors and MUSB structure declarations. It integrates with platform ops in glue drivers, core register helpers, endpoint programming, FIFO movement, host toggle handling, and bus-control addressing for external hubs.

## Risks and Edge Cases

Because register access is indirect, callback mismatches can corrupt the wrong register silently. The `musb_ep_select` macro assumes a visible `musb` variable in scope, which is a local coding convention rather than a self-contained API. Platform-specific layouts must keep offsets, busctl mapping, and toggle semantics consistent with common code expectations.

## Test Signals

Signals are compile coverage for platform glue, tracing of register reads/writes, enumeration on indexed and non-indexed controllers, hub/multipoint addressing tests, and endpoint toggle preservation across host transfers.
