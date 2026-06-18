# sources/distributed-fs/ceph-client/include/linux/i3c/master.h

## Purpose
Defines the internal Linux I3C master-controller interface, including mixed I3C/I2C bus modeling, board information, device descriptors, IBI handling, address-slot state, master operations, DMA helpers, bus notification, and registration APIs. It is a framework contract consumed by I3C controller drivers and the I3C core, not a standalone implementation.

## Important APIs, Types, And Functions
Core types are `i3c_master_controller`, `i3c_master_controller_ops`, `i3c_bus`, `i3c_dev_desc`, `i2c_dev_desc`, `i3c_device`, `i3c_device_ibi_info`, `i3c_ibi_slot`, and `i3c_dma`. Important operations include `bus_init`, `do_daa`, `send_ccc_cmd`, `i3c_xfers`, `i2c_xfers`, IBI request/enable/disable/recycle hooks, hotjoin hooks, open-drain speed configuration, and NACK retry configuration. Exported helpers cover CCCs, DAA, address allocation, dynamic device add, DMA map/unmap, master registration, hotjoin, IBI pooling, notifier registration, and private per-device master data.

## Control Flow
Typical controller flow is registration through `i3c_master_register()`, controller `bus_init`, master information setup, static/boardinfo device attachment, optional SETDASA/DAA through `do_daa`, and steady-state I3C/I2C transfers through ops callbacks. IBI flow is preallocation, hardware receives an interrupt payload into an `i3c_ibi_slot`, the controller queues it with `i3c_master_queue_ibi()`, the workqueue invokes the device handler, then the master recycles the slot.

## State And Persistence
Bus state is in address-slot bitmaps, current master, I2C/I3C device lists, SCL rates, and the bus `rw_semaphore`. Device state is in descriptors, dynamic/static addresses, boardinfo pointers, controller-private data, and IBI counters/completions. State is runtime kernel state only; persistence comes from firmware/DT boardinfo and rediscovery during bus initialization.

## Dependencies And Integration Points
Depends on I2C core, I3C CCC/device headers, Linux device model, workqueues, completions, mutexes, spinlocks, rwsems, DMA mapping, notifiers, and firmware nodes. Ceph has no direct dependency, but this header is part of the imported kernel client tree and may be compiled with other kernel subsystems in integrated builds.

## Risks
High-risk areas are bus-lock ordering, address-slot corruption during DAA/reattach, incorrect mixed-bus timing, IBI lifetime races, missing IBI disable/drain before free, DMA bounce/mapping mistakes, and optional operation hooks being treated as mandatory. Multi-master state makes `cur_master` and bus ownership assumptions especially sensitive.

## Test Signals
Useful tests include controller registration/unregistration, pure and mixed I2C/I3C enumeration, DAA and RSTDAA/ENTDAA paths, address collision handling, I2C fallback transfers, I3C SDR/HDR transfers, IBI request/enable/disable/drain, hotjoin detection, runtime PM interactions, DMA mapping error paths, and lockdep/KASAN/KCSAN runs around concurrent transfers and bus maintenance.
