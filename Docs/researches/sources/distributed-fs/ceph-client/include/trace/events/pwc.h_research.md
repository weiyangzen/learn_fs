# sources/distributed-fs/ceph-client/include/trace/events/pwc.h

Purpose: Defines tracepoints for Philips webcam driver handler entry and exit. It tracks USB request handling around driver-specific control or data paths.

Important APIs/types/functions: `pwc_handler_enter` and `pwc_handler_exit` record the USB device pointer, handler identifier/name, and exit status or return value.

Control flow: The PWC driver emits enter before invoking a handler and exit after completion. Trace output pairs start/end records to diagnose handler latency and failures.

State and persistence: No state is owned. It observes `struct usb_device` and handler-local status while the webcam driver owns the device.

Dependencies and integration points: Depends on USB and tracepoint headers. It integrates with the PWC V4L/USB driver, USB device lifecycle, and media debugging.

Risks and test signals: Risks include tracing after USB disconnect, handler-name lifetime issues, and missing pairing on early returns. Test webcam probe, streaming start/stop, control requests, disconnect during active operation, and handler error paths with tracing enabled.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/pwc.h` completely for this pass (65 lines, 1672 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/pwc.h_research.md`.
