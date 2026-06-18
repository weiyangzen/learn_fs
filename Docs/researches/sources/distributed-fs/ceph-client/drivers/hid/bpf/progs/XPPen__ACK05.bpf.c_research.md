# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/XPPen__ACK05.bpf.c

## Purpose
This program fixes the XPPen/Hanvon Ugee ACK05 shortcut remote. The device normally emits programmable buttons as ambiguous keyboard shortcuts; the program switches it into raw mode, disables normal keyboard/stylus descriptors, appends a fixed vendor descriptor describing pad and battery reports, and rewrites raw vendor reports into tablet-pad and battery events.

## Important APIs, Types, And Functions
The match is USB UGEE VID `0x28BD`, PID `0x0202`; it applies both direct and dongle connections. The file enables async support with `HID_BPF_ASYNC_MAX_CTX 1` and `hid_bpf_async.h`. Known descriptor sizes are wired pad 102, dongle pad 177, stylus 109, and vendor 36. `ack05_fix_rdesc()` appends `fixed_rdesc_vendor[]` to the vendor descriptor or disables non-vendor descriptors. `switch_to_raw_mode()` sends a 32-byte output report through `hid_bpf_hw_output_report()`. `ack05_fix_events()` handles reconnect, raw pad, and raw battery reports. `probe()` initializes async support and immediately switches to raw mode for the vendor descriptor.

## Control Flow
Descriptor fixup appends the fixed pad/battery descriptor after the vendor descriptor to preserve output reports required for raw-mode commands. Non-vendor descriptors are renamed as disabled and replaced with a fixed-size vendor report. Probe accepts all four known descriptor sizes; for the vendor descriptor it allocates a HID context, calls `HID_BPF_ASYNC_INIT()`, sends the raw-mode magic report, and releases the context. Event fixup ignores non-vendor report ID 2. A reconnect signature `f8 02 01` schedules a delayed raw-mode switch. Raw pad report `0xf0` is promoted into report ID `0xf0`, converts wheel direction value 2 to `0xff`, and returns length 8. Raw battery report `0xf2` is promoted and returned with length 5.

## State And Persistence
`last_button_state` is declared but not used by the current event path. Async context state is managed by `hid_bpf_async.h` for delayed calls. The device's raw-mode state is external hardware state triggered by output reports.

## Dependencies And Integration Points
The program depends on HID-BPF async infrastructure, hardware output reports, HID report helper macros, and the ACK05 raw protocol. It integrates with the kernel by making the remote look like a tablet function-key device and by exposing battery state without allowing the kernel to query battery state directly.

## Risks
The raw-mode magic packet is protocol-specific and may fail silently on firmware changes. The fixed descriptor is appended rather than replacing the vendor descriptor, so descriptor-size budget and parser behavior matter. Reconnect handling relies on a specific signature. Button mapping in raw mode includes an extra usage for BTN_A/BTN_SOUTH; keyboard-mode ambiguities are avoided by disabling those descriptors, not solved there.

## Test Signals
Tests should verify the vendor descriptor grows by the fixed descriptor size, other descriptors are disabled and renamed, probe sends the raw-mode report, reconnect schedules the delayed call, raw pad reports become 8-byte report `0xf0`, wheel counter-clockwise becomes `0xff`, and battery reports become 5-byte report `0xf2`.
