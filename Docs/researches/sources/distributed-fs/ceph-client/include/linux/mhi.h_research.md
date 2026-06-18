# sources/distributed-fs/ceph-client/include/linux/mhi.h

## Purpose
Public host-side MHI bus API. It defines controller configuration, MHI devices and drivers, execution environments, MHI states, callbacks, transfer flags, and lifecycle/transfer entry points for MHI controller and client drivers.

## Important APIs/Types
Major enums include `mhi_callback`, `mhi_flags`, `mhi_device_type`, `mhi_ch_type`, `mhi_ee_type`, `mhi_state`, channel EE masks, event-ring data type, and doorbell burst mode. Configuration structures are `mhi_channel_config`, `mhi_event_config`, and `mhi_controller_config`. `struct mhi_controller` is the central host object with MMIO bases, IOVA ranges, firmware/RDDM image data, channel/event/command contexts, PM locks, state transition work, execution environment, IRQs, bounce-buffer state, and controller callbacks. `struct mhi_device`, `mhi_result`, and `mhi_driver` define client-facing device, completion, and driver contracts.

Key APIs cover controller allocation/registration, driver registration, power-up/down, suspend/resume, forced resume, RDDM handling, state reads, runtime wake references, transfer preparation, raw buffer/SKB queueing, queue fullness, SoC reset, and doorbell-offset discovery.

## Control Flow
Controller drivers allocate and populate `mhi_controller`, register with a config, then power up through firmware/device state transitions until channel devices probe. Client drivers bind through `mhi_driver`, prepare channels, queue buffers/SKBs, and receive transfer/status callbacks. Power-down and suspend paths reset or retain channel devices depending on the API used.

## State And Persistence
Persistent state includes register mappings, IOVA window, image buffers, channel/event/command arrays, PM state, EE/device state, transition list, wake/pending packet counters, workqueues, and callback vectors. Locks protect PM state, transitions, and wake handling.

## Dependencies And Integration Points
Depends on the Linux device model, DMA direction, locks, waitqueues, workqueues, SKBs, and allocation helpers. Integrates with bus-specific controller drivers, runtime PM, firmware loading, IRQ/event handling, debugfs, DMA/IOMMU mapping, and crash-dump/RDDM flows.

## Risks
Incorrect required callbacks, invalid MMIO/IOMMU ranges, PM races, wake reference leaks, EE/channel mismatches, and queueing before channel preparation can break the bus. `mhi_pm_resume_force()` intentionally bypasses strict M3 expectations and needs device-specific validation.

## Test Signals
Controller registration, sync/async boot, firmware download, channel probe/remove, UL/DL transfers, queue-full checks, suspend/resume/forced resume, RDDM download, graceful and ungraceful power-down, callback ordering, and event/IRQ delivery.
