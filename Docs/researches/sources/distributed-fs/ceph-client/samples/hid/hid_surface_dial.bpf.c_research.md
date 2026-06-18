# sources/distributed-fs/ceph-client/samples/hid/hid_surface_dial.bpf.c

Purpose: HID-BPF program that morphs a Microsoft Surface Dial into mouse-like wheel/button behavior and optionally configures haptic feedback.

Important APIs/functions: HID event struct-op clears touch/X/Y fields; syscall program `set_haptic` uses `hid_bpf_allocate_context`, `hid_bpf_hw_request`, and `hid_bpf_release_context`; descriptor fixup changes HID usages, resolution multiplier, physical resolution, and relative flags.

Control flow: on events, report bytes are edited in place. On loader-triggered test-run syscall, feature report 1 is read, haptic auto-trigger is set or cleared based on resolution, then written back. Descriptor fixup rewrites fixed offsets for touch/button, dial/wheel, resolution, and X/Y relative mode.

State and persistence: global BPF data variables `resolution`, `physical`, and `haptic_data`; attached struct ops alter the device while active.

Dependencies and integration: loaded by `hid_surface_dial.c`, which sets data variables and calls the syscall program using `bpf_prog_test_run_opts`.

Risks: fixed descriptor offsets are device-specific. Feature report manipulation can misconfigure unsupported devices. Static `haptic_data` is shared BPF global state.

Test signals: attach to Surface Dial, vary `-r`, observe wheel events and haptic behavior, and inspect BPF printk logs for feature request results.
