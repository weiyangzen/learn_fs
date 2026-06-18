# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_trigger.c

- Purpose: Creates an IIO triggered-buffer device for MGB4 external/video-synchronized trigger events.
- Important APIs/types/functions: Private `struct trigger_data`, `trigger_read_raw`, `trigger_set_state`, `trigger_handler`, `probe_trigger`, `remove_trigger`, `mgb4_trigger_create`, and `mgb4_trigger_free`.
- Control flow: Create allocates an IIO device, sets channel metadata, allocates/registers an IIO trigger on XDMA user IRQ 11, sets up triggered buffer, and registers the device. Trigger state toggles the user IRQ. Handler reads event register 0xA0, acknowledges it, pushes data plus timestamp to buffers, notifies trigger done, and clears IRQ in register 0xB4.
- State and persistence: Stores IIO trigger pointer and parent `mgbdev` in IIO private data; event register state is volatile hardware state.
- Dependencies and integration points: Integrated with core probe/remove, XDMA user IRQs, Linux IIO trigger and buffer frameworks.
- Risks: IRQ 11 is shared by assumption with hardware event source. Raw reads are blocked while buffers are enabled. Correct cleanup order matters for trigger, IRQ, buffer, and IIO device.
- Test signals: Test raw read, triggered buffer capture, enabling/disabling trigger, timestamp/data correctness, and remove while buffer is enabled.
