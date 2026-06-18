# Research Group subset-b-005919

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ti/ti_sci_protocol.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/ti/ti_sci_protocol.h

Purpose: This header is the client-facing contract for the Texas Instruments System Control Interface firmware protocol. It does not implement mailbox transport itself; it defines version data, the opaque `ti_sci_handle`, operation tables, request parameter structs, resource descriptors, and build-time stubs used by TI SoC drivers.

Important APIs/types/functions: `struct ti_sci_handle` aggregates `ti_sci_ops`, including core reboot, device lifecycle, clock, low-power, resource-management, IRQ routing, ring accelerator, PSI-L, UDMAP, and processor-control operations. UDMAP/ring config structs use `valid_params` bitmasks such as `TI_SCI_MSG_VALUE_RM_RING_*_VALID` and `TI_SCI_MSG_VALUE_RM_UDMAP_*_VALID` to describe partial firmware updates. Public helpers include `ti_sci_get_handle()`, phandle lookup variants, devm-managed lookup, resource allocation/release, and OF resource acquisition.

Control flow: Consumers first acquire a handle, then call function pointers under `handle->ops`. The header encodes protocol sequencing obligations rather than logic: device and clock `get_*` calls must be balanced with `put_*`, resources are allocated from `ti_sci_resource` bitmaps, and processor ownership flows through request/release/handover before configuration/control.

State and persistence: Runtime state is external to the header: firmware owns SoC resource state; client drivers own usage balancing; `ti_sci_resource` persists local allocation bitmaps guarded by a raw spinlock. Context-loss counters and requested/current state calls are exposed for recovery after power transitions.

Dependencies/integration: Integrates with the device model, OF phandles, TI firmware, clock/reset/device drivers, IRQ domains, DMA/ring accelerator users, and remote processor/boot code. When `CONFIG_TI_SCI_PROTOCOL` is disabled, inline stubs return `-EINVAL`, `ERR_PTR(-EINVAL)`, zero, or `TI_SCI_RESOURCE_NULL`.

Risks and test signals: Main risks are unbalanced get/put calls, incorrect `valid_params` masks, stale firmware ABI assumptions, invalid resource subtype IDs, and using the stub path as if it were functional. Test signals include TI SCI probe logs, resource exhaustion behavior, handle acquisition error paths, reset/clock state readbacks, UDMAP/ring programming validation, and suspend/resume context-loss recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ti/ti_sci_protocol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sock_diag.h -->
# sources/distributed-fs/ceph-client/include/linux/sock_diag.h

Purpose: This header declares the in-kernel socket diagnostics registration and helper API used by protocol families to expose socket state over netlink diagnostic interfaces.

Important APIs/types/functions: `struct sock_diag_handler` binds a module owner, address family, and callbacks for dump, per-socket info, and destroy requests. `sock_diag_register()` and `sock_diag_unregister()` manage handler lifetime. `struct sock_diag_inet_compat` provides compatibility dispatch for INET. Cookie helpers include `sock_gen_cookie()`, `sock_diag_check_cookie()`, and `sock_diag_save_cookie()`. Reporting helpers populate memory and filter attributes.

Control flow: Protocol diagnostic code registers a handler; netlink requests call the handler's dump/get/destroy callback. `sock_gen_cookie()` disables preemption around `__sock_gen_cookie()` to keep per-socket cookie generation stable. Destroy notifications route through `sock_diag_destroy_group()` and `sock_diag_has_destroy_listeners()` before broadcasting.

State and persistence: Handler state is held by the diagnostics core; socket cookies persist on socket objects. Net namespace state matters because listener checks read `sock_net(sk)->diag_nlsk`.

Dependencies/integration: Depends on netlink, net namespaces, `struct sock`, `sk_buff`, user namespaces, and UAPI sock_diag definitions. It integrates with AF_INET/AF_INET6 TCP/UDP destroy multicast groups and deliberately ignores raw sockets for destroy broadcast routing.

Risks and test signals: Risks include module lifetime mismatches, incorrect family/protocol-to-group mapping, privacy exposure through filter/memory info, and cookie mismatch handling. Test with `ss`, `inet_diag`, netns-specific listeners, socket destroy events, raw socket exclusion, and module unload after unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sock_diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/socket.h -->
# sources/distributed-fs/ceph-client/include/linux/socket.h

Purpose: This header is the kernel-side socket ABI and syscall helper declaration layer. It defines socket address/message structures, ancillary-data macros, address/protocol family numbers, send/receive flags, socket option levels, and internal syscall entry helpers.

Important APIs/types/functions: Key types are `struct sockaddr`, `sockaddr_unsized`, `linger`, `msghdr`, `user_msghdr`, `mmsghdr`, `cmsghdr`, `ucred`, and `scm_timestamping_internal`. Helper macros include `CMSG_ALIGN`, `CMSG_DATA`, `CMSG_SPACE`, `CMSG_LEN`, `CMSG_FIRSTHDR`, `CMSG_OK`, and `for_each_cmsghdr`. Internal APIs include `move_addr_to_kernel()`, `put_cmsg*()`, timestamping helpers, `__sys_*msg`, `__sys_socket*`, bind/connect/listen/accept/shutdown helpers, and `do_getsockname()`.

Control flow: The header documents how syscalls copy user message headers into kernel `msghdr`, iterate control messages with strict bounds, execute protocol operations through socket objects, and copy addresses/control messages back to user space. `__cmsg_nxthdr()` advances by aligned control-message length and returns NULL if the next header would exceed the supplied buffer.

State and persistence: No standalone state is stored here; it defines per-call message state and constants that must remain ABI stable. `msg_control_is_user`, `msg_get_inq`, zerocopy state, and iterator state are transient syscall/message fields.

Dependencies/integration: Pulls in architecture socket constants, sockios, UIO iterators, kernel types, compiler user-pointer annotations, and UAPI socket definitions. The declared helpers integrate with `net/socket.c`, protocol families, procfs socket display, timestamping, io_uring/kiocb paths, and compat handling via `MSG_CMSG_COMPAT`.

Risks and test signals: Risks cluster around ancillary-data length checks, user pointer copying, compat flag filtering, ABI number stability, and internal flags leaking into user-visible paths. Test signals include socket syscall tests, control-message fuzzing, compat 32-bit tests, timestamp SCM tests, address-length boundary tests, and build assertions such as `__sockaddr_check_size()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sockptr.h -->
# sources/distributed-fs/ceph-client/include/linux/sockptr.h

Purpose: This header provides `sockptr_t`, a small tagged pointer abstraction for socket options and similar APIs that can accept either kernel memory or user memory without duplicating copy logic.

Important APIs/types/functions: `sockptr_t` stores either `void *kernel` or `void __user *user` plus `is_kernel`. Constructors are `KERNEL_SOCKPTR()` and `USER_SOCKPTR()`. Helpers cover null checks, offset copies, safe fixed-size copies, extensible struct copies, copy-to, memdup with and without NUL termination, string copy, and zero-tail validation.

Control flow: Callers receive a `sockptr_t` and branch only through helpers. User-backed paths use `copy_from_user()`, `copy_to_user()`, `copy_struct_from_user()`, `strncpy_from_user()`, and `check_zeroed_user()`. Kernel-backed paths use `memcpy()`, `memset()`, `memchr_inv()`, and local string length checks.

State and persistence: The abstraction has no persistence; it wraps pointer provenance for a single call. Allocating helpers return kernel allocations via `kmalloc_track_caller_noprof()` and report errors as `ERR_PTR()`.

Dependencies/integration: Depends on slab allocation and uaccess helpers. It is integrated heavily with socket option paths where the same implementation may be reached from syscalls, BPF/kernel callers, or internal protocol code.

Risks and test signals: The deprecated `copy_from_sockptr()` is unsafe unless the caller already validated length. `copy_struct_from_sockptr()` must reject non-zero excess bytes for forward-compatible kernel inputs and zero-fill short kernel inputs. Test with small `optlen`, user fault injection, oversized non-zero tails, kernel pointer callers, NUL termination, and KASAN/KMSAN coverage for offset arithmetic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sockptr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/softirq.h -->
# sources/distributed-fs/ceph-client/include/linux/softirq.h

Purpose: This compatibility header simply includes `linux/interrupt.h`, making softirq-related declarations available through the traditional `linux/softirq.h` include path.

Important APIs/types/functions: It declares no symbols of its own in this tree; all exported content comes from `interrupt.h`.

Control flow: There is no local control flow.

State and persistence: There is no local state.

Dependencies/integration: Any user including this file is implicitly coupled to the interrupt/softirq APIs provided by `linux/interrupt.h`. It preserves source compatibility for existing kernel code.

Risks and test signals: Risks are limited to include-order and dependency churn if `interrupt.h` changes. Test signal is compile coverage for files including `linux/softirq.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/softirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sonet.h -->
# sources/distributed-fs/ceph-client/include/linux/sonet.h

Purpose: This header provides kernel support types for SONET/SDH physical-layer statistics while reusing the UAPI item list.

Important APIs/types/functions: `struct k_sonet_stats` expands `__SONET_ITEMS` into `atomic_t` fields using a temporary macro. `sonet_copy_stats()` copies atomic kernel counters into a UAPI `struct sonet_stats`; `sonet_subtract_stats()` subtracts a UAPI snapshot from kernel counters.

Control flow: Device drivers maintain atomic counters, then call copy/subtract helpers when serving stats requests or delta computations.

State and persistence: The persistent state is per-device statistics stored as atomics. This header does not allocate or own storage; drivers embed `k_sonet_stats`.

Dependencies/integration: Depends on `linux/atomic.h` and `uapi/linux/sonet.h`. Integrates with ATM/SONET drivers that expose stats to userspace.

Risks and test signals: Risks include UAPI item-list drift, torn non-atomic reads if helpers are bypassed, and incorrect delta handling. Test with counter increments under load, ioctl/stat readouts, and compile checks after changing `__SONET_ITEMS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sonet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sonypi.h -->
# sources/distributed-fs/ceph-client/include/linux/sonypi.h

Purpose: This legacy Sony Programmable I/O header preserves kernel-private command IDs used for communication between the VAIO sonypi driver and video/camera-related code.

Important APIs/types/functions: It includes `uapi/linux/sonypi.h` and defines `SONYPI_COMMAND_*` numeric constants for camera configuration. Many `GET*` commands are marked obsolete; `SET*` commands cover camera enable, brightness, contrast, hue, color, sharpness, picture, and AGC.

Control flow: Consumers pass these integer command IDs through the sonypi communication path; no functions are declared here.

State and persistence: There is no local state. Persistent effects are device-specific firmware/hardware camera settings controlled elsewhere.

Dependencies/integration: Integrates with legacy VAIO platform support and V4L-era camera glue. Depends on UAPI sonypi definitions for shared constants.

Risks and test signals: Risks are mostly compatibility and dead-code related: changing numbers can break old glue, and obsolete commands may not be handled. Test signal is compile coverage for sonypi/V4L integration and runtime command behavior on supported VAIO hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sonypi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sort.h -->
# sources/distributed-fs/ceph-client/include/linux/sort.h

Purpose: This header declares generic in-kernel array sorting helpers, including variants that periodically reschedule for non-atomic contexts.

Important APIs/types/functions: `cmp_int(l, r)` performs a safe three-way comparison without subtraction overflow. `sort()` and `sort_r()` sort arrays using caller-provided compare/swap callbacks, with `sort_r()` carrying private context. `sort_nonatomic()` and `sort_r_nonatomic()` are variants that may call `cond_resched()`.

Control flow: Callers provide base pointer, element count, element size, comparator, optional swap routine, and optional private context. The implementation lives elsewhere and invokes callbacks while rearranging the array.

State and persistence: No global state. The only persistent effect is mutation of the caller-provided array.

Dependencies/integration: Depends on kernel type definitions and callback typedefs from included headers. Used by subsystems needing deterministic in-place ordering without open-coding sort algorithms.

Risks and test signals: Risks include comparators with inconsistent ordering, using nonatomic variants in atomic context, invalid element sizes, and swap callbacks that corrupt data. Test with duplicate keys, large arrays, custom swap callbacks, resched-enabled paths, and sanitizers for bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sort.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sound.h -->
# sources/distributed-fs/ceph-client/include/linux/sound.h

Purpose: This header declares legacy sound core registration functions for OSS-style special, mixer, and DSP devices.

Important APIs/types/functions: `register_sound_special()`, `register_sound_special_device()`, `register_sound_mixer()`, and `register_sound_dsp()` register file operations for sound minor units. Matching unregister calls remove special, mixer, and DSP devices.

Control flow: A sound driver registers file operations and receives a unit/minor; teardown unregisters the same unit. The `_device` form associates a backing `struct device`.

State and persistence: Device registration state is owned by the sound core. This header only declares the interface.

Dependencies/integration: Includes `uapi/linux/sound.h`, forward declares `struct device`, and depends on `struct file_operations` being visible to callers. Integrates with legacy OSS device nodes.

Risks and test signals: Risks include unit leaks, unregister/register imbalance, stale device nodes, and mismatch between file operations and device lifetime. Test with module load/unload, `/dev` node creation, and open-device teardown races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sound.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundcard.h -->
# sources/distributed-fs/ceph-client/include/linux/soundcard.h

Purpose: This compatibility header wraps the OSS soundcard UAPI and defines native-endian sample format aliases for kernel users.

Important APIs/types/functions: It includes architecture byte order and `uapi/linux/soundcard.h`, then maps `AFMT_S16_NE` to `AFMT_S16_BE` or `AFMT_S16_LE` depending on byte order.

Control flow: No executable control flow; preprocessor selection fails the build if neither big-endian nor little-endian is known.

State and persistence: No state.

Dependencies/integration: Used by OSS-compatible audio drivers and user/kernel shared format definitions. Relies on architecture byte-order macros.

Risks and test signals: Main risk is wrong endian detection causing sample format mismatch. Test with big-endian and little-endian build coverage and OSS format negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundcard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundwire/sdw.h -->
# sources/distributed-fs/ceph-client/include/linux/soundwire/sdw.h

Purpose: This is the central Linux SoundWire bus API. It defines SoundWire protocol constants, slave/master properties, device and bus objects, stream lifecycle state, bus parameters, driver callback tables, BPT helpers, messaging APIs, and disabled-config stubs.

Important APIs/types/functions: Core types include `sdw_slave`, `sdw_bus`, `sdw_master_device`, `sdw_driver`, `sdw_stream_runtime`, `sdw_stream_config`, `sdw_port_config`, `sdw_bus_params`, `sdw_slave_prop`, `sdw_master_prop`, and callback tables `sdw_slave_ops`, `sdw_master_ops`, and `sdw_master_port_ops`. Public APIs cover bus add/delete, property parsing, stream allocation/release/add/remove/prepare/enable/disable/deprepare, clock stop/exit, slave ID extraction, BPT send/wait, and register read/write/update.

Control flow: A master driver creates an `sdw_bus`, provides master/port ops, and registers it. Slave drivers bind through `sdw_driver` and optionally implement property, status, interrupt, bus config, port prep, and clock-stop callbacks. Stream control moves through `ALLOCATED -> CONFIGURED -> PREPARED -> ENABLED -> DISABLED -> DEPREPARED -> RELEASED`; bus parameter computation feeds frame shape, bandwidth, bank switching, and port programming.

State and persistence: `sdw_bus` holds locks, slave lists, runtime stream lists, deferred messages, current/next bank, assigned device-number bitmap, clock/bank-switch timeouts, IRQ domain/chip, stream/BPT refcounts, and lane bandwidth. `sdw_slave` holds status, sticky and current device numbers, completions for enumeration/initialization/port readiness, first-interrupt flags, unattach reasons, and SDCA data.

Dependencies/integration: Integrates with the driver core, fwnode/OF, IRQ domains, debugfs, SDCA helpers, ASoC stream users, PM/clock-stop paths, and vendor master drivers. `CONFIG_SOUNDWIRE` stubs warn once and return errors when disabled.

Risks and test signals: Risks include stream state misuse, bank mismatch, enumeration/read races, missed completions, device-number leaks, BPT multiple-stream violations, and callbacks racing with remove. Test with SoundWire codec enumeration, stream prepare/enable/deprepare ordering, suspend/resume clock-stop modes, interrupt routing, debugfs status, no-PM register access, and disabled-config compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundwire/sdw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_amd.h -->
# sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_amd.h

Purpose: This header defines the AMD SoundWire manager integration contract, including ACP resource descriptions, manager state, ACPI scan results, and probe/exit APIs.

Important APIs/types/functions: `acp_sdw_pdata` carries instance, ACP revision, and a shared ACP register mutex. `sdw_amd_dai_runtime` links DAI names to SoundWire streams. `amd_sdw_manager` embeds `sdw_bus`, MMIO bases, work items, status array, port/frame-shape fields, quirks, wake mask, power mode mask, clock-stopped flag, and DAI runtime array. `sdw_amd_res` and `sdw_amd_ctx` describe global resources and probe context. APIs are `sdw_amd_probe()`, `sdw_amd_exit()`, `sdw_amd_get_slave_info()`, and `amd_sdw_scan_controller()`.

Control flow: Parent audio/DSP code scans ACPI, prepares `sdw_amd_res`, probes managers, retrieves slave information, and exits through the context. Runtime work is split between IRQ/status workqueues and shared ACP register locking.

State and persistence: Manager state persists per link. `clk_stopped` and `power_mode_mask` drive suspend behavior: clock-stop mode keeps bus context, while power-off mode requires reset and re-enumeration.

Dependencies/integration: Depends on ACPI, platform devices, SoundWire core, workqueues, MMIO, and ACP shared register locking. Revision constants identify ACP63/70/71/72 variants.

Risks and test signals: Risks include missing ACP lock coverage, wrong link mask/count, power-mode wake limitations, stale port offset maps, and re-enumeration after power-off. Test via ACPI scan results, two-manager systems, suspend/runtime suspend, wake masks, IRQ work execution, and slave-info population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_amd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_intel.h -->
# sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_intel.h

Purpose: This header defines Intel SoundWire platform integration: SHIM/ALH register maps, ACE2+ register definitions, ACPI/resource context, DSP callback glue, clock-stop quirks, hardware operation hooks, and public probe/startup/IRQ APIs.

Important APIs/types/functions: Register macros cover SHIM LCAP/LCTL/SYNC/IOCTL/WAKE/CTMCTL, ALH stream config, SHIM2 generic/vendor registers, stream channel maps, and mic privacy support. `sdw_intel_ops` exposes DSP/audio callbacks for stream params/free/trigger. `sdw_intel_ctx` tracks links, MMIO, masks, link list, shared SHIM lock/mask, and peripherals. `sdw_intel_res` supplies platform resources and clock-stop quirks. `sdw_intel_hw_ops` abstracts chip-specific debugfs, link count, DAI registration, power, bus start/stop, wake, bank-switch sync, SDI programming, and BPT operations.

Control flow: Intel initialization is intentionally phased: ACPI scan, allocation/probe, startup/hardware enable, then threaded IRQ handling. Power and clock-stop paths choose among normal start, reset start, clock-stop resume, or teardown based on quirks.

State and persistence: Persistent state lives in context/link objects and shared SHIM/ALH registers. `shim_lock`, `shim_mask`, link masks, and `clock_stop_quirks` protect shared multi-link behavior and wake/sync state.

Dependencies/integration: Depends on ACPI, HDaudio/extended link resources, SoundWire core, ASoC PCM/DAI types, IRQ threading, debugfs, and DSP parent drivers. External hardware op tables are declared for CNL and LNL.

Risks and test signals: Risks include shared-register races, wrong SHIM base for ACE generation, clock-stop quirk misuse that breaks wake-capable slaves, multi-link sync failures, and ALH stream mismatches. Test with ACPI link masks, startup/exit cycles, threaded IRQs, runtime/system suspend, wake events, multi-link bank switch, and DSP params/free/trigger callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_intel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_registers.h -->
# sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_registers.h

Purpose: This header enumerates SoundWire 1.2 register addresses, bitfields, banked port register offsets, interrupt masks, PHY controls, and SDCA address construction/extraction helpers.

Important APIs/types/functions: Macros define address masks and paging flags, DP0/DPN interrupt and control registers, SCP interrupt/status/control/system registers, device ID registers, SDCA interrupt masks, banked frame/clock/port registers, PHY control masks, cascaded interrupt layout constants, and `SDW_SDCA_CTL()` plus field extraction/validation macros.

Control flow: No functions execute here; drivers use the constants to build register addresses for `sdw_read()`, `sdw_write()`, and update sequences. Banked macros direct programming into current or next bank before SoundWire bank switches.

State and persistence: Hardware registers hold all state. This header maps software names to persistent slave/control-port/data-port state, including interrupts, clock stop, device numbering, frame shape, lane control, and SDCA control selectors.

Dependencies/integration: Depends on `bitfield.h` and `bits.h`. Integrated by SoundWire core and codec/master drivers that parse interrupts, program ports, and access SDCA controls.

Risks and test signals: Risks include wrong bank offset, clearing write-clear interrupt bits accidentally, invalid SDCA address construction, and mismatch with spec revisions. Test with register read/write traces, interrupt cascade decoding, SDCA address round trips, bank switch validation, and compile checks for bitfield masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_type.h -->
# sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_type.h

Purpose: This header declares SoundWire bus/device types and driver registration helpers used by SoundWire slave drivers.

Important APIs/types/functions: Exports `sdw_bus_type`, `sdw_slave_type`, and `sdw_master_type`; `is_sdw_slave()` tests a device type; `drv_to_sdw_driver()` converts from `device_driver`; `sdw_register_driver()`, `__sdw_register_driver()`, `sdw_unregister_driver()`, `sdw_slave_uevent()`, and `module_sdw_driver()` provide driver model integration.

Control flow: Modules define an `sdw_driver`, register it through the helper macro or direct call, then the driver core probes matching SoundWire slaves. `module_sdw_driver()` wires init/exit automatically.

State and persistence: Driver registration state is owned by the driver core; this header has no local state.

Dependencies/integration: Depends on SoundWire driver definitions from `sdw.h`, kernel module helpers, and the driver model. Uevent support exports device identity to userspace.

Risks and test signals: Risks include registering malformed drivers, wrong device type checks, and uevent modalias mismatches. Test with module load/unload, driver binding, uevents, and `is_sdw_slave()` behavior for master/slave devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/ad7877.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/ad7877.h

Purpose: This board-data header describes platform configuration for the AD7877 SPI touchscreen controller.

Important APIs/types/functions: `struct ad7877_platform_data` contains model, VREF delay, X/Y plate resistance, X/Y/pressure calibration ranges, stop-acquisition polarity, first conversion delay, acquisition time, averaging, and pen-down acquisition interval.

Control flow: Board code passes this structure through `spi_board_info.platform_data`; the touchscreen driver consumes it during probe and sampling setup.

State and persistence: The fields are static board calibration/configuration data. Runtime pen samples and filtering state are owned by the driver.

Dependencies/integration: Integrates with SPI device registration and input/touchscreen driver setup. It relies on fixed enum-like numeric delay/acquisition encodings documented in comments.

Risks and test signals: Risks include wrong plate resistance or min/max calibration causing bad coordinates, incorrect polarity preventing pen detection, and delay settings that produce noisy conversions. Test with input events, calibration, pressure range, pen-down interrupt behavior, and board variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/ad7877.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/ads7846.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/ads7846.h

Purpose: This header defines platform data for ADS7843/7845/7846/7873 SPI touchscreen controllers.

Important APIs/types/functions: `ads7846_platform_data` carries model, VREF delay/value, VREF retention, XY swapping, settle and penirq recheck delays, plate resistances, coordinate/pressure bounds, debounce thresholds, optional GPIO pendown debounce, `get_pendown_state()` and `wait_for_sync()` callbacks, wakeup flag, and IRQ flags.

Control flow: The driver reads this data at probe to configure sampling, filtering, IRQ behavior, and optional board-specific synchronization/pendown checks.

State and persistence: Static board data persists through the device lifetime; runtime debounce and input state are driver-owned.

Dependencies/integration: Integrates with SPI, input touchscreen, GPIO/IRQ wiring, and platform-specific callbacks.

Risks and test signals: Risks include false touch events from bad recheck/debounce values, wrong VREF policy, swapped axes, callback sleep-context issues, and wakeup IRQ misconfiguration. Test with touch calibration, interrupt storms, suspend wake, noisy-panel debounce, and pendown GPIO behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/ads7846.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/altera.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/altera.h

Purpose: This header defines platform data, controller private state, and shared entry points for the Altera SPI controller driver.

Important APIs/types/functions: `ALTERA_SPI_MAX_CS` caps chip selects. `altera_spi_platform_data` provides mode bits, chip-select count, bits-per-word mask, and optional child `spi_board_info` entries. `struct altera_spi` stores IRQ, transfer length/count, bytes-per-word, interrupt mask, TX/RX pointers, regmap, register offset, and device pointer. Shared functions are `altera_spi_irq()` and `altera_spi_init_host()`.

Control flow: Platform code supplies controller capabilities and child devices. The controller driver initializes a `spi_controller` through `altera_spi_init_host()`, then interrupt-driven transfers use `altera_spi_irq()` to advance TX/RX buffers and counters.

State and persistence: Per-controller state persists in `altera_spi`; in-flight transfer state is `len`, `count`, `bytes_per_word`, `tx`, and `rx`, while `imr` caches interrupt-mask state.

Dependencies/integration: Depends on interrupt handling, regmap, SPI core, device model, and board-info registration.

Risks and test signals: Risks include count/length underflow, regmap offset errors, unsupported word sizes, and registering too many chip selects. Test PIO/IRQ transfers, different bits-per-word, child enumeration, interrupt masking, and full-duplex data integrity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/altera.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/at73c213.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/at73c213.h

Purpose: This board-data header describes how an AT73C213 SPI audio DAC is wired to the system.

Important APIs/types/functions: `at73c213_board_info` stores the SSC platform-driver ID used for audio streaming, an external DAC master clock pointer, and a short user-visible name.

Control flow: Board setup passes the structure as SPI platform data; the DAC driver uses it at probe to bind the SPI control path to SSC/I2S audio streaming and clock setup.

State and persistence: The data is static hardware description. Runtime audio stream and clock enable state live in the driver and clock framework.

Dependencies/integration: Integrates SPI control, Atmel SSC audio, clock framework, and userspace ALSA-visible naming.

Risks and test signals: Risks include wrong SSC ID, missing clock, and too-long/non-terminated short names. Test with DAC probe, clock rate/enable, ALSA card naming, and playback path validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/at73c213.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/corgi_lcd.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/corgi_lcd.h

Purpose: This header defines platform data and a helper for the SPI-attached Corgi LCD/backlight controller.

Important APIs/types/functions: It defines QVGA/VGA mode constants, `corgi_lcd_platform_data` with initial mode, max/default intensity, limit mask, and optional `notify()`/`kick_battery()` callbacks, plus `corgi_lcd_limit_intensity()`.

Control flow: Board data configures probe-time display/backlight behavior. The driver may notify intensity changes, kick battery handling, and apply external intensity limits through the exported helper.

State and persistence: Static board data persists in platform data; runtime intensity limits are maintained by the driver.

Dependencies/integration: Integrates with SPI, LCD/backlight subsystems, board battery logic, and legacy Sharp device support.

Risks and test signals: Risks include intensity outside supported range, incorrect mode, callback lifetime issues, and limit mask misapplication. Test display mode, brightness transitions, battery callbacks, and external limit updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/corgi_lcd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/ds1305.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/ds1305.h

Purpose: This header supplies one-time platform configuration for DS1305/DS1306 SPI RTC chips.

Important APIs/types/functions: `ds1305_platform_data` stores trickle-charge configuration bits, DS1306 variant flag, and DS1306 1 Hz output enable flag. Trickle macros define magic value, diode count, and resistor selection.

Control flow: Board code provides this data through SPI platform data. The RTC driver applies it when initializing or reinitializing the chip, especially after backup-power loss.

State and persistence: Configuration persists in RTC hardware registers after driver programming. The header stores desired policy only.

Dependencies/integration: Integrates with SPI board info and RTC driver setup; comments note expected alarm IRQ wiring.

Risks and test signals: Risks include unsafe trickle-charge settings, wrong DS1306 flag, missing magic bit handling, and alarm IRQ wiring assumptions. Test RTC probe, trickle register values, 1 Hz output, alarm interrupt, and backup-power-loss recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/ds1305.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/eeprom.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/eeprom.h

Purpose: This header defines platform data for AT25-like SPI EEPROMs.

Important APIs/types/functions: `spi_eeprom` includes byte length, name, page size, flags, and opaque context. Flags select one-, two-, or three-byte addresses, read-only policy, and `EE_INSTR_BIT3_IS_ADDR` for devices that extend address space through instruction bit 3.

Control flow: Board code passes the structure as platform data; the at25 driver uses it to choose command/address formatting, write page size, device name, and write permissions.

State and persistence: Platform data is static. Persistent state is the EEPROM contents and hardware write-protect behavior.

Dependencies/integration: Depends on `linux/memory.h` and integrates with SPI EEPROM/MTD/NVMEM style users.

Risks and test signals: Risks include wrong address-width flags causing wraparound, page-size mismatch corrupting writes, accidental writes to read-only hardware, and incorrect instruction-bit addressing. Test read/write boundaries, page crossing, read-only enforcement, NVMEM/MTD registration, and device-size probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/eeprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/flash.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/flash.h

Purpose: This header defines board-specific data for SPI flash devices, especially legacy non-DT/static partition configurations.

Important APIs/types/functions: `flash_platform_data` contains optional MTD device name, static partition array, partition count, and optional flash type string for devices that cannot be queried reliably.

Control flow: Board initialization supplies this data; SPI NOR/DataFlash drivers consume it during probe to name the MTD, choose type hints, and register partitions.

State and persistence: The header stores static layout hints. Persistent state is flash contents and partition layout exposed by MTD.

Dependencies/integration: Forward declares `mtd_partition` and integrates with SPI flash, MTD partition registration, and board files.

Risks and test signals: Risks include partition misalignment, wrong type override, stale static layouts, and DataFlash non-power-of-two geometry assumptions. Test MTD partition table, JEDEC/type fallback, erase/write/read across partition boundaries, and boot arguments such as `mtdparts=`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/flash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/libertas_spi.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/libertas_spi.h

Purpose: This header defines board-specific configuration for the Libertas SPI WLAN driver.

Important APIs/types/functions: `libertas_spi_platform_data` exposes `use_dummy_writes` to select one of two module read methods and optional board-specific `setup()`/`teardown()` callbacks receiving the `spi_device`.

Control flow: During probe, the WLAN driver uses platform data to perform board setup and choose read protocol behavior; removal calls teardown if provided.

State and persistence: The data is static board policy. Runtime WLAN state, firmware loading, and SPI transaction state are driver-owned.

Dependencies/integration: Integrates SPI, WLAN/Libertas driver setup, and board-specific power/reset/IRQ glue.

Risks and test signals: Risks include selecting a read method incompatible with clock speed or module wiring, setup/teardown imbalance, and callback failures during probe unwind. Test firmware load, network bring-up, slow SPI clock operation, dummy-write toggle, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/libertas_spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/max7301.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/max7301.h

Purpose: This header defines shared state and platform data for MAX7301/MAX730x GPIO expander support over SPI-like buses.

Important APIs/types/functions: `struct max7301` stores a mutex, cached port configuration array, cached output levels, pullup mask, `gpio_chip`, device pointer, and register read/write callbacks. `max7301_platform_data` supplies GPIO base and pullup mask. Shared probe/remove helpers are `__max730x_probe()` and `__max730x_remove()`.

Control flow: Bus-specific code fills `max7301` with read/write functions and calls the shared probe helper; GPIO operations then update cached state under lock and synchronize hardware registers.

State and persistence: `port_config`, `out_level`, and `input_pullup_active` are software caches of hardware state; mutex protects read-modify-write sequences.

Dependencies/integration: Depends on GPIO driver framework, device model, and bus-specific register access.

Risks and test signals: Risks include stale register caches, missing lock coverage, incorrect GPIO base numbering, and pullup mask misuse for unused low ports. Test GPIO direction/value operations, concurrent access, suspend/resume cache restore, and probe/remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/max7301.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/mc33880.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/mc33880.h

Purpose: This small header defines platform data for the MC33880 SPI GPIO/output driver.

Important APIs/types/functions: `mc33880_platform_data` contains only `base`, the first GPIO number assigned to the device.

Control flow: Board code passes the base number to the driver at probe; GPIO registration uses it for legacy static numbering.

State and persistence: No local state. Output state is driver/hardware-owned.

Dependencies/integration: Integrates with SPI device registration and GPIO subsystem.

Risks and test signals: Risks include GPIO number collisions or relying on static numbering where dynamic bases are preferred. Test GPIO registration, line count, output value changes, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/mc33880.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/mmc_spi.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/mmc_spi.h

Purpose: This header defines platform glue for managing MMC/SD card slots over SPI.

Important APIs/types/functions: `mmc_spi_platform_data` provides optional `init()` and `exit()` hooks for card-detect IRQ setup, MMC capability masks, card-detect debounce delay, power-up delay, OCR voltage mask, and `setpower()` callback. Accessors are `mmc_spi_get_pdata()` and `mmc_spi_put_pdata()`.

Control flow: The mmc_spi driver obtains platform data at probe, calls `init()` with an IRQ callback if needed, sets MMC host capabilities/voltage, handles power changes through `setpower()`, and calls `exit()` on teardown.

State and persistence: Platform data is static; card detect, power, and host state are owned by the MMC/SPI driver. The accessor pair may allocate or reference firmware-derived data.

Dependencies/integration: Depends on SPI, interrupt handling, MMC host core, device power callbacks, and board-specific card slot wiring.

Risks and test signals: Risks include wrong voltage OCR, missing debounce causing card flaps, sleeping in IRQ callbacks, and unbalanced pdata get/put. Test card insertion/removal, power cycling, voltage negotiation, suspend/resume, and polling-capable slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/mmc_spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/mxs-spi.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/mxs-spi.h

Purpose: This header defines Freescale i.MX23/i.MX28 SSP/SPI register offsets, bitfields, helpers, and shared controller state.

Important APIs/types/functions: Register macros cover SSP control, command, transfer/block size, timing, data, response, and status registers with old/new offset differences via `ssp_is_old()`. `BF_SSP()` builds field values. `enum mxs_ssp_id` distinguishes IMX23 and IMX28. `struct mxs_ssp` stores device, MMIO base, clock, clock rate, device ID, DMA channel/direction, and PIO command words. `mxs_ssp_set_clk_rate()` programs clock rate.

Control flow: Controller code uses variant-aware register offsets, builds control words, configures clocks/timing, selects DMA or PIO, and monitors status/interrupt bits for transfer completion or errors.

State and persistence: Persistent controller state includes MMIO registers, clock rate, DMA direction/channel, and cached PIO words. The struct tracks enough state to program both SPI and related SSP modes.

Dependencies/integration: Depends on DMA engine, clocks, MMIO, SPI/MMC-capable SSP hardware, and SoC variant knowledge.

Risks and test signals: Risks include using wrong register map for IMX23 vs IMX28, bad clock divisors, DMA direction mismatch, FIFO/status error mishandling, and CRC/timeout bits crossing SPI/MMC modes. Test with PIO and DMA transfers, clock-rate changes, both SoC variants, FIFO under/overflow handling, and timeout/error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/mxs-spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/offload/consumer.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/offload/consumer.h

Purpose: This header exposes the consumer-side SPI offload API for peripheral drivers that want controller/provider hardware to execute SPI transfers triggered by external events or DMA streams.

Important APIs/types/functions: `devm_spi_offload_get()` acquires an offload instance for a `spi_device` and config. Trigger APIs acquire, validate, enable, and disable `spi_offload_trigger` objects. DMA helpers request managed TX/RX stream DMA channels. The module imports the `SPI_OFFLOAD` namespace.

Control flow: A consumer requests an offload, obtains a matching trigger, validates a trigger configuration, enables it around prepared transfers, and disables it during teardown or stop. Stream DMA requests are optional based on provider capabilities.

State and persistence: Managed devres lifetime controls offload, trigger, and DMA channel references. Runtime trigger enable state is held by provider implementations.

Dependencies/integration: Depends on SPI offload types, module namespaces, device-managed resources, DMA engine, and provider callbacks linked through `spi_controller.get_offload()`.

Risks and test signals: Risks include capability mismatch, enabling invalid trigger configs, DMA channel lifetime leaks, and leaving triggers enabled after device stop. Test devm cleanup, trigger validate failures, TX/RX stream transfers, provider absence, and suspend/remove paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/offload/consumer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/offload/provider.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/offload/provider.h

Purpose: This header exposes the provider-side SPI offload API for controllers or companion devices that can supply offload engines and triggers.

Important APIs/types/functions: `devm_spi_offload_alloc()` allocates an offload with private storage. `spi_offload_trigger_ops` defines match, request, release, validate, enable, and disable callbacks. `spi_offload_trigger_info` binds a provider fwnode, ops, and private state. Providers register triggers with `devm_spi_offload_trigger_register()` and retrieve private trigger state with `spi_offload_trigger_get_priv()`.

Control flow: Provider drivers allocate offload instances, register trigger providers, match consumer requests by firmware node/type/args, validate runtime configs, and enable/disable hardware triggers.

State and persistence: Provider-private state hangs from offload and trigger info. Devres controls allocation/registration lifetime; hardware trigger state persists until disabled or device removal.

Dependencies/integration: Depends on SPI offload types, fwnode matching, module namespace import, and device-managed resource cleanup.

Risks and test signals: Risks include weak match semantics, trigger reference leaks, accepting invalid frequencies/offsets, and disabling callbacks not restoring hardware. Test multiple consumers, fwnode matching, validation bounds, enable/disable cycles, and provider removal with active consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/offload/provider.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/offload/types.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/offload/types.h

Purpose: This header defines shared SPI offload data structures, capability flags, transfer flags, trigger configuration types, and provider operation callbacks.

Important APIs/types/functions: Transfer flags `SPI_OFFLOAD_XFER_TX_STREAM` and `SPI_OFFLOAD_XFER_RX_STREAM` identify transfers backed by external streams. Capability flags describe trigger support, static TX playback, and TX/RX stream DMA. `spi_offload_config` requests required capabilities. `spi_offload` holds provider device, provider-private pointer, ops, and supported transfer flags. Trigger config supports data-ready and periodic modes with frequency/offset. `spi_offload_ops` includes trigger enable/disable and optional TX/RX DMA channel request callbacks.

Control flow: Consumers request offloads by capabilities, configure triggers, then message transfers can mark offload-specific stream behavior using `spi_transfer.offload_flags`. Providers implement callbacks to arm hardware and expose DMA channels.

State and persistence: Offload instance state persists for the consumer/provider lifetime. Trigger runtime state is external but controlled through ops.

Dependencies/integration: Depends on `bits.h`, integer types, device references, DMA channels, and SPI core fields that reference `spi_offload`.

Risks and test signals: Risks include capability flag drift, using stream flags without matching DMA support, provider device reference leaks, and periodic trigger overflow/precision issues. Test capability negotiation, message optimization with offload, DMA channel request/release, periodic trigger timing, and inactive-provider errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/offload/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/sh_hspi.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/sh_hspi.h

Purpose: This minimal header preserves the platform-data type for the Renesas SuperH HSPI driver.

Important APIs/types/functions: It defines an empty `struct sh_hspi_info`, leaving room for board data without any current fields.

Control flow: No control flow is declared here. Platform code may still use the type as a marker.

State and persistence: No state.

Dependencies/integration: Integrates only by type name with legacy SH HSPI platform data.

Risks and test signals: Risks are limited to compatibility and dead field assumptions. Test signal is compile coverage for any HSPI board files using `sh_hspi_info`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/sh_hspi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/sh_msiof.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/sh_msiof.h

Purpose: This header defines Renesas SH/MSIOF SPI register offsets, bitfields, mode constants, and platform data.

Important APIs/types/functions: Macros cover transmit/receive mode registers, clock select, control, FIFO control, status, interrupt enable, FIFO data, frame sync, word length, FIFO watermarks, DMA enable, and error flags. The anonymous enum distinguishes host and target modes. `sh_msiof_spi_info` supplies FIFO overrides, chip-select count, mode, DMA IDs, and timing delay fields `dtdl`/`syncdl`.

Control flow: The driver programs TX/RX mode registers, clock dividers, FIFO thresholds, control enable/reset bits, and interrupt/DMA masks according to platform data and transfer requirements.

State and persistence: Hardware registers hold transfer mode, FIFO, clock, and error state. Platform info is static per controller.

Dependencies/integration: Depends on bitfield/bits helpers and integrates with Renesas SPI controller, DMA, and platform data.

Risks and test signals: Risks include asymmetric TX/RX register programming, wrong FIFO threshold override, DMA ID mismatch, SPI host/target confusion, and unhandled frame/FIFO errors. Test PIO/DMA transfers, target mode, FIFO watermark interrupts, clock polarity/phase, and error bit recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/sh_msiof.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi-fsl-dspi.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/spi-fsl-dspi.h

Purpose: This header defines platform data for Freescale DSPI controllers.

Important APIs/types/functions: `fsl_dspi_platform_data` contains chip-select count, bus number, SCK-to-CS delay, and CS-to-SCK delay.

Control flow: Board code provides these values at controller probe; the DSPI driver configures bus identity, chip-select capacity, and timing.

State and persistence: Static platform data only. Runtime transfer and register state are driver-owned.

Dependencies/integration: Integrates with SPI controller registration and Freescale/NXP platform setup.

Risks and test signals: Risks include wrong bus numbering, too few chip selects, and timing delays that violate peripheral setup/hold constraints. Test chip-select enumeration, transfer timing on a logic analyzer, and multiple attached devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi-fsl-dspi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi-mem.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/spi-mem.h

Purpose: This header defines the SPI memory abstraction used by flash-like devices and QSPI/OSPI controllers, expressing operations as command/address/dummy/data phases rather than generic byte transfers.

Important APIs/types/functions: Builder macros create STR/DTR command, address, dummy, data, and full `SPI_MEM_OP()` descriptors. `spi_mem_op` carries phase widths, DTR, ECC, swap16, direction, byte counts, buffers, and per-operation max frequency. Direct mapping types are `spi_mem_dirmap_info` and `spi_mem_dirmap_desc`. `spi_mem` wraps a `spi_device`; `spi_controller_mem_ops` supplies adjust/support/exec/name/dirmap/poll callbacks; `spi_controller_mem_caps` advertises DTR/ECC/swap16/per-op frequency. `spi_mem_driver` wraps `spi_driver`.

Control flow: Memory drivers build an operation, adjust size/frequency, check support, then execute it or use direct mapping. Direct mapping creation may fall back to `exec_op()` through `nodirmap`, letting drivers use one path even when hardware lacks mapping support.

State and persistence: `spi_mem` stores driver private data and name; dirmap descriptors persist mapping metadata and provider private state until destroyed. Hardware memory contents persist externally.

Dependencies/integration: Depends on SPI core, DMA scatterlists for mapped data, SPI NOR/NAND-style drivers, and QSPI controller native mem ops. Disabled `CONFIG_SPI_MEM` stubs return unsupported/default false for DMA/support helpers.

Risks and test signals: Risks include duplicate macro definition for `SPI_MEM_DTR_OP_RPT_ADDR`, bad address-width/value fit, DTR phase mismatches, direct-map short I/O handling, unsupported ECC/swap16 use, and DMA mapping lifetime. Test with JEDEC read, page program, erase/status polling, DTR octal modes, direct-map fallback and partial reads/writes, and controller capability negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi-mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/spi.h

Purpose: This is the main Linux SPI core API. It defines SPI devices, protocol drivers, controllers, transfer/message objects, statistics, registration helpers, synchronous/asynchronous I/O helpers, board-info templates, DMA/timestamp/offload hooks, and message-resource management.

Important APIs/types/functions: Key types include `spi_device`, `spi_driver`, `spi_controller`, `spi_transfer`, `spi_message`, `spi_statistics`, `spi_delay`, `spi_board_info`, `spi_res`, and `spi_replaced_transfers`. Important APIs cover driver registration, controller allocation/registration, device allocation/add/remove, message init/add/free, `spi_async()`, `spi_sync()`, `spi_sync_transfer()`, `spi_write/read()`, `spi_write_then_read()`, bus lock/unlock, controller suspend/resume, transfer/message finalization, PTP timestamp helpers, message optimization, transfer splitting, and board-info registration.

Control flow: Protocol drivers configure `spi_device`, build `spi_message` lists of `spi_transfer` segments, then submit asynchronously or synchronously. Controller drivers either provide a raw `transfer()` queue entry point or use core queuing with `transfer_one_message()`/`transfer_one()`. The generic queue tracks `cur_msg`, completions, queue state, runtime PM, DMA mapping, chip-select state, error handling, and finalization callbacks.

State and persistence: `spi_controller` owns bus-wide locks, queues, current message, runtime PM flags, DMA channels, GPIO chip-select descriptors, stats, and controller capabilities. `spi_device` owns per-target mode, max speed, word size, CS mapping, lane maps, delays, IRQ, controller-private state, and per-device stats. `spi_message` and `spi_transfer` are caller-owned until completion.

Dependencies/integration: Integrates with the driver core, ACPI/OF firmware, GPIO descriptors, DMA engine, PTP timestamping, statistics/u64 sync, offload, spi-mem, board files, and UAPI SPI mode constants. Compile-time assertion prevents kernel-only mode bits from overlapping user-visible bits.

Risks and test signals: Risks include message/transfer lifetime violations, forgetting `spi_finalize_current_*()`, unsupported mode or bits-per-word, DMA alignment/size errors, chip-select timing mistakes, queue fast-path races, PTP timestamp quality issues, and offload misuse. Test with spi-loopback/spidev, sync/async stress, suspend/resume, GPIO CS and native CS, DMA/PIO fallback, transfer splitting, multi-CS/lane setups, stats counters, and controller unregister with queued messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi_bitbang.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/spi_bitbang.h

Purpose: This header defines the helper framework for SPI controllers implemented by bit-banging GPIO or similar software-controlled lines.

Important APIs/types/functions: `spi_bb_txrx_word_fn` is the per-mode word shift function type. `spi_bitbang` stores a mutex, busy/use_dma flags, extra mode flags, controller pointer, setup-transfer hook, chipselect hook, optional MOSI idle setter, buffer TX/RX hook, per-mode word functions, and optional line-direction hook. Helpers include setup/cleanup/setup_transfer and queue start/init/stop APIs.

Control flow: A bitbang driver fills callbacks, initializes/starts the helper, and the framework sequences chipselect, setup, and transfer functions for queued SPI messages.

State and persistence: `lock` and `busy` serialize controller state. Callback tables and `ctlr` persist for the controller lifetime.

Dependencies/integration: Depends on workqueues and SPI core types. Used by GPIO and other simple software SPI controllers.

Risks and test signals: Risks include timing jitter, wrong mode-specific shift functions, direction errors for 3-wire modes, and chipselect polarity mistakes. Test all SPI modes, different word sizes, half-duplex transfers, queue start/stop, and logic analyzer timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi_bitbang.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi_gpio.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/spi_gpio.h

Purpose: This header provides platform data for the `spi_gpio` bitbanged SPI host controller.

Important APIs/types/functions: `spi_gpio_platform_data` contains `num_chipselect`, the number of target devices the GPIO-backed controller should allow.

Control flow: Platform code creates a `spi_gpio` platform device and passes this data; the driver registers a bitbang SPI controller with the requested chip-select count.

State and persistence: Static platform data only. GPIO line state and bitbang controller state are driver-owned.

Dependencies/integration: Integrates platform devices, SPI board info, GPIO-backed SPI, and the bitbang helper.

Risks and test signals: Risks include stale platform devices when switching to native controllers, wrong chip-select count, and GPIO descriptor mismatch. Test controller registration, multiple chip selects, transfer timing, and replacement with native controller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi_gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi_oc_tiny.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/spi_oc_tiny.h

Purpose: This header defines platform data for the OpenCores tiny SPI controller.

Important APIs/types/functions: `tiny_spi_platform_data` provides input clock frequency and baud-rate divider width, used when the divider is programmable.

Control flow: Controller probe reads these values to compute and program SPI clock dividers.

State and persistence: Static platform data only. Runtime clock divider/register state is driver-owned.

Dependencies/integration: Integrates with SPI controller registration and OpenCores tiny SPI hardware.

Risks and test signals: Risks include wrong input frequency, invalid divider width, and resulting out-of-spec SCK rates. Test clock calculation, transfer speed requests, and logic analyzer SCK measurement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi_oc_tiny.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/tdo24m.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/tdo24m.h

Purpose: This header defines platform data for TDO24M/TDO35S SPI display panels.

Important APIs/types/functions: `enum tdo24m_model` identifies `TDO24M` and `TDO35S`; `tdo24m_platform_data` stores the selected model.

Control flow: Board code provides the model; the display driver uses it during probe to select initialization and timing behavior.

State and persistence: Static board description only. Panel power, mode, and framebuffer state are driver-owned.

Dependencies/integration: Integrates with SPI display/panel driver setup.

Risks and test signals: Risks include wrong model selection causing invalid panel init. Test panel probe, mode timing, color output, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/tdo24m.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/tle62x0.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/tle62x0.h

Purpose: This header supplies platform glue for Infineon TLE62x0 SPI output/GPIO driver chips.

Important APIs/types/functions: `tle62x0_pdata` contains initial output state and GPIO count.

Control flow: Board data passes initial state and line count to the driver at probe; the driver registers output GPIOs and programs initial hardware state.

State and persistence: Static platform data plus persistent hardware output state after programming.

Dependencies/integration: Integrates SPI device setup and GPIO/output drivers.

Risks and test signals: Risks include unsafe initial output levels, wrong GPIO count, and no include guard in this short legacy header. Test probe initialization, GPIO line count, output changes, and reboot-safe default states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/tle62x0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/xilinx_spi.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/xilinx_spi.h

Purpose: This header defines platform data for Xilinx SPI controller drivers.

Important APIs/types/functions: `xspi_platform_data` supplies child `spi_board_info` entries, child count, chip-select count, bits-per-word value, and `force_irq` for QSPI transaction requirements.

Control flow: Controller probe uses this data to register child devices, set chip-select capacity, configure word width, and choose interrupt-forced behavior when required.

State and persistence: Static platform data only. Controller runtime state is driver-owned.

Dependencies/integration: Depends on kernel types and forward-declared `spi_board_info`; integrates with Xilinx SPI/QSPI controller and board files.

Risks and test signals: Risks include registering wrong child devices, unsupported bits-per-word, insufficient chip-select count, and forced IRQ path regressions. Test child enumeration, word-size transfers, IRQ/PIO behavior, and multi-device buses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/xilinx_spi.h -->
