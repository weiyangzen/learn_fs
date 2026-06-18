# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_loopback.c

## Purpose

`f_loopback.c` implements the USB gadget loopback function used by Gadget Zero style testing. It exposes one vendor-specific interface with a bulk OUT endpoint and a bulk IN endpoint. Data received from the host on OUT is queued back to the host on IN using the same buffer, making it a compact test vehicle for endpoint autoconfiguration, request queueing, transfer completion, and configfs option plumbing.

## Important APIs, Types, And Functions

The central runtime type is `struct f_loopback`, which embeds `struct usb_function` and stores the selected IN/OUT endpoints plus `qlen` and `buflen` copied from `struct f_lb_opts` in `g_zero.h`.

Descriptor objects include one interface descriptor, full-speed bulk source/sink endpoint descriptors, high-speed descriptors with 512-byte max packet size, super-speed descriptors with 1024-byte max packet size plus companion descriptors, and a single English interface string.

Major functions:

- `loopback_bind()` allocates interface/string IDs, autoconfigures endpoints from the full-speed descriptors, copies endpoint addresses into high/super-speed descriptors, assigns descriptor arrays with `usb_assign_descriptors()`, and logs selected endpoints.
- `loopback_alloc()` creates a function instance, increments the configfs option refcount, copies `bulk_buflen` and `qlen`, installs callbacks, and defaults zero `qlen` to 32.
- `enable_loopback()` enables both endpoints by speed and prequeues transfer pairs.
- `alloc_requests()` allocates `qlen` pairs of requests. Each OUT request owns the data buffer; the paired IN request points at the same buffer. The two requests reference each other through `context`.
- `loopback_complete()` is the ping-pong completion handler that turns an OUT completion into an IN queue and an IN completion back into a fresh OUT queue.
- `loopback_set_alt()` restarts the function for altsetting zero by disabling and enabling endpoints.
- `loopback_disable()` and `disable_loopback()` stop both endpoints.
- Configfs handlers expose writable `qlen` and `bulk_buflen` while no function references exist.

## Control Flow

Configfs instance creation starts with `loopback_alloc_instance()`, which allocates `f_lb_opts`, initializes its mutex and defaults from `GZERO_BULK_BUFLEN` and `GZERO_QLEN`, and registers the configfs attributes. Attribute stores parse unsigned integers and return `-EBUSY` if a function has already been allocated from the instance.

When the function is allocated, `loopback_alloc()` creates `struct f_loopback`, increments `opts->refcnt`, copies option values, sets the function name to `"loopback"`, and installs bind/set_alt/disable/free callbacks. `lb_free_func()` decrements the option refcount, frees descriptors, and releases the function object.

Binding assigns one interface number and one string ID, then autoconfigures a bulk IN endpoint and a bulk OUT endpoint. The full-speed endpoint descriptors are the templates used for autoconfig; assigned addresses are propagated to high-speed and super-speed descriptors. Descriptor arrays are then assigned for full, high, super, and super-plus speeds.

Enablement configures endpoint descriptors for the current gadget speed, enables both endpoints, stores `loop` as `ep->driver_data`, and calls `alloc_requests()`. Each queue slot consists of one IN request and one OUT request. The OUT request is allocated with a data buffer of `buflen`; the IN request reuses that buffer and has its length set later from `out_req->actual`. Initial traffic waits on all OUT requests.

On OUT completion, `loopback_complete()` retrieves the paired IN request, sets `in_req->zero` when the host sent a short packet, sets `in_req->length` to the received byte count, and queues it on the IN endpoint. On IN completion, it retrieves the paired OUT request and requeues it to receive more data. On queue failure or terminal request statuses (`-ECONNABORTED`, `-ECONNRESET`, `-ESHUTDOWN`) it frees both paired requests through the opposite endpoint and the current endpoint helper.

## State And Persistence Behavior

Runtime state is limited to endpoint pointers, copied queue depth, copied buffer length, and queued USB requests. No data persists beyond the life of a transfer; buffers are recycled between OUT and IN until endpoint disable or error. Configfs option state persists in memory while the function instance exists. `f_lb_opts->refcnt` prevents changing `qlen` or `bulk_buflen` after a function has been allocated.

There is intentionally no explicit list of submitted requests. The code relies on the UDC/composite endpoint disable path to complete or purge queued requests; the completion handler frees request pairs on error statuses. This small state model is simple but makes correctness depend on UDC request completion semantics during disconnect and disable.

## Dependencies And Integration Points

The file depends on the USB composite framework, endpoint autoconfiguration, `config_ep_by_speed()`, `usb_ep_enable()`, `usb_ep_queue()`, descriptor assignment/free helpers, configfs attribute macros, and shared Gadget Zero helpers/types from `g_zero.h` and `linux/usb/func_utils.h`. It registers a USB function named `Loopback` with `DECLARE_USB_FUNCTION()` and also exposes `lb_modinit()`/`lb_modexit()` for Gadget Zero module initialization.

## Risks And Edge Cases

The important risks are around request-pair lifetime and option bounds. `qlen` and `bulk_buflen` accept any `u32`; very large values can create memory pressure because enablement allocates `qlen` buffers of `buflen` bytes. `qlen == 0` is normalized to 32 only at function allocation; later stores before allocation can set zero and still get the default. The completion handler assumes `req->context` always points at its paired request and frees both sides on errors, so any future change to allocation or queuing must preserve that invariant. High-speed descriptor order differs from full-speed order (`source` before `sink` in the array), but endpoint addresses are explicitly assigned and should be verified against enumeration behavior.

## Test Signals

Tests should bind the loopback function at full/high/super speed and verify descriptor endpoint addresses, packet sizes, and interface string. Functional tests should send host OUT transfers of zero length, short packets, exact maxpacket multiples, and larger buffers, then verify the same bytes return through IN. Stress tests should vary `qlen` and `bulk_buflen`, disconnect while requests are queued, force endpoint queue failures if possible with a dummy UDC, and confirm configfs stores return `-EBUSY` after allocation and parse errors for invalid input.
