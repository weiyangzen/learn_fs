# Research: subset-b-005861

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/huge_mm.h -->
# sources/distributed-fs/ceph-client/include/linux/huge_mm.h

## Purpose
Defines the public MM interface for transparent huge pages (THP), multi-size THP statistics, huge PMD/PUD fault handling, splitting, migration, and huge zero folio helpers. It is a high fan-out header for MM code and architecture page-table code, with most behavior gated by `CONFIG_TRANSPARENT_HUGEPAGE`, `CONFIG_PGTABLE_HAS_HUGE_LEAVES`, and `CONFIG_HAVE_ARCH_TRANSPARENT_HUGEPAGE_PUD`.

## APIs, Control Flow, and State
Important exports include `do_huge_pmd_anonymous_page()`, `do_huge_pmd_wp_page()`, `copy_huge_pmd()`, `zap_huge_pmd()`, `change_huge_pmd()`, PUD equivalents, `vmf_insert_pfn_pmd/pud()`, and folio insertion helpers. THP policy flows through `transparent_hugepage_flags`, per-order anonymous masks, `thp_vma_suitable_orders()`, and `thp_vma_allowable_orders()`, which first applies sysfs/madvise/global policy for anonymous VMAs and then delegates to `__thp_vma_allowable_orders()`. Split control is exposed through `split_huge_page_to_list_to_order()`, `folio_split()`, `try_folio_split_to_order()`, and `deferred_split_folio()`. State is mostly global or per-cpu: THP flags, zero-folio pointers, per-order `mthp_stats`, and mm flags disabling THP. Disabled builds provide stubs returning false, zero, or `-EINVAL`.

## Dependencies, Integration, Risks, and Tests
Depends on core `mm_types`, VMA flags, pgtable primitives, sysfs kobjects, memcg, and architecture THP support. Integration points are page fault handling, madvise, khugepaged, NUMA migration, DAX/PFNMAP insertion, and zero-page mapping. Risks are alignment/order mistakes, split races, stale huge-zero-folio lifetime assumptions, and calling enabled-only paths in !THP builds. Test signals include THP sysfs policy, `smaps` THP eligibility, PMD/PUD fault tests, split/deferred split counters, migration tests, and multi-size THP stat movement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/huge_mm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hugetlb.h -->
# sources/distributed-fs/ceph-client/include/linux/hugetlb.h

## Purpose
Provides the central hugetlb and hugetlbfs interface: reservation maps, subpools, hstate accounting, hugepage page-table walking, page flags, allocation/freeing, migration, bootmem/CMA setup, and hugetlbfs inode/superblock helpers.

## APIs, Control Flow, and State
The main state types are `struct hugepage_subpool`, `struct resv_map`, `struct file_region`, `struct hugetlb_vma_lock`, `struct hstate`, and `struct huge_bootmem_page`. `hstate` persists pool counts and per-node free/surplus/max counts; reservation state persists in `resv_map` regions and cgroup uncharge metadata. Key APIs cover VMA duplication/reservation cleanup, table copy/move/unmap, `hugetlb_fault()`, `hugetlb_reserve_pages()`, `hugetlb_unreserve_pages()`, `huge_pte_alloc()`, `hugetlb_walk()`, PMD sharing/unsharing, vma locks, protection changes, page allocation, page-cache insertion, dissolution, migration support, and mm usage accounting. Control flow is lock-sensitive: shared mappings require hugetlb VMA locks or mapping `i_mmap_rwsem` for stable page-table walks; `huge_pte_lockptr()` selects lock level based on hugepage size.

## Dependencies, Integration, Risks, and Tests
Depends on MM, fs, page-table, userfaultfd, cgroup, mempolicy, architecture `asm/hugetlb.h`, CMA, NUMA, and memory-failure support. Integration spans hugetlbfs, shm, page fault, migration, memory hotplug, hwpoison, bootmem, sysfs/proc meminfo, and TLB flushing. Risks include reservation leaks, incorrect cgroup uncharges, unsafe PMD sharing walks, wrong page flag synchronization, gigantic page fallback breaking per-node pools, and disabled-config stubs that either BUG or silently return neutral values. Test signals include hugetlb selftests, meminfo/node counters, reservation/subpool accounting, PMD sharing stress, userfaultfd hugetlb tests, migration/hwpoison tests, and config-matrix builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hugetlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hugetlb_cgroup.h -->
# sources/distributed-fs/ceph-client/include/linux/hugetlb_cgroup.h

## Purpose
Defines hugetlb cgroup accounting structures and charge/uncharge hooks for allocated huge pages and reservations.

## APIs, Control Flow, and State
With `CONFIG_CGROUP_HUGETLB`, `struct hugetlb_cgroup` embeds cgroup CSS state, per-hstate `page_counter` arrays for used and reserved huge pages, event counters, event files, and per-node usage. Folios hold separate allocation and reservation cgroup pointers accessed by `hugetlb_cgroup_from_folio()` and `_rsvd()` and set by `set_hugetlb_cgroup()` and `_rsvd()`. Reservation maps can hold CSS/page-counter metadata; dup/put helpers manage CSS references. The charge flow is charge cgroup, commit charge to folio or reservation, and uncharge on folio/free-region/reservation cleanup. Disabled builds turn accounting into no-ops and report `hugetlb_cgroup_disabled()` as true.

## Dependencies, Integration, Risks, and Tests
Depends on hugetlb folios, `struct resv_map`, `struct file_region`, cgroup CSS, and page counters. It integrates with hugetlb allocation, reservation creation, reservation map duplication/release, file-region deletion, and migration. Risks are mismatched reservation vs allocation cgroup pointers, lost CSS references, uncharging the wrong hstate index or page count, and assuming accounting exists in non-cgroup builds. Test signals include hugetlb cgroup limit enforcement, reservation accounting tests, migration preserving cgroup state, cgroup event counters, and config builds with and without `CONFIG_CGROUP_HUGETLB`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hugetlb_cgroup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hugetlb_inline.h -->
# sources/distributed-fs/ceph-client/include/linux/hugetlb_inline.h

## Purpose
Provides minimal inline predicates for identifying hugetlb VMAs and VMA flag sets without pulling in the full hugetlb header.

## APIs, Control Flow, and State
The enabled path maps `is_vm_hugetlb_flags()` to `VM_HUGETLB` and `is_vma_hugetlb_flags()` to the VMA flag bitset helper `vma_flags_test_any(..., VMA_HUGETLB_BIT)`. `is_vm_hugetlb_page()` applies the raw `vm_flags` test to a `vm_area_struct`. In !`CONFIG_HUGETLB_PAGE` builds, all tests return false. There is no persistent state.

## Dependencies, Integration, Risks, and Tests
Depends only on `linux/mm.h` definitions. It is included by broader MM headers to avoid include cycles while still allowing cheap hugetlb decisions. Risks are mostly config-sensitive: code using this predicate must tolerate all-false results when hugetlb is compiled out. Test signals are compile coverage across hugetlb-enabled and disabled builds and VMA classification checks in mmap/unmap paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hugetlb_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hung_task.h -->
# sources/distributed-fs/ceph-client/include/linux/hung_task.h

## Purpose
Defines lightweight blocker tracking for hung task diagnostics, encoding the lock pointer and blocking primitive type into `current->blocker`.

## APIs, Control Flow, and State
Blocker type constants use the two low pointer bits for mutex, semaphore, rwsem reader, and rwsem writer. With `CONFIG_DETECT_HUNG_TASK_BLOCKER`, `hung_task_set_blocker()` validates non-null input, warns if a blocker is already set, skips unaligned locks whose low bits are unavailable, and writes `lock_ptr | type` to the current task. `hung_task_clear_blocker()` clears the field. `hung_task_get_blocker_type()` masks the low bits, and `hung_task_blocker_to_lock()` recovers the aligned pointer. Disabled builds are no-ops or return neutral values.

## Dependencies, Integration, Risks, and Tests
Depends on task state in `sched.h`, compiler READ/WRITE_ONCE, and warning helpers. It integrates with locking slow paths that want hung-task reports to identify the contested lock. Risks are missing clear calls, nested blocker writes, lock pointers with low bits set, and reading blocker values without checking zero. Test signals include hung-task diagnostics showing expected lock type, lockdep/hung-task stress, and config builds with blocker tracking disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hung_task.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hw_bitfield.h -->
# sources/distributed-fs/ceph-client/include/linux/hw_bitfield.h

## Purpose
Adds helper macros for hardware registers whose upper 16 bits are a write-enable mask for lower 16-bit fields.

## APIs, Control Flow, and State
`FIELD_PREP_WM16(mask, val)` performs normal bitfield preparation for the low half and ORs `mask << 16` into the result. It uses `__BF_FIELD_CHECK()` to catch invalid masks or values. `FIELD_PREP_WM16_CONST()` provides constant-expression support by combining `FIELD_PREP_CONST()` with a build-time check that the mask fits in 16 bits. There is no runtime state or control flow beyond macro expansion.

## Dependencies, Integration, Risks, and Tests
Depends on `linux/bitfield.h`, build bug helpers, and `U16_MAX`. It integrates with register programming code for mask-write hardware blocks. Risks are passing masks outside the lower half, assuming side effects in macro arguments are safe, or using the non-const macro in initializers. Test signals are compile-time assertion failures for bad masks/values and driver register write tests confirming upper-half write-enable bits are emitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hw_bitfield.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hw_breakpoint.h -->
# sources/distributed-fs/ceph-client/include/linux/hw_breakpoint.h

## Purpose
Declares the kernel hardware breakpoint interface built on perf events, plus fallback stubs for architectures without breakpoint support.

## APIs, Control Flow, and State
When `CONFIG_HAVE_HW_BREAKPOINT` is enabled, `hw_breakpoint_init()` initializes a `perf_event_attr` as a pinned breakpoint event with period 1, and `ptrace_breakpoint_init()` additionally excludes kernel hits. Registration APIs cover user/task breakpoints, wide per-cpu kernel breakpoints, direct perf breakpoint registration, modification, slot reservation/release, unregister, ptrace flush, and usage checks. `bp_type_idx` accounts for architectures with shared or separate instruction/data breakpoint registers. State is mostly in `perf_event`, architecture breakpoint info (`bp->hw.info`), and slot accounting managed by implementation files. Disabled builds return `NULL`, `-ENOSYS`, false, or no-op.

## Dependencies, Integration, Risks, and Tests
Depends on perf event internals and UAPI breakpoint definitions. Integrates with ptrace debug registers, perf, kernel watchpoints, and architecture-specific breakpoint backends. Risks include leaking reserved slots, modifying attrs without validation, assuming returned `NULL` vs `ERR_PTR`, and missing arch constraints on breakpoint length/type/alignment. Test signals include perf/hw-breakpoint selftests, ptrace watchpoint tests, slot exhaustion tests, and !CONFIG fallback builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hw_breakpoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hw_random.h -->
# sources/distributed-fs/ceph-client/include/linux/hw_random.h

## Purpose
Defines the hardware random number generator driver contract and registration API for feeding entropy from device-specific RNGs.

## APIs, Control Flow, and State
`struct hwrng` carries driver callbacks (`init`, `cleanup`, obsolete `data_present`/`data_read`, preferred `read`), private data, quality estimate, and internal list/refcount/work/completion fields. Drivers register through `hwrng_register()` or `devm_hwrng_register()` and unregister through matching unregister functions. `hwrng_msleep()` and `hwrng_yield()` provide cooperative waits tied to RNG lifetime. State persists in the core-maintained hwrng list, reference count, cleanup work, and completion objects.

## Dependencies, Integration, Risks, and Tests
Depends on completions, krefs, workqueues, and typed kernel buffers. Integrates with the kernel hwrng core and random subsystem. Risks are implementing only obsolete callbacks, returning incorrect byte counts or quality, sleeping incorrectly in read paths, or freeing driver state before cleanup completion. Test signals include hwrng device registration, reads under blocking/nonblocking wait modes, unregister race tests, entropy quality exposure, and devm cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hw_random.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hwmon-sysfs.h -->
# sources/distributed-fs/ceph-client/include/linux/hwmon-sysfs.h

## Purpose
Provides legacy sysfs attribute helper structs and macros for hardware monitoring sensor drivers.

## APIs, Control Flow, and State
`struct sensor_device_attribute` embeds `device_attribute` plus one integer index; `struct sensor_device_attribute_2` adds `nr` and `index` bytes for two-dimensional sensor attributes. `to_sensor_dev_attr()` and `_2()` recover containers from attributes. `SENSOR_ATTR*` and `SENSOR_DEVICE_ATTR*` macros generate read-only, write-only, and read-write attribute initializers or definitions using conventional `_show` and `_store` function names. State is per static/global attribute object and per sysfs file created elsewhere.

## Dependencies, Integration, Risks, and Tests
Depends on driver core device attributes and kstrtox helpers commonly used by store callbacks. Integrates with hwmon drivers that expose raw sysfs groups instead of the newer `hwmon_chip_info` API. Risks include duplicate static symbol names, wrong permissions, index/nr truncation in `_2`, and callbacks misinterpreting the encoded indices. Test signals are sysfs file presence, permissions, read/write callback coverage, and sensor index mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hwmon-sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hwmon-vid.h -->
# sources/distributed-fs/ceph-client/include/linux/hwmon-vid.h

## Purpose
Declares VID/VRM voltage conversion helpers for hwmon drivers.

## APIs, Control Flow, and State
`vid_from_reg()` and `vid_which_vrm()` are implemented elsewhere. Inline `vid_to_reg()` converts millivolts to a VID code for VRM 9.0/9.1 only, returning `-EINVAL` for unsupported VRM revisions or `-1` for voltages outside 1100-1850 mV. The conversion is integer-only and avoids floating point. There is no persistent state.

## Dependencies, Integration, Risks, and Tests
Depends on errno definitions through common include context and `u8`. Integrates with older voltage regulator/sensor hwmon drivers. Risks are unsupported VRM revisions, millivolt vs volt unit confusion, and callers not distinguishing `-EINVAL` from out-of-range `-1`. Test signals include known VID/voltage conversion vectors and hwmon sensor output checks for legacy boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hwmon-vid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hwmon.h -->
# sources/distributed-fs/ceph-client/include/linux/hwmon.h

## Purpose
Defines the modern hardware monitoring class interface, sensor types, standard attribute bits, chip/channel descriptors, callback operations, and registration helpers.

## APIs, Control Flow, and State
The header enumerates sensor classes (`chip`, `temp`, `in`, `curr`, `power`, `energy`, `humidity`, `fan`, `pwm`, `intrusion`) and per-class attribute IDs, then maps them to `HWMON_*` bitmasks consumed by channel configs. `struct hwmon_ops` supplies visibility, read, read-string, and write callbacks. `HWMON_CHANNEL_INFO()` builds null-terminated per-channel attribute lists, and `struct hwmon_chip_info` binds those lists to ops. Registration APIs include deprecated group-based registration, preferred `hwmon_device_register_with_info()` and devm variant, thermal registration, unregister, event notification, name sanitization, and hwmon device lock/unlock.

## Dependencies, Integration, Risks, and Tests
Depends on bitops, device core, and optional sysfs attribute groups. Integrates with sysfs hwmon class, thermal zone registration, user-space monitoring tools, and driver-managed private data. State persists in the registered hwmon device, attribute files, driver private data, and class lock. Risks include mismatched config bits and callbacks, bad visibility permissions, invalid names (`-`, `*`, whitespace), missed event notifications, and continuing to use deprecated group APIs. Test signals include sysfs ABI attribute presence/permissions, read/write callback error handling, `hwmon_notify_event()` uevents, name sanitization tests, and lock coverage for concurrent reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hwmon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hwspinlock.h -->
# sources/distributed-fs/ceph-client/include/linux/hwspinlock.h

## Purpose
Defines the public hardware spinlock framework API for inter-processor or inter-core locks implemented in shared hardware.

## APIs, Control Flow, and State
Enabled builds provide registration/unregistration for lock banks, specific lock request/free, devm variants, device-tree ID lookup, lock busting, and internal trylock/timeout/unlock primitives. Inline wrappers select mode: normal disables preemption, irq disables local interrupts, irqsave preserves flags, raw leaves broader protection to the caller, and in-atomic is for atomic contexts. Timeout helpers busy-loop until success or timeout and never sleep; trylock helpers fail immediately on contention. Disabled builds intentionally let most users compile away and succeed, while registration fails/omits framework availability and specific request returns `ERR_PTR(-ENODEV)`.

## Dependencies, Integration, Risks, and Tests
Depends on device core, OF nodes, scheduler/preemption, and framework-private structs. Integrates with remoteproc, SoC mailbox/shared-resource drivers, and device-tree described hardware locks. Risks include sleeping while holding a non-raw hwspinlock, using raw mode without external serialization, long timeouts in atomic context, forgetting matching unlock mode, and treating `ERR_PTR(-ENODEV)` as a usable lock. Test signals include lock contention/timeout tests, irq/preemption state assertions, DT lookup coverage, devm cleanup, and !CONFIG compile behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hwspinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hyperv.h -->
# sources/distributed-fs/ceph-client/include/linux/hyperv.h

## Purpose
Defines Linux Hyper-V VMBus ABI structures, ring-buffer helpers, channel/device/driver state, GPADL packet formats, integration component messages, and public VMBus helper APIs.

## APIs, Control Flow, and State
Core state includes packed GPADL descriptors, `struct hv_ring_buffer`, `struct hv_ring_buffer_info`, VMBus channel offer/message structures, `struct vmbus_requestor`, `struct vmbus_channel`, `struct hv_driver`, and `struct hv_device`. Ring flow uses read/write indices, interrupt masks, pending-send-size flow control, `hv_begin_read()`/`hv_end_read()` barriers, and packet iterators. Channel flow negotiates VMBus version, accepts offers, opens channels with ring-buffer GPADLs, sends packets or GPA-direct buffers, receives packets, tears down GPADLs, changes target CPU, and closes channels. Persistent state lives in channel lists, ring pages, GPADL handles, request bitmaps, callback/tasklet/work objects, sysfs/debugfs objects, per-channel state, feature flags, and statistics counters.

## Dependencies, Integration, Risks, and Tests
Depends on Hyper-V UAPI/HVHDK definitions, memory management, scatterlists, device model, interrupts, timers, workqueues, GUIDs, PCI, DMA, and reciprocal division. Integrates with VMBus drivers for storage/network/video/KVP/time/heartbeat/hvsock/PCI and with confidential-computing paravisor flags for encrypted ring/external memory. Risks include packed ABI layout drift, ring index races, missing memory barriers, request ID reuse, rescind/open/close races, wrong GPADL page accounting when `PAGE_SIZE != HV_HYP_PAGE_SIZE`, and a suspicious `VMPACKET_TRANSFER_MODE()` cast to undefined `struct IMPACT`. Test signals include Hyper-V channel negotiation, ring wraparound and full-ring flow-control tests, GPADL establish/teardown, packet iterator tests, rescind stress, hvsock subchannel tests, and build checks for packet macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hyperv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hypervisor.h -->
# sources/distributed-fs/ceph-client/include/linux/hypervisor.h

## Purpose
Provides tiny generic hypervisor helpers for pinning vCPUs and detecting isolated PCI-function environments.

## APIs, Control Flow, and State
On x86, `hypervisor_pin_vcpu()` dispatches to `x86_platform.hyper.pin_vcpu()`. On non-x86, it is a no-op and `jailhouse_paravirt()` checks the device tree for a `jailhouse,cell` compatible node. `hypervisor_isolated_pci_functions()` returns true for s390, loongarch, or Jailhouse paravirtual cells. There is no local persistent state.

## Dependencies, Integration, Risks, and Tests
Depends on x86 platform hypervisor hooks or OF device-tree helpers. Integrates with scheduler/CPU placement and PCI isolation policy. Risks include the include guard typo spelling `HYPEVISOR`, non-x86 `of_find_compatible_node()` reference lifetime expectations, and architecture-specific assumptions hidden behind `IS_ENABLED`. Test signals include x86 hypervisor hook calls, OF Jailhouse detection, and config builds for x86, s390, loongarch, and generic non-x86.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hypervisor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i2c-algo-bit.h -->
# sources/distributed-fs/ceph-client/include/linux/i2c-algo-bit.h

## Purpose
Defines the bit-banging I2C adapter algorithm contract for controllers implemented through GPIO-like SDA/SCL callbacks.

## APIs, Control Flow, and State
`struct i2c_algo_bit_data` stores private callback data, setters/getters for SDA/SCL, optional transfer prologue/epilogue, half-cycle delay, timeout, and a `can_do_atomic` flag for non-sleeping callbacks. Adapters attach the algorithm through `i2c_bit_add_bus()` or `i2c_bit_add_numbered_bus()`, and can reference the exported `i2c_bit_algo`. State resides in adapter `algo_data` and timing parameters; transfers are implemented by the bit algorithm using these callbacks.

## Dependencies, Integration, Risks, and Tests
Depends on core I2C adapter types. Integrates with GPIO/pinctrl-backed I2C adapters and any hardware that needs software clocking. Risks include callbacks that sleep despite `can_do_atomic`, invalid `udelay` for SMBus/I2C timing, missing SCL reads for clock stretching, and bus hangs without proper timeout/recovery. Test signals include I2C transfer vectors, SMBus timing checks, arbitration/clock-stretch tests, and atomic transfer path coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i2c-algo-bit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i2c-algo-pca.h -->
# sources/distributed-fs/ceph-client/include/linux/i2c-algo-pca.h

## Purpose
Defines the algorithm interface and register constants for NXP PCA9564/PCA9665 I2C bus controller adapters.

## APIs, Control Flow, and State
The header exposes chip IDs, PCA9564 clock constants, direct/indirect register offsets, control bits, and PCA9665 bus modes. `struct pca_i2c_bus_settings` records derived mode, low/high SCL periods, and clock frequency. `struct i2c_algo_pca_data` supplies low-level byte read/write, wait, reset callbacks, selected clock, chip type, and bus settings. `i2c_pca_add_bus()` and `i2c_pca_add_numbered_bus()` attach the algorithm to adapters. State persists in adapter `algo_data` and hardware registers.

## Dependencies, Integration, Risks, and Tests
Depends on I2C core structures supplied by including translation units. Integrates with platform drivers wrapping PCA9564/PCA9665 register access. Risks include wrong oscillator assumptions, unsupported clock selection, wait callback timeouts, reset ordering, and mixing direct PCA9564 registers with PCA9665 indirect registers. Test signals include controller probe, selected bus frequency validation, transfer completion interrupts/polling, timeout recovery, and register access tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i2c-algo-pca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i2c-algo-pcf.h -->
# sources/distributed-fs/ceph-client/include/linux/i2c-algo-pcf.h

## Purpose
Defines the PCF8584 I2C adapter algorithm interface.

## APIs, Control Flow, and State
`struct i2c_algo_pcf_data` carries private data plus callbacks to set/get PCF controls, get own address and clock, wait for pin/interrupt, and optional transfer begin/end hooks. `lab_mdelay` controls multi-master lost-arbitration backoff. `i2c_pcf_add_bus()` attaches the algorithm. State lives in adapter `algo_data`, hardware control/status registers, and the configured arbitration delay.

## Dependencies, Integration, Risks, and Tests
Depends on I2C adapter definitions from surrounding includes. Integrates with board drivers for PCF8584-like hardware. Risks include missing multi-master backoff, callbacks that do not serialize hardware access, incorrect own-address/clock reporting, and wait callbacks that hang indefinitely. Test signals include transfer tests, arbitration-loss injection, bus clock verification, and timeout behavior during missing interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i2c-algo-pcf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i2c-atr.h -->
# sources/distributed-fs/ceph-client/include/linux/i2c-atr.h

## Purpose
Defines the I2C Address Translator helper API for devices that expose downstream buses using address aliases.

## APIs, Control Flow, and State
`enum i2c_atr_flags` distinguishes static mapping and passthrough behavior. `struct i2c_atr_ops` lets hardware drivers attach or detach an alias for a downstream address on a channel. `struct i2c_atr_adap_desc` describes each child adapter, including channel ID, parent device, firmware node, and optional private alias pool. `i2c_atr_new()` creates an ATR helper tied to a parent adapter and device; `i2c_atr_add_adapter()` creates child buses; `i2c_atr_del_adapter()` removes them; `i2c_atr_delete()` requires all child adapters be removed first; set/get driver-data helpers attach private state.

## Dependencies, Integration, Risks, and Tests
Depends on I2C core, device/fwnode APIs, and bit flags. Integrates with camera/serializer/deserializer and similar topologies where identical downstream devices need address translation. Risks include alias pool exhaustion, deleting ATR before child adapters, static mapping assumptions with dynamic devices, incorrect firmware-node channel matching, and passthrough address conflicts. Test signals include adding/removing downstream devices, alias attach/detach callback order, private alias pool selection, duplicate address handling, and hot-unplug cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i2c-atr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i2c-dev.h -->
# sources/distributed-fs/ceph-client/include/linux/i2c-dev.h

## Purpose
Provides the in-kernel wrapper for the userspace I2C character-device UAPI and defines the I2C char-device major number.

## APIs, Control Flow, and State
The header includes `<uapi/linux/i2c-dev.h>` and defines `I2C_MAJOR` as 89. It has no functions or local state; actual char-device control flow is implemented by the i2c-dev driver and UAPI ioctl definitions.

## Dependencies, Integration, Risks, and Tests
Depends on the exported UAPI header. Integrates with `/dev/i2c-*` nodes, userspace ioctl clients, and device-number registration. Risks are ABI mismatch with UAPI definitions or incorrect assumptions that this header implements device operations. Test signals include i2c-dev module/device creation, major number registration, and ioctl compatibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i2c-dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i2c-mux.h -->
# sources/distributed-fs/ceph-client/include/linux/i2c-mux.h

## Purpose
Defines I2C mux core data structures and helpers for creating child I2C adapters behind a multiplexer, arbitrator, or gate.

## APIs, Control Flow, and State
Within `__KERNEL__`, `struct i2c_mux_core` stores parent adapter, owning device, mode flags, private data, select/deselect callbacks, adapter counts, and flexible array of child adapters. `i2c_mux_alloc()` allocates the core with private storage and callbacks. `I2C_MUX_LOCKED`, `I2C_MUX_ARBITRATOR`, and `I2C_MUX_GATE` configure locking/behavior. `i2c_mux_add_adapter()` creates child buses identified by channel ID, and `i2c_mux_del_adapters()` removes them. `i2c_root_adapter()` finds the root adapter for a device.

## Dependencies, Integration, Risks, and Tests
Depends on bitops and I2C adapter definitions. Integrates with I2C mux drivers, nested mux topologies, and bus locking. Risks include incorrect select/deselect symmetry, deadlocks with locked muxes, orphaned child adapters, wrong force bus numbers, and private data sizing mistakes. Test signals include nested mux transfer routing, channel select/deselect traces, adapter add/remove cleanup, and locking stress across root vs segment locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i2c-mux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i2c-of-prober.h -->
# sources/distributed-fs/ceph-client/include/linux/i2c-of-prober.h

## Purpose
Defines an OF dynamic component prober for discovering I2C-attached components that need temporary resources enabled before normal driver probing.

## APIs, Control Flow, and State
`struct i2c_of_probe_ops` supplies optional ordered callbacks: `enable()` powers or prepares components, `cleanup_early()` releases exclusive resources before probing a found component, and `cleanup()` balances enable on exit. `struct i2c_of_probe_cfg` binds ops to a device-node prefix type. With `CONFIG_OF_DYNAMIC`, `i2c_of_probe_component()` performs the probing. Simple helpers support one regulator and optional GPIO, with `struct i2c_of_probe_simple_opts` describing supply, GPIO polarity, and delays, and `struct i2c_of_probe_simple_ctx` storing regulator/GPIO handles.

## Dependencies, Integration, Risks, and Tests
Depends on kconfig, OF dynamic nodes, devices, regulators, GPIO descriptors, and sleeps. Integrates with display/touchpad/touchscreen-style components that are board-described but require power sequencing to respond on I2C. Risks include using devres from callbacks despite the warning, leaking resources when `cleanup_early()` already released them, misspelled documentation reference `free_resourcs_late`, delay/polarity mistakes, and missing `-EPROBE_DEFER` handling. Test signals include OF dynamic probe success/failure paths, regulator/GPIO sequencing, no-component cleanup, component-found cleanup-early order, and !CONFIG_OF_DYNAMIC builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i2c-of-prober.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i2c-smbus.h -->
# sources/distributed-fs/ceph-client/include/linux/i2c-smbus.h

## Purpose
Declares SMBus-specific helper devices and alert/host-notify support layered on the I2C core.

## APIs, Control Flow, and State
`struct i2c_smbus_alert_setup` optionally passes an IRQ to the SMBus alert client. `i2c_new_smbus_alert_device()` creates the alert response address client, and `i2c_handle_smbus_alert()` handles alerts. If both SMBus and I2C slave support are enabled, host-notify slave helpers create/free a host-notify device; otherwise they return `ERR_PTR(-ENOSYS)` or no-op. If SMBus and DMI are enabled, SPD write-protect registration helpers expose platform policy; otherwise they are no-ops.

## Dependencies, Integration, Risks, and Tests
Depends on I2C core, spinlocks, and workqueues. Integrates with SMBus alert protocol, host notify, DIMM SPD write-protection policy, and adapter interrupt/polling implementations. Risks include assuming IRQ handling exists when `irq` is omitted, failing to free host-notify clients, not checking `ERR_PTR`, and SPD policy being compiled out. Test signals include SMBALERT# events, host-notify slave callbacks, alert polling fallback, SPD write enable/disable registration, and config combinations for SMBus/slave/DMI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i2c-smbus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i2c.h -->
# sources/distributed-fs/ceph-client/include/linux/i2c.h

## Purpose
Defines the Linux I2C bus core interface: clients, drivers, adapters, algorithms, board info, transfers, SMBus helpers, slave mode, recovery, quirks, firmware discovery, and registration helpers.

## APIs, Control Flow, and State
Important types are `struct i2c_driver`, `struct i2c_client`, `struct i2c_board_info`, `struct i2c_algorithm`, `struct i2c_lock_operations`, `struct i2c_timings`, `struct i2c_bus_recovery_info`, `struct i2c_adapter_quirks`, and `struct i2c_adapter`. Transfer flow starts at `i2c_master_send/recv()` or `i2c_transfer()`, then dispatches through adapter `algo` callbacks; SMBus helpers dispatch through `i2c_smbus_xfer()` or emulation. Adapter state includes locks, timeout/retries, device object, suspend flags, userspace client list, recovery info, quirks, host-notify IRQ domain, regulator, debugfs, and address-instantiation bitmap. Registration APIs add/del adapters and drivers, create static/scanned/dummy/ancillary clients, parse firmware timings, and find clients/adapters by fwnode/OF/ACPI. Disabled I2C/OF/ACPI paths provide stubs.

## Dependencies, Integration, Risks, and Tests
Depends on device model, ACPI, OF, regulator, rtmutex, IRQ domains, uapi I2C messages, and optional slave/mux support. It integrates with almost every I2C controller and device driver, userspace i2c-dev, firmware enumeration, runtime/system suspend, bus recovery, and SMBus alert/host notify. Risks include missing adapter functionality checks, violating adapter quirks, transfer while suspended, incorrect root-vs-segment locking, DMA-unsafe buffers, client lifetime leaks from find helpers, and broken firmware enumeration fallback. Test signals include I2C selftests, adapter registration/removal, SMBus protocol vectors, bus recovery, mux locking, suspend transfer rejection, ACPI/OF enumeration, and config-matrix builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i3c/ccc.h -->
# sources/distributed-fs/ceph-client/include/linux/i3c/ccc.h

## Purpose
Defines I3C Common Command Code identifiers and payload structures used by master controllers to configure and query I3C devices.

## APIs, Control Flow, and State
`I3C_CCC_ID()` builds broadcast/direct command IDs. Macros enumerate broadcast, unicast, dual-mode, vendor, event, status, HDR, and XTIME command IDs. Payload structs cover event enable/disable, max write/read length, DEFSLVS device descriptors, test mode, dynamic address assignment, PID/BCR/DCR/status reads, master handoff, bridged targets, max data speed, HDR capability, SETXTIME/GETXTIME, and generic command destinations. `struct i3c_ccc_cmd` binds direction, command ID, destination payloads, destination count, and returned `enum i3c_error_code`. State is transient command/payload buffers; payload data must be DMA-able.

## Dependencies, Integration, Risks, and Tests
Depends on bitops and `i3c/device.h` for error codes and device concepts. Integrates with I3C master controller command paths, dynamic address assignment, multi-master support, IBI control, HDR capability negotiation, and vendor extensions. Risks include using broadcast commands with multiple destinations incorrectly, endian mistakes in packed payloads, non-DMA-able payload buffers, mismatched payload length, and subcommand typos such as the comment spelling `ddefined`. Test signals include CCC command encoding tests, ENTDAA/SETDASA/SETNEWDA flows, GETPID/BCR/DCR parsing, HDR capability negotiation, and controller error-code propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i3c/ccc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i3c/device.h -->
# sources/distributed-fs/ceph-client/include/linux/i3c/device.h

## Purpose
Defines the I3C device-driver interface, transfer descriptors, device information, ID matching helpers, combined I2C/I3C driver registration, and in-band interrupt management.

## APIs, Control Flow, and State
`enum i3c_error_code` carries M0/M1/M2 protocol error detail. `enum i3c_xfer_mode` distinguishes SDR and HDR modes. `struct i3c_xfer` describes one private transfer with direction/command, length, actual length, DMA-able buffer, and error code. PID/BCR macros decode manufacturer, part, role, HDR, bridge, offline, IBI, and speed-limitation capabilities. `struct i3c_device_info` caches discovered PID/BCR/DCR, static/dynamic address, HDR capability, speed limits, IBI length, turnaround, and max transfer sizes. `struct i3c_driver` wraps device-driver callbacks and ID table. Registration helpers support pure I3C drivers, module boilerplate, and paired I2C/I3C drivers that fall back to I2C-only when `CONFIG_I3C` is disabled. IBI APIs request/free/enable/disable preallocated slots and workqueue-context handlers.

## Dependencies, Integration, Risks, and Tests
Depends on device model, I2C core, module infrastructure, and mod_devicetable IDs. Integrates with I3C master core, dual-mode devices, dynamic address assignment (`i3c_device_do_setdasa()`), private SDR/HDR transfers, and IBI event delivery. Risks include non-DMA-safe buffers, ignoring `actual_len` or `err` after `-EIO`, mismatched I2C/I3C registration rollback, insufficient IBI slots, slow sleeping IBI handlers delaying queued IBIs, and assuming I3C APIs work in !CONFIG builds. Test signals include I3C driver probe/remove, ID matching by PID/DCR/extra info, SDR/HDR transfer vectors, paired I2C/I3C registration failure rollback, IBI flood tests, and disabled-I3C fallback builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i3c/device.h -->
