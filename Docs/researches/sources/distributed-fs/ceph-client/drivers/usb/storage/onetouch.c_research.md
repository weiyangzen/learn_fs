<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/onetouch.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/onetouch.c

## Purpose

`onetouch.c` supports Maxtor OneTouch USB hard drives that expose a storage interface plus a hardware button. It uses the standard usb-storage storage path while registering an input device for the interrupt endpoint that reports the button.

## Important APIs, Types, and Functions

`struct usb_onetouch` stores the input device, USB device, interrupt URB, coherent packet buffer, DMA address, physical/name strings, and open state. `onetouch_connect_input()` creates and registers the input device, `usb_onetouch_irq()` decodes packets, `usb_onetouch_open()` and `usb_onetouch_close()` start/stop the interrupt URB, `usb_onetouch_pm_hook()` handles suspend/resume, and `onetouch_release_input()` frees resources.

## Control Flow

Probe calls `usb_stor_probe1()` and then `usb_stor_probe2()` without replacing the normal storage protocol or transport. The unusual-device table supplies the init hook that calls `onetouch_connect_input()`. Input setup validates that endpoint 2 is interrupt-in, allocates a 2-byte coherent buffer and URB, builds a name and physical path, configures an `EV_KEY`/`KEY_PROG1` input device, and registers it. When open, the URB is submitted continuously; each successful packet reports button state from bit 1 of byte 0 and resubmits.

## State and Persistence Behavior

The only driver-owned state is the live input allocation stored in `us->extra`. The button state is transient and emitted through the Linux input subsystem. Suspend kills the URB if the input device is open; resume resubmits it. There is no persistent storage behavior beyond the underlying usb-storage disk handled by the core.

## Dependencies and Integration Points

The file depends on usb-storage probe/lifecycle hooks, the input subsystem, coherent USB DMA allocation, interrupt URBs, PM hooks in `struct us_data`, and `unusual_onetouch.h`. It integrates one USB interface with both SCSI storage and input event reporting.

## Risks and Test Signals

Risk areas are endpoint assumptions, URB resubmission after transient errors, open-state handling across suspend/resume/disconnect, and resource cleanup after partial allocation or failed input registration. Tests should verify storage still probes normally, button events appear as `KEY_PROG1`, URB shutdown during disconnect is race-free, suspend/resume does not double-submit or lose open state, and malformed endpoint layouts return `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/onetouch.c -->
