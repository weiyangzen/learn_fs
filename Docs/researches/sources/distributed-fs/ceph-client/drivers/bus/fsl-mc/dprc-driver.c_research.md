# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/dprc-driver.c

## Purpose
Implements the Linux driver for DPAA2 Data Path Resource Container objects. It opens DPRCs, scans Management Complex objects into Linux devices, reconciles add/remove/plug state, sets up MSI-backed DPRC interrupts, and tears everything down on removal.

## Important APIs, Types, And Functions
Key exported functions include `dprc_remove_devices()`, `fsl_mc_device_lookup()`, `dprc_scan_objects()`, `dprc_scan_container()`, `disable_dprc_irq()`, `get_dprc_irq_state()`, `enable_dprc_irq()`, `dprc_setup()`, and `dprc_cleanup()`. Static helpers include `fsl_mc_device_match()`, allocatable-object detection, child add/remove callbacks, `check_plugged_state_change()`, `dprc_irq0_handler_thread()`, `register_dprc_irq_handler()`, and `dprc_setup_irq()`.

## Control Flow
Probe calls `dprc_setup()`, scans the container, then sets up IRQs. Setup creates a child MC portal when needed or creates the root UAPI device file, finds and assigns the MSI domain, opens the DPRC, reads attributes, and validates API version. Scanning initializes resource pools, locks the bus scan mutex, queries object count/descriptors, applies a dpseci coherency quirk, optionally populates the IRQ pool, removes Linux child devices no longer present in MC, then adds newly discovered devices with allocatable resources first. The threaded IRQ handler reads/clears DPRC interrupt status and rescans on object/container add/remove/create/destroy events.

## State And Persistence
State lives in the fsl-mc bus/device model: MC handle, MC portal, DPRC attributes, MSI domain, IRQ pool, scan mutex, IRQ enabled flag, and Linux child devices. Firmware owns the authoritative object inventory; the driver continually reconciles Linux state to it.

## Dependencies And Integration Points
It depends on `dprc.c` command wrappers, `fsl-mc-bus` device creation/removal, fsl-mc MSI allocation, UAPI file support for root DPRCs, resource pools from `fsl-mc-allocator.c`, and Linux driver-core attach/release behavior.

## Risks And Test Signals
Risks include races while objects are added/removed during scanning, child devices bound before allocatable pools exist, IRQ pool sizing mistakes, MSI-domain absence, teardown failure when `mc_io` is lost, and incomplete rollback on probe errors. Test signals include dynamic MC object hotplug, DPRC IRQ-triggered rescans, root and child DPRC probe/remove, interrupt pool allocation/free, and no stale Linux devices after MC object removal.
