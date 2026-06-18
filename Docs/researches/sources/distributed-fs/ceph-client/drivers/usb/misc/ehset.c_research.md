# sources/distributed-fs/ceph-client/drivers/usb/misc/ehset.c

Purpose: USB-IF EHSET high-speed electrical test fixture driver. When a fixture PID enumerates, probe sends the appropriate hub class command to place the parent port or device into a USB 2.0 compliance test state.

Important APIs and types: test PIDs map to `USB_TEST_SE0_NAK`, `USB_TEST_J`, `USB_TEST_K`, `USB_TEST_PACKET`, suspend/resume, single-step descriptor, and single-step set-feature paths. `ehset_prepare_port_for_testing()` suspends the port for normal hubs or disables power for a small quirk list.

Control flow: `ehset_probe()` derives the parent hub and child port number, switches on the device PID, performs required delays for timing-sensitive tests, sends `USB_REQ_SET_FEATURE` or `CLEAR_FEATURE` to the parent hub, or sends a descriptor request directly to the fixture for single-step descriptor testing. The single-step set-feature test is rejected unless the parent is the root hub.

State and persistence: no per-device state is kept; probe side effects are immediate hub-port state changes. Risks include intentionally disruptive port state manipulation, fixed 15-second sleeps in probe, dependence on hub behavior, no cleanup on disconnect, and an external declaration for `usb_device_match_id()`. Test signals are mostly hardware compliance-lab signals: correct PID selection, hub quirk behavior, root-hub-only rejection, and expected control-transfer traces.
