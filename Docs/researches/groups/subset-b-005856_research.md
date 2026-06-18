# subset-b-005856 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/qcom/qcom_qseecom.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/qcom/qcom_qseecom.h

## Purpose
This header exposes the Qualcomm QSEECOM client-facing wrapper for Secure Execution Environment applications. It models a QSEE application as an auxiliary bus client and gives consumers a narrow send/receive entry point.

## APIs, types, and control flow
`struct qseecom_client` embeds `struct auxiliary_device` and stores the loaded secure app `app_id`. `qcom_qseecom_app_send()` is an inline wrapper around `qcom_scm_qseecom_app_send(client->app_id, req, req_size, rsp, rsp_size)`. The effective flow is client driver owns a `qseecom_client`, allocates TrustZone/DMA-safe request and response buffers, fills the request, then routes the call through the Qualcomm SCM layer.

## State and dependencies
Persistent state is the auxiliary device identity plus firmware app id. It depends on `linux/auxiliary_bus.h`, DMA mapping types, and `qcom_scm.h`; QSEECOM behavior is provided by the SCM implementation and `CONFIG_QCOM_QSEECOM`.

## Integration, risks, and tests
Callers must pass TZ memory buffers with valid sizes and app-specific layout. Risks are stale app ids, non-secure buffers, bad request ABI, and treating SCM errors as app responses. Test signals include disabled-config `-EINVAL` paths in SCM, successful auxiliary client bind/probe, DMA/TZ allocation lifetime tests, and app-specific request/response round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/qcom/qcom_qseecom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/qcom/qcom_scm.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/qcom/qcom_scm.h

## Purpose
This header is the broad public contract for Qualcomm Secure Channel Manager calls. It lets Linux drivers invoke secure firmware services for boot vectors, remote processor PAS authentication, IOMMU and memory ownership, secure IO, crypto/ICE keys, HDCP, GPU setup, shared memory bridges, QSEECOM, and QTEE callbacks.

## APIs, types, and control flow
Important types include `struct qcom_scm_vmperm`, OCMEM and secure device enums, ICE cipher ids, and `struct qcom_scm_pas_context`, which carries remoteproc metadata, memory address/size, DMA/TZ allocation state, and device ownership. PAS users typically allocate a context, initialize/authenticate metadata, set memory, authenticate/reset, then shut down or release metadata. Memory assignment uses `qcom_scm_assign_mem()` with source VM mask and destination permissions. QSEECOM functions are compiled to real declarations only with `CONFIG_QCOM_QSEECOM`; otherwise they return `-EINVAL`.

## State and dependencies
The header has no storage but defines firmware-visible ids, permission bits, and context fields that implementations persist across calls. It depends on firmware device tree bindings, cpumasks, device/resource-table users, DMA/TZ memory, and secure monitor availability.

## Integration, risks, and tests
This interface sits below remoteproc, storage encryption, GPU, display, IOMMU, and trusted-app drivers. Risks include wrong PAS id, mismatched physical addresses, bad VM permissions that strand memory, unsupported optional calls, and key-size/cipher mistakes in ICE. Tests should cover `qcom_scm_is_available()`, feature-available predicates, disabled QSEECOM stubs, PAS happy/failure sequencing, memory assign rollback, and firmware error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/qcom/qcom_scm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/qcom/qcom_tzmem.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/qcom/qcom_tzmem.h

## Purpose
This header defines a Qualcomm TrustZone memory pool API. It provides controlled allocation of memory intended for secure firmware interactions and optional shared-memory bridge registration.

## APIs, types, and control flow
`enum qcom_tzmem_policy` selects static, multiplier growth, or on-demand growth. `struct qcom_tzmem_pool_config` supplies initial size, increment, maximum size, and growth policy. Callers create pools with `qcom_tzmem_pool_new()` or `devm_qcom_tzmem_pool_new()`, allocate with `qcom_tzmem_alloc(pool, size, gfp)`, free with `qcom_tzmem_free()`, and translate virtual allocation addresses with `qcom_tzmem_to_phys()`. `DEFINE_FREE(qcom_tzmem, ...)` enables cleanup-based release. With `CONFIG_QCOM_TZMEM_MODE_SHMBRIDGE`, bridge create/delete calls register physical ranges with secure firmware; otherwise they are harmless no-ops.

## State and dependencies
Pool state is opaque and implementation-owned. Allocation lifetime is tied to explicit free or devres for devm pools. Dependencies include cleanup helpers, GFP allocation context, physical addresses, and SCM shared-memory bridge support.

## Integration, risks, and tests
QSEECOM, QTEE, PAS, and secure-memory callers can use this to avoid ad hoc DMA buffer handling. Risks are freeing memory while firmware still owns it, using the no-op bridge stubs as proof of secure isolation, exceeding max growth, and calling physical translation on invalid pointers. Tests should cover policy growth boundaries, devm cleanup, phys conversion, allocation failure under GFP constraints, and bridge enabled/disabled behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/qcom/qcom_tzmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/samsung/exynos-acpm-protocol.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/samsung/exynos-acpm-protocol.h

## Purpose
This header defines the client handle and operation table for Samsung Exynos ACPM firmware protocol services. It focuses on firmware-mediated DVFS clock rates and PMIC register access.

## APIs, types, and control flow
`struct acpm_dvfs_ops` supplies `set_rate()` and `get_rate()` keyed by ACPM channel and clock id. `struct acpm_pmic_ops` supplies single, bulk, write, bulk-write, and masked update register operations keyed by channel plus PMIC type/register/channel fields. `struct acpm_ops` groups the service tables, and `struct acpm_handle` embeds those ops. Consumers obtain a handle by device tree node through `devm_acpm_get_by_node()`, then call the handle's function pointers.

## State and dependencies
State is opaque to clients and represented by `struct acpm_handle`. The API depends on `struct device_node`, device-managed acquisition, and `CONFIG_EXYNOS_ACPM_PROTOCOL`; when disabled, handle lookup returns `NULL`.

## Integration, risks, and tests
Clock, regulator, PMIC, and SoC power drivers integrate through this protocol instead of programming hardware directly. Risks include unchecked `NULL` handles, channel-id mismatches, register width/count misuse, and firmware serialization or timeout failures hidden behind callback-style ops. Test signals are devm cleanup, disabled-config fallback, DVFS set/get consistency, PMIC bulk count bounds, masked update correctness, and firmware error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/samsung/exynos-acpm-protocol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/thead/thead,th1520-aon.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/thead/thead,th1520-aon.h

## Purpose
This header describes the T-Head TH1520 always-on firmware RPC ABI used for power, watchdog, low-power, miscellaneous, and system services.

## APIs, types, and control flow
It defines service ids (`TH1520_AON_RPC_SVC_*`), per-service function ids for misc, watchdog, system, low-power, and power management, and packed wire structures `th1520_aon_rpc_msg_hdr` plus `th1520_aon_rpc_ack_common`. Header access macros set/get version, service id, message type, and ack type by bit packing into `svc`. Runtime entry points are `th1520_aon_init(dev)`, `th1520_aon_deinit()`, `th1520_aon_call_rpc(aon_chan, msg)`, and `th1520_aon_power_update(aon_chan, rsrc, power_on)`.

## State and dependencies
The opaque `struct th1520_aon_chan` owns channel state. Message headers are packed/aligned for firmware transport, and constants encode power modes and power-domain ids such as audio, video, NPU, GPU, and DSP islands.

## Integration, risks, and tests
Power domain, watchdog, suspend, and low-power drivers use this as their firmware transport. Risks include bit-setting macros using OR semantics on uncleared fields, packed ABI drift, wrong message sizes, missing ack handling, and concurrent RPC serialization. Tests should check init/deinit lifetime, header encode/decode, ack error-code paths, power-domain toggles, watchdog commands, and suspend/resume RPC ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/thead/thead,th1520-aon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/trusted_foundations.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/trusted_foundations.h

## Purpose
This header provides the platform contract for NVIDIA Trusted Foundations secure monitor support on older ARM/Tegra consumer devices. It exists because those systems require proprietary SMC calls for CPU reset vectors and power management rather than PSCI.

## APIs, types, and control flow
`struct trusted_foundations_platform_data` carries secure monitor version fields. With `CONFIG_TRUSTED_FOUNDATIONS`, the header declares registration, device-tree registration, and status queries. Without support, `register_trusted_foundations()` deliberately degrades the system: it logs errors, optionally installs a dummy L2X0 secure write hook, disables SMP by setting `setup_max_cpus = 0`, and enables idle polling. `of_register_trusted_foundations()` detects the compatible node and triggers the degraded path when support is missing.

## State and dependencies
State is global secure-monitor registration and platform version information. Dependencies include Open Firmware, CPU/SMP control, printk, L2X0 outer cache hooks, and idle polling.

## Integration, risks, and tests
This header affects early boot, secondary CPU bring-up, cache controller access, and CPU PM. Risks are silent feature loss when support is disabled, nonstandard SMC ABI assumptions, and boot failures if device tree requires TF but the kernel cannot implement it. Tests include DT-compatible detection, disabled-config degradation logs, SMP disabled behavior, L2X0 fallback hook installation, and registered-status checks on supported builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/trusted_foundations.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/xlnx-event-manager.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/xlnx-event-manager.h

## Purpose
This header defines the AMD/Xilinx firmware event manager client API for subscribing to platform management callbacks.

## APIs, types, and control flow
`event_cb_func_t` receives a pointer to up to `CB_MAX_PAYLOAD_SIZE` 32-bit payload words plus caller data. `xlnx_register_event(cb_type, node_id, event, wake, cb_fun, data)` subscribes a callback to a PM callback type, node id, event id, and wake behavior. `xlnx_unregister_event()` removes the matching subscription. The callback id type comes from `xlnx-zynqmp.h`, and constants include subsystem restart and ACPU node ids.

## State and dependencies
Subscription state is owned by the event-manager implementation and keyed by callback type/node/event/function/data tuple. With `CONFIG_XLNX_EVENT_MANAGER` unreachable, both calls return `-ENODEV`. It depends on the ZynqMP firmware definitions and firmware callback delivery.

## Integration, risks, and tests
Users include restart, error, power, and device event consumers that must react to firmware notifications. Risks are unregister tuple mismatches, callback lifetime after module removal, wake flag misuse, and payload length assumptions. Tests should cover disabled stubs, duplicate registration policy, callback dispatch with sample payloads, unregister during callback or module teardown, and wake-capable event delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/xlnx-event-manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/xlnx-zynqmp-crypto.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/xlnx-zynqmp-crypto.h

## Purpose
This header exposes Xilinx/AMD secure firmware crypto calls for ZynqMP and Versal platforms, including AES engine operation, SHA hashing, feature selection, and Versal AES-GCM staged operations.

## APIs, types, and control flow
`struct xlnx_feature` maps platform family and feature id to device data. `XSECURE_API_*` constants identify AES firmware commands. When ZynqMP firmware is reachable, callers can invoke `zynqmp_pm_aes_engine(address, out)`, `zynqmp_pm_sha_hash(address, size, flags)`, feature-data lookup, and Versal AES operations: key write/zero, operation init, AAD update, encrypt/decrypt update, finalization, and initialization. Without firmware, functions return `-ENODEV` or `ERR_PTR(-ENODEV)`.

## State and dependencies
State is mostly firmware-resident. Callers pass DMA/physical addresses containing request structures and buffers; key state may persist in secure hardware until zeroed. The header relies on ZynqMP firmware reachability and common error-pointer handling.

## Integration, risks, and tests
Crypto drivers and firmware-backed secure services integrate here. Risks include passing non-DMA-safe addresses, wrong request structure layout, key lifetime leaks, treating `ERR_PTR` as data, and missing feature gating by family. Tests should cover disabled stubs, key zero after use, AES staged sequencing, SHA size/flag validation, firmware error propagation, and feature map lookup for each supported family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/xlnx-zynqmp-crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/xlnx-zynqmp-ufs.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/xlnx-zynqmp-ufs.h

## Purpose
This header exposes small AMD/Xilinx firmware helpers for UFS/MPHY bring-up on ZynqMP-family firmware platforms.

## APIs, types, and control flow
The real API, enabled through reachable `CONFIG_ZYNQMP_FIRMWARE`, includes readiness probes for MPHY TX/RX configuration and SRAM initialization, a call to set SRAM bypass, and a call to fetch UFS calibration values. Each writes results through caller-provided `bool *` or `u32 *` output pointers. Disabled stubs uniformly return `-ENODEV`.

## State and dependencies
No local state is defined. State is firmware and hardware init state, observed or mutated through the PM firmware channel. Dependencies are minimal but the header is included by `xlnx-zynqmp.h` and UFS platform drivers.

## Integration, risks, and tests
UFS host initialization can use these calls to decide when MPHY/SRAM setup is ready and to program calibration. Risks include assuming output values are initialized on error, polling indefinitely, calling bypass at the wrong phase, and missing firmware availability checks. Tests should cover disabled stubs, timeout behavior around readiness polling, calibration output validation, and probe deferral or failure handling when firmware reports not-ready states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/xlnx-zynqmp-ufs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/xlnx-zynqmp.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/xlnx-zynqmp.h

## Purpose
This is the central public firmware API definition for Xilinx ZynqMP, Versal, and Versal NET platform management. It enumerates firmware command ids, status codes, reset ids, pinctrl/clock/query controls, node capabilities, FPGA loading, secure register access, suspend/shutdown modes, and PM call wrappers.

## APIs, types, and control flow
The primary low-level gateways are `zynqmp_pm_invoke_fn()` and `zynqmp_pm_invoke_fw_fn()`, taking PM API ids and variadic payloads. High-level wrappers cover API/chip/family discovery, clock enable/disable/divider/parent, PLL fractional mode/data, SD/GEM config, resets, boot mode, suspend mode, node request/release/requirements, efuse, FPGA load/status/config status, global/persistent global storage registers, tap delay, system shutdown, pinctrl, PDI load, notifier registration, feature checks/config, secure register read/mask-write, SGI registration, powerdown/wake, RPU mode/TCM config, and node status. When firmware is unavailable, wrappers return `-ENODEV`.

## State and dependencies
State is firmware-owned but Linux caches/uses constants for API versions, module ids, callback payload widths, node ids, reset ids, and PM return statuses. The header includes UFS and crypto sub-APIs and is consumed by clock, pinctrl, reset, FPGA, power, UFS, crypto, and event drivers.

## Integration, risks, and tests
Risks include API id drift, wrong enum/node id selection, insufficient feature checks before optional calls, output pointer misuse after errors, variadic argument count mistakes in the invoke layer, and firmware version mismatch. Tests should validate disabled stubs, feature discovery, each subsystem wrapper's argument packing, reset/status paths, clock tree queries, pinctrl config, FPGA load flags, shutdown commands, and conversion of firmware return codes to Linux errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/xlnx-zynqmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fixp-arith.h -->
# sources/distributed-fs/ceph-client/include/linux/fixp-arith.h

## Purpose
This header provides simple fixed-point trigonometry and interpolation helpers for kernel code that cannot use floating point.

## APIs, types, and control flow
`sin_table[]` stores sine values for 0..90 degrees scaled to signed 32-bit range. `__fixp_sin32()` folds degrees into quadrants and sign; `fixp_sin32()` normalizes arbitrary signed degrees into 0..359. Cosine is `fixp_sin32(v + 90)`, and 16-bit variants right-shift the 32-bit result. `fixp_sin32_rad(radians, twopi)` maps caller-defined radian units to degrees, interpolates between adjacent table entries, and uses `div_s64()` for precision. `fixp_linear_interpolate()` computes a y value from two points.

## State and dependencies
The table is static const. There is no mutable state. Dependencies are `BUG_ON`, `div_s64`, and integer types. `fixp_sin32_rad()` hard-stops with `BUG_ON(twopi > 1 << 18)` to avoid overflow.

## Integration, risks, and tests
This is useful for drivers needing approximate geometry without FPU use. Risks include kernel BUG from unvalidated `twopi`, interpolation overflow for large deltas, precision limits from degree table spacing, and division by zero if `twopi < 360` makes `dx` zero. Tests should compare known quadrants, negative angles, wraparound, radian interpolation, boundary `twopi`, and linear interpolation degenerate cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fixp-arith.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/flat.h -->
# sources/distributed-fs/ceph-client/include/linux/flat.h

## Purpose
This header defines the uClinux flat executable file format used by binary loaders on no-MMU systems.

## APIs, types, and control flow
`FLAT_VERSION` identifies the current format. `struct flat_hdr` stores network-byte-order fields for magic, revision, entry offset, data range, bss end, stack size, relocation table offset/count, flags, build date, and reserved filler. Flags describe load mode, GOT/PIC usage, gzip compression, compressed data/relocs, and kernel tracing. Legacy v2 support defines relocation type constants and `flat_v2_reloc_t`, a union exposing the raw 32-bit relocation value or endian-dependent bitfields for offset and type.

## State and dependencies
There is no runtime state. The header encodes on-disk ABI and depends on endian bitfield configuration and fixed-width big-endian integer types.

## Integration, risks, and tests
The binary-format loader and no-MMU exec path consume this format. Risks include endian conversion bugs, accepting unsupported old-format enhancements, relocation bitfield layout mismatch, malformed offsets/counts, and compressed payload bounds errors in loader code. Tests should parse known flat binaries, reject bad magic/version, verify big-endian field decoding on both endian builds, exercise v2 relocation interpretation, and validate flags combinations for XIP and compressed data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/flat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/flex_proportions.h -->
# sources/distributed-fs/ceph-client/include/linux/flex_proportions.h

## Purpose
This header defines flexible aging-period proportion counters. It lets subsystems track a local event class as a fraction of a global event stream while periods advance and old counts decay.

## APIs, types, and control flow
`struct fprop_global` owns a per-cpu global event counter, current period, and sequence counter for period transitions. `struct fprop_local_percpu` owns a local per-cpu event counter, last-updated period, and raw spinlock protecting period/numerator updates. Initialization and teardown are split for global and local counters. `fprop_new_period()` advances aging periods. `__fprop_add_percpu()` and `_max()` add local/global events, with the max variant limiting by `FPROP_FRAC_SHIFT` precision. `fprop_fraction_percpu()` returns numerator/denominator. `fprop_inc_percpu()` wraps add-one with IRQ disable/restore.

## State and dependencies
State persists in percpu counters and period fields. Dependencies are percpu counters, spinlocks, seqcount, and GFP allocation.

## Integration, risks, and tests
Used by writeback and resource-balancing code that needs low-overhead approximate proportions. Risks include missing local destruction, period races if sequence handling is wrong in implementation, IRQ-context misuse outside the wrapper, and overflow/precision limits documented by `FPROP_FRAC_SHIFT`. Tests should cover init failure cleanup, period advancement, fraction monotonicity/decay, max-fraction limiting, concurrent increments, and teardown after active periods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/flex_proportions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/folio_batch.h -->
# sources/distributed-fs/ceph-client/include/linux/folio_batch.h

## Purpose
This header defines a compact fixed-size batch of folio pointers used to amortize page-cache and memory-management operations.

## APIs, types, and control flow
`FOLIO_BATCH_SIZE` is 31, leaving room for the header while keeping the object power-of-two aligned. `struct folio_batch` stores count `nr`, iterator index `i`, a `percpu_pvec_drained` flag, and the folio array. `folio_batch_init()` resets all counters and drain flag; `folio_batch_reinit()` resets count/index only. Helpers report count and free space. `folio_batch_add()` appends without internal bounds checking and returns remaining slots. `folio_batch_next()` consumes entries in insertion order. `folio_batch_release()` calls `__folio_batch_release()` only when non-empty, and `folio_batch_remove_exceptionals()` removes exceptional entries.

## State and dependencies
State is caller-owned stack or heap storage. The batch does not own folios semantically but release helpers may drop references as implemented elsewhere.

## Integration, risks, and tests
Callers include page cache, LRU, delete, and writeback paths. Risks include overfilling when callers ignore returned space, reusing without reinit, ordering bugs for operations where order matters, and mixing exceptional entries without cleanup. Tests should cover init/reinit, add capacity, iteration exhaustion, release on empty/non-empty batches, and exceptional-entry removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/folio_batch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/folio_queue.h -->
# sources/distributed-fs/ceph-client/include/linux/folio_queue.h

## Purpose
This header defines a segmented queue of folios for running buffers and `ITER_FOLIOQ` users. It extends `folio_batch` with linked queue segments, per-slot order metadata, and two mark bitmaps.

## APIs, types, and control flow
`struct folio_queue` contains a `folio_batch`, `orders[]`, explicit `next`/`prev` links, two `unsigned long` mark fields, request/debug ids, and a compile-time check that one word can cover all slots. `folioq_init()` resets links, marks, ids, and batch state. Capacity/count/full helpers operate on the embedded batch. Mark helpers test/set/clear first and second bitmaps. `folioq_append()` and `folioq_append_mark()` append a folio, store its `folio_order()`, and optionally set the first mark. Accessors retrieve the folio, order, and size. `folioq_clear()` nulls a slot and clears marks without decreasing occupancy.

## State and dependencies
State is per segment, often chained by producer/consumer code that can add at tail and remove at head without list-head locking. It depends on folio APIs, `PAGE_SIZE`, bit operations, and `folio_batch`.

## Integration, risks, and tests
Netfs, buffered IO, and iterator code can use these queues. Risks are no bounds checks on slot access/append, occupancy not decreasing after clear, stale orders for cleared slots, and lockless link assumptions. Tests should cover segment init, append/full behavior, mark independence, clear semantics, multi-segment traversal, and invalid slot handling under debug instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/folio_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/font.h -->
# sources/distributed-fs/ceph-client/include/linux/font.h

## Purpose
This header defines kernel soft-font metadata, reference-counted font data helpers, glyph sizing helpers, rotation helpers, and declarations for built-in console fonts.

## APIs, types, and control flow
`font_glyph_pitch(width)` rounds bits per scanline to bytes, and `font_glyph_size(width, vpitch)` multiplies pitch by scanlines. `font_data_t` is an opaque raw glyph pointer with a hidden negative-offset header for optional CRC32, byte count, and refcount. Helpers import/export console fonts, get/put references, query size, compare data, and expose read-only raw bytes with `font_data_buf()`. Rotation helpers transform individual glyphs or full font data by 90/180/270 degrees. `struct font_desc` describes built-in fonts by id, name, geometry, character count, data, and preference. `find_font()` and `get_default_font()` select fonts.

## State and dependencies
Font data owns hidden metadata and refcount state. Built-in font descriptors are extern constants. Dependencies include console font structures, math helpers, CRC callback supplied by import, and video/console consumers.

## Integration, risks, and tests
Console, framebuffer, DRM console, and font loading paths use this interface. Risks include treating `font_data_t *` as a plain allocation, bad vertical pitch, refcount imbalance, CRC mismatch, rotation buffer sizing errors, and width/pitch confusion. Tests should cover glyph pitch for non-byte widths, import/export round trips, refcount put-to-zero behavior, equality checks, all rotations, default font selection, and malformed userspace font geometry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/font.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fortify-string.h -->
# sources/distributed-fs/ceph-client/include/linux/fortify-string.h

## Purpose
This header implements Linux `FORTIFY_SOURCE` wrappers for common string and memory functions. It adds compile-time and runtime object-size checking while preserving sanitizer-aware underlying calls.

## APIs, types, and control flow
It defines fortify function ids, read/write reasons, panic/report hooks, compile-time overflow diagnostics, and object-size helper attributes (`POS`, `POS0`). Sanitizer branches map underlying `memcpy`, `memmove`, `memset`, string, and memory-search calls to builtins or ASAN/HWASAN/KMSAN implementations. Fortified wrappers cover `strncpy`, `strnlen`, `strlen`, `sized_strscpy`, `strlcat`, `strcat`, `strncat`, `memset`, `memcpy`, `memmove`, `memscan`, `memcmp`, `memchr`, `memchr_inv`, `kmemdup`, and `strcpy`. Control flow generally captures compile-time/dynamic object sizes, emits compile-time errors/warnings for constant violations, calls `fortify_panic()` for runtime overflows, then delegates to the underlying operation. `unsafe_memcpy()` intentionally bypasses checks but requires a justification argument.

## State and dependencies
No persistent state is stored here. Behavior depends heavily on compiler object-size support, sanitizer configuration, KUnit override hooks, warning level, and allocation hooks for `kmemdup`.

## Integration, risks, and tests
This header is globally sensitive because it macro-redefines core functions. Risks include false positives with flexible arrays, missing checks for unknown dynamic sizes, field-spanning copies that should use `struct_group()`, sanitizer aliasing mistakes, and hiding real bugs behind `unsafe_memcpy`. Tests should include KUnit panic/warn overrides, compile-fail overflow cases, runtime overflow detection, sanitizer builds, flexible-array cases, and return-value preservation on panic paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fortify-string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fpga/altera-pr-ip-core.h -->
# sources/distributed-fs/ceph-client/include/linux/fpga/altera-pr-ip-core.h

## Purpose
This small header exposes registration for the Altera/Intel Partial Reconfiguration IP core driver.

## APIs, types, and control flow
`alt_pr_register(struct device *dev, void __iomem *reg_base)` registers an FPGA manager or related partial-reconfiguration provider backed by memory-mapped IP registers. The caller supplies the owning device and an already mapped register base.

## State and dependencies
All state is implementation-owned after registration, likely tied to the device and register base. The header depends on `linux/io.h` for `__iomem` annotations and device declarations through included kernel headers.

## Integration, risks, and tests
Platform drivers for Altera partial reconfiguration use this as a helper to bind the IP core into the FPGA framework. Risks include passing an unmapped or wrongly sized register window, registering before clock/reset readiness, and failing to unregister through devm or remove paths if the implementation requires it. Tests should cover probe failure cleanup, MMIO access error paths, partial bitstream load through the resulting manager, and static analysis for `__iomem` misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fpga/altera-pr-ip-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fpga/fpga-bridge.h -->
# sources/distributed-fs/ceph-client/include/linux/fpga/fpga-bridge.h

## Purpose
This header defines FPGA bridge devices, operations, registration, lookup, and list helpers. Bridges gate traffic between the processor system and FPGA fabric during reconfiguration.

## APIs, types, and control flow
`struct fpga_bridge_ops` provides status, enable/disable, remove-state, and optional sysfs groups. `struct fpga_bridge_info` is the stable registration input. `struct fpga_bridge` embeds a device, mutex, ops owner, image info pointer, list node, and private data. Consumers get bridges by device or OF node, enable/disable individual bridges, aggregate them into lists, enable/disable/put lists, and register/unregister providers through module-owner-wrapped macros.

## State and dependencies
Bridge state includes exclusive-reference mutex, module ownership, associated `fpga_image_info`, and low-level private data. It depends on the FPGA manager image-info type, device tree, lists, modules, and device core lifetime.

## Integration, risks, and tests
FPGA regions coordinate bridges with manager loads: disable bridges, program fabric, then re-enable. Risks are unbalanced get/put, enabling traffic before programming completes, module removal while ops are active, and partial list failure rollback. Tests should cover individual enable/disable, bridge list rollback on failure, OF lookup, unregister with active refs, sysfs attribute exposure, and timeout handling from image info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fpga/fpga-bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fpga/fpga-mgr.h -->
# sources/distributed-fs/ceph-client/include/linux/fpga/fpga-mgr.h

## Purpose
This header defines the FPGA manager framework interface. Managers own the programming sequence and state machine for loading bitstreams into FPGA hardware.

## APIs, types, and control flow
`enum fpga_mgr_states` describes power, request, parse, write, complete, error, and operating states. Image flags select partial/external/encrypted/LSB-first/compressed bitstreams. `struct fpga_image_info` carries firmware name, scatterlist or buffer, sizes, header/data split, timeouts, region id, device, and optional overlay. `struct fpga_manager_ops` provides state/status, parse header, write init, contiguous/scatter write, write complete, remove, and sysfs groups. `fpga_mgr_load()` runs the load sequence: request/parse/init/write/complete, using ops and updating state. Registration APIs include normal, full, and devm variants with module-owner wrappers.

## State and dependencies
`struct fpga_manager` embeds a device, reference mutex, current state, compatibility id, ops/module owner, and private data. Dependencies include platform/device core, mutexes, scatter-gather tables, firmware loading, and module lifetime.

## Integration, risks, and tests
FPGA regions and low-level platform drivers rely on this API. Risks include inconsistent state transitions, missing `write_sg` or `write` handling, header size/data size confusion, timeout misuse, incompatible images, and module unload during programming. Tests should cover registration/devm cleanup, full and partial loads, parse-header `-EAGAIN`, buffer vs scatter input, status error bits, lock exclusion, and remove-state callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fpga/fpga-mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fpga/fpga-region.h -->
# sources/distributed-fs/ceph-client/include/linux/fpga/fpga-region.h

## Purpose
This header defines FPGA regions, which coordinate a manager, compatibility id, image info, and bridge list for programming a portion of FPGA fabric.

## APIs, types, and control flow
`struct fpga_region_info` supplies a manager, optional compatibility id/private data, and optional `get_bridges()` callback. `struct fpga_region` embeds a device, mutex, bridge list, manager, image info, compatibility id, module owner, private data, and callback. `fpga_region_program_fpga()` is the orchestration entry point: it gathers/uses bridges, coordinates manager programming, and restores traffic. Registration APIs include full and compact macros that capture `THIS_MODULE`, plus class search and unregister.

## State and dependencies
Region state ties together bridge references, selected manager, image info, and exclusive region mutex. It depends on FPGA manager and bridge frameworks, device core, lists, modules, and optionally device tree/overlays through image info.

## Integration, risks, and tests
Regions are the policy layer for dynamic FPGA reconfiguration. Risks include programming with stale image info, bridge leaks on failure, compatibility-id mismatch, concurrent region programming, and module-owner lifetime bugs for `get_bridges`. Tests should cover registration/unregistration, class find matching, bridge acquisition failure rollback, successful program ordering, manager-load errors, and concurrent program exclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fpga/fpga-region.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fprobe.h -->
# sources/distributed-fs/ceph-client/include/linux/fprobe.h

## Purpose
This header defines `fprobe`, a simple ftrace-based function entry/exit probe wrapper, with optional sharing for kprobes.

## APIs, types, and control flow
Entry callbacks return `int` and receive the probe, entry IP, return IP, ftrace registers, and per-entry data. Exit callbacks receive the same context and entry data. `struct fprobe_hlist_node` and `struct fprobe_hlist` support address-based hash lookup with RCU-deferred release. `struct fprobe` tracks missed events, flags, entry data size, callbacks, and hash-list array. Registration can be by ftrace filter strings, raw IPs, or symbol names; unregister can be synchronous or async. With `CONFIG_FPROBE` disabled, all operations return `-EOPNOTSUPP` or false. Inline helpers soft-disable/enable probes and test shared/disabled flags.

## State and dependencies
State includes registered ftrace hooks, hash tables, RCU lifetime, missed counters, and optional per-entry data bounded by `MAX_FPROBE_DATA_SIZE`. Dependencies include ftrace, RCU, refcounting, rhashtable, and slab allocation.

## Integration, risks, and tests
Tracing, profiling, and dynamic instrumentation use this layer. Risks include unregister races with callbacks, excessive entry data, probing invalid or duplicate addresses, missed-event accounting, and flag mutation without synchronization. Tests should cover filter/IP/symbol registration, disabled stubs, soft disable/enable, async unregister lifetime, entry/exit data passing, and max data-size rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fprobe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fpu.h -->
# sources/distributed-fs/ceph-client/include/linux/fpu.h

## Purpose
This header is the generic gate for architecture FPU support in kernel code.

## APIs, types, and control flow
It deliberately rejects inclusion from a compilation unit that defines `_LINUX_FPU_COMPILATION_UNIT`, emitting an error that floating-point code must be compiled separately. Otherwise it includes `<asm/fpu.h>`, making architecture-specific FPU save/restore or kernel-mode FPU helpers available.

## State and dependencies
No state is defined here. All behavior and state live in architecture-specific `asm/fpu.h` code and the build-system discipline around isolated floating-point compilation units.

## Integration, risks, and tests
Kernel code generally avoids FPU use; consumers must follow `Documentation/core-api/floating-point.rst` and architecture rules. Risks include accidental FPU instructions in normal kernel objects, missing preemption/context handling, and architecture mismatch. Test signals are compile-time enforcement for marked FPU units, architecture build coverage, static checks for unintended floating-point code, and runtime tests around any subsystem that explicitly enters/leaves kernel FPU context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/framer/framer-provider.h -->
# sources/distributed-fs/ceph-client/include/linux/framer/framer-provider.h

## Purpose
This header defines the provider-side API for the generic framer framework. Framer providers create framer devices, expose operations, register OF providers, and notify status changes.

## APIs, types, and control flow
`struct framer_ops` supplies init/exit, power on/off, optional get-status, set-config, get-config, flags, and owner. `FRAMER_FLAG_POLL_STATUS` asks the core to poll `get_status()` and notify consumers on change if hardware cannot interrupt. `struct framer_provider` stores provider device, module owner, list node, and `of_xlate()` callback. Provider helpers create/destroy framers, devm-create, simple OF translate, register/unregister providers, and notify status changes. When `CONFIG_GENERIC_FRAMER` is disabled, creation/register calls return `ERR_PTR(-ENOSYS)` and notification/destruction are no-ops.

## State and dependencies
Provider state includes registered provider list entries, module ownership, framer device private data via `framer_set_drvdata()`, and optional polling work managed by the core. Dependencies include the consumer `framer.h`, device tree phandles, modules, lists, and error-pointer conventions.

## Integration, risks, and tests
Hardware framer drivers implement this side. Risks include provider unregister while consumers hold framers, missing owner assignment, polling without `get_status`, failing to notify status changes, and disabled-config `ERR_PTR` handling. Tests should cover create/destroy, devm cleanup, OF translation, provider unregister, polling flag behavior, notifier delivery, and disabled stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/framer/framer-provider.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/framer/framer.h -->
# sources/distributed-fs/ceph-client/include/linux/framer/framer.h

## Purpose
This header defines the consumer-facing generic framer API for telecom line framers, including configuration, status, power/runtime PM, notifier registration, and device lookup.

## APIs, types, and control flow
Enums describe E1/T1 interfaces and external/internal clocks. `struct framer_config` carries interface, clock type, and line clock rate. `struct framer_status` reports link state, and `FRAMER_EVENT_STATUS` identifies status notifications. `struct framer` embeds a device, id, ops pointer, mutex, init/power reference counts, regulator, work for notifications, blocking notifier list, delayed polling work, and previous status. Consumer calls get a framer, initialize it, power it on, set/get config, read status, register notifiers, then power off/exit and put. With `CONFIG_GENERIC_FRAMER` disabled, operations return `-ENOSYS`, get returns `ERR_PTR(-ENOSYS)`, and optional devm get returns `NULL`.

## State and dependencies
State is shared by multiple consumers through init and power refcounts protected by the framer mutex. Dependencies include device core, OF, mutexes, regulators, workqueues, and blocking notifiers.

## Integration, risks, and tests
Line interface consumers, network/HDLC drivers, and provider drivers use this API. Risks include unbalanced init/power counts, notifier callbacks after put, optional-get handling, PM runtime mismatch, and config/status calls before init. Tests should cover refcounted init/power sequencing, optional absent framer, notifier registration/unregistration, polling status changes, runtime PM errors, and disabled stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/framer/framer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/framer/pef2256.h -->
# sources/distributed-fs/ceph-client/include/linux/framer/pef2256.h

## Purpose
This header exposes a small consumer API for Infineon/Siemens PEF2256 framer devices.

## APIs, types, and control flow
It forward-declares `struct pef2256` and `struct regmap`. `pef2256_get_regmap()` returns the device regmap for consumers that need direct register access. `enum pef2256_version` distinguishes unknown, 1.2, 2.1, and 2.2 hardware revisions. `pef2256_get_version()` returns the detected hardware version.

## State and dependencies
Device state is opaque and owned by the PEF2256 driver. The regmap is shared state and must obey regmap locking/lifetime rules. Dependencies are limited to types and the regmap subsystem.

## Integration, risks, and tests
Board or line-interface drivers can query version-specific behavior or access registers. Risks include using a regmap after the device is removed, bypassing higher-level framer abstractions, incorrect version-specific register programming, and failing to handle `PEF2256_VERSION_UNKNOWN`. Tests should cover version detection, regmap lifetime with consumer references, unsupported-version fallback, and register access error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/framer/pef2256.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/freezer.h -->
# sources/distributed-fs/ceph-client/include/linux/freezer.h

## Purpose
This header declares the kernel freezer API used by suspend/hibernate and cgroup v1 freezer interactions. It lets tasks observe freeze requests, enter the refrigerator, and thaw.

## APIs, types, and control flow
With `CONFIG_FREEZER`, global state includes `freezer_active`, `pm_freezing`, `pm_nosig_freezing`, and `freeze_timeout_msecs`. `freezing()` uses a static branch before calling `freezing_slow_path()`. `try_to_freeze()` may sleep, returns false when no freeze is pending, checks locks for normal freezable tasks, and calls `__refrigerator(false)`. APIs freeze/thaw user processes and kernel threads, freeze/thaw individual tasks, set current task freezable, and query cgroup v1 freezing. Without freezer support, predicates return false, freeze calls return `-ENOSYS`, and thaw calls no-op.

## State and dependencies
State spans task flags, PM freezer globals, static keys, wait queues, atomics, and cgroup v1 freezer if enabled. It deliberately notes that cgroup v2 freezer uses job control and does not interact with PM freezer.

## Integration, risks, and tests
Drivers and kernel threads must call `try_to_freeze()` at safe sleep points. Risks include freezer deadlocks from held locks, tasks marked `PF_NOFREEZE`, timeout failures, cgroup v1/v2 semantic confusion, and assuming freezer exists in disabled builds. Tests should cover suspend freeze/thaw, kernel thread cooperation, no-locks-held warnings, cgroup v1 freezing, disabled stubs, and timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/freezer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fs.h -->
# sources/distributed-fs/ceph-client/include/linux/fs.h

## Purpose
This header is the central VFS contract for Linux filesystem, inode, file, address-space, permission, writeback, mount, direct-I/O, mmap, and simple filesystem helpers. It defines the object model and function tables that real filesystems, stacked filesystems, character/block devices, and generic VFS code share.

## APIs, types, and control flow
Major objects include `struct inode`, `struct file`, `struct address_space`, `struct kiocb`, `struct file_ra_state`, `struct file_system_type`, `struct file_operations`, `struct inode_operations`, and `struct address_space_operations`. Important flows are: open creates a `struct file` with `f_mode`, `f_op`, path, credentials, mapping, refcount, and position state; reads/writes pass through VFS helpers to file operations and `kiocb` flags; page-cache operations call address-space ops for read, writeback, direct IO, migration, swap, and invalidation; inode operations implement lookup, create, unlink, rename, getattr/setattr, ACLs, tmpfile, xattrs, and directory offset contexts. Helper layers cover idmapped ownership translation, timestamp access/update including multigrain ctime, inode state helpers, i_size ordering, mmap compatibility between old `mmap` and new `mmap_prepare`, write-freeze protection, write denial for executables, fasync ownership, name acquisition, char-device registration, simple filesystem operations, directory emit helpers, and RWF-to-IOCB validation.

## State and persistence
Persistent runtime state is extensive: inode dirty/lifetime flags, link counts, ownership, size, timestamps, locks, write/read/direct-IO counts, mapping page-cache xarray, mmap trees, writeback errors, file credentials/path/position/refcount, superblock/filesystem registrations, and per-mount idmaps. Synchronization relies on inode `i_lock`, `i_rwsem`, address-space invalidate and mmap locks, atomics, seqcounts, RCU, module refs, superblock freeze writers, and lockdep subclasses.

## Dependencies and integration points
The header pulls in dcache, path, mount, superblock, mm, credentials, idmaps, xarray/maple tree, workqueues, unicode, block, security, fsnotify, fanotify, DAX, IMA, file locking, and uapi flags. It is consumed by nearly every filesystem and by subsystems such as block devices, overlay/backing files, proc/sys/debugfs-style simple files, io_uring, AIO, mmap, writeback, freeze/thaw, and permission/security hooks.

## Risks and test signals
Risks include lock-order violations, unbalanced file/inode references, stale idmapped uid/gid translation, i_size races on 32-bit, incorrect dirty-state transitions, writeback error loss, RWF flag acceptance without filesystem support, direct-IO/writeback races, freeze protection leaks, backing-file path confusion, incorrect mmap hook combinations, and simple helper misuse outside their assumptions. Tests should cover VFS xfstests, lockdep/KCSAN, idmapped mount ownership changes, lazytime/multigrain timestamp behavior, O_DIRECT and buffered fallback, `RWF_NOWAIT/ATOMIC/DONTCACHE` validation, file range clone/dedupe, fsnotify suppression modes, executable write denial, char-device registration, simple filesystem create/remove/rename, and disabled optional subsystems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fs.h -->
