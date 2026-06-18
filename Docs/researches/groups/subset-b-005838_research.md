# subset-b-005838 research

Grouped research for Linux header files under `sources/distributed-fs/ceph-client/include/linux`. Each file section is delimited for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/avf/virtchnl.h -->
# sources/distributed-fs/ceph-client/include/linux/avf/virtchnl.h

## Purpose
Defines Intel AVF/IAVF virtual channel ABI used by a virtual function (VF) driver to communicate with a physical function (PF) over the admin queue. The header is a wire contract: opcode numbers, status codes, capability flags, fixed-size structures, variable-length payload sizing helpers, and inline validation must remain layout-stable across VF/PF versions.

## Important APIs, types, and functions
- `enum virtchnl_status_code`, `enum virtchnl_ops`, `struct virtchnl_version_info`, and `VIRTCHNL_VERSION_*` describe the base protocol and compatibility gates.
- Resource and queue setup types include `virtchnl_vf_resource`, `virtchnl_vsi_resource`, `virtchnl_txq_info`, `virtchnl_rxq_info`, `virtchnl_vsi_queue_config_info`, `virtchnl_irq_map_info`, `virtchnl_queue_select`, and `virtchnl_vf_res_request`.
- Feature families cover MAC/VLAN filters, RSS, cloud filters, RDMA interrupt mapping, FDIR, PTP, QoS, queue bandwidth, and quanta.
- `VIRTCHNL_CHECK_STRUCT_LEN` and `VIRTCHNL_CHECK_UNION_LEN` intentionally fail compilation if ABI layouts drift.
- `virtchnl_struct_size()` handles legacy flexible-array sizing for selected message structs.
- `virtchnl_vc_validate_vf_msg()` is the only executable logic: it maps an opcode to the expected payload length and rejects malformed VF messages.

## Control flow and state
The documented VF initialization sequence is version negotiation, reset, resource discovery, queue and interrupt configuration, queue enablement, optional filter/offload setup, then traffic. The reset operation is asynchronous and has no PF response; the VF polls hardware reset state instead. `virtchnl_vc_validate_vf_msg()` switches on the opcode, computes a fixed or flexible payload length, performs selected semantic checks such as nonzero element counts and nonzero quanta size, and returns `VIRTCHNL_STATUS_ERR_OPCODE_MISMATCH` or `VIRTCHNL_STATUS_ERR_PARAM` for invalid input.

## State and persistence behavior
The header itself persists no state, but it defines state exchanged between PF and VF: VF capabilities, queue resources, VLAN/offload settings, RSS keys/LUTs, flow IDs, PTP capability grants, QoS limits, and reset states. Flexible arrays are protocol payloads and must be sized from count fields. Reserved fields are compatibility state and should be zeroed and validated by participants.

## Dependencies and integration points
Depends on kernel bit macros, overflow/`struct_size()` helpers, and Ethernet address constants. Integrated by Intel virtual NIC PF/VF drivers and RDMA clients that route opaque RDMA messages. The `REQ` style validation is PF-side defensive code for messages arriving from a VF and should align with firmware admin-queue transport constraints.

## Risks
ABI drift is the dominant risk: changing enum values, structure padding, or legacy size constants can break PF/VF interoperability. Flexible-array length calculations are sensitive to untrusted count fields. Several comments mark deprecated or legacy fields that must still be understood. PTP and VLAN v2 negotiation require cross-checking requested capability bits against PF-granted bits.

## Test signals
Compile-time layout assertions should remain green on all target architectures. Unit or driver tests should feed `virtchnl_vc_validate_vf_msg()` valid and invalid payloads for fixed-size, zero-length, flexible-array, and reserved opcodes. Integration tests should cover VF startup, reset polling, queue setup, VLAN v1/v2 negotiation, RSS/FDIR programming, and capability downgrade paths with older PFs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/avf/virtchnl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/backing-dev-defs.h -->
# sources/distributed-fs/ceph-client/include/linux/backing-dev-defs.h

## Purpose
Defines the core backing-device and writeback data structures used by the VM, filesystem, and block layers to track dirty data, writeback bandwidth, throttling, and cgroup-specific writeback ownership.

## Important APIs, types, and functions
- `enum wb_state`, `enum wb_stat_item`, and `enum wb_reason` describe writeback state bits, per-wb counters, and trigger reasons.
- `struct wb_completion` and `WB_COMPLETION_INIT` support waiting for queued writeback work.
- `struct bdi_writeback` owns dirty inode lists, writeback work queues, bandwidth estimates, throttling fields, and optional memcg/blkcg associations.
- `struct backing_dev_info` owns device-level identity, readahead/IO limits, reference count, capabilities, aggregate bandwidth, root `bdi_writeback`, cgroup-wb index, waitqueue, and debug/device metadata.
- Inline refcount helpers `wb_tryget()`, `wb_get()`, `wb_put_many()`, `wb_put()`, and `wb_dying()` abstract cgroup versus root writeback lifetime rules.

## Control flow and state
Callers register a `backing_dev_info`, then writeback code queues work onto a `bdi_writeback` and moves inodes among `b_dirty`, `b_io`, `b_more_io`, and `b_dirty_time` under `list_lock`. Work scheduling is guarded by `work_lock`. With cgroup writeback, per-memcg/blkcg writeback objects are indexed through `cgwb_tree` and refcounted independently.

## State and persistence behavior
All state is in-memory kernel state. Dirty counters are percpu and approximate until summed. Write bandwidth and throttle rates persist for the lifetime of the BDI/WB and inform later dirty throttling. Cgroup writeback objects pin associated cgroup CSS objects and are released asynchronously via percpu refs, work, or RCU.

## Dependencies and integration points
Depends on kernel list, radix-tree, rb-tree, spinlock, percpu counter/refcount, flex proportions, workqueue, timer, kref, and refcount APIs. Integrated by `backing-dev.h`, writeback core, filesystems, memory cgroups, block cgroups, debugfs, and device model ownership.

## Risks
Locking and lifetime are the primary hazards. Dirty inode lists require `list_lock`; work queues require `work_lock`; cgroup writeback requires percpu-ref and RCU discipline. `WB_has_dirty_io` and `tot_write_bandwidth` are used as fast signals and can become misleading if not updated consistently.

## Test signals
Kernel writeback tests should exercise dirtying, background writeback, sync writeback, BDI unregister, and cgroup writeback creation/offline. Lockdep and KCSAN are useful for list/refcount races. Debugfs or tracepoint observations should show correct `wb_reason` and bandwidth updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/backing-dev-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/backing-dev.h -->
# sources/distributed-fs/ceph-client/include/linux/backing-dev.h

## Purpose
Provides the public helper API for allocating, registering, querying, and using `backing_dev_info` and `bdi_writeback` objects from filesystems, block devices, and VM writeback paths.

## Important APIs, types, and functions
- Lifecycle: `bdi_alloc()`, `bdi_init()`, `bdi_register()`, `bdi_register_va()`, `bdi_unregister()`, `bdi_get_by_id()`, `bdi_get()`, and `bdi_put()`.
- Writeback control: `wb_start_background_writeback()`, `wb_workfn()`, `wb_wait_for_completion()`, `writeback_in_progress()`, and `wb_writeout_inc()`.
- Counters and policy: `wb_stat_mod()`, `wb_stat()`, `wb_stat_sum()`, `wb_stat_error()`, `bdi_get_min_bytes()`, `bdi_get_max_bytes()`, ratio/byte setters, and `bdi_set_strict_limit()`.
- Mapping helpers: `inode_to_bdi()`, `mapping_can_writeback()`, `inode_to_wb()`, `inode_to_wb_wbc()`, and unlocked inode-WB transaction helpers.
- Cgroup writeback helpers: `inode_cgwb_enabled()`, `wb_find_current()`, `wb_get_create_current()`, `wb_memcg_offline()`, and `wb_blkcg_offline()`.

## Control flow and state
Device setup allocates and registers a BDI, then filesystems use `inode_to_bdi()` and `inode_to_wb()` to attribute dirtying and writeback. For cgroup-aware filesystems, current task memory/io cgroups are mapped to a WB under RCU; missing or stale entries are created via `wb_get_create()`. Unlocked WB lookup uses `I_WB_SWITCH`, an RCU read-side section, and optional `i_pages` locking to keep inode-WB association stable.

## State and persistence behavior
The API manipulates in-memory BDI and WB lifetimes. `bdi_has_dirty_io()` uses aggregate write bandwidth as a dirtiness signal. Ratio and byte limit setters alter runtime dirty throttling policy. Cgroup writeback association can change dynamically with cgroup configuration and inode switching.

## Dependencies and integration points
Depends on scheduler, filesystem, device, writeback, slab, and `backing-dev-defs.h`. Integrated by address-space writeback checks, filesystem dirty accounting, cgroup writeback, blk-wbt, and global `bdi_wq`.

## Risks
Filesystems that support cgroup writeback must not use root-only helpers like `bdi_wb_dirty_exceeded()` and `bdi_wb_stat_mod()`. Calling unlocked inode-WB accessors while sleeping or without ending the transaction can leak RCU/locks. Incorrect BDI capabilities can either lose dirty accounting or throttle devices incorrectly.

## Test signals
Build both `CONFIG_CGROUP_WRITEBACK=y` and `n`. Exercise dirty accounting for normal and cgrouped writes, inode WB switching, BDI unregister while dirty work is pending, and strict dirty limit changes. Lockdep should not flag unlocked inode-WB lookup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/backing-dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/backing-file.h -->
# sources/distributed-fs/ceph-client/include/linux/backing-file.h

## Purpose
Declares common helpers for stackable filesystems that operate on real backing files while preserving the user file context and credentials.

## Important APIs, types, and functions
- `struct backing_file_ctx` carries the credentials used for backing access plus optional `accessed()` and `end_write()` callbacks.
- Open helpers: `backing_file_open()` and `backing_tmpfile_open()`.
- I/O helpers: `backing_file_read_iter()`, `backing_file_write_iter()`, `backing_file_splice_read()`, and `backing_file_splice_write()`.
- Mapping helper: `backing_file_mmap()`.

## Control flow and state
A stackable filesystem opens a backing file or tmpfile with explicit credentials, then routes read/write/splice/mmap operations through these helpers. The context callbacks let the caller mirror access-time or write-completion side effects back into the upper file/inode.

## State and persistence behavior
This header defines no storage itself. Persistent effects are delegated to the opened backing file and filesystem. Credential state is explicit and must be chosen by the stackable filesystem rather than inherited accidentally from the current task.

## Dependencies and integration points
Depends on `file.h`, `uio.h`, and `fs.h`. Integrated by overlay/stackable filesystem implementations and VFS iterator/splice/mmap paths.

## Risks
Credential confusion is the main risk: using the wrong `cred` can bypass or over-restrict access. Callback ordering must match actual I/O completion. The helper prototypes expose flags and iterators directly, so callers must respect VFS iterator ownership and partial-I/O semantics.

## Test signals
Tests should cover read/write/splice/mmap through stackable files with overridden credentials, partial I/O, permission-denied paths, atime updates, and delayed write completion callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/backing-file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/backlight.h -->
# sources/distributed-fs/ceph-client/include/linux/backlight.h

## Purpose
Defines the kernel backlight class abstraction used by display, platform, firmware, and raw hardware drivers to expose brightness and power control to userspace and display-notification paths.

## Important APIs, types, and functions
- `enum backlight_update_reason`, `enum backlight_type`, and `enum backlight_scale` classify update source, control mechanism, and brightness scale.
- `struct backlight_ops` supplies `update_status()`, optional `get_brightness()`, and optional `controls_device()` callbacks.
- `struct backlight_properties` stores user brightness, maximum brightness, power, type, core state bits, and scale.
- `struct backlight_device` stores properties, locks, ops pointer, class device, list entry, and `use_count`.
- Registration and lookup APIs include `backlight_device_register()`, `devm_backlight_device_register()`, unregister variants, `backlight_device_get_by_name()`, `backlight_device_get_by_type()`, OF lookup helpers, and brightness/update helpers.

## Control flow and state
Drivers register a `backlight_device` with immutable maximum brightness and type. Userspace or display events mutate `props` and call `backlight_update_status()`, which serializes `ops->update_status()` under `update_lock`. `backlight_enable()` and `backlight_disable()` change power and blank state before invoking the callback. Drivers should call `backlight_get_brightness()` in `update_status()` so blank/suspend state maps to zero brightness.

## State and persistence behavior
State is runtime class-device state visible via `/sys/class/backlight`. Core state bits such as `BL_CORE_SUSPENDED` and `BL_CORE_FBBLANK` are owned by the core, not drivers. Device-managed registration ties lifetime to a parent device.

## Dependencies and integration points
Depends on device model, mutexes, types, OF support, and optional `CONFIG_BACKLIGHT_CLASS_DEVICE`. Integrates with framebuffer/display blank notifications, sysfs, platform and firmware display drivers, and device-managed resource cleanup.

## Risks
Drivers must not mutate core-owned state or use internal locks directly. `ops` can be NULL after driver unload, so callbacks are checked. Incorrect `controls_device()` can blank or unblank the wrong display. Brightness values must stay within `0..max_brightness`.

## Test signals
Test registration/unregistration, sysfs brightness and `bl_power`, suspend/resume when `BL_CORE_SUSPENDRESUME` is set, display blank notifications, OF lookup fallback, and driver unload while class device references exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/backlight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/badblocks.h -->
# sources/distributed-fs/ceph-client/include/linux/badblocks.h

## Purpose
Declares a compact bad-block extent table used by block-like devices to track damaged sectors, including acknowledged versus unacknowledged bad blocks.

## Important APIs, types, and functions
- `BB_*` masks/macros encode a bad-block extent in a 64-bit entry: 54-bit sector offset, 9-bit length minus one, and one acknowledged bit.
- `MAX_BADBLOCKS` stores one page of 64-bit entries.
- `struct badblocks` contains device association, count, unacknowledged hint, sector shift, extent page, change flag, seqlock, and device range.
- `badblocks_check()`, `badblocks_set()`, `badblocks_clear()`, `ack_all_badblocks()`, `badblocks_show()`, `badblocks_store()`, init/exit, and devm helpers are the main API.

## Control flow and state
Device code initializes the table, sets or clears bad sector ranges, checks I/O ranges against it, and exposes show/store helpers for sysfs-like control. Writers update the sorted table under the seqlock; readers can retry if the sequence changes.

## State and persistence behavior
The in-memory table records extents only for the lifetime of `struct badblocks`; persistence depends on the owning device or metadata layer. `changed` signals dirty metadata to the owner, and `unacked_exist` is a hint that is only cleared after a read finds none.

## Dependencies and integration points
Depends on seqlocks, device warnings, kernel types, and page-size storage. Integrated by md/raid, nvdimm, and other block subsystems that need bad-sector bookkeeping.

## Risks
The table can fill (`MAX_BADBLOCKS`), range encoding is limited to `BB_MAX_LEN`, and shift conversions can disable badblocks if negative. Incorrect use of `devm_exit_badblocks()` on the wrong device emits a warning and leaves cleanup to the correct owner.

## Test signals
Tests should cover set/check/clear overlap cases, acknowledged and unacknowledged states, full-table behavior, sysfs parsing/printing, changed-flag transitions, and concurrent readers during updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/badblocks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/balloon.h -->
# sources/distributed-fs/ceph-client/include/linux/balloon.h

## Purpose
Defines the common memory balloon interface, including page migration support for pages inflated by balloon drivers.

## Important APIs, types, and functions
- `struct balloon_dev_info` tracks isolated pages, the balloon page list, optional `migratepage()` callback, and managed-page accounting preference.
- Page APIs include `balloon_page_alloc()`, enqueue/dequeue helpers, and list enqueue/dequeue helpers.
- `balloon_devinfo_init()` initializes counters, list head, migration callback, and accounting flag.

## Control flow and state
Balloon drivers allocate pages, associate them with a balloon device via `page->private`, and enqueue them on the balloon list. Migration uses movable-ops page migration: isolation/dequeue and inflation/deflation must synchronize through the balloon page lock rules documented in the header.

## State and persistence behavior
State is volatile guest memory-management state. `page->private` indicates whether a page belongs to the balloon or is isolated for migration; clearing it means isolation is no longer possible. `isolated_pages` tracks pages removed from the list for migration.

## Dependencies and integration points
Depends on pagemap, page flags, migration, GFP allocation, error helpers, and list APIs. Integrated by virtio-balloon, Xen, Hyper-V, and compaction/migration code.

## Risks
Lockless compaction scanners can race with inflation/deflation. The documented rules around `page->private` and the balloon list are correctness-critical. Incorrect managed-page accounting can skew VM memory totals.

## Test signals
Exercise inflate/deflate under memory pressure, page migration/compaction of balloon pages, concurrent isolation and dequeue, and accounting changes when `adjust_managed_page_count` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/balloon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/base64.h -->
# sources/distributed-fs/ceph-client/include/linux/base64.h

## Purpose
Declares kernel base64 encode/decode helpers supporting standard RFC 4648, URL-safe RFC 4648, and IMAP RFC 3501 alphabets.

## Important APIs, types, and functions
- `enum base64_variant` selects `BASE64_STD`, `BASE64_URLSAFE`, or `BASE64_IMAP`.
- `BASE64_CHARS(nbytes)` computes an encoded character upper bound for a byte count.
- `base64_encode()` and `base64_decode()` take explicit lengths, destination buffers, padding policy, and variant.

## Control flow and state
The header has no inline logic beyond size calculation. Callers provide source and destination buffers; implementation performs stateless conversion according to variant and padding.

## State and persistence behavior
No persistent state. Encoded data may become persistent only through callers, for example filenames, keys, or metadata.

## Dependencies and integration points
Depends on kernel integer types. Likely integrated by filesystem crypto/name handling and other subsystems that need in-kernel textual binary representation.

## Risks
Callers must size `dst` correctly and match decode padding/variant to the encoded input. `BASE64_CHARS` is useful for expansion but does not account for terminators unless callers add space.

## Test signals
Use known vectors for all variants, padded and unpadded inputs, invalid characters, short/truncated inputs, and buffer-boundary lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/base64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcd.h -->
# sources/distributed-fs/ceph-client/include/linux/bcd.h

## Purpose
Provides binary-coded decimal conversion helpers for kernel code that reads or writes BCD-encoded hardware or firmware fields.

## Important APIs, types, and functions
- `bcd2bin(x)` and `bin2bcd(x)` choose compile-time constant conversions when possible and otherwise call `_bcd2bin()` or `_bin2bcd()`.
- `bcd_is_valid(x)` validates that both nibbles are decimal digits.
- `const_bcd2bin()`, `const_bin2bcd()`, and `const_bcd_is_valid()` implement simple constant expressions.

## Control flow and state
No runtime state. The macros use `__builtin_constant_p` to select constant arithmetic for constant inputs, reducing call overhead and enabling initializer use.

## State and persistence behavior
No persistence. Callers usually translate persistent RTC, firmware, or device-register fields into normal integers and back.

## Dependencies and integration points
Depends on compiler attributes. Integrated by RTC, firmware, NVRAM, and device drivers with BCD registers.

## Risks
`bin2bcd()` assumes values are in a representable two-digit range unless the caller enforces bounds. `bcd_is_valid()` is separate and must be used before trusting external BCD input.

## Test signals
Test all valid `00..99` conversions, invalid nibbles, constant-expression use in initializers, and runtime conversion paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bch.h -->
# sources/distributed-fs/ceph-client/include/linux/bch.h

## Purpose
Declares the generic binary BCH error-correcting code library, configurable by Galois field order and error-correction strength.

## Important APIs, types, and functions
- `struct bch_control` stores BCH parameters (`m`, `n`, `t`, ECC sizes), lookup tables, working buffers, polynomial state, and bit-swap mode.
- `bch_init()` allocates and initializes a control object.
- `bch_free()` releases it.
- `bch_encode()` computes ECC bytes for data.
- `bch_decode()` uses data, received/calculated ECC, optional syndromes, and outputs error locations.

## Control flow and state
Callers initialize a reusable control object once, then use it for repeated encode/decode operations. Decode computes or consumes syndromes, builds locator polynomials, and reports correctable error positions through `errloc`.

## State and persistence behavior
The control object owns runtime lookup tables and scratch buffers; it is not persistent metadata. ECC bytes generated by callers are persistent only when stored with NAND/flash or other protected data.

## Dependencies and integration points
Depends on kernel types. Integrated by NAND/MTD, storage, and firmware code needing software BCH ECC.

## Risks
Parameters must match the storage format exactly: field order, correction strength, primitive polynomial, ECC byte count, and bit order. Sharing one `bch_control` concurrently may be unsafe unless the implementation is externally serialized because it contains scratch buffers.

## Test signals
Use encode/decode vectors for configured NAND layouts, inject up to `t` bit errors, inject more than `t` errors, verify `swap_bits` behavior, and run allocation-failure cleanup tests around `bch_init()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcm47xx_nvram.h -->
# sources/distributed-fs/ceph-client/include/linux/bcm47xx_nvram.h

## Purpose
Declares Broadcom BCM47xx NVRAM initialization and lookup helpers, with stubbed `-ENOTSUPP` behavior when support is disabled.

## Important APIs, types, and functions
- `bcm47xx_nvram_init_from_iomem()` and `bcm47xx_nvram_init_from_mem()` initialize NVRAM contents from mapped or physical memory ranges.
- `bcm47xx_nvram_getenv()` retrieves a named variable into a caller buffer.
- `bcm47xx_nvram_gpio_pin()` parses a named GPIO pin setting.
- `bcm47xx_nvram_get_contents()` returns a vmalloc-backed copy and `bcm47xx_nvram_release_contents()` releases it with `vfree()`.

## Control flow and state
Platform code initializes NVRAM early, then drivers query variables. When `CONFIG_BCM47XX_NVRAM` is unset, all lookup/init calls fail or return NULL and release is a no-op.

## State and persistence behavior
NVRAM is persistent board firmware data. The header exposes read-only access and copied content release; mutation is not declared here.

## Dependencies and integration points
Depends on errno, integer types, and vmalloc. Integrated by BCM47xx platform setup, wireless/ethernet GPIO configuration, SPROM fallback, and board detection.

## Risks
Callers must handle disabled support and missing keys. Buffer lengths for `getenv()` must include terminator space. Contents returned from `get_contents()` must be released only with the matching helper.

## Test signals
Test enabled and disabled config builds, lookup of present/missing variables, truncation behavior, GPIO parsing, init from memory bounds, and content-copy release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcm47xx_nvram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcm47xx_sprom.h -->
# sources/distributed-fs/ceph-client/include/linux/bcm47xx_sprom.h

## Purpose
Declares BCM47xx SPROM filling and fallback registration helpers used to populate shared SSB/BCMA SPROM data from board-specific NVRAM sources.

## Important APIs, types, and functions
- `bcm47xx_fill_sprom()` fills an `ssb_sprom` using an optional prefix and fallback flag.
- `bcm47xx_sprom_register_fallbacks()` registers fallback callbacks for devices lacking physical SPROM contents.
- Disabled-config stubs do nothing or return `-ENOTSUPP`.

## Control flow and state
Platform initialization registers fallbacks, then bus/device code asks for SPROM contents. The fill helper maps NVRAM key prefixes into SPROM fields when support is compiled in.

## State and persistence behavior
SPROM data reflects persistent board calibration/configuration but is represented in memory in `struct ssb_sprom`. This header does not expose writeback to persistent storage.

## Dependencies and integration points
Depends on errno/types/vmalloc and forward-declares `struct ssb_sprom`. Integrated with SSB/BCMA bus probing and BCM47xx NVRAM.

## Risks
Incorrect prefix or fallback selection can apply wrong board calibration data to a wireless device. Callers must handle `-ENOTSUPP` when platform support is absent.

## Test signals
Test SPROM population from representative NVRAM sets, fallback registration with missing physical SPROM, disabled support builds, and multi-device prefix selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcm47xx_sprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcm47xx_wdt.h -->
# sources/distributed-fs/ceph-client/include/linux/bcm47xx_wdt.h

## Purpose
Defines the BCM47xx watchdog device wrapper tying hardware timer operations, a generic `watchdog_device`, and optional software timer fallback state together.

## Important APIs, types, and functions
- `struct bcm47xx_wdt` stores hardware timer callbacks `timer_set()` and `timer_set_ms()`, `max_timer_ms`, driver-private data, embedded `watchdog_device`, `soft_timer`, and `soft_ticks`.
- `bcm47xx_wdt_get_drvdata()` returns driver-private data.

## Control flow and state
The watchdog driver fills the structure with timer callbacks and registers the embedded watchdog device. Runtime pings program the hardware timer directly or maintain a software timer that refreshes hardware before its maximum interval expires.

## State and persistence behavior
State is runtime watchdog state. Hardware timer state can outlive Linux if not stopped, but this header only describes in-memory bookkeeping and callbacks.

## Dependencies and integration points
Depends on kernel timers, atomics via included types, and watchdog framework. Integrated by BCM47xx chipcommon/watchdog drivers.

## Risks
Callback units must be respected (`timer_set` ticks versus `timer_set_ms` milliseconds). `soft_ticks` is atomic because soft timer and watchdog operations can race. Incorrect `max_timer_ms` can allow premature resets or ineffective pings.

## Test signals
Exercise watchdog start/stop/ping, timeout values above and below hardware maximum, software timer refresh, driver-data retrieval, and shutdown/reboot behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcm47xx_wdt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcm963xx_nvram.h -->
# sources/distributed-fs/ceph-client/include/linux/bcm963xx_nvram.h

## Purpose
Defines the Broadcom BCM963xx board NVRAM layout, size/version constants, NAND partition helpers, and an inline checksum verifier.

## Important APIs, types, and functions
- `BCM963XX_NVRAM_V4_SIZE`, `BCM963XX_NVRAM_V5_SIZE`, and `BCM963XX_DEFAULT_PSI_SIZE` define versioned layout sizes.
- `enum bcm963xx_nvram_nand_part` indexes boot, rootfs, data, and BBT partition arrays.
- `struct bcm963xx_nvram` lays out bootline, board name, PSI size, MAC count/base, v4 checksum, NAND offsets/sizes, and v5 checksum.
- `bcm963xx_nvram_nand_part_offset()` and `_size()` convert KiB fields to bytes.
- `bcm963xx_nvram_checksum()` verifies CRC32 with the checksum field treated as zero.

## Control flow and state
Boot/platform code reads the persistent NVRAM block, verifies checksum according to `version`, then consumes fixed fields and NAND partition descriptors. Macros provide named partition access.

## State and persistence behavior
The structure maps persistent firmware NVRAM. Offsets and sizes are stored in KiB and converted to bytes. Checksum choice depends on layout version: v4 uses the 300-byte minimum, newer versions use 1 KiB.

## Dependencies and integration points
Depends on CRC32, Ethernet address length, size macros, and fixed-width types. Integrated by BCM63xx/BCM963xx platform boot, MTD partitioning, and network MAC provisioning.

## Risks
Do not use `sizeof(struct bcm963xx_nvram)` to decide firmware data length; comments require versioned minimum sizes. Endianness and untrusted flash contents must be handled by callers. Bad checksum should prevent trusting partition/MAC data.

## Test signals
Use known-good v4/v5 NVRAM images, checksum mismatch images, boundary partition indexes, KiB-to-byte conversion checks, and corrupted version values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcm963xx_nvram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcm963xx_tag.h -->
# sources/distributed-fs/ceph-client/include/linux/bcm963xx_tag.h

## Purpose
Defines the Broadcom BCM963xx firmware image tag layout and constants used to parse or generate bootloader-compatible firmware headers.

## Important APIs, types, and functions
- Fixed field length macros describe tag version, signatures, board/chip IDs, image lengths, addresses, sequence, RSA placeholder, vendor info, and CRC fields.
- `BCM963XX_EXTENDED_SIZE` accounts for extended flash addressing that must be subtracted from tag offsets.
- `PIRELLI_BOARDS` names boards with alternate vendor info sizing.
- `struct bcm_tag` is a 256-byte header containing ASCII numeric fields plus several CRC32 fields.

## Control flow and state
Firmware tools or MTD parsers read the tag, validate board/chip identity and CRC fields, then derive kernel/rootfs/CFE locations and lengths. The comments describe the Broadcom bootloader assumption that rootfs starts the image and how OpenWrt-style kernel-first images encode addresses and lengths.

## State and persistence behavior
The tag is persistent on flash and controls bootloader flashing/validation behavior. Most numeric fields are character arrays, so parsing is string-based outside this header.

## Dependencies and integration points
Depends only on kernel types. Integrated by BCM963xx image parsers, MTD splitters, firmware builders, and board-specific update logic.

## Risks
Incorrect lengths or address interpretation can brick firmware upgrades. CRC fields cover different regions and must be computed exactly. Vendor variants such as Pirelli alter interpretation of information fields.

## Test signals
Parse representative firmware tags, validate CRC coverage, test kernel-first/rootfs-first images, extended flash address adjustment, board ID matching, and malformed ASCII length fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcm963xx_tag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcma/bcma.h -->
# sources/distributed-fs/ceph-client/include/linux/bcma/bcma.h

## Purpose
Defines the Broadcom AMBA (BCMA) bus core model: host operations, core/device IDs, bus/device structures, driver registration, MMIO access wrappers, core lookup, host hooks, and core power/IRQ/DMA helpers.

## Important APIs, types, and functions
- `enum bcma_hosttype`, `struct bcma_chipinfo`, `struct bcma_boardinfo`, and `enum bcma_clkmode` describe bus host and clock context.
- `struct bcma_host_ops` abstracts 8/16/32-bit register access, optional block I/O, and agent register access.
- `struct bcma_device` models a discovered core with device identity, MMIO addresses, wrapper address, IRQ, core index/unit, driver data, and list linkage.
- `struct bcma_driver` is the BCMA driver binding object with probe/remove/suspend/resume/shutdown callbacks and `module_bcma_driver()` helper.
- `struct bcma_bus` aggregates host info, chip/board info, core list, mapped core, and embedded driver state for chipcommon, PCI/PCIe2, MIPS, GMAC common, and shared SPROM.
- Inline accessors wrap host ops and read/modify/write helpers.

## Control flow and state
Host code registers a BCMA bus, enumerates cores into `bus->cores`, and binds `bcma_driver` instances through the device model. Drivers call `bcma_read*()`/`bcma_write*()` on their core, use `bcma_find_core()` for companion cores, and manage core enable/disable, clock mode, PLL, DMA translation, and IRQ mapping through exported helpers.

## State and persistence behavior
BCMA state is runtime bus enumeration and MMIO/device state. Shared SPROM reflects persistent board calibration but is cached in the bus object. Core power and clock changes affect hardware state immediately.

## Dependencies and integration points
Depends on PCI, module device tables, BCMA driver-specific headers, SSB SPROM sharing, and common BCMA registers. Integrated by Broadcom wireless, ethernet, PCI host/endpoint, SoC, and platform drivers.

## Risks
Register accessors assume `bus->ops` is valid and mapped to the current core. Read/modify/write helpers are not inherently locked, so shared registers need caller-side serialization. Core IDs and chip IDs are ABI-like constants for driver matching. Host-specific stubs return `-ENOTSUPP` only for PCI host IRQ control on PCI hosts.

## Test signals
Probe on PCI and SoC hosts, enumerate multiple core units, bind/unbind BCMA drivers, exercise register access wrappers, core enable/disable, IRQ mapping, SPROM fallback, and DMA translation for known chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcma/bcma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_arm_c9.h -->
# sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_arm_c9.h

## Purpose
Provides ARM Cortex-A9 BCMA DMU/CRU register offsets and bit masks for USB PLL and strap control.

## Important APIs, types, and functions
- Defines `BCMA_DMU_CRU_USB2_CONTROL` and masks/shifts for USB PLL NDIV/PDIV.
- Defines `BCMA_DMU_CRU_CLKSET_KEY`.
- Defines `BCMA_DMU_CRU_STRAPS_CTRL` bits for USB3 and 4-byte strap behavior.

## Control flow and state
No functions are declared. Platform or BCMA ARM code reads and writes DMU registers using these constants during SoC initialization or USB/strap configuration.

## State and persistence behavior
State is hardware register state. Strap fields may reflect boot-time configuration; writes to clock/PLL controls affect live hardware.

## Dependencies and integration points
Included by `bcma.h`; used by ARM-based Broadcom SoC initialization and USB clock setup.

## Risks
Wrong PLL mask/shift use can misprogram USB clocks. Strap bits may be read-only or boot-sensitive depending on chip, so callers must verify hardware revision.

## Test signals
Boot on supported ARM BCMA SoCs, verify USB2/USB3 enumeration, confirm strap decoding, and test clock setup against datasheet register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_arm_c9.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_chipcommon.h -->
# sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_chipcommon.h

## Purpose
Defines the BCMA ChipCommon and ChipCommon-B register map, capability bits, PMU/PLL constants, flash/NAND/GPIO/watchdog support structures, and access helpers.

## Important APIs, types, and functions
- Large register catalog: chip ID/capabilities, OTP/JTAG/flash/GPIO/watchdog/clock/PMU/SPROM/NAND/serial registers and many chip-specific control bits.
- `struct bcma_chipcommon_pmu` stores PMU core, revision, and crystal frequency.
- Optional flash descriptors: `bcma_pflash`, `bcma_sflash`, and `bcma_nflash`.
- Optional `struct bcma_serial_port` supports MIPS serial setup.
- `struct bcma_drv_cc` tracks chipcommon core, capabilities, setup flags, PMU data, flash data, serial ports, ticks per ms, watchdog platform device, GPIO lock, and optional GPIO chip.
- `struct bcma_drv_cc_b` tracks ChipCommon-B core and MII mapping.
- Register macros wrap core and PMU read/write/mask/set operations.
- Exported functions cover watchdog timer programming, ALP clock, IRQ mask/status, GPIO in/out/outen/control/interrupt/pullup/pulldown, PLL/chipctl/regctl mask-set, spur avoidance, bus clock, and MII writes.

## Control flow and state
ChipCommon setup reads `BCMA_CC_ID`, `BCMA_CC_CAP`, extended capabilities, and PMU data, then initializes clock, flash, GPIO, watchdog, and serial support based on revision and capability bits. Callers use register access macros for direct operations and exported helpers for multi-step PMU/GPIO/watchdog behavior.

## State and persistence behavior
Most state is hardware MMIO state. Flash/SPROM/NAND registers address persistent storage. The driver structure caches capabilities, setup progress, clocks, flash geometry, and platform device state. GPIO register access is protected by `gpio_lock`.

## Dependencies and integration points
Depends on platform devices, Broadcom NAND platform data, GPIO driver framework, and `bcma.h` accessors. Integrated by BCMA SoC boot, MTD, GPIO, watchdog, serial, wireless, and ethernet drivers.

## Risks
Revision-specific register availability is extensive; using a register on the wrong chip revision can hang or misconfigure hardware. GPIO and PMU read/modify/write sequences require locking or helper use. Flash command constants must match vendor protocols. PMU PLL changes can destabilize the system if masks/shifts are wrong.

## Test signals
Test chipcommon setup on multiple chip IDs/revisions, GPIO operations under concurrency, watchdog programming, flash detection, NAND boot detection, PMU clock calculations, PLL update paths, and register dumps against known hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_chipcommon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_gmac_cmn.h -->
# sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_gmac_cmn.h

## Purpose
Defines BCMA GMAC common-core registers for switch tags, parser, PHY access/control, CFP/TCAM, and user-defined fields, plus the driver state used to serialize PHY register access.

## Important APIs, types, and functions
- Register constants cover `BCMA_GMAC_CMN_STAG*`, parser/MIB length, PHY access/control fields, RGMII control, CFP/TCAM data/mask/action/status, and UDF registers.
- `struct bcma_drv_gmac_cmn` stores the core pointer and `phy_mutex`.
- Access macros wrap 16/32-bit BCMA read/write operations.

## Control flow and state
Ethernet drivers use the common core to configure shared GMAC parsing and PHY operations. Access to `BCMA_GMAC_CMN_PHY_ACCESS` and `BCMA_GMAC_CMN_PHY_CTL` must take `phy_mutex` first, preventing concurrent MDIO-like transactions.

## State and persistence behavior
All state is live hardware register state; no persistence is defined here. The mutex is runtime serialization state.

## Dependencies and integration points
Depends on kernel types and BCMA core accessors. Integrated by Broadcom GMAC ethernet drivers sharing PHY and parser hardware.

## Risks
Ignoring `phy_mutex` can interleave PHY transactions. TCAM/UDF register programming is position-sensitive and may affect packet classification globally across ports.

## Test signals
Run concurrent PHY reads/writes, verify RGMII/PHY settings, exercise CFP/TCAM programming, and check packet classification after UDF/parser updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_gmac_cmn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_mips.h -->
# sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_mips.h

## Purpose
Declares BCMA MIPS core register constants and minimal driver state for MIPS 74K/interrupt routing support.

## Important APIs, types, and functions
- `BCMA_MIPS_IPSFLAG` and IRQ masks/shifts describe routing of backplane flags to MIPS interrupt lines.
- MIPS 74K register offsets cover core control, exception base, BIST, interrupt masks, NMI mask, GPIO select/out/en, and clock control/status.
- `BCMA_MIPS_MIPS74K_INTMASK(int)` computes per-interrupt mask register offsets.
- `struct bcma_drv_mips` stores core pointer and setup flags.
- `bcma_cpu_clock()` returns CPU clock for the MIPS core.

## Control flow and state
Platform initialization configures interrupt routing and core setup once, then downstream code queries CPU clock. The setup flags prevent duplicate early/full initialization.

## State and persistence behavior
State is hardware register configuration plus runtime setup flags. Exception-base and interrupt masks affect CPU execution behavior immediately.

## Dependencies and integration points
Included by `bcma.h` and used by BCMA MIPS SoC platform code, interrupt setup, serial clock configuration, and watchdog/timer code.

## Risks
Wrong interrupt mask shifts can route device interrupts to the wrong CPU line. Clock calculation must match PMU/chipcommon state or serial/timer configuration will be wrong.

## Test signals
Boot supported MIPS BCMA SoCs, verify IRQ routing for multiple cores, confirm CPU clock and serial baud accuracy, and check setup idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_mips.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_pci.h -->
# sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_pci.h

## Purpose
Defines BCMA PCI/PCIe core registers, SERDES/MDIO constants, host-mode structures, PCI-core state, register access macros, and optional host-mode callbacks.

## Important APIs, types, and functions
- Register constants cover PCI control/arbiter/interrupt/mailbox/GPIO, backplane-to-PCI translation, config access, MDIO/SERDES, PCIe indirect registers, SPROM, PLP/DLLP diagnostics, and root capability bits.
- `struct bcma_drv_pci_host` exists under host-mode config and owns config-space lock, PCI controller/ops, and IO/memory resources.
- `struct bcma_drv_pci` stores core pointer, setup flags, hostmode flag, and optional host controller.
- Access macros `pcicore_read16/32()` and write variants wrap BCMA core access.
- Optional APIs include `bcma_core_pci_power_save()`, `bcma_core_pci_pcibios_map_irq()`, and `bcma_core_pci_plat_dev_init()`, with disabled stubs.

## Control flow and state
BCMA PCI setup programs translation windows, interrupt masks, SERDES/MDIO, and optionally host-mode PCI controller resources. Endpoint code can power-save the PCI core. Host-mode PCI config access is serialized by `cfgspace_lock`.

## State and persistence behavior
State is live PCI/PCIe core register state plus runtime setup flags. SPROM shadow registers mirror persistent board configuration but writes require explicit enable/control sequences.

## Dependencies and integration points
Depends on kernel PCI types, resources, spinlocks, and BCMA core accessors. Integrated by BCMA PCI host/endpoint support, PCI IRQ mapping, SPROM handling, and wireless/SoC devices behind BCMA.

## Risks
The register map is revision-sensitive. MDIO field shifts differ for old revisions. Translation window mistakes can corrupt bus addressing. Host-mode config accesses must be locked and resource ranges must match SoC address maps.

## Test signals
Test endpoint and host-mode builds, PCI enumeration, config-space access, IRQ mapping, power-save transitions, SERDES link status, SPROM reads, and legacy revision MDIO paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_pcie2.h -->
# sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_pcie2.h

## Purpose
Defines BCMA PCIe Gen2 core registers, interrupt/window/MSI/EQ state, memory/ECC/status registers, private config registers, and simple access macros.

## Important APIs, types, and functions
- Register constants cover clock control, root/endpoint power management, LTR/OBFF, error status, AXI config, MDIO, interrupt lazy/masks/status, MSI and event queues, inbound/outbound address windows, memory ECC, link/reset/strap status, and SPROM.
- `struct bcma_drv_pcie2` stores the core pointer and request size.
- Access and bit helpers wrap `bcma_read/write16/32()`, `bcma_set32()`, and `bcma_mask32()`.

## Control flow and state
PCIe2 setup code configures reset/clock behavior, power states, link/LTR behavior, interrupts/MSI, and inbound/outbound mappings. Runtime code reads link/error/ECC status and manipulates masks or windows through the macros.

## State and persistence behavior
State is live PCIe core hardware state. SPROM window reflects persistent device configuration. `reqsize` is runtime driver state for PCIe request sizing.

## Dependencies and integration points
Included by `bcma.h` and used by BCMA PCIe2 host/endpoint support and drivers that need Gen2-specific register access.

## Risks
Inbound/outbound mapping and MSI/EQ registers are easy to misprogram and can break DMA or interrupts. Reset/clock flags can affect link training and survivability across PERST. LTR settings must match platform power policy.

## Test signals
Validate PCIe link training, config access, DMA windows, MSI delivery, interrupt masks, low-power transitions, ECC/error reporting, and SPROM access on PCIe2 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_pcie2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcma/bcma_regs.h -->
# sources/distributed-fs/ceph-client/include/linux/bcma/bcma_regs.h

## Purpose
Defines common BCMA registers shared across cores, agent reset/control/status bits, PCI config-space registers, and SoC backplane address map constants.

## Important APIs, types, and functions
- `BCMA_CLKCTLST` and clock status/request bits are shared by ChipCommon, PCIe, and 80211 cores.
- Agent registers include OOB select, `BCMA_IOCTL`, `BCMA_IOST`, `BCMA_RESET_CTL`, and `BCMA_RESET_ST`.
- NS ROM boot-device bits describe NOR/NAND/ROM boot source.
- PCI config-space constants cover BAR windows, SPROM control, IRQs, GPIO, and PCIe2 BAR window.
- SoC address constants define SDRAM, PCI memory/config, swapped SDRAM, and region 2 mappings.

## Control flow and state
BCMA core management helpers use these constants to request clocks, force/reset cores, check BIST/status, map BAR windows, and interpret boot devices.

## State and persistence behavior
All fields map hardware registers or fixed SoC physical address regions. Writes alter live core, reset, clock, GPIO, or PCI window state.

## Dependencies and integration points
Included by `bcma.h` and driver-specific BCMA code. Used by core enable/disable, clock mode, PCI host mapping, and SoC boot logic.

## Risks
Some chips invert ALP/HT status bits, and comments call out BCM4328A0 reversal. Reset and IO-control bits are shared primitives and must be sequenced carefully. Address-map constants are platform-specific.

## Test signals
Check core reset/enable flows, clock status polling, PCI BAR window programming, boot-device detection, and chip-specific clock status quirks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcma/bcma_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcma/bcma_soc.h -->
# sources/distributed-fs/ceph-client/include/linux/bcma/bcma_soc.h

## Purpose
Declares the SoC-host wrapper for registering BCMA buses embedded in Broadcom SoCs.

## Important APIs, types, and functions
- `struct bcma_soc` contains an embedded `bcma_bus` and parent `device`.
- `bcma_host_soc_register()` registers an SoC-hosted BCMA bus.
- `bcma_host_soc_init()` initializes SoC-host BCMA state.
- `bcma_bus_register()` registers an already prepared bus.

## Control flow and state
SoC platform code initializes a `bcma_soc`, sets up mappings/device context, calls the SoC init/register helpers, and the common BCMA bus then enumerates cores.

## State and persistence behavior
State is runtime bus/platform state. The embedded `bcma_bus` holds discovered cores and chipcommon/PCI/MIPS/etc. driver state.

## Dependencies and integration points
Depends on `bcma.h`. Integrated by Broadcom SoC platform initialization and shared BCMA bus registration.

## Risks
The wrapper assumes the SoC host has mapped MMIO and device context before registration. Calling common `bcma_bus_register()` too early can expose incomplete core state to drivers.

## Test signals
Boot supported SoC hosts, verify bus enumeration and device binding, test init/register ordering, and validate error cleanup for failed registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bcma/bcma_soc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/binfmts.h -->
# sources/distributed-fs/ceph-client/include/linux/binfmts.h

## Purpose
Defines kernel binary-format loading interfaces, the `linux_binprm` execution context, binfmt handler registration, and exec/coredump helper declarations.

## Important APIs, types, and functions
- `struct linux_binprm` carries argument memory, target mm, file/interpreter/executable, new credentials, exec flags, unsafe mask, personality clearing, argument/environment counts, names, fd path, stack rlimit, and initial binary buffer.
- `struct linux_binfmt` registers `load_binary()` and optional `core_dump()` handlers with module ownership and coredump minimum size.
- Optional `struct binfmt_misc` tracks misc handler entries and enabled state.
- Registration helpers: `register_binfmt()`, `insert_binfmt()`, and `unregister_binfmt()`.
- Exec helpers include `remove_arg_zero()`, `begin_new_exec()`, `setup_new_exec()`, `finalize_exec()`, `would_dump()`, `setup_arg_pages()`, `transfer_args_to_stack()`, `bprm_change_interp()`, `copy_string_kernel()`, `set_binfmt()`, `read_code()`, and `kernel_execve()`.

## Control flow and state
Exec builds a `linux_binprm`, reads the initial bytes into `buf`, walks registered binfmt handlers, and calls a handler's `load_binary()`. Handlers may change interpreter, credentials, stack layout, and point-of-no-return state. Registration order matters: `insert_binfmt()` places a handler before existing handlers.

## State and persistence behavior
State is per-exec transient until `finalize_exec()` commits the new program. Credentials and mm changes become the task's persistent runtime state after successful exec. `point_of_no_return` marks the transition where errors can no longer be reported to the original userspace image.

## Dependencies and integration points
Depends on scheduler, unistd, architecture exec definitions, and UAPI binfmt constants. Integrated by ELF, script, misc, flat, and other binary loaders, LSM hooks, coredump code, and kernel users of `kernel_execve()`.

## Risks
Credential transitions, `secureexec`, nondump flags, and inaccessible path flags are security-sensitive. Binfmt handlers must honor point-of-no-return and avoid leaking file/credential references. Stack setup differs for MMU and NOMMU builds.

## Test signals
Run exec tests for ELF, script interpreters, binfmt_misc, `execveat`, setuid/secureexec, nondump behavior, coredumps, argument limits, NOMMU builds, and handler registration order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/binfmts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bio-integrity.h -->
# sources/distributed-fs/ceph-client/include/linux/bio-integrity.h

## Purpose
Declares block-layer data integrity payload support for bios, including protection information vectors, mapping helpers, cloning, trimming, and filesystem-generated integrity metadata.

## Important APIs, types, and functions
- `enum bip_flags` describes ownership, remapping, disk check suppression, checksum mode, user bounce buffer, guard/ref/app tag checks, and mempool ownership.
- `struct bio_integrity_payload` stores an integrity iterator, vector counts, flags, app tag, and integrity `bio_vec` array.
- `bio_integrity()`, `bio_integrity_flagged()`, `bip_get_seed()`, and `bip_set_seed()` are inline helpers when integrity support is enabled.
- Enabled APIs allocate/init payloads, add pages, map user or metadata iterators, unmap, prepare, advance, trim, and clone.
- Always-declared helpers allocate/free buffers, set up defaults, and generate/verify filesystem integrity metadata.

## Control flow and state
When a bio carries `REQ_INTEGRITY`, `bio_integrity()` returns its payload. Callers allocate/map integrity vectors, prepare them for the requested operation, advance them as data completes, and trim/clone with the parent bio. Filesystem helpers allocate/generate/verify protection metadata around bios.

## State and persistence behavior
Integrity payload state is attached to a bio for one I/O. Protection information may be written to disk or verified on read depending on device format and flags. User mapping may allocate bounce buffers that must be unmapped/freed correctly.

## Dependencies and integration points
Depends on `bio.h` and block integrity configuration. Integrated by block layer, filesystem direct I/O, devices with T10 PI/DIF/DIX-like protection, and metadata verification paths.

## Risks
Config-disabled stubs return `-EINVAL`, NULL, false, or no-op, so callers must handle absence. Seed sector must track remapping and trimming. Mismatched guard/ref/app tag flags can silently skip or over-apply checks.

## Test signals
Build with and without `CONFIG_BLK_DEV_INTEGRITY`; test user metadata mapping, cloning/splitting/trimming, remapped sector seeds, guard/ref/app tag verification, bounce-buffer cleanup, and filesystem generate/verify failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bio-integrity.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bio.h -->
# sources/distributed-fs/ceph-client/include/linux/bio.h

## Purpose
Provides the main block I/O bio helper API: segment iteration, allocation, splitting, chaining, completion, page/vector attachment, iov handling, cgroup association, bio lists, biosets, polling flags, and discard/zone helpers.

## Important APIs, types, and functions
- Iteration helpers include `bio_iter_*`, `bio_for_each_segment`, `bio_for_each_bvec`, all-segment variants, and `bio_for_each_folio_all()`.
- State helpers include `bio_flagged()`, `bio_set_flag()`, `bio_clear_flag()`, `bio_has_data()`, `bio_data()`, `bio_segments()`, `bio_get()`, `bio_cnt_set()`, and `bio_inc_remaining()`.
- Advancement/splitting: `bio_advance_iter()`, `bio_advance()`, `bio_trim()`, `bio_split()`, `bio_split_io_at()`, and `bio_next_split()`.
- Allocation/lifecycle: `bioset_init()`, `bioset_exit()`, `bio_alloc_bioset()`, `bio_alloc()`, `bio_kmalloc()`, `bio_put()`, `bio_init()`, `bio_reset()`, `bio_reuse()`, `bio_chain()`, and `bio_await()`.
- I/O submission and completion: `submit_bio()`, `bio_endio()`, `bio_io_error()`, `bio_wouldblock_error()`, and `submit_bio_wait()`.
- Data attachment/copying: `bio_add_page()`, `bio_add_folio()`, vmalloc helpers, iov page helpers, bounce helpers, copy helpers, dirty/release helpers, zero fill, and end-of-device guard.
- `struct bio_list` and helpers implement singly-linked bio queues.
- `struct bio_set` owns bio/bvec pools, optional per-CPU cache, rescue list/workqueue, and CPU hotplug node.

## Control flow and state
Callers allocate/init a bio, set device/op/sector, attach pages or iterator-backed vectors, optionally associate cgroups, submit it, and later receive completion. Splitting advances or clones iterators so lower layers process only their slice. Chaining uses remaining counters so parent completion waits for child bios. List helpers queue bios in remapping drivers. Biosets provide preallocated pools and rescue work to avoid stacking deadlocks.

## State and persistence behavior
Bio state is transient per I/O. It references pages, folios, block devices, cgroup associations, operation flags, iterator position, status, and completion counters. Data may persist to block devices when the op writes. Page pin/dirty state must be released correctly after completion.

## Dependencies and integration points
Depends on mempool, block types, UIO, request queues, block devices, cgroups, folios, and queue limits. Integrated by filesystems, direct I/O, block drivers, device mapper, md, loop, discard/zone code, and integrity support.

## Risks
Drivers must not use `bio_for_each_segment_all()` or all-bvec variants on bios they do not fully own because bios may have been split. Iterator advancement differs for discard/secure erase/write zeroes. Reference count barriers around `BIO_REFFED` and `BIO_CHAIN` are required. Polled I/O must not block waiting for unavailable resources. `bio_set_dev()` clears throttle/remap flags and re-associates blkcg state, which matters for remappers.

## Test signals
Run block tests covering split/merge, discard/write-zeroes, zone append emulation, chained completions, bio list ordering, cgroup association, page pin release, iov/vmalloc attachment, bounce/unbounce, polled NOWAIT failures, and bioset rescuer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bit_spinlock.h -->
# sources/distributed-fs/ceph-client/include/linux/bit_spinlock.h

## Purpose
Implements compact spin locks backed by individual bits in an unsigned long, for cases where a full `spinlock_t` is too costly or unavailable.

## Important APIs, types, and functions
- `__bitlock(bitnum, addr)` creates a sparse/static-analysis lock token per bit/address pair.
- `bit_spin_lock()` disables preemption and acquires the bit lock.
- `bit_spin_trylock()` tries to acquire and returns success.
- `bit_spin_unlock()` releases with atomic clear semantics.
- `__bit_spin_unlock()` releases with non-atomic clear semantics for cases where the bit lock protects the rest of the word.
- `bit_spin_is_locked()` reports lock state with SMP/debug/preempt-count fallbacks.

## Control flow and state
Lock acquisition disables preemption, uses `test_and_set_bit_lock()` on SMP/debug builds, and busy-waits with a non-atomic `test_bit()` plus `cpu_relax()` to reduce bus traffic before retrying. Unlock clears the bit and re-enables preemption.

## State and persistence behavior
The lock state is one bit in caller-owned memory. No persistent state exists beyond that word. Preemption state is part of the lock contract and must be restored by unlock.

## Dependencies and integration points
Depends on preemption, atomic bit operations, bug checks, processor relax, sparse lock annotations, and debug spinlock config. Used by memory-management and low-level structures needing embedded bit locks.

## Risks
This is slower than normal spinlocks and should be used only when necessary. Non-atomic unlock is only safe when the lock bit protects the word being modified. Missing unlock leaves preemption disabled. Lock ordering is less visible than named spinlocks.

## Test signals
Use lockdep/sparse annotations, SMP contention tests, trylock failure paths, debug spinlock BUG checks, preempt-count balance checks, and non-atomic unlock users that modify protected flag words.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bit_spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bitfield.h -->
# sources/distributed-fs/ceph-client/include/linux/bitfield.h

## Purpose
Provides type-safe bitfield extraction, preparation, replacement, and endian-aware helpers for shifted contiguous masks in registers and protocol fields.

## Important APIs, types, and functions
- `FIELD_MAX()`, `FIELD_FIT()`, `FIELD_PREP()`, `FIELD_PREP_CONST()`, `FIELD_GET()`, and `FIELD_MODIFY()` operate on compile-time constant masks with build-time validation.
- Internal checks validate nonzero masks, contiguous masks, value fit, and register type width.
- `field_multiplier()`, `field_mask()`, `field_max()`, and generated `u8/u16/u32/u64`, `le16/le32/le64`, and `be16/be32/be64` helpers support runtime field masks and endian conversions.
- `field_prep()` and `field_get()` allow non-constant masks while using checked constant paths when possible.

## Control flow and state
The macros compute the shift from the low set bit, validate mask shape and width, then mask/shift values into or out of registers. Endian helpers convert to/from CPU order around the same mask arithmetic. Compile-time errors are intentionally produced for invalid constant use.

## State and persistence behavior
No runtime state. The macros transform caller-owned register or protocol values. `FIELD_MODIFY()` mutates the pointed-to value in place.

## Dependencies and integration points
Depends on build bug helpers, compiler support, type checking, and byteorder conversion APIs. Heavily integrated with register definition headers, device drivers, networking, storage, and firmware parsing.

## Risks
Masks must be shifted and contiguous. Passing too-small register types or values that do not fit triggers compile errors for constants; runtime masks have less checking. Side effects in macro arguments should be avoided despite local temporaries in some helpers.

## Test signals
Compile-time negative tests for zero/non-contiguous masks, value overflow, and type width. Runtime tests for field prep/get/replace across u8/u16/u32/u64 and little/big endian fields, including non-constant masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bitfield.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bitmap-str.h -->
# sources/distributed-fs/ceph-client/include/linux/bitmap-str.h

## Purpose
Declares bitmap string parsing and formatting helpers for kernel and userspace buffers, supporting both hexadecimal bitmask and list forms.

## Important APIs, types, and functions
- `bitmap_parse_user()` parses a user buffer into a bitmap.
- `bitmap_print_to_pagebuf()` formats into a page buffer in list or mask mode.
- `bitmap_print_bitmask_to_buf()` and `bitmap_print_list_to_buf()` support offset/count streaming for sysfs/procfs-style reads.
- `bitmap_parse()` parses kernel memory buffers.
- `bitmap_parselist()` and `bitmap_parselist_user()` parse list syntax from kernel or user buffers.

## Control flow and state
Callers provide destination bitmaps and bit counts for parsing or source bitmaps and output buffers for printing. User-buffer functions handle `__user` pointers and lengths; streaming print helpers honor `loff_t off` and `count`.

## State and persistence behavior
No internal state. Parsed bitmaps become caller-owned runtime state, often cpumasks, nodemasks, or device resource masks exposed through sysfs/procfs.

## Dependencies and integration points
Depends on kernel types and user pointer annotations. Integrated by sysfs/procfs attributes, CPU/node masks, device affinity, and kernel parameter parsing.

## Risks
Callers must pass the correct `nbits`/`nmaskbits` to avoid accepting out-of-range bits or truncating output. User-buffer parsers can fail on invalid syntax or access errors. Streaming output must correctly handle offsets to avoid duplicate or missing text.

## Test signals
Test mask and list parsing, user and kernel buffers, invalid ranges, high bits beyond `nbits`, empty input, large masks, page-buffer output, and offset/count streaming reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bitmap-str.h -->
