<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/most.h -->
# sources/distributed-fs/ceph-client/include/linux/most.h

## Purpose
`most.h` defines the MOST (Media Oriented Systems Transport) core API for hardware driver modules, application/interface modules, components, channels, and MOST buffer objects.

## Important APIs, Types, and Functions
It defines interface types (`enum most_interface_type`), channel directions, channel data types, and MBO status flags. Data structures include `struct most_channel_capability`, `struct most_channel_config`, `struct mbo`, `struct most_interface`, and `struct most_component`.

Registration and channel APIs include `most_register_interface()`, `most_deregister_interface()`, `most_submit_mbo()`, `most_stop_enqueue()`, `most_resume_enqueue()`, `most_register_component()`, `most_deregister_component()`, `most_get_mbo()`, `most_put_mbo()`, `channel_has_mbo()`, `most_start_channel()`, `most_stop_channel()`, configfs registration, link add/remove, channel configuration setters, `most_cfg_complete()`, and `most_interface_register_notify()`.

## Control Flow and State
Hardware drivers allocate and initialize `struct most_interface`, then register it with the core. Components register `struct most_component` and are connected to channels. The core allocates MBOs and hands them to hardware drivers through `enqueue()`. Ownership transfers to the hardware driver until it fills status/processed length and calls `mbo->complete()`. Channel close flows through `poison_channel()` and requires all outstanding MBOs to be returned.

## State and Persistence Behavior
MOST state is runtime device/channel/component state. Capabilities and configs are exposed through sysfs/configfs. MBOs are recycled or freed by the core after completion. The header explicitly states the core does not track MBOs while owned by hardware drivers.

## Dependencies and Integration Points
It depends on device model types, DMA addressing, modules, configfs, sysfs, and MOST core implementation. It integrates adapter drivers (USB, PCIe, MediaLB, etc.) with higher-level application modules.

## Risks
MBO ownership is the largest risk: hardware drivers must return every MBO before deregistration or unload, or memory leaks and dangling DMA buffers occur. Calling core-owned fields while an HDM owns the MBO violates the contract. Channel config values may be adjusted by hardware callbacks and must be honored by components.

## Test Signals
Register/deregister HDM drivers under load, start/stop channels, poison channels with outstanding MBOs, verify DMA allocation/free pairing, configfs link creation/removal, sysfs capability reporting, and fault injection for enqueue failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/most.h -->
