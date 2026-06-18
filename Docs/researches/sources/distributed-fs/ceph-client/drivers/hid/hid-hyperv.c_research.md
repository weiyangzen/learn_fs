# sources/distributed-fs/ceph-client/drivers/hid/hid-hyperv.c

Implements the Microsoft Hyper-V synthetic HID mouse/input driver. It speaks the VMBus synthetic input protocol, retrieves HID descriptors from the host, creates a virtual HID device, and forwards host input reports into HID core.

Protocol structs model request/response, device info, ACK, and input reports inside pipe messages. `struct mousevsc_dev` stores VMBus state, completions, protocol buffers, descriptor copies, HID device pointer, and input buffer. `mousevsc_connect_to_vsp()` negotiates version 2.0 and waits for device info. `mousevsc_on_receive()` handles protocol responses, descriptor info, and input reports. `mousevsc_hid_parse()` feeds the host report descriptor to HID core. `mousevsc_probe()` opens VMBus, negotiates, allocates a `BUS_VIRTUAL` HID device, and adds it.

Module init registers the virtual HID driver and VMBus driver. Channel callbacks iterate packets and forward input reports after `init_complete`. Remove closes VMBus, stops/destroys HID, and frees descriptors. Suspend closes the channel; resume reopens and renegotiates.

State is runtime-only in `mousevsc_dev`, with descriptor copies refreshed after hibernation/resume. Wakeup is enabled on the VMBus device. Dependencies include Hyper-V VMBus APIs, HID low-level driver API, completions, PM wakeup, and virtual bus matching.

Risks include host-controlled descriptors/reports, protocol timeouts, raw requests stubbed to success, and resume relying on existing HID state. Test signals include negotiation, timeouts, malformed packet sizes, input forwarding, descriptor workaround byte 14, resume, wakeup, and partial-probe removal.
