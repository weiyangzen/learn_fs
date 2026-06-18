# sources/distributed-fs/ceph-client/drivers/usb/class/cdc-acm.h

Purpose: defines constants and private data structures for the CDC ACM TTY driver.

Important types and constants: `ACM_TTY_MAJOR` is 166, `ACM_TTY_MINORS` is 256, and `ACM_MINOR_INVALID` marks unallocated state. `USB_RT_ACM` defines class interface control request type. `ACM_NW` and `ACM_NR` set write and read URB ring counts to 16. `struct acm_wb` tracks an outgoing buffer, coherent DMA address, length, URB, owning ACM instance, and in-use flag. `struct acm_rb` tracks an incoming buffer, DMA address, index, and owner. `struct acm` is the driver state object shared by probe, TTY operations, URB callbacks, PM, disconnect, sysfs, and ioctl paths.

Control flow: the header has no executable logic, but its fields define the control flow in `cdc-acm.c`: read/write buffer allocation, URB callback ownership, minor lookup, line coding, delayed work, notification reassembly, modem status wait queues, autosuspend-delayed write anchors, and quirk-dependent behavior.

State and persistence: `struct acm` carries all runtime state for one CDC ACM function: device/interface pointers, TTY port, buffers, DMA handles, free-bitmaps, locks, mutexes, flags, counters, control lines, line coding, minor, suspend count, and quirks. State is in memory only and is destroyed after disconnect and final TTY port release.

Dependencies and integration points: the structures depend on USB core URBs and interfaces, TTY port and async counter types, wait queues, delayed work, anchors, DMA addresses, and CDC line-coding definitions from the including C file.

Risks and test signals: header risks are structure lifetime assumptions and fields accessed from different locking domains. Changes require tests for open/close lifetime, write buffer accounting, read URB bitmap handling, notification reassembly, modem-line ioctls, PM delayed writes, and disconnect cleanup.
