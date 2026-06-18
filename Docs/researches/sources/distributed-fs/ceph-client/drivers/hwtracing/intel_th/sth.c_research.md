
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/sth.c

Purpose: Intel TH Software Trace Hub source driver. It registers Intel TH STH hardware as a generic STM device and implements packet writes into STH MMIO channels.

Important APIs/types/functions: `struct sth_device` holds control MMIO, channel MMIO, physical channel base, device pointer, embedded `struct stm_data`, and master count. `sth_stm_packet()` translates generic STP packet requests into Intel TH STH register writes. `sth_stm_mmio_addr()` supplies mmap-able channel MMIO. `sth_stm_link()` routes an STP master through GTH with `intel_th_set_output()`. `intel_th_sw_init()` reads STH capabilities.

Control flow: probe maps STH control and channel resources, initializes `stm_data` callbacks and metadata, reads master/channel ranges, then calls `stm_register_device()`. Generic STM writers later call `sth_stm_packet()` for DATA/FLAG/USER/MERR/global packets. Remove unregisters the STM device.

State and persistence: STH state is volatile: MMIO mappings, STM device registration, hardware capability ranges, and GTH master routing created during link callbacks.

Dependencies and integration: bridges Intel TH source devices to the generic STM subsystem in `drivers/hwtracing/stm`. Depends on `linux/stm.h`, STH register/channel layout from `sth.h`, and Intel TH GTH routing.

Risks: packet size is rounded down to a power of two; unsupported or zero sizes can drop writes. 32-bit builds clamp writes above 4 bytes. `sth_stm_mmio_addr()` requires page-aligned channel ranges. Routing relies on GTH driver presence and policy-driven STM links.

Test signals: register STH as `/sys/class/stm`, create STM configfs policy, write through STM char device and STM sources, mmap channel range, validate generated STP packets, and test master ranges from hardware capabilities.
