# sources/distributed-fs/ceph-client/drivers/input/misc/keyspan_remote.c

Purpose: USB input driver for the Keyspan UIA-11/DMR remote, decoding pulse-coded interrupt-in byte streams into key events.

Important APIs/types/functions: uses `usb_driver`, interrupt URBs, coherent DMA buffers, vendor `usb_control_msg` setup, and input keymaps. `struct usb_keyspan` stores USB/input objects, endpoint/URB/buffer, parser stage, toggle, and `struct bit_tester`. Core routines are `keyspan_load_tester`, `keyspan_check_data`, `keyspan_report_button`, URB callback, open/close, probe, and disconnect.

Control flow: probe finds an interrupt-in endpoint, allocates objects and 8-byte buffer, sends setup messages for bit rate/sensitivity/receive enable, builds name/phys, installs keymap, initializes URB, registers input, and stores interface data. Open submits URB; close kills it. Completion parses data and resubmits unless canceled/disconnected.

State/persistence: parser state spans URBs: stage 0 finds non-gap data, stage 1 searches sync, stage 2 decodes system/button/toggle/stop. Toggle changes emit press plus release and suppress repeats. No durable state.

Dependencies/integration: USB VID/PID `06cd:0202`, EV_KEY plus MSC_SCAN input reporting.

Risks: bit parser correctness protects keymap indexing. Malformed data resets parser and drops messages. Manual allocation/disconnect ordering is important. Vendor setup values are opaque.

Test signals: matching probe, open/close, disconnect while active, malformed sync/data recovery, toggle suppression, all mapped keys, MSC_SCAN, and debug byte output.
