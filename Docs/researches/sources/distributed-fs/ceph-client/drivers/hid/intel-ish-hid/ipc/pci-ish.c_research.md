<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/pci-ish.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/pci-ish.c

## Purpose
`pci-ish.c` is the PCI glue for the Intel ISH IPC provider. It binds supported Intel ISH PCI functions, maps BARs, allocates IRQs, initializes the ISHTP hardware device, starts the protocol, handles system sleep/resume, exposes firmware version sysfs attributes, and advertises firmware filenames.

## Important APIs, Types, and Functions
`ishtp_driver_data` stores firmware generation strings for newer platforms. `ish_pci_tbl` maps PCI IDs to optional generation data. `ish_event_tracer` routes driver logs into tracepoints. `ish_init` starts hardware and ISHTP. `ish_probe`, `ish_remove`, and `ish_shutdown` are PCI lifecycle callbacks. PM helpers include `ish_should_enter_d0i3`, `ish_should_leave_d0i3`, `ish_suspend`, `ish_resume`, `ish_resume_handler`, and `ish_freeze`. Sysfs attributes `base_version` and `project_version` expose firmware versions when a generation is known.

## Control Flow
Probe rejects invalid Mehlow IDs, enables the PCI device with managed resources, sets bus mastering, maps BAR0, allocates the ISHTP device through `ish_dev_init`, stores trace and platform firmware metadata, allocates one IRQ vector, requests the IRQ, initializes suspend/resume waitqueues, enables wakeup for EHL, and calls `ish_init`. `ish_init` calls `ish_hw_start` to set host ready/wakeup firmware and `ishtp_start` to begin host bus management enumeration.

Suspend either requests D0i3-style ISHTP suspend and waits briefly for RX complete, or disables DMA before D3. If the suspend ACK does not arrive, it disables DMA so firmware will reset on resume. Resume queues unbound work: if leaving D0i3, it disables IRQ wake if needed, restores host ready, sends resume, waits for ACK, and falls back to full init on failure; otherwise it runs full init. Remove removes all ISHTP clients and disables hardware.

## State and Persistence Behavior
Persistent PCI driver state is stored in `struct ishtp_device` via driver data. Firmware generation metadata controls sysfs visibility and firmware path expectations. Suspend/resume flags and waitqueues persist across PM transitions. Hardware state spans PCI power state, IRQ wake, DMA enable, host-ready bits, and firmware runtime state.

## Dependencies and Integration Points
The file depends on PCI managed APIs, Linux PM/suspend helpers, ISHTP bus/core functions, IPC hardware hooks from `hw-ish.h`, and trace events. It integrates with the optional firmware loader through firmware-name generation metadata and `MODULE_FIRMWARE` declarations.

## Risks and Edge Cases
`ish_resume_device` is file-static, so concurrent resume of multiple devices would be unsafe, though typical systems have one ISH. D0i3 decisions depend on platform firmware suspend/resume paths and CHV exceptions. If resume ACKs are missed, the fallback reinitializes the protocol and clients. Sysfs firmware attributes are hidden unless generation data exists; older devices still work without them. Invalid-platform filtering affects all ISH devices when matching IDs are present.

## Test Signals
Check PCI probe/remove, IRQ mode fallback, HBM/client enumeration, suspend/resume via firmware and non-firmware paths, IRQ wake on EHL, D0i3 versus D3 transitions, sysfs firmware versions on new platforms, tracepoint output, and successful HID sensor operation after resume fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/pci-ish.c -->
