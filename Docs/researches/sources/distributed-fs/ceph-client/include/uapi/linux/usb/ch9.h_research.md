# sources/distributed-fs/ceph-client/include/uapi/linux/usb/ch9.h

Purpose: Provides the central USB device-model UAPI: control request constants, standard descriptor structures, class codes, endpoint helpers, capability descriptors, speeds, states, and link-power definitions from USB chapter 9 and related ECNs/specs.

Important APIs/types/functions: Defines directions, request types/recipients, standard and wireless/PD requests, feature selectors, status bits, `struct usb_ctrlrequest`, descriptor type constants, packed descriptor structs for device/config/string/interface/endpoint/qualifier/OTG/debug/IAD/security/BOS/capabilities/PD/PTM/wireless/authentication, endpoint transfer/sync/usage masks, inline endpoint classification helpers, SuperSpeed companion helpers, speed/state/link-state enums, and LPM selector structures.

Control flow: USB host/gadget code uses `usb_ctrlrequest` for setup packets, parses descriptors returned by GET_DESCRIPTOR, sets configuration/interface/feature state, and classifies endpoints through inline helpers. Device state progresses through attached, powered, default, address, configured, suspended, and related wireless/auth states.

State and persistence behavior: The header defines wire-format descriptors and runtime state labels. Actual state lives in USB devices, host controller drivers, and gadget functions; descriptors may be static firmware/gadget data.

Dependencies and integration points: Includes `linux/types.h` and `asm/byteorder.h`; used by usbfs, kernel USB host APIs, gadget APIs, FunctionFS, raw gadget, class drivers, and userspace descriptor tooling.

Risks: All descriptors are packed and many fields are little-endian on the wire. Device/config descriptors read from `/dev/bus/usb` are an exception where the kernel may convert selected fields. Endpoint helper correctness depends on masks and endian conversion. ABI constants are broadly consumed and must not change.

Test signals: Descriptor layout static assertions, endpoint helper unit tests, enumeration against USB2/USB3 devices, BOS/capability parsing, LPM timeout validation, usbfs/gadget descriptor round trips, and malformed descriptor fuzzing.
