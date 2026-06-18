# sources/distributed-fs/ceph-client/drivers/s390/net/ism_drv.c

## Purpose
`ism_drv.c` implements the s390 ISM PCI driver and exposes ISM devices as DIBS devices. It manages PCI probe/remove, command serialization, summary-bit and interrupt-event queue registration, DMB allocation and registration, VLAN/GID commands, data movement, interrupt dispatch, and DIBS client notifications.

## Important APIs, Types, And Functions
- PCI/module integration: `ism_device_table`, `ism_driver`, `ism_init()`, `ism_exit()`, `ism_probe()`, and `ism_remove()`.
- Command path: `ism_cmd()`, `ism_cmd_simple()`, `query_info()`, `register_sba()`, `register_ieq()`, `unregister_sba()`, and `unregister_ieq()`.
- DIBS operations in `ism_ops`: `ism_get_chid()`, `ism_query_rgid()`, `ism_max_dmbs()`, `ism_register_dmb()`, `ism_unregister_dmb()`, `ism_move()`, VLAN add/delete, and `ism_signal_ieq()`.
- DMB memory management: `ism_alloc_dmb()`, `ism_free_dmb()`, and bitmap management with `sba_bitmap`.
- Interrupt/event path: `ism_handle_irq()`, `ism_handle_event()`, `ism_match_event_type()`, and `ism_match_event_subtype()`.
- Device setup/teardown: `ism_dev_init()` and `ism_dev_exit()`.

## Control Flow
On module init, `ism_init()` registers a s390 debug area and the PCI driver. `ism_probe()` allocates `struct ism_dev`, enables PCI memory access, requests regions, sets a 64-bit DMA mask and segment constraints, allocates a DIBS device, wires `dibs->drv_priv` and ops, then calls `ism_dev_init()`. Device init allocates one MSI vector, requests the IRQ, registers a coherent summary-bit area and interrupt-event queue with the device, and queries device info. After local GID is read, probe names and registers the DIBS device so clients can subscribe.

`ism_cmd()` serializes device commands with `cmd_lock`. It writes the request payload, writes the request header to trigger the command, initializes the response return to `ISM_ERROR`, reads the response header, logs failures, and reads the response payload on success. Higher-level helpers fill the specific aligned command union and call `ism_cmd()`.

DMB registration allocates a folio of requested size, maps it for DMA_FROM_DEVICE, chooses or validates an SBA bitmap index above `ISM_DMB_BIT_OFFSET`, sends `ISM_REG_DMB`, stores the returned token, and records the owning DIBS client id under `dibs->lock`. Unregistration clears the client id first, sends `ISM_UNREG_DMB`, tolerates `ISM_ERROR` during teardown, and frees/unmaps the DMB.

The IRQ handler clears the summary bit, scans inverted DMB bits, clears each bit and mask, looks up the DIBS client id, and calls the client's `handle_irq()` with the DMB index and mask. If the event bit is set, it clears it and calls `ism_handle_event()`, which walks the IEQ ring, maps s390 event type/subtype to DIBS event values, fills `struct dibs_event`, and broadcasts to subscribed clients.

## State And Persistence Behavior
The driver keeps live state in `struct ism_dev`: PCI/DIBS pointers, command lock, coherent SBA and IEQ memory, DMA addresses, DMB allocation bitmap, and event queue index. DIBS state stores client subscriptions and DMB owner ids. Hardware-visible registrations persist only until `ism_dev_exit()` unregisters IEQ/SBA and frees IRQ vectors. There is no disk persistence.

## Dependencies And Integration Points
The file integrates with Linux PCI, DMA mapping, MSI IRQs, s390 debug features, zpci helpers from `ism.h`, DIBS device/client APIs, and folio memory allocation. It is a provider for DIBS clients, so its operation table and event mappings are external behavioral contracts.

## Risks
- `ism_cmd()` depends on strict command ordering under `cmd_lock`; any unlocked direct command path would corrupt device command state.
- DMB allocation uses a folio but the DMA mapping failure path calls `kfree(dmb->cpu_addr)` instead of folio-specific release, which is a code path worth auditing against the kernel version's allocation semantics.
- `ism_unregister_dmb()` clears the DIBS client id before the hardware unregister command completes, so failures can leave hardware state with software no longer routing interrupts for that DMB.
- IRQ scanning uses inverted bit operations and offset arithmetic; off-by-one errors would dispatch wrong DMB indexes or miss events.
- Event broadcast holds `dibs->lock` while invoking client callbacks through `ism_handle_event()` from the IRQ handler, so client callback locking and latency constraints matter.

## Test Signals
- Probe/remove tests should verify all rollback labels free IRQs, DMA pages, DIBS devices, PCI regions, and driver data.
- Command tests should cover success and nonzero response codes for all command helpers, including teardown with `ISM_ERROR`.
- DMB tests should cover requested index, auto index allocation, duplicate indexes, too-large buffers, DMA mapping failure, register failure cleanup, and unregister failure.
- IRQ tests should cover DMB bit delivery, event queue wraparound, no-client cases, client callback dispatch, and mixed DMB/event interrupts.
