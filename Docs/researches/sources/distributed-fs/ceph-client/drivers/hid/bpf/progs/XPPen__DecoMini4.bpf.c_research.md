# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/XPPen__DecoMini4.bpf.c

Purpose: This HID-BPF program fixes XP-Pen Deco Mini 4 compatibility-mode pad and pen interfaces. It replaces pad and pen report descriptors with tablet-appropriate descriptors, uses vendor-provided logical/physical maximums for the pen, and converts keyboard-like pad reports into a six-button mask.

Important APIs/types/functions: `HID_BPF_CONFIG()` matches UGEE product `PID_DECO_MINI_4`. Constants define pad descriptor size 177, pen descriptor size 109, pad report ID 6, logical X/Y maxima, calculated physical X/Y maxima, and pressure maximum 8191. `pad_buttons` maps firmware key codes for buttons 1, 2, 4, 5, and 6, with button 3 inferred from a modifier bit. `fixed_pad_rdesc` is a compact tablet-function-key descriptor. `fixed_pen_rdesc` describes a stylus report with tip, barrel, tablet pick, in-range, X/Y coordinates, pressure, and padding. `hid_rdesc_fixup_xppen_deco_mini_4()` selects the replacement descriptor by input descriptor size. `hid_device_event_xppen_deco_mini_4()` rewrites pad reports into button masks.

Control flow: Probe accepts the two compatibility-mode descriptor sizes and rejects other interfaces, including the raw-mode-only interface. Descriptor fixup copies the fixed pad or pen descriptor and returns its size. Event processing reads 8 bytes, ignores non-pad report IDs, sets button 3 from bit 2 of `data[1]`, scans bytes 2 through 7 for matching key codes in `pad_buttons`, and writes a normalized report with byte 1 as the button mask.

State and persistence: No mutable global or map state is used. The selected fixed descriptor persists in the HID core after fixup. Per-report state is transient and consists of the computed `button_mask`.

Dependencies and integration points: The program depends on HID-BPF kfunc access to descriptor and report buffers, HID report semantics for tablet function keys and stylus axes, and userspace tablet stacks that expect pad buttons rather than keyboard shortcuts. It integrates with compatibility mode and intentionally does not switch the tablet into raw mode.

Risks: The descriptor constants encode values from a device query comment; if firmware changes resolution or maxima, coordinates and pressure may be misdeclared. Raw mode is out of scope, so users expecting raw-mode behavior need a different program. Button decoding has the same modifier-bit dependency as related XP-Pen pad fixups. The replacement pad descriptor has many padding bits, so report-length compatibility should be checked carefully.

Test signals: Validate descriptor replacement on both pad and pen interfaces, rejection of unrelated descriptor sizes, correct pen coordinate maxima and pressure maximum, all six pad buttons under single and multi-button presses, button 3 modifier-bit handling, no keyboard shortcut leakage, and unchanged behavior for non-pad reports.
