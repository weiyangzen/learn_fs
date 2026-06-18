# sources/distributed-fs/ceph-client/include/uapi/linux/uhid.h

Purpose: Defines the userspace HID device ABI for `/dev/uhid`, allowing a userspace process to create and drive HID devices.

Important APIs/types/functions: Event types cover create/destroy, start/stop, open/close, output, input, get/set report and replies, with legacy aliases retained. `uhid_create2_req` embeds device identity and report descriptor. `uhid_start_req` returns numbered-report flags. Report/input/output structures carry up to `UHID_DATA_MAX` bytes. `struct uhid_event` is a packed tagged union of all request/reply payloads.

Control flow: Userspace writes `UHID_CREATE2`, then handles kernel-generated lifecycle/report/output events read from the device and writes `UHID_INPUT2`, report replies, or destroy events. The kernel extends short events with zeroes and userspace must do the same for short reads.

State and persistence behavior: The virtual HID device exists while the uhid file/session remains active or until destroy. Open/close and start/stop events reflect kernel HID consumer state.

Dependencies and integration points: Includes `linux/input.h`, `linux/types.h`, and `linux/hid.h`; integrates with HID core, input subsystem, Bluetooth/USB emulation layers, and userspace device emulators.

Risks: Packed ABI contains obsolete pointer-based legacy create fields; new code should use `UHID_CREATE2`. Report sizes and IDs must match descriptors. Blocking report requests need timely replies to avoid stalled clients.

Test signals: Create virtual HID devices with numbered/un-numbered reports, send input, handle output and get/set report, verify legacy compatibility, short write/read zero extension, and 32/64-bit packing.
