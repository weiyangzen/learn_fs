# Research Report: subset-b-004046

Scope: source-tree-aligned research for the RAID5 stripe header and the Linux media CEC core, build selection, and selected CEC I2C/platform drivers under `sources/distributed-fs/ceph-client`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/raid5.h -->
# sources/distributed-fs/ceph-client/drivers/md/raid5.h

Purpose: This header defines the core in-memory model for the md RAID4/5/6 personality: stripe heads, per-device stripe buffers, stripe-cache configuration, parity/check/reconstruction states, algorithm constants, and exported helpers used by the implementation files. It is not a standalone algorithm implementation, but it is the contract that the RAID5 engine, async parity operations, reshape handling, write journal/PPL integration, and cache sizing all share.

Important APIs, types, and functions: `struct stripe_head` is the central stripe object, keyed by `sector`, hash node, LRU/release lists, refcount, parity indices, generation, per-stripe locks, batching fields, journal/PPL fields, operation state, and flexible `dev[]` array of `struct r5dev`. `struct r5dev` tracks the bio pair for original/replacement devices, page/orig_page, request lists (`toread`, `read`, `towrite`, `written`), per-block sector, flags, checksums, and write hints. `struct stripe_head_state` is a transient aggregation used by `handle_stripe()` to count locked/uptodate/read/write/failed/compute state and to record blocked devices and log failures. `enum r5dev_flags`, stripe state bits, operation request bits, `enum check_states`, and `enum reconstruct_states` encode the legal transitions described in the file comments. `struct r5conf` holds array geometry, reshape state, queues, stripe hash/inactive pools, journal/cache state, worker groups, per-cpu scratch space, bio pending lists, and md integration pointers. Inline helpers validate RAID5/RAID6 layouts, detect DDF layouts, walk non-overlapping bio chains with `r5_next_bio()`, and, for non-default page/stripe sizes, compute backing pages and offsets. External declarations include `raid5_set_cache_size()`, `raid5_compute_blocknr()`, `raid5_release_stripe()`, `raid5_compute_sector()`, `raid5_get_active_stripe()`, `raid5_calc_degraded()`, and `r5c_journal_mode_set()`.

Control flow and state: The leading comments are the behavioral specification. A stripe buffer moves through Empty, Want, Dirty, and Clean states using `R5_UPTODATE` and `R5_LOCKED`, with interrupt-time completions allowed for read/write transitions. Stripe heads move among hash buckets, inactive lists, handle lists, delayed/hold/bitmap/log lists, and release lists depending on `atomic_t count`, `STRIPE_HANDLE`, preread state, and cache pressure. `handle_stripe()`-side code sets operation-request bits, then `raid5_run_ops` performs async-copy/xor/syndrome/check/reconstruct work while honoring dependencies such as parity checks clobbering parity cache contents and compute-block results being consumed by later operations. Reshape state is tracked through `reshape_progress`, `reshape_safe`, previous geometry fields, generation counters, and flags such as `STRIPE_EXPANDING`, `STRIPE_EXPAND_SOURCE`, and `STRIPE_EXPAND_READY`.

State and persistence behavior: This file defines only volatile kernel state, but it mirrors persistent array facts held by md metadata: RAID level, layout algorithm, chunk size, disk count, reshape progress, bad-block status, bitmap sequence numbers, and journal/PPL state. Stripe cache contents are transient; journal-related fields (`log`, `log_private`, `r5c_*` lists, `R5_InJournal`, `STRIPE_LOG_TRAPPED`, `r5c_journal_mode`) coordinate with persistent or semi-persistent write-back/write-through logging handled elsewhere.

Dependencies and integration points: The header depends on Linux bio/page/list/hash/spinlock/atomic/waitqueue/mempool/shrinker/percpu infrastructure, md `struct mddev`/`struct md_rdev`, async_tx/xor/dmaengine parity helpers, RAID5 journal/PPL structures, and block-layer bio semantics. It integrates with md personality code, sysfs cache tuning, reshape/recovery machinery, bitmap flushing, replacement-device handling, and optional DMA offload.

Risks and edge cases: The highest-risk areas are lock ordering across hash locks, `device_lock`, per-stripe locks, and RCU-protected `disk_info.rdev`; interrupt-time flag transitions; reshape generation races; replacement vs original device I/O; non-4K page/stripe mapping; journal/cache pressure states; and layout compatibility between md and DDF RAID6. The `R5_OrigPageUPTDODATE` spelling is preserved from source and should be treated as ABI-internal flag naming rather than corrected casually.

Test signals: Meaningful tests are md RAID5/6 stress runs with concurrent reads/writes, degraded and double-degraded recovery, reshape grow/shrink, replacement devices, bad blocks, journal write-back/write-through mode changes, discard, FUA/write-hint propagation, cache-size changes, and layout validation for all algorithm constants. Runtime signals include md debug/status output, lockdep, KASAN/KCSAN, parity-check mismatch counters, reshape progress stability, and absence of stuck stripes or leaked active stripe refs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/raid5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/Kconfig

Purpose: This top-level media Kconfig file defines the user-visible multimedia subsystem menu and sources the subordinate Kconfig trees for remote controllers, CEC, V4L2, DVB, media controller, platform drivers, test drivers, and ancillary drivers. It explicitly keeps CEC and remote-controller support outside the `MEDIA_SUPPORT` dependency so those subsystems can be enabled independently.

Important APIs, types, and functions: Kconfig symbols include `MEDIA_SUPPORT`, `MEDIA_SUPPORT_FILTER`, `MEDIA_SUBDRV_AUTOSELECT`, media device-type selectors (`MEDIA_CAMERA_SUPPORT`, `MEDIA_ANALOG_TV_SUPPORT`, `MEDIA_DIGITAL_TV_SUPPORT`, `MEDIA_RADIO_SUPPORT`, `MEDIA_SDR_SUPPORT`, `MEDIA_PLATFORM_SUPPORT`, `MEDIA_TEST_SUPPORT`), core API selectors (`VIDEO_DEV`, `MEDIA_CONTROLLER`, `DVB_CORE`), `MEDIA_HIDE_ANCILLARY_SUBDRV`, and `MEDIA_ATTACH`.

Control flow and state: Kconfig flow starts by sourcing RC and CEC support unconditionally, then presents `menuconfig MEDIA_SUPPORT`. When enabled, filter and device-type choices set defaults for V4L2/DVB/media-controller core symbols, which then source their option submenus. Driver menus conditionally source USB/PCI/radio/platform/mmc/test/firewire/common and ancillary I2C/SPI/tuner/frontend trees. `MEDIA_SUPPORT_FILTER` controls whether users see a focused set of driver classes or all core functionality.

State and persistence behavior: Build selections are persisted in kernel `.config`; there is no runtime state. Defaults depend on whether the user selected filtering, expert mode, module support, and digital-TV/media-platform/test support.

Dependencies and integration points: The file integrates the media subsystem with `HAS_IOMEM`, `I2C`, `I2C_MUX`, `MODULES`, `CRC32`, V4L2, DVB, media controller, RC, and CEC Kconfig namespaces. Its sourcing order is important because it exposes CEC/RC even without `MEDIA_SUPPORT` and allows ancillary drivers to be hidden unless selected automatically.

Risks and edge cases: Mis-gating can hide required drivers or silently disable hardware functionality on embedded systems. `MEDIA_SUBDRV_AUTOSELECT` is convenient but can pull in broad ancillary dependencies; disabling it can create kernels that build but lack required tuners/sensors/frontends. CEC/RC independence means users may see those options even when the rest of media is off.

Test signals: Kernel config tests should verify expected visibility/defaults for expert and non-expert configs, allnoconfig/allyesconfig/modular builds, `MEDIA_SUPPORT=n` with CEC or RC enabled, and platform-only embedded configurations with autoselect disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/Makefile

Purpose: This Makefile orders and gates compilation of the media driver subtree. It ensures foundational subtrees such as I2C/tuners, media controller, V4L2, DVB, RC, and CEC are linked before dependent drivers.

Important APIs, types, and functions: Build variables include unconditional `obj-y += i2c/ tuners/`, `obj-$(CONFIG_DVB_CORE) += dvb-frontends/`, conditional `mc/`, `v4l2-core/`, `dvb-core/`, unconditional `rc/`, `obj-$(CONFIG_CEC_CORE) += cec/`, and final driver directory aggregation for `common/ platform/ pci/ usb/ mmc/ firewire/ spi/ test-drivers/` plus `radio/` under `CONFIG_VIDEO_DEV`.

Control flow and state: Kbuild descends into core/ancillary directories first so built-in drivers that depend on I2C subdrivers or core APIs can resolve symbols. `CONFIG_MEDIA_CONTROLLER=y` is special-cased so the media controller core is only linked into `MEDIA_SUPPORT` when built in.

State and persistence behavior: There is no runtime state. The file transforms `.config` symbols into object-directory traversal.

Dependencies and integration points: It integrates Kconfig symbols with Kbuild and relies on each child directory to gate individual drivers. It also reflects a link-order dependency: I2C drivers before other drivers, RC core before RC drivers, and CEC subtree when `CEC_CORE` is selected.

Risks and edge cases: Reordering can break built-in link dependencies or cause drivers to initialize before the core they require. Adding a new CEC or media subtree in the wrong position can create unresolved symbols in non-modular builds that would not appear in module-only testing.

Test signals: Build coverage should include built-in and modular media configs, `CONFIG_CEC_CORE=y/m`, `CONFIG_VIDEO_DEV=n`, `CONFIG_DVB_CORE=y/m`, and `CONFIG_MEDIA_CONTROLLER=y` to catch ordering and link failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/cec/Kconfig

Purpose: This file defines the CEC core feature symbols and the user-visible HDMI CEC driver menu. It separates internal core objects (`CEC_CORE`, `CEC_NOTIFIER`, `CEC_PIN`) from optional RC integration, pin error injection, and the driver families sourced beneath I2C/platform/USB.

Important APIs, types, and functions: Symbols include tristate `CEC_CORE`, bool `CEC_NOTIFIER`, bool `CEC_PIN`, `MEDIA_CEC_RC`, `CEC_PIN_ERROR_INJ`, and menuconfig `MEDIA_CEC_SUPPORT`. `MEDIA_CEC_RC` depends on `CEC_CORE` and `RC_CORE` with module/builtin compatibility; `CEC_PIN_ERROR_INJ` depends on `CEC_PIN` and `DEBUG_FS`.

Control flow and state: When `MEDIA_CEC_SUPPORT` is enabled, this file sources the CEC I2C, platform, and USB driver menus. Drivers select `CEC_CORE` and any helper features they require. Pin error injection is only available for pin-backed adapters and debugfs-enabled kernels.

State and persistence behavior: Only `.config` state is affected. Runtime behavior is delegated to the core and drivers selected here.

Dependencies and integration points: Integrates with RC core for CEC remote-control passthrough, debugfs for pin error injection, and subordinate CEC driver trees. The core symbol is tristate so CEC can be a module while helper flags are boolean feature inclusions.

Risks and edge cases: Incorrect `depends on CEC_CORE=m || RC_CORE=y`-style module compatibility can produce invalid link combinations. Because `CEC_NOTIFIER` and `CEC_PIN` are bool helpers selected by drivers, new drivers must select them explicitly when they call notifier or pin APIs.

Test signals: Kconfig tests should cover CEC core as built-in/module, RC integration with RC built-in vs module, debugfs on/off, and driver menus hidden when `MEDIA_CEC_SUPPORT=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/cec/Makefile

Purpose: This Kbuild file descends into all CEC subtrees: core, I2C, platform, and USB.

Important APIs, types, and functions: It uses `obj-y += core/ i2c/ platform/ usb/`, leaving each subtree to decide which objects are actually built based on configuration.

Control flow and state: The CEC subtree is entered from `drivers/media/Makefile` when `CONFIG_CEC_CORE` is enabled. Within this directory, all child Makefiles are parsed so drivers can be built when their config symbols are set.

State and persistence behavior: No runtime state; object traversal only.

Dependencies and integration points: Integrates top-level media Kbuild with CEC-specific core and driver directories.

Risks and edge cases: New CEC driver families must be added here or they will never be reached by Kbuild. Since all child directories are unconditional from this file, child Makefiles must correctly guard their objects.

Test signals: Build with selected CEC I2C, platform, and USB drivers to confirm the relevant child directories are reached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/core/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/cec/core/Makefile

Purpose: This Makefile composes the `cec.o` core module/object from the mandatory CEC core sources and optional notifier, pin, and pin error-injection implementation files.

Important APIs, types, and functions: `cec-objs := cec-core.o cec-adap.o cec-api.o` is the mandatory object set. Conditional additions are `cec-notifier.o` for `CONFIG_CEC_NOTIFIER`, `cec-pin.o` for `CONFIG_CEC_PIN`, and `cec-pin-error-inj.o` for `CONFIG_CEC_PIN_ERROR_INJ`. `obj-$(CONFIG_CEC_CORE) += cec.o` gates the composite object.

Control flow and state: Kbuild links optional helpers into the same CEC core object when selected, ensuring exported symbols and internal helpers are available to drivers in one module/built-in unit.

State and persistence behavior: Build-only state. Runtime state is defined in the source files.

Dependencies and integration points: Depends on the symbols selected by CEC drivers in Kconfig. The optional source files use internal headers and are not independent modules.

Risks and edge cases: A driver selecting `CEC_PIN` without `CEC_CORE` would be invalid, but current Kconfig selects the core. Enabling error injection without pin support is blocked by Kconfig; bypassing that would create missing symbols.

Test signals: Build matrix for `CEC_CORE=y/m`, with notifier-only, pin-only, and pin plus error-injection configurations, should catch missing object composition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/core/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-adap.c -->
# sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-adap.c

Purpose: This is the central HDMI CEC adapter implementation. It manages adapter state, filehandle message/event queues, transmit queueing and completion, reply matching, logical-address claiming, physical-address changes, monitor modes, CEC protocol auto-replies, and debug status.

Important APIs, types, and functions: Exported helpers include `cec_get_edid_phys_addr()`, `cec_fill_conn_info_from_drm()`, `cec_queue_pin_cec_event()`, `cec_queue_pin_hpd_event()`, `cec_queue_pin_5v_event()`, `cec_transmit_done_ts()`, `cec_transmit_attempt_done_ts()`, `cec_transmit_msg()`, `cec_received_msg_ts()`, `cec_s_phys_addr()`, `cec_s_phys_addr_from_edid()`, `cec_s_conn_info()`, and `cec_s_log_addrs()`. Internal key functions include `cec_thread_func()`, `cec_transmit_msg_fh()`, `cec_wait_timeout()`, `cec_config_thread_func()`, `cec_claim_log_addrs()`, `cec_adap_enable()`, `__cec_s_phys_addr()`, `__cec_s_log_addrs()`, `cec_receive_notify()`, and monitor count helpers. It relies heavily on `struct cec_adapter`, `struct cec_data`, `struct cec_fh`, `struct cec_msg`, and `struct cec_event`.

Control flow and state: Transmits enter through ioctl or driver calls, are validated, assigned a sequence, wrapped in `cec_data`, placed on `adap->transmit_queue`, and consumed by `cec_thread_func()`. The thread computes CEC signal-free timing, calls the driver `adap_transmit` op, and waits for `cec_transmit_done_ts()` or timeout. Completion updates counters/status, retries if appropriate, queues monitor copies, and either schedules reply timeout work or completes the blocking/nonblocking request. Received messages are normalized in `cec_received_msg_ts()`, filtered for self-reception and spec length/addressing, matched against `wait_queue` replies, queued to monitor filehandles, and passed to `cec_receive_notify()` for core protocol handling and follower delivery. Logical-address configuration runs in `cec_config_thread_func()`, polling candidate logical addresses, handling reconfiguration, setting driver addresses, broadcasting Report Features/Physical Address/Vendor ID, and posting state events.

State and persistence behavior: Adapter state is volatile and protected mostly by `adap->lock`: physical address, logical address set, configuration flags, monitor counts, exclusive initiator/follower pointers, transmit queues, wait queues, sequence counters, diagnostics, and connector info. Persistent facts such as EDID physical address and logical-address preferences are supplied by drivers or userspace and are not stored by this file. Queued user events/messages live per open filehandle and are bounded; overflow sets lost/dropped indicators.

Dependencies and integration points: It integrates with driver ops from `struct cec_adap_ops`, DRM EDID/connector helpers, CEC notifier users, debugfs status, optional RC core for user-control key events, kthreads, delayed work, waitqueues, capabilities checks (`CAP_SYS_RAWIO`, `CAP_NET_ADMIN`), and userspace ioctls via `cec-api.c`. Drivers must call transmit/receive completion APIs exactly once for each hardware transaction and must honor `adap_enable`, `adap_log_addr`, and monitor ops.

Risks and edge cases: High-risk areas include races among blocking transmit cancellation, delayed reply timeout, filehandle release, adapter unregistration, HPD-driven unconfiguration, and driver completion callbacks. Protocol risks include malformed CEC lengths, broadcast/directed restrictions, self-addressed transmits, unregistered fallback, CEC 1.4 vs 2.0 behavior, and vendor-command reply matching. Queue bounds protect memory but can drop messages/events, so lost-event signaling is important.

Test signals: Use `cec-ctl`/`cec-compliance` to exercise transmit/reply, nonblocking receive, monitor all/pin modes, exclusive follower/initiator arbitration, physical/logical address changes, HPD disconnects, CEC 1.4/2.0 logical-address rules, passthrough mode, RC passthrough, queue overflow, and driver timeout handling. Debugfs `status` should show queue state, timeout/error counters, and driver-specific status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-adap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-api.c -->
# sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-api.c

Purpose: This file implements the CEC character-device userspace API: open/release, poll, and ioctl handling for adapter capabilities, physical/logical addresses, connector info, transmit/receive, event dequeue, and filehandle mode selection.

Important APIs, types, and functions: The exported `cec_devnode_fops` provides `.open`, `.unlocked_ioctl`, `.compat_ioctl`, `.release`, and `.poll`. Key internal functions are `cec_poll()`, `cec_is_busy()`, `cec_adap_g_caps()`, `cec_adap_g_phys_addr()`, `cec_validate_phys_addr()`, `cec_adap_s_phys_addr()`, `cec_adap_g_log_addrs()`, `cec_adap_s_log_addrs()`, `cec_adap_g_connector_info()`, `cec_transmit()`, `cec_receive_msg()`, `cec_receive()`, `cec_dqevent()`, `cec_g_mode()`, `cec_s_mode()`, `cec_ioctl()`, `cec_open()`, and `cec_release()`.

Control flow and state: `cec_open()` allocates a `struct cec_fh`, initializes message/event queues and waitqueue, acquires the adapter device reference, queues initial state and optional HPD/5V events, then links the filehandle into `devnode.fhs`. `cec_ioctl()` checks registration and dispatches commands. Setters validate capabilities and busy/exclusive state before calling core helpers. Transmit copies a user `struct cec_msg`, invokes `cec_transmit_msg_fh()`, and copies completion state back. Receive and event dequeue block or return `-EAGAIN` based on file flags and user timeouts. `cec_release()` clears exclusive ownership, monitor counts, follower count, pending transmit filehandle links, queued messages/events, and adapter references.

State and persistence behavior: Filehandle state is per open descriptor: mode bits, queued received messages, queued events, pending transfer links, and waitqueue. Adapter global state is changed only through locked helper calls. Nothing persists beyond the file descriptor or adapter lifetime.

Dependencies and integration points: Depends on the internal adapter API in `cec-priv.h`, public CEC uAPI structs/ioctls, optional pin APIs for initial HPD/5V reads, waitqueues, mutexes, copy_to/from_user, capabilities, and poll semantics. It is the only file attached directly to the char-device fops created by `cec-core.c`.

Risks and edge cases: Risks include user/kernel copy failures, leaking padding from `struct cec_log_addrs` (explicitly avoided with `memcpy`), invalid physical addresses, invalid mode combinations, monitor modes without privileges, exclusive initiator/follower conflicts, file release while blocking transmit is pending, and event/message queue lifetime cleanup.

Test signals: Validate all ioctls with good/bad user pointers, blocking and nonblocking receive/transmit, poll readiness transitions, invalid mode combinations, CAP checks for raw/monitor modes, initial events on open, release cleanup while a transmit waits for a reply, and unregistration returning `ENODEV`/poll hangup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-core.c

Purpose: This file owns CEC device-node registration, adapter allocation/registration/unregistration/deletion, module parameters, debugfs setup, bus/chrdev initialization, and optional RC input-device allocation.

Important APIs, types, and functions: Exported APIs are `cec_allocate_adapter()`, `cec_register_adapter()`, `cec_unregister_adapter()`, and `cec_delete_adapter()`. Internal functions include `cec_devnode_register()`, `cec_devnode_unregister()`, `cec_devnode_release()`, debugfs `cec_error_inj_*` handlers, and module init/exit `cec_devnode_init()`/`cec_devnode_exit()`. Global state includes `cec_debug`, `debug_phys_addr`, `cec_dev_t`, `cec_devnode_nums`, `cec_devnode_lock`, `cec_bus_type`, and `top_cec_dir`.

Control flow and state: Allocation validates caps/ops/available LAs, initializes adapter fields and queues, starts the main adapter kthread, and optionally creates an RC device. Registration attaches the adapter to a parent device, sets transfer timeout, registers RC if present, allocates a minor, initializes cdev/device state, creates debugfs entries, and stores adapter drvdata. Unregistration removes RC, debugfs, notifier connection, invalidates addresses/logical addresses, disables the adapter, removes the cdev/device, and drops the final device reference. Device release frees the minor and calls `cec_delete_adapter()`, which stops config/main kthreads, invokes driver `adap_free`, frees RC leftovers, and releases memory.

State and persistence behavior: Device minor allocation is process-global and protected by `cec_devnode_lock`. Adapter state is volatile and lifetime-managed by char-device references. Debugfs exposes status and optional error injection but does not persist settings across adapter teardown.

Dependencies and integration points: Integrates with Linux char devices, device model, bus registration, debugfs, kthreads, optional RC core, CEC notifier, and `cec_devnode_fops` from `cec-api.c`. Driver authors use this file’s exported allocation/register/unregister/delete lifecycle.

Risks and edge cases: Lifecycle ordering is critical: after successful `cec_register_adapter()`, drivers should call `cec_unregister_adapter()` rather than direct delete. Minor exhaustion, failure paths around RC registration/cdev registration, open filehandles during unregister, config kthread shutdown, and debugfs error-injection parsing are important risk areas. `debug_phys_addr` can expose physical-address capability for debug and changes userspace behavior.

Test signals: Exercise adapter probe/remove failure paths, repeated register/unregister, open fd during remove, RC integration enabled/disabled, debugfs status/error-injection availability, minor reuse across 256-device boundary tests, and module unload with active adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-notifier.c -->
# sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-notifier.c

Purpose: This file implements the CEC notifier bridge between HDMI/DRM devices that know connector physical addresses and CEC adapters that need those addresses and connector metadata.

Important APIs, types, and functions: `struct cec_notifier` stores lock, list node, kref, HDMI device key, connector info, port name, attached CEC adapter, and physical address. Exported APIs are `cec_notifier_conn_register()`, `cec_notifier_conn_unregister()`, `cec_notifier_cec_adap_register()`, `cec_notifier_cec_adap_unregister()`, `cec_notifier_set_phys_addr()`, `cec_notifier_set_phys_addr_from_edid()`, and `cec_notifier_parse_hdmi_phandle()`. Internal helpers are `cec_notifier_get_conn()`, `cec_notifier_release()`, and `cec_notifier_put()`.

Control flow and state: Connector providers and CEC adapters independently obtain a notifier keyed by `(hdmi_dev, port_name)`. Registration bumps a kref or creates a new object under the global notifier list lock. Connector registration stores connector info and invalidates/updates attached adapters. Adapter registration stores the adapter pointer, copies connector info into it, and pushes the current physical address unless the adapter controls its own physical address. Unregister clears the corresponding side and drops references. EDID helpers parse the source physical address before updating.

State and persistence behavior: Notifier state is volatile, reference-counted, and global within the kernel. It persists only while either connector or CEC adapter holds a reference. Physical address starts invalid and changes as HDMI/EDID state changes.

Dependencies and integration points: Depends on the Linux device model, kref/list/mutex primitives, platform and I2C OF lookup, DRM EDID helpers, public CEC notifier APIs, and adapter functions `cec_s_phys_addr()`/`cec_s_conn_info()`. Platform drivers use `cec_notifier_parse_hdmi_phandle()` for device-tree `hdmi-phandle` integration.

Risks and edge cases: Keying by raw `struct device *` plus optional port name requires providers and consumers to use exactly matching objects/names. The phandle helper drops the device reference because the device is used only as a key; misuse elsewhere would be unsafe. Probe deferral is expected when the HDMI device is not registered. Race protection uses both global and per-notifier locks; all adapter update paths must avoid lifetime cycles.

Test signals: Test adapter-before-connector and connector-before-adapter ordering, EDID physical-address changes, connector unregister invalidation, multi-port matching by port name, DT phandle probe deferral, I2C HDMI device lookup, and adapter-controlled physical-address drivers such as CH7322.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-notifier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-pin-error-inj.c -->
# sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-pin-error-inj.c

Purpose: This file implements debugfs command parsing and reporting for CEC pin-level error injection, allowing tests to force malformed receive/transmit behavior such as NACKs, low-drive, arbitration loss, bad timings, custom pulses, and byte insertion/removal.

Important APIs, types, and functions: `struct cec_error_inj_cmd` maps command text to bit offsets and argument slots. Exported/internal-to-core functions are `cec_pin_rx_error_inj()`, `cec_pin_tx_error_inj()`, `cec_pin_error_inj_parse_line()`, and `cec_pin_error_inj_show()`. It operates on `struct cec_pin` fields `error_inj`, `error_inj_args`, `rx_toggle`, `tx_toggle`, `rx_no_low_drive`, `tx_ignore_nack_until_eom`, custom pulse/glitch timing, and glitch flags.

Control flow and state: The debugfs write handler in `cec-core.c` feeds lines here. Global commands clear RX/TX state or set custom/glitch options. Opcode-scoped commands parse an opcode or `any`, optional mode (`off`, `once`, `always`, `toggle`), command name, and optional position/argument. The parser validates bit positions and command-specific constraints, updates the packed error-injection mask, and stores arguments. `cec_pin_rx_error_inj()`/`cec_pin_tx_error_inj()` choose opcode-specific settings when available, otherwise fallback to `any`. The show function prints command help and current non-default settings.

State and persistence behavior: Error injection state is per pin adapter, volatile, and debugfs-controlled. `once` modes clear themselves in `cec-pin.c` after firing; `toggle` depends on tx/rx toggle bits flipped when the pin state machine returns to idle.

Dependencies and integration points: Depends on `cec-pin-priv.h`, debugfs seq output, kstrto parsing helpers, and the pin state machine consuming offsets/arguments. It is compiled only when `CONFIG_CEC_PIN_ERROR_INJ` is enabled.

Risks and edge cases: Parser bugs can make tests inject unintended line states. Position validation must avoid ACK-bit misuse for certain TX timing errors and must distinguish opcode-specific vs any-opcode arbitration loss. There is a likely typo in the source path for `tx-custom-high-usecs`: it assigns `tx_glitch_high_usecs` instead of `tx_custom_high_usecs`, which should be reviewed against upstream intent before changing. Long custom pulses are bounded to 10,000,000 usec; glitch pulses to 100 usec.

Test signals: Write/read debugfs `error-inj`, verify clear/rx-clear/tx-clear, opcode-specific and any-opcode matching, once/always/toggle modes, invalid syntax rejection, CEC compliance tests for low-drive/arbitration/NACK/timing errors, and status behavior after pin state-machine consumption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-pin-error-inj.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-pin-priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-pin-priv.h

Purpose: This internal header defines the software bit-banged CEC pin engine’s state enum, error-injection bit layout, event queue constants, `struct cec_pin`, and internal pin helper prototypes.

Important APIs, types, and functions: `call_pin_op()`/`call_void_pin_op()` safely invoke `struct cec_pin_ops` callbacks if the adapter is registered. `enum cec_pin_state` enumerates Off/Idle, TX wait/start/data/custom/low-drive states, RX start/data/ack/low-drive states, and IRQ-monitor state. Error-injection defines pack RX and TX modes in a 64-bit per-op mask plus argument indices. `struct cec_pin` carries adapter/ops/kthread/timer state, logical-address mask, monitor flags, TX/RX bit/message state, event ring buffers, overrun/error counters, custom pulse/glitch settings, and optional `error_inj` arrays. Prototypes expose `cec_pin_start_timer()` and error-injection helpers.

Control flow and state: The enum is consumed by `cec-pin.c`’s timer and kthread. The event ring (`CEC_NUM_PIN_EVENTS`) decouples hrtimer/IRQ pin updates from userspace event queueing. `work_irq_change` requests IRQ enable/disable transitions between hrtimer polling and interrupt mode.

State and persistence behavior: All fields are per-adapter volatile state. The structure tracks transient bus timing, queued work, diagnostics counters, and debug injection settings; nothing is persisted outside the adapter lifetime.

Dependencies and integration points: Depends on public `<media/cec-pin.h>`, Linux atomic/types, and the core adapter registration model. Platform drivers such as `cec-gpio` supply the low/high/read/IRQ/status ops that this structure wraps.

Risks and edge cases: The state enum and timing code must remain in sync with `states[]` in `cec-pin.c`; adding states without updating timing/status can break the hrtimer engine. The event ring is bounded and drops events with a flag, so monitor-pin users must handle loss. Error-injection bit offsets are ABI-like for debugfs parser/show and pin consumption.

Test signals: Compile with and without `CONFIG_CEC_PIN_ERROR_INJ`, run pin-backed adapter RX/TX, monitor-pin event overflow, IRQ-mode transitions, and debugfs status to ensure every state/counter remains coherent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-pin-priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-pin.c -->
# sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-pin.c

Purpose: This file implements a software CEC transceiver over generic pin operations. It bit-bangs CEC timing with an hrtimer, decodes received frames, generates transmitted frames, handles arbitration/ACK/low-drive behavior, queues pin-monitor events, and exposes `cec_pin_allocate_adapter()` for GPIO-like drivers.

Important APIs, types, and functions: Exported functions are `cec_pin_changed()` and `cec_pin_allocate_adapter()`. Important internal functions include `cec_pin_update()`, `cec_pin_read()`, `cec_pin_low()`, `cec_pin_high()`, error-injection helpers, `cec_pin_to_idle()`, `cec_pin_tx_states()`, `cec_pin_rx_states()`, `cec_pin_timer()`, `cec_pin_thread_func()`, `cec_pin_adap_enable()`, `cec_pin_adap_log_addr()`, `cec_pin_start_timer()`, `cec_pin_adap_transmit()`, `cec_pin_adap_status()`, `cec_pin_adap_monitor_all_enable()`, `cec_pin_adap_free()`, and `cec_pin_received()`. It defines the CEC timing constants and the `states[]` table mapping pin states to nominal delays.

Control flow and state: On enable, the engine reads/releases the bus, starts a kthread if needed, and starts an hrtimer. The timer samples the pin, progresses TX/RX states, records overruns, queues pin-level events for monitor mode, and chooses the next timer delay. Transmit starts when the bus has been high for the requested signal-free time, then sends start bit, data bits, EOM, and ACK slots while checking arbitration loss and low-drive. Receive starts on a low start bit, validates start/data timing, samples bits, ACKs messages addressed to this adapter or broadcasts correctly, and hands complete frames to the kthread. The kthread calls `cec_received_msg_ts()`, reports transmit completion with `cec_transmit_attempt_done_ts()`, drains pin event rings, and handles IRQ enable/disable requests.

State and persistence behavior: Per-pin state includes current state, timestamps, TX/RX bit positions and messages, low-drive/NACK/arbitration status, logical address mask, monitor flags, event ring, diagnostics counters, and error-injection settings. It is volatile and reset on disable/free. Debug status reads also clear many counters after printing.

Dependencies and integration points: It depends on `struct cec_pin_ops` supplied by a lower-level driver, the CEC adapter core, hrtimer, kthread, waitqueues, atomic ops, optional error injection, and monitor-pin userspace events. `cec-gpio.c` is a direct consumer.

Risks and edge cases: Software timing is sensitive to scheduler/timer latency; overrun counters are essential diagnostics. IRQ mode is only entered for monitor-pin-only idle cases and must disable itself when real RX/TX/configuration begins. Races between hrtimer and kthread use atomics/work fields rather than a broad lock. Error injection intentionally violates protocol and can confuse normal tests if left enabled. Broadcast ACK semantics differ from directed messages and must be preserved.

Test signals: Use pin-backed CEC compliance tests for start/data timing, arbitration, ACK/NACK, broadcast vs directed behavior, monitor pin events, HPD/5V event integration through drivers, timer overrun reporting, IRQ-mode transitions, disable/free during activity, and every debugfs error-injection mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-pin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-priv.h

Purpose: This private CEC core header shares internal macros and function prototypes among `cec-core.c`, `cec-adap.c`, and `cec-api.c`.

Important APIs, types, and functions: Macros include `dprintk()` for debug-level gated logging, `call_op()` and `call_void_op()` for registered-driver operation calls, `to_cec_adapter()` for devnode-to-adapter conversion, and `msg_is_raw()`. Prototypes cover monitor count helpers, debug status, adapter thread, adapter enable, internal physical/logical address setters, filehandle transmit, event queueing, and `cec_devnode_fops`.

Control flow and state: The macros centralize adapter-operation dispatch and ensure callbacks are skipped when the devnode is unregistered. The prototypes allow implementation files to call each other without exposing these helpers in public media headers.

State and persistence behavior: No state is stored here except the external `cec_debug` declaration. It shapes access to runtime adapter state through function boundaries.

Dependencies and integration points: Includes `<linux/cec-funcs.h>` and `<media/cec-notifier.h>`, and assumes public CEC structs are already available through included media headers in users. It is internal to the composite `cec.o`.

Risks and edge cases: `dprintk()` assumes a local variable named `adap`, so careless use in a scope without that symbol will not compile. `call_op()` returns `0` when a callback is absent or device is unregistered, which is correct for optional operations but can hide missing mandatory ops if misused.

Test signals: Compile coverage is the main signal. Runtime unregister tests should confirm callbacks stop after `devnode.unregistered` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/i2c/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/cec/i2c/Kconfig

Purpose: This file exposes I2C-attached CEC controller driver choices for CH7322 and NXP TDA9950/TDA998x.

Important APIs, types, and functions: `CEC_CH7322` is a tristate driver depending on `I2C`, selecting `REGMAP`, `REGMAP_I2C`, and `CEC_CORE`. `CEC_NXP_TDA9950` is a tristate driver depending on `I2C`, selecting `CEC_NOTIFIER` and `CEC_CORE`, and defaulting to `DRM_I2C_NXP_TDA998X`.

Control flow and state: Selecting either symbol causes the corresponding object to be compiled by the CEC I2C Makefile and selects core/helper features needed by the driver.

State and persistence behavior: Only `.config` build state.

Dependencies and integration points: Integrates I2C CEC devices with regmap for CH7322 and notifier-based HDMI physical-address propagation for TDA9950.

Risks and edge cases: TDA9950’s default ties it to a DRM encoder config, so build coverage should include both standalone and glue use. CH7322 requires regmap selection or probe-time register access cannot compile.

Test signals: Kconfig/build tests for both drivers as built-in and modules, with and without the related DRM TDA998x symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/i2c/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/i2c/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/cec/i2c/Makefile

Purpose: This Kbuild file maps I2C CEC config symbols to object files.

Important APIs, types, and functions: `obj-$(CONFIG_CEC_CH7322) += ch7322.o` and `obj-$(CONFIG_CEC_NXP_TDA9950) += tda9950.o`.

Control flow and state: Kbuild compiles each driver when the matching tristate is enabled.

State and persistence behavior: Build-only; no runtime state.

Dependencies and integration points: Consumed by the parent CEC Makefile and Kconfig selections.

Risks and edge cases: New I2C CEC drivers must be added here and to Kconfig. Object names must match source files exactly for module builds.

Test signals: Build with each symbol as `m` and `y` to validate module names and built-in linking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/i2c/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/i2c/ch7322.c -->
# sources/distributed-fs/ceph-client/drivers/media/cec/i2c/ch7322.c

Purpose: This is the I2C regmap driver for the Chrontel CH7322 CEC controller. It disables the chip’s limited auto mode, registers a CEC adapter, drives logical-address/transmit registers, receives interrupt-driven messages, and lets the chip discover the physical address from DDC/HPD.

Important APIs, types, and functions: `struct ch7322` stores I2C client, regmap, CEC adapter, access mutex, and TX interpretation flags. Key functions are `ch7322_send_message()`, `ch7322_receive_message()`, `ch7322_tx_done()`, `ch7322_rx_done()`, `ch7322_phys_addr()`, `ch7322_irq()`, CEC ops `ch7322_cec_adap_enable()`, `ch7322_cec_adap_log_addr()`, `ch7322_cec_adap_transmit()`, DMI/PCI port matching via `ch7322_get_port()`, and probe/remove. Register constants describe write/read buffers, mode, interrupt control/data, physical address, logical address, and device ID.

Control flow and state: Probe optionally maps the I2C device to a DRM connector via DMI/PCI, initializes regmap, verifies device ID, switches to software mode, enables the logical-address register, allocates a one-LA CEC adapter, marks `adap_controls_phys_addr`, optionally registers a notifier for connector info, configures interrupts, reads initial physical address if HPD is high, requests a threaded IRQ, unmasks interrupts, and registers the adapter. IRQ handling acknowledges interrupt data and dispatches HPD fall invalidation, TX completion, RX message read, new physical address read, and error logging. Transmit writes length and bytes into the write buffer when `MSENT` says ready; completion maps CH7322’s `BOK` bit into CEC OK/NACK semantics depending on poll/broadcast/retry flags.

State and persistence behavior: Runtime state is device-local and volatile. `tx_flags` remembers how to interpret the next TX completion. Physical address is owned by the chip and pushed into the CEC core via `cec_s_phys_addr()`. No persistent settings are stored by the driver.

Dependencies and integration points: Depends on I2C, regmap, IRQs, CEC core, optional PCI/DMI connector matching, and CEC notifier for connector info. It uses public CEC completion APIs and chip registers.

Risks and edge cases: The chip’s one-bit TX status has inverted meaning for polls/broadcasts, making `tx_flags` correctness critical. `regmap_config.disable_locking = true` means the driver mutex must cover all multi-register sequences. Probe failure must unregister notifier/delete adapter in the right order. DMI connector mapping is best-effort and platform-specific. The driver accepts only `CH7322_DID_CH7322`, not CH7323 despite a constant existing.

Test signals: Test probe/remove, IRQ TX/RX/HPD/new-PA paths, logical address setting, poll to self, broadcast transmit, NACK/retry mapping, HPD fall invalidation, DMI connector-info presence on known systems, and I2C error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/i2c/ch7322.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/i2c/tda9950.c -->
# sources/distributed-fs/ceph-client/drivers/media/cec/i2c/tda9950.c

Purpose: This driver supports the NXP TDA9950 CEC controller and TDA998x-integrated CEC block through an I2C mailbox interface. It registers a CEC adapter, starts/stops the chip command processor, handles transmit confirmations and received indications, and integrates with HDMI notifier/glue code.

Important APIs, types, and functions: `struct tda9950_priv` stores I2C client, HDMI parent, CEC adapter, optional glue, logical-address bitmask, RX message, notifier, and open state. Key functions include `tda9950_write_range()`, `tda9950_read_range()`, `tda9950_irq()`, `tda9950_cec_transmit()`, `tda9950_cec_adap_log_addr()`, glue open/release/init/exit helpers, `tda9950_open()`, `tda9950_release()`, `tda9950_cec_adap_enable()`, probe/remove, and devm cleanup.

Control flow and state: Probe requires full I2C transactions and an IRQ, allocates adapter with default caps plus connector info, initializes optional TDA998x glue, briefly opens the chip to read hardware version, requests a threaded shared IRQ, registers a notifier keyed by the HDMI parent, and registers the adapter. Adapter enable opens glue, resets the chip, clears logical addresses, starts the command processor; disable stops it and waits for non-busy. Transmit writes retry count then sends a mailbox request with length/service ID/payload. IRQ reads status and the mailbox, then maps confirmation codes to CEC TX status/counters or copies indication payloads into `cec_received_msg()`.

State and persistence behavior: Runtime state is volatile. `addresses` caches the active ACK mask and is mirrored into chip ACK registers, excluding address 15. `open` gates shared IRQ handling. The notifier supplies physical-address changes from HDMI/EDID; the driver does not persist them.

Dependencies and integration points: Depends on I2C_FUNC_I2C for contiguous mailbox access, IRQs, optional platform `tda9950_glue`, DRM EDID/CEC notifier, and CEC adapter core. It may be associated with the HDMI transmitter’s device rather than its own I2C device for class-device grouping.

Risks and edge cases: Multi-byte mailbox accesses must remain single I2C transactions. Shared IRQs can be harmed if the command processor fails to stop, as the warning notes. Confirmation retry count is derived from `REG_CCONR`; firmware handles retries and the core is told `MAX_RETRIES` on failure. Glue open/release ordering and devm cleanup must avoid leaving the chip powered or adapter leaked.

Test signals: Test with standalone and TDA998x-glue configurations, missing IRQ, non-I2C-capable adapter, enable/disable cycles, logical address masks including unregistered address handling, transmit success/arbitration/NACK/error confirmations, receive indications, shared IRQ behavior, notifier physical-address updates, and remove while adapter is open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/i2c/tda9950.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/Kconfig

Purpose: This file defines platform CEC driver options for ChromeOS EC, Amlogic Meson, GPIO bit-banged CEC, Samsung S5P, STi/STM32, Tegra, and SECO board controllers, plus SECO RC5 support.

Important APIs, types, and functions: Config symbols include `CEC_CROS_EC`, `CEC_MESON_AO`, `CEC_MESON_G12A_AO`, `CEC_GPIO`, `CEC_SAMSUNG_S5P`, `CEC_STI`, `CEC_STM32`, `CEC_TEGRA`, `CEC_SECO`, and `CEC_SECO_RC`. Each selects `CEC_CORE`; many select `CEC_NOTIFIER`; GPIO selects `CEC_PIN` and `GPIOLIB`; Meson G12A and STM32 select regmap helpers.

Control flow and state: Driver visibility depends on architecture, `COMPILE_TEST`, firmware subsystems, GPIO/preemption, PCI/DMI, and RC core combinations. Selected drivers are compiled through the platform Makefile and subdirectories.

State and persistence behavior: Build-time `.config` only.

Dependencies and integration points: Ties CEC platform drivers to SoC/board subsystems, notifier physical-address integration, GPIO library, ChromeOS EC protocol, regmap MMIO, PCI/DMI, and RC core.

Risks and edge cases: Architecture and `COMPILE_TEST` gates must keep drivers buildable without making invalid runtime assumptions. GPIO CEC depends on preemption or compile test because software timing is latency-sensitive. SECO RC dependency must match built-in/module RC core compatibility.

Test signals: Kconfig/build tests across supported architectures and COMPILE_TEST, with notifier, regmap, GPIO, CROS_EC, PCI/DMI, and RC combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/Makefile

Purpose: This Kbuild file descends into platform CEC driver subdirectories and keeps platform driver linkage in alphabetical order.

Important APIs, types, and functions: It maps `CONFIG_CEC_CROS_EC` to `cros-ec/`, `CONFIG_CEC_GPIO` to `cec-gpio/`, unconditionally descends into `meson/`, and gates `s5p/`, `seco/`, `sti/`, `stm32/`, and `tegra/` by their config symbols.

Control flow and state: The unconditional Meson descent lets that subdirectory gate multiple Meson variants internally. Other subdirectories are only traversed when selected.

State and persistence behavior: Build-only state.

Dependencies and integration points: Consumed by the parent CEC Makefile and platform Kconfig symbols.

Risks and edge cases: Adding platform drivers out of alphabetic order violates local convention and can complicate review. Missing subdirectory entries cause selected Kconfig options to build nothing.

Test signals: Build each platform symbol as module and built-in, especially Meson variants through the unconditional subdir.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/cec-gpio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/cec-gpio/Makefile

Purpose: This Makefile maps the generic GPIO CEC platform driver config to its object file.

Important APIs, types, and functions: `obj-$(CONFIG_CEC_GPIO) += cec-gpio.o`.

Control flow and state: Kbuild compiles `cec-gpio.c` when `CONFIG_CEC_GPIO` is enabled.

State and persistence behavior: Build-only.

Dependencies and integration points: Integrates the platform/CEC Kbuild tree with the GPIO bit-banged driver.

Risks and edge cases: Object name must remain aligned with source file and module expectations.

Test signals: Build `CEC_GPIO=y` and `CEC_GPIO=m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/cec-gpio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/cec-gpio/cec-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/cec-gpio/cec-gpio.c

Purpose: This platform driver implements a generic GPIO-backed CEC adapter using the `cec-pin` software transceiver. It optionally monitors HDMI HPD and 5V GPIOs and integrates with an HDMI notifier when an `hdmi-phandle` is present.

Important APIs, types, and functions: `struct cec_gpio` stores adapter, notifier, device, CEC GPIO/IRQ/state, optional HPD GPIO/IRQ/state/timestamp, and optional 5V GPIO/IRQ/state/timestamp. Pin ops include `cec_gpio_read()`, `cec_gpio_high()`, `cec_gpio_low()`, IRQ enable/disable, status, `read_hpd`, and `read_5v`. IRQ handlers cover CEC pin edge updates (`cec_pin_changed()`), HPD events (`cec_queue_pin_hpd_event()`), and 5V events (`cec_queue_pin_5v_event()`). Probe/remove register and unregister the pin adapter.

Control flow and state: Probe parses HDMI phandle; if absent, it adds `CEC_CAP_PHYS_ADDR` so userspace can set the physical address. It gets the CEC open-drain GPIO as output-high, optional HPD/5V inputs, allocates a pin adapter with monitor capabilities, requests CEC edge IRQ with `IRQF_NO_AUTOEN`, requests threaded HPD/5V IRQs, optionally registers a notifier, registers the CEC adapter, and stores driver data. CEC low/high ops drive the open-drain line and maintain `cec_is_low` to avoid reading a line actively driven low. HPD/5V hard IRQs timestamp edges and threaded handlers read sleepable GPIO values before queueing events.

State and persistence behavior: All state is volatile. The pin engine stores CEC protocol state; this driver stores physical GPIO state snapshots for status and event filtering. Physical address either comes from notifier or userspace depending on DT.

Dependencies and integration points: Depends on platform devices, GPIO descriptors, IRQs, CEC notifier, and `cec_pin_allocate_adapter()`. The device tree compatible is `"cec-gpio"` with GPIO names `"cec"`, optional `"hpd"`, optional `"v5"`, and optional `hdmi-phandle`.

Risks and edge cases: Software CEC timing depends on low latency; PREEMPTION dependency in Kconfig reflects that. Open-drain semantics are important: driving high means releasing the line. CEC IRQ is enabled/disabled by the pin engine, not always-on. HPD/5V IRQs use sleepable reads in threaded context. If the HDMI phandle lookup fails with a non-deferral error, userspace must set physical address manually.

Test signals: Test DT probe with and without HDMI phandle, CEC line TX/RX compliance, monitor-pin mode, IRQ enable/disable transitions, HPD/5V event initial and edge behavior, debugfs status, suspend/resume IRQ behavior if platform-specific, and remove while userspace has device open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/cec-gpio/cec-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/cros-ec/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/cros-ec/Makefile

Purpose: This Makefile maps the ChromeOS EC CEC platform driver config to its object file.

Important APIs, types, and functions: `obj-$(CONFIG_CEC_CROS_EC) += cros-ec-cec.o`.

Control flow and state: Kbuild builds the ChromeOS EC CEC driver when the config symbol is enabled.

State and persistence behavior: Build-only.

Dependencies and integration points: Integrates the platform CEC Kbuild tree with the ChromeOS EC CEC implementation.

Risks and edge cases: Must stay aligned with Kconfig and source file name for module builds.

Test signals: Build `CEC_CROS_EC=y` and `CEC_CROS_EC=m` with CROS_EC protocol support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/cros-ec/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/cros-ec/cros-ec-cec.c -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/cros-ec/cros-ec-cec.c

Purpose: This platform driver exposes ChromeOS Embedded Controller CEC ports as Linux CEC adapters. It translates EC MKBP events and host commands into CEC core receive/transmit/logical-address/enable operations and associates each EC port with a DRM connector via DMI/PCI tables.

Important APIs, types, and functions: `struct cros_ec_cec_port` stores EC port number, adapter, notifier, RX message, and parent pointer. `struct cros_ec_cec` stores EC device, notifier block, write command version, port count, and port array. Key functions include message/event handlers (`handle_cec_message()`, `cros_ec_cec_read_message()`, `handle_cec_event()`, `cros_ec_cec_event()`), CEC ops (`cros_ec_cec_set_log_addr()`, `cros_ec_cec_transmit()`, `cros_ec_cec_adap_enable()`), PM ops, DMI connector matching, EC capability queries (`cros_ec_cec_get_num_ports()`, `cros_ec_cec_get_write_cmd_version()`), per-port init, probe, and remove.

Control flow and state: Probe finds the HDMI DRM device and connector list from DMI/PCI tables, allocates driver state, enables wakeup, queries EC port count with fallback to one port on old firmware, determines whether write command v1 is supported, initializes each port by allocating/registering a one-LA adapter and notifier, then registers an EC event notifier. EC events either report old single-port inline messages, multi-port event bitmasks, transmit OK/failure, or data-ready; data-ready triggers `EC_CMD_CEC_READ_MSG`. Transmits send `EC_CMD_CEC_WRITE_MSG` using v0 single-port payload or v1 port-aware payload. Enable and logical-address changes use `EC_CMD_CEC_SET`.

State and persistence behavior: Runtime state is volatile and mirrors EC firmware capabilities: number of ports and write command version. Logical address and enabled state are set in the EC but not persisted by this driver. Connector mapping is static DMI table data.

Dependencies and integration points: Depends on ChromeOS EC device/protocol, EC MKBP event notifier, platform device parent data, DMI/PCI lookup, CEC core/notifier, and PM wake IRQ handling. DMI tables must match hardware connector ordering to EC port numbering.

Risks and edge cases: Hardware support is table-driven; unsupported systems return `ENODEV` after warning. Old firmware supports one port and old message events; multi-port firmware needs command v1. Event port bounds must be enforced. The EC firmware handles retries, so failures are reported with `MAX_RETRIES` to prevent duplicate core retries. Probe cleanup must unregister only successfully registered ports.

Test signals: Test supported DMI systems with one and multiple ports, old and new EC firmware, transmit OK/failure events, receive data-ready flow, inline old message events, invalid port events, logical-address/enable commands, suspend/resume wake IRQ, connector info propagation, and remove after partial probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/cros-ec/cros-ec-cec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/meson/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/meson/Makefile

Purpose: This Makefile maps Amlogic Meson CEC config symbols to their platform driver objects.

Important APIs, types, and functions: `obj-$(CONFIG_CEC_MESON_AO) += ao-cec.o` and `obj-$(CONFIG_CEC_MESON_G12A_AO) += ao-cec-g12a.o`.

Control flow and state: The parent platform Makefile always descends into `meson/`; this file gates each Meson object by its config symbol.

State and persistence behavior: Build-only.

Dependencies and integration points: Integrates Meson AO CEC driver variants with Kbuild. The G12A variant depends on regmap MMIO/common clock/OF per Kconfig.

Risks and edge cases: Object names must match source files and Kconfig symbols. The unconditional parent descent means this file must not add unguarded objects.

Test signals: Build `CEC_MESON_AO` and `CEC_MESON_G12A_AO` as modules and built-ins, including COMPILE_TEST configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/meson/Makefile -->
