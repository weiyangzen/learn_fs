# sources/distributed-fs/ceph-client/drivers/usb/musb/musb_gadget.h

## Purpose

`musb_gadget.h` is the peripheral-side internal interface for MUSB gadget support. It declares gadget IRQ and lifecycle entry points used by the core, defines request and endpoint state containers used by `musb_gadget.c` and `musb_gadget_ep0.c`, and provides no-op stubs when gadget or dual-role support is not built. The source was read as a complete 116-line file.

## Important APIs, Types, and Functions

The header declares `musb_g_ep0_irq`, `musb_g_tx`, `musb_g_rx`, `musb_g_reset`, `musb_g_suspend`, `musb_g_resume`, `musb_g_wakeup`, `musb_g_disconnect`, `musb_gadget_cleanup`, and `musb_gadget_setup` for enabled configurations. It defines `enum buffer_map_state`, `struct musb_request`, `struct musb_ep`, `to_musb_request`, `to_musb_ep`, `next_request`, `musb_alloc_request`, `musb_free_request`, `musb_g_ep0_ops`, `musb_g_giveback`, and `musb_ep_restart`.

## Control Flow

The header has no runtime flow, but it defines the contracts used by the gadget implementation. Core interrupt dispatch calls the declared IRQ/endpoint handlers. Gadget endpoint operations allocate `struct musb_request`, attach them to `struct musb_ep.req_list`, and use `next_request` to find the active request.

## State and Persistence Behavior

`struct musb_request` wraps `struct usb_request` with list membership, owning endpoint/controller pointers, direction, endpoint number, and DMA mapping state. `struct musb_ep` stores the Linux `usb_ep`, hardware endpoint backlink, descriptor/type/maxpacket, DMA channel, request list, wedge state, busy flag, and high-bandwidth multiplier. All state is in-memory controller state.

## Dependencies and Integration Points

The header depends on Linux list support and USB gadget/core types included by surrounding MUSB headers. It integrates with `musb_gadget.c`, `musb_gadget_ep0.c`, and `musb_core.h`; the stubs let host-only builds compile without gadget code.

## Risks and Edge Cases

The main risks are structure contract drift between EP0 and non-EP0 gadget code, misuse of `busy` semantics during callbacks, and incorrect assumptions around shared FIFO endpoints where one `musb_hw_ep` may expose bidirectional gadget capabilities.

## Test Signals

Build matrix coverage for gadget-only, host-only, and dual-role configurations is the key signal. Runtime tests should confirm request allocation/free, EP0 and non-EP0 queue progression, and correct no-op behavior in host-only builds.
