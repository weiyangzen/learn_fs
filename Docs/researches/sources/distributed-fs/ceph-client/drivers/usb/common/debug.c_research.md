# Research: sources/distributed-fs/ceph-client/drivers/usb/common/debug.c

Purpose: provides `usb_decode_ctrl`, an exported helper that formats USB control requests into human-readable strings for tracing and diagnostics.

Important functions: internal decoders cover GET_STATUS, SET/CLEAR_FEATURE, SET_ADDRESS, GET/SET_DESCRIPTOR, GET/SET_CONFIGURATION, GET/SET_INTERFACE, SYNCH_FRAME, SET_SEL, and SET_ISOCH_DELAY. `usb_decode_ctrl_generic` formats type, recipient, direction, request, value, index, and length for vendor, class, unknown, or unrecognized standard requests. `usb_decode_device_feature` and `usb_decode_test_mode` name feature selectors and test modes.

Control flow: `usb_decode_ctrl` dispatches by request type. Standard requests are further dispatched by `bRequest`; unsupported requests fall back to generic formatting. Output is written into the caller-provided buffer with `snprintf` and the same pointer is returned, which lets tracepoint print formatters call it inline.

State and persistence: stateless. The only state is the caller's output buffer. The function expects `wValue`, `wIndex`, and `wLength` already converted to CPU byte order.

Dependencies and integration points: depends on USB chapter 9 constants and is built into `usb-common.o` only under `CONFIG_TRACING`. Tracepoints and debug code can use it to keep control-message output consistent.

Risks: buffer size is caller-managed; comments suggest about 200 bytes. Adding longer strings can truncate output. Missing new standard requests or descriptor types reduces diagnostic quality but should not affect USB behavior. Incorrect recipient handling can mislead debugging of interface/endpoint requests.

Test signals: trace or KUnit-style checks for representative standard, class, vendor, unknown, endpoint-direction, test-mode, and descriptor-type requests. Build with tracing enabled and disabled.
