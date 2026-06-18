# sources/distributed-fs/ceph-client/drivers/usb/musb/musb_host.h

## Purpose

`musb_host.h` defines the host-side queue-head structure and internal host API for the MUSB HCD implementation. It gives `musb_host.c`, virtual hub code, and the core common declarations for scheduling, endpoint queues, root hub control, and host-only stubs. The source was read as a complete 124-line file.

## Important APIs, Types, and Functions

The central type is `struct musb_qh`, which stores usbcore endpoint/device pointers, bound hardware endpoint, ring linkage, transfer offset and segment size, precomputed type/interval/address/hub registers, readiness/type/endpoint/high-bandwidth fields, iso index/frame, and scatterlist iterator state. Helpers include `first_qh` and `next_urb`. Declarations include host IRQ handlers, allocation/setup/cleanup/free, TX/RX handlers, root disconnect, root hub resume/poke, port suspend/reset, finish resume, and hub status/control.

## Control Flow

The header has no executable driver flow except small queue helpers. `first_qh` maps a control or bulk list head to the active queue head. `next_urb` maps a `musb_qh` to the first URB on its usbcore endpoint list.

## State and Persistence Behavior

The queue head is transient scheduling state owned by the HCD. Its fields persist only while an endpoint has queued URBs or is bound to a MUSB hardware endpoint.

## Dependencies and Integration Points

The header depends on scatterlist APIs and usbcore structures. It is included by `musb_host.c` and by core paths needing host stubs; it also declares the `musb_virthub.c` interfaces used by the HCD.

## Risks and Edge Cases

The `musb_qh` contract is shared by scheduling, DMA, PIO, and cleanup paths. Misinterpreting `is_ready`, `mux`, or direction parameters can cause URBs to be started on the wrong hardware endpoint, lost during giveback, or freed while still referenced.

## Test Signals

Build coverage across host-only, gadget-only, and dual-role configs matters because the header supplies stubs. Runtime host tests should exercise multiple URBs per endpoint, bulk ring multiplexing, scatterlist PIO, and endpoint disable/unlink.
