# sources/distributed-fs/ceph-client/drivers/pci/vgaarb.c

## Purpose
`vgaarb.c` implements VGA legacy-resource arbitration for systems with multiple VGA-class PCI devices. It coordinates ownership of legacy VGA I/O and memory ranges, exposes kernel APIs for GPU drivers, provides the `/dev/vga_arbiter` userspace ABI, tracks the default boot VGA device, and reacts to PCI hotplug notifications.

## Important APIs, types, and functions
The central type is `struct vga_device`, which tracks a PCI device, decoded resources, owned resources, locks, per-resource counters, bridge-control eligibility, firmware-default status, and an optional client `set_decode()` callback. Exported APIs include `vga_default_device()`, `vga_set_default_device()`, `vga_remove_vgacon()`, `vga_get()`, `vga_put()`, `vga_set_legacy_decoding()`, and `vga_client_register()`. Userspace state uses `struct vga_arb_private` and `struct vga_arb_user_card`. The miscdevice file operations implement read, write, poll, open, and release.

## Control flow and behavior
Initialization registers `/dev/vga_arbiter`, registers a PCI bus notifier, and scans existing PCI devices for VGA class. Adding a VGA device initializes default decodes, derives owned legacy resources from command bits and bridge VGA forwarding, selects a boot default based on firmware framebuffer, legacy decode, integrated GPU, and enabled non-legacy devices, checks whether bridge VGA forwarding can control the device exclusively, and appends it to `vga_list`.

`vga_get()` calls `vga_check_first_use()` to notify registered clients on first arbitration use, finds the target, and tries to acquire requested resources. `__vga_tryget()` expands normal-resource requests to legacy locks when needed, detects conflicts, disables conflicting owners via `pci_set_vga_state()`, enables the target's decode and bridge routing, updates ownership, and increments lock counters. If a conflicting device holds locks, `vga_get()` waits on `vga_wait_queue`; `vga_tryget()` returns busy. `vga_put()` decrements counters and wakes waiters when lock bits clear.

The userspace ABI parses text commands: `target`, `lock`, `trylock`, `unlock`, `unlock all`, and `decodes`. Open defaults to the current default device and release unwinds all locks held by the file descriptor. Reads return a status line with decode, ownership, and lock counts. PCI add/remove notifications update the arbiter and notify clients.

## State and persistence
Global state includes `vga_list`, `vga_count`, `vga_decode_count`, `vga_arbiter_used`, `vga_default`, `vga_lock`, `vga_wait_queue`, and `vga_user_list`. State is in-memory only, but it directly affects PCI command bits and bridge VGA forwarding through `pci_set_vga_state()`. File descriptors persist per-client lock accounting until release.

## Dependencies and integration points
It integrates with PCI device hotplug notifiers, VGA console removal, sysfb firmware default detection on x86, ACPI integrated-GPU detection, GPU driver decode callbacks, miscdevice registration, waitqueues, spinlocks, and the documented vgaarbiter userspace ABI.

## Risks
This code touches legacy decode routing with global effects. Lock counter mismatches can deadlock users or leave resources owned. Bridge sharing logic is conservative but complex in multi-bridge topologies. Userspace command parsing is string-based and has legacy quirks, including treating `io` or `mem` requests as `io+mem` to avoid deadlocks. Hot removal must wake waiters and invalidate userspace targets.

## Test signals
Test multi-GPU systems across shared and separate bridges, default-device selection, driver `set_decode()` callbacks, `/dev/vga_arbiter` command parsing and release cleanup, blocking and trylock contention, hotplug add/remove, VGA console removal, and wakeups after unlock or device removal.
