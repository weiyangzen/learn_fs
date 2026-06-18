<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ccid.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/ccid.h

Purpose: defines the USB Chip/Smart Card Interface Device class code and packed CCID functional descriptor layout.

Important APIs and types: `USB_INTERFACE_CLASS_CCID` is class `0x0b`. `struct ccid_descriptor` mirrors the CCID descriptor fields including spec version, slot/voltage/protocol support, clock/data-rate ranges, IFSD, sync/mechanical/features bitmaps, message length, class envelope/get-response values, LCD layout, PIN support, and busy-slot count.

Control flow: CCID drivers parse this descriptor during probe to determine supported card slots, protocols, rates, message size, and optional PIN/LCD features.

State and persistence: no state is stored here. Descriptor values are device-provided capabilities cached by drivers.

Dependencies and integration points: depends on `linux/types.h` for packed little-endian fields. It integrates with USB smart-card reader drivers and user-facing CCID stacks.

Risks and test signals: risks include trusting malformed descriptor lengths, endian mistakes for capability bitmaps, and feature flags inconsistent with endpoint behavior. Test probe against diverse readers, descriptor fuzzing, multi-slot handling, and maximum message length enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ccid.h -->
