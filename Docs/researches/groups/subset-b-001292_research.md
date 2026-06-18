# subset-b-001292 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/ti_sci.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/ti_sci.c

## Purpose
`ti_sci.c` is the Linux platform driver and exported client API implementation for Texas Instruments System Control Interface firmware. It turns kernel subsystems and child drivers' device, clock, resource-management, interrupt-routing, DMA, processor-control, reboot, and low-power requests into TI SCI mailbox messages, waits for firmware acknowledgements when required, and publishes a `struct ti_sci_handle` populated with operation tables. The driver is central firmware glue for TI K2G/AM65x-style SoCs: probe establishes mailbox channels, queries firmware revision/capability state, registers reboot and system-off handlers, and exposes child devices via `of_platform_populate()`.

## Important APIs, types, and functions
The main private state is `struct ti_sci_info`, containing the device, SoC descriptor, mailbox client/channels, transfer pool, exported handle, host id, firmware capability bits, debugfs state, and global-list usage count. `struct ti_sci_xfer` represents one message transaction and reuses the same preallocated buffer for TX and RX. `struct ti_sci_xfers_info` owns the bounded transfer pool with a semaphore, allocation bitmap, and spinlock. `struct ti_sci_desc` supplies per-compatible default host id, timeout, max in-flight messages, and max message size.

The low-level transaction path is `ti_sci_get_one_xfer()` -> request struct fill -> `ti_sci_do_xfer()` -> `ti_sci_rx_callback()` -> `ti_sci_put_one_xfer()`. `ti_sci_get_one_xfer()` validates sizes against `desc->max_msg_size`, reserves one sequence id from the bitmap, initializes the common header, sets RX expectations, and arms a completion. `ti_sci_do_xfer()` sends through the mailbox framework and waits for completion, using normal completion waits while the system is running and atomic polling in late shutdown/noirq states. `ti_sci_rx_callback()` validates the sequence id and length, copies the firmware response into the transfer buffer, and completes the waiter. `ti_sci_is_response_ack()` centralizes ACK/NACK flag interpretation.

Protocol operation implementations cover device state (`ti_sci_set_device_state()`, `ti_sci_get_device_state()`, `ti_sci_cmd_get_device()`, `ti_sci_cmd_put_device()`, reset state helpers), clock state/parent/frequency (`ti_sci_set_clock_state()`, `ti_sci_cmd_clk_*()`), low power (`ti_sci_cmd_prepare_sleep()`, `ti_sci_msg_cmd_query_fw_caps()`, `ti_sci_cmd_set_io_isolation()`, wake reason and constraint helpers), resource ranges (`ti_sci_get_resource_range()`), IRQ/event routing (`ti_sci_manage_irq()` and set/free wrappers), NAVSS ring/PSI-L/UDMAP configuration, and processor control (`ti_sci_cmd_proc_*()`). `ti_sci_setup_ops()` binds these concrete functions into `info->handle.ops`.

The exported client entry points are `ti_sci_get_handle()`, `ti_sci_put_handle()`, managed variants, phandle lookup variants, `ti_sci_get_free_resource()`, `ti_sci_release_resource()`, `ti_sci_get_num_resources()`, `devm_ti_sci_get_of_resource()`, and `devm_ti_sci_get_resource()`.

## Control flow and integration
Probe allocates `ti_sci_info`, reads `ti,host-id` or uses descriptor defaults, preallocates the transfer pool and per-transfer buffers, optionally maps a `debug_messages` resource for debugfs, requests RX/TX mailbox channels by name, sends `TI_SCI_MSG_VERSION`, queries firmware capabilities, installs the operation table, registers restart/sys-off handlers, logs ABI details, adds the instance to the global list, and populates DT children.

Client lookup is DT-centric. `ti_sci_get_handle()` compares the requesting device's parent node with registered TI SCI device nodes. `ti_sci_get_by_phandle()` resolves an explicit phandle. Both increment `info->users` under `ti_sci_list_mutex`; `ti_sci_put_handle()` decrements it. Managed variants attach release actions to devres.

Power-management flow is capability-gated. Suspend sends latency constraints derived from CPU PM QoS when DM-managed LPM is available, maps `PM_SUSPEND_MEM` to `TISCI_MSG_VALUE_SLEEP_MODE_DM_MANAGED`, enables IO isolation during noirq suspend if supported, disables it on resume, queries wake reason on resume, and issues LPM abort in complete when supported. System-off checks wakeup-source phandles for an `off-wake` idle state and uses Partial-IO prepare-sleep before emergency restart if a wake-enabled device is present.

## State and persistence behavior
Persistent in-kernel state is limited to the driver instance, the global `ti_sci_list`, client `users`, firmware capability cache, version info in the exported handle, debug buffer, and resource allocation bitmaps. Resource objects returned by `devm_ti_sci_get_resource*()` maintain per-client allocation bitmaps guarded by a raw spinlock; the firmware resource assignment itself is queried but not persisted by this driver. Device/clock/power/IRQ/UDMAP/proc state lives in firmware and is changed by messages. Debugfs reads copy a firmware-provided memory region on demand and do not store historical logs.

## Dependencies and integration points
This file depends on the mailbox framework, TI message manager mailbox message format, DT/of_platform, debugfs, PM QoS and suspend state, reboot/sys-off registration, TI SCI protocol public headers, and the private message definitions in `ti_sci.h`. It integrates with clock, reset, power-domain, DMA/ringacc, interrupt, remoteproc, and platform child drivers through `linux/soc/ti/ti_sci_protocol.h` operation tables.

## Risks and test signals
Important risks are protocol struct layout drift versus firmware ABI, incorrect message-size limits, mailbox timeout handling, sequence-id corruption, using response buffers before ACK validation, and unbalanced handle/resource usage by clients. There is also a subtle dependency on noirq-safe polling during late suspend/shutdown. Test signals include successful probe with ABI log, child device population, clock/device power APIs succeeding under client drivers, IRQ/event routing on NAVSS devices, suspend/resume with IO isolation and wake-reason logs, reboot/sys-off behavior, debugfs log reads when a debug region exists, and error-path coverage for mailbox timeouts/NACKs/resource exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/ti_sci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/ti_sci.h -->
# sources/distributed-fs/ceph-client/drivers/firmware/ti_sci.h

## Purpose
`ti_sci.h` is the private TI SCI wire-protocol schema used by `ti_sci.c`. It defines message IDs, generic header flags, request/response layouts, state constants, resource masks, and packed firmware ABI structures for generic, device, clock, low-power, resource-management, IRQ, NAVSS, UDMAP, and processor-control operations.

## Important APIs, types, and constants
The core type is `struct ti_sci_msg_hdr`, a packed header with message type, host id, sequence id, and request/response flags. All other protocol structures embed it first. Generic messages include firmware version, system reset, and capability query. Device messages model state transitions, reset bits, context-loss counts, programmed state, and current hardware state. Clock messages cover state, parent selection, parent count, frequency query, set, and get; they include the 8-bit `clk_id` plus `clk_id_32` escape path for IDs >= 255.

Low-power structs define prepare-sleep modes for Partial-IO and DM-managed suspend, IO isolation enable/disable, wake reason reporting, device constraints, and latency constraints. Resource-management structs define resource ranges, IRQ route management with validity bitmasks, ring configuration, PSI-L pair/unpair, UDMAP TX channel, RX channel, and RX flow configuration. Processor-control structs define request/release/handover, boot vector config, control flags, and status response.

## Control flow and integration
The header has no executable control flow, but its layout directly controls `ti_sci.c` message construction and response parsing. The driver allocates a transfer buffer, casts it to one of these request structs, fills fields, sends it through the mailbox, then casts the same buffer to a matching response struct. The common ACK/NACK semantics come from `TI_SCI_FLAG_RESP_GENERIC_ACK` in `struct ti_sci_msg_hdr`.

## State and persistence behavior
The file defines state values but stores none itself. Firmware-visible state represented here includes device software/hardware state, clock software/hardware state, firmware capability bits, resource ranges, low-power constraints, and processor boot/control/status flags. The `__packed` annotations are part of the persistence and compatibility contract because they keep C layout aligned with the firmware wire format.

## Dependencies and integration points
The header assumes kernel bit helpers such as `GENMASK()`/`GENMASK_ULL()` are available through including contexts. It is included by the TI SCI driver and complements public client-facing definitions in `linux/soc/ti/ti_sci_protocol.h`. Integration is ABI-sensitive: clients do not normally include this private header, but their public operation calls depend on these internal structs matching the firmware specification.

## Risks and test signals
The main risk is ABI drift: any field ordering, size, packing, message ID, flag, or mask error can silently break firmware communication. The 255 escape convention for clock parent/clock IDs is especially easy to mishandle. Test signals are build coverage for all structs referenced by `ti_sci.c`, successful firmware version/capability queries, ACK/NACK handling across message families, and hardware/firmware integration tests that exercise clock IDs and resource ranges near boundary values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/ti_sci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/trusted_foundations.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/trusted_foundations.c

## Purpose
`trusted_foundations.c` registers ARM firmware operations for NVIDIA/Tegra Trusted Foundations secure firmware. It provides secure monitor call wrappers for CPU boot address programming, idle low-power preparation, and optional secure L2X0 cache controller operations.

## Important APIs, types, and functions
The SMC primitive is `tf_generic_smc(type, arg1, arg2)`, which places arguments in ARM registers, preserves r4-r11, enables the `sec` architecture extension, and executes `smc #0`. `tf_set_cpu_boot_addr()` caches the boot address and sends `TF_SET_CPU_BOOT_ADDR_SMC`. `tf_prepare_idle()` maps Linux Trusted Foundations idle modes (`TF_PM_MODE_LP0`, `LP1`, `LP1_NO_MC_CLK`, `LP2`, `LP2_NOFLUSH_L2`) to firmware power commands and records `tf_idle_mode`.

When `CONFIG_CACHE_L2X0` is enabled, `tf_cache_write_sec()` handles secure writes to the L2X0 control register by issuing enable, re-enable, or disable SMCs. It derives the way mask from saved L2X0 auxiliary control and chooses `TF_CACHE_REENABLE` for LP2 resume. `tf_init_cache()` installs that hook into `outer_cache.write_sec`.

## Control flow and integration
`of_register_trusted_foundations()` looks for the `tlm,trusted-foundations` compatible node and requires `tlm,version-major` and `tlm,version-minor`; missing properties panic because firmware support was explicitly described but malformed. It then calls `register_trusted_foundations()`, which registers `trusted_foundations_ops` with the ARM firmware ops layer. `trusted_foundations_registered()` lets other code detect whether these ops are active.

## State and persistence behavior
The file maintains only two static variables: `tf_idle_mode`, used to adjust cache re-enable behavior, and `cpu_boot_addr`, reused by idle preparation SMCs. Actual CPU power, boot, and cache state is held by secure firmware and hardware.

## Dependencies and integration points
Dependencies include ARM firmware ops, ARM inline assembly/SMC support, DT, optional L2X0 cache support, and `linux/firmware/trusted_foundations.h`. It integrates with ARM CPU hotplug/suspend paths through `struct firmware_ops` and with outer-cache code through `outer_cache.write_sec`.

## Risks and test signals
Risks are architecture-specific inline assembly correctness, secure firmware availability, boot-address width/truncation on 32-bit paths, and panic-on-DT-malformation behavior. Cache operations are sensitive because incorrect way masks or idle mode tracking can corrupt L2 state. Test signals include DT registration, `firmware_ops` selection, CPU idle/suspend resume, secondary CPU boot, and L2X0 enable/disable paths on Trusted Foundations platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/trusted_foundations.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/turris-mox-rwtm.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/turris-mox-rwtm.c

## Purpose
`turris-mox-rwtm.c` is the platform firmware driver for the Turris MOX rWTM firmware mailbox. It exposes board manufacturing data through sysfs, registers a hardware RNG backed by firmware random generation, and optionally registers a Turris signing key that delegates ECDSA signing to firmware.

## Important APIs, types, and functions
`struct mox_rwtm` contains the mailbox client/channel, HWRNG descriptor, last reply, coherent 4 KiB DMA buffer and physical address, command mutex, completion, board info fields, MAC addresses, and optional public key. The mailbox command set includes random, board info, ECDSA public key, hash/sign/verify, and OTP operations. `mox_get_status()` validates that a reply matches the requested command and maps firmware status encodings to Linux errno values.

`mox_rwtm_exec()` is the common command executor. It fills the command id, sends a mailbox message, waits either interruptibly or with a half-second timeout, then decodes the reply. `mox_rwtm_rx_callback()` stores the reply and completes the command if one is pending. `mox_get_board_info()` reads serial, board version, RAM size, and two MAC addresses. `mox_hwrng_read()` serializes access with `busy`, requests random bytes into the DMA buffer, copies up to 4 KiB out, and supports nonblocking `-EBUSY` behavior.

When `CONFIG_TURRIS_MOX_RWTM_KEYCTL` is enabled, helpers convert firmware's 521-bit ECC number format to binary, read the board public key, create a `turris_signing_key` subtype, and implement `mox_rwtm_sign()` by placing a SHA-512 digest and signature output slots into the DMA buffer for firmware signing.

## Control flow and integration
Probe allocates private state and a coherent DMA buffer, initializes the mutex and completion, requests mailbox channel 0, registers a devm action to free it, reads board info, optionally registers the signing key, verifies random-generation support, registers the HWRNG, and creates `/sys/firmware/turris-mox-rwtm` as an ABI compatibility symlink. The device exposes read-only attributes for serial number, board version, RAM size, and MAC addresses via `dev_groups`; attributes return `-ENODATA` when board info was not burned.

## State and persistence behavior
The driver caches board info and public key in RAM after probe. The coherent DMA buffer is reused for random and signing commands and protected by the `busy` mutex for command paths that share it. Firmware owns persistent manufacturing data, OTP state, random generation, and private key material. The sysfs compatibility symlink is removed through a devm cleanup action.

## Dependencies and integration points
Dependencies include the Armada 37xx rWTM mailbox message ABI, mailbox framework, DMA coherent allocation, HWRNG framework, sysfs/firmware kobject, Ethernet address formatting, SHA-512 constants, and optional keyctl/Turris signing key support. Device matching supports both `cznic,turris-mox-rwtm` and `marvell,armada-3700-rwtm-firmware`.

## Risks and test signals
Risks include stale completions because `mox_rwtm_exec()` does not reinitialize `cmd_done` in the function body, command/reply mismatch handling, DMA buffer bounds, firmware errno mapping, and concurrent command users sharing one reply buffer. Signing paths are sensitive to endian conversion and 521-bit number offsets. Test signals include successful probe, board info sysfs reads, HWRNG registration and reads under blocking/nonblocking modes, unsupported-command handling, signing key creation on keyed boards, and mailbox timeout/error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/turris-mox-rwtm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/xilinx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/firmware/xilinx/Kconfig

## Purpose
This Kconfig fragment defines the configuration menu for Xilinx Zynq MPSoC firmware support. It controls whether the core ZynqMP firmware interface and its optional debugfs API surface are built.

## Important symbols
`ZYNQMP_FIRMWARE` is a boolean enabled under `ARCH_ZYNQMP`, defaults to yes for that architecture, and selects `MFD_CORE`. Its help text describes the firmware interface as the common platform-management service channel used by other drivers. `ZYNQMP_FIRMWARE_DEBUG` is a boolean depending on both `ZYNQMP_FIRMWARE` and `DEBUG_FS`; it enables debug APIs.

## Control flow and integration
Kconfig has declarative control flow. The enclosing menu is visible only for `ARCH_ZYNQMP`. The core symbol gates compilation of `zynqmp.o`, `zynqmp-ufs.o`, and `zynqmp-crypto.o` through the sibling Makefile, while the debug symbol gates `zynqmp-debug.o` and the inline stubs in `zynqmp-debug.h`.

## State and persistence behavior
No runtime state is stored here. The persistent effect is the kernel build configuration, which decides whether firmware APIs and debugfs controls exist in the image.

## Dependencies and integration points
The fragment integrates with the architecture selection, debugfs availability, and the MFD subsystem. Downstream drivers that call exported ZynqMP firmware APIs implicitly depend on this configuration being present.

## Risks and test signals
Risks are mostly build-configuration risks: disabling the core symbol removes exported firmware services needed by platform drivers, while enabling debug APIs exposes a privileged debugfs command path. Test signals include expected objects in build logs for each config combination, `CONFIG_ZYNQMP_FIRMWARE=y` on ZynqMP defconfigs, and absence of debug object/stubs mismatch when `DEBUG_FS=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/xilinx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/xilinx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/firmware/xilinx/Makefile

## Purpose
This Makefile maps Xilinx firmware Kconfig symbols to the objects compiled into the kernel. It is the build linkage for core ZynqMP firmware support, UFS helpers, crypto helpers, and optional debugfs support.

## Important rules
`obj-$(CONFIG_ZYNQMP_FIRMWARE) += zynqmp.o zynqmp-ufs.o zynqmp-crypto.o` builds the core firmware driver plus UFS and crypto extension files when the firmware interface is enabled. `obj-$(CONFIG_ZYNQMP_FIRMWARE_DEBUG) += zynqmp-debug.o` builds the debugfs command interface only when selected.

## Control flow and integration
The Makefile is declarative and follows standard kbuild `obj-*` expansion. It depends on `xilinx/Kconfig` for symbol selection and on public headers such as `linux/firmware/xlnx-zynqmp.h` for exported APIs used by these objects.

## State and persistence behavior
No runtime state exists here. Its persistent effect is object inclusion in the kernel build graph.

## Dependencies and integration points
The file integrates the firmware directory with kbuild. It assumes `zynqmp.o` exists as the core implementation that provides `zynqmp_pm_invoke_fn()` and register access helpers used by `zynqmp-ufs.o`, `zynqmp-crypto.o`, and `zynqmp-debug.o`.

## Risks and test signals
Risks include unresolved symbols if extension objects are built without the core implementation or if future files are added without matching Kconfig dependencies. Test signals are successful allmodconfig/allyesconfig builds, symbol export availability for UFS and crypto clients, and debug object inclusion only under `CONFIG_ZYNQMP_FIRMWARE_DEBUG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/xilinx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/xilinx/zynqmp-crypto.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/xilinx/zynqmp-crypto.c

## Purpose
`zynqmp-crypto.c` exports firmware-call wrappers for Xilinx/AMD secure crypto services. It lets kernel crypto/security clients invoke AES-GCM, SHA, platform-feature discovery, and Versal AES key/operation APIs through the ZynqMP firmware invocation layer.

## Important APIs and functions
`zynqmp_pm_aes_engine()` invokes `PM_SECURE_AES` with a physical address to an AES parameter structure and returns a firmware output word through `out`. `zynqmp_pm_sha_hash()` invokes `PM_SECURE_SHA` with address, size, and flags controlling init/update/final behavior. `xlnx_get_crypto_dev_data()` reads the platform family code, scans a caller-provided `struct xlnx_feature` table, checks feature availability with `zynqmp_pm_feature()`, and returns feature-specific data or an error pointer.

The Versal AES wrappers call XSecure API ids through the same `zynqmp_pm_invoke_fn()` transport: key write/zero, operation init, AAD update, encrypt update/final, decrypt update/final, and AES block init. All exported functions use `EXPORT_SYMBOL_GPL`.

## Control flow and integration
Each function is intentionally thin: validate required output pointer where applicable, split 64-bit addresses into lower/upper 32-bit arguments in the order required by the firmware API, invoke the PM function id, and return the firmware-layer status. The feature discovery helper adds a small table scan and returns `ERR_PTR()` on firmware or matching failure.

## State and persistence behavior
This file stores no driver-private state. Persistent crypto state, volatile keys, AES operation context, SHA engine state, and feature information are owned by firmware/hardware. Callers must provide DMA-safe buffers and manage operation sequencing.

## Dependencies and integration points
The file depends on `linux/firmware/xlnx-zynqmp.h` for API ids, `PAYLOAD_ARG_CNT`, feature structures, and `zynqmp_pm_invoke_fn()`. It integrates with downstream crypto drivers that need firmware-mediated secure operations and with platform-family/feature detection for selecting implementation data.

## Risks and test signals
Risks center on address argument ordering, DMA/cache coherency expectations, invalid caller buffers, firmware API availability by platform family, and minimal local validation. `zynqmp_pm_aes_engine()` writes `*out` even if the firmware call fails, so callers must check the return code before trusting it. Test signals include exported symbol resolution, secure AES/SHA known-answer tests, feature-table selection on each supported family, and negative tests for absent firmware features and null output pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/xilinx/zynqmp-crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/xilinx/zynqmp-debug.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/xilinx/zynqmp-debug.c

## Purpose
`zynqmp-debug.c` implements a debugfs interface for invoking selected ZynqMP firmware power-management APIs from userspace. It is a diagnostic and bring-up tool, not a normal production control plane.

## Important APIs, types, and functions
`struct pm_api_info` maps firmware API ids to symbolic names. `pm_api_list[]` enumerates supported operations such as powerdown, wakeup, request/release node, reset, chip ID, pinctrl, ioctl, clocks, and query data. `debugfs_buf` is a page-sized global response buffer exposed by reads. `zynqmp_pm_ioctl()` is a local wrapper for `PM_IOCTL`.

`get_pm_api_id()` resolves an API name prefix or decimal API id. `zynqmp_pm_argument_value()` parses each string argument as a u64, returning zero on missing or invalid input. `process_api_request()` dispatches the selected API id to the corresponding exported ZynqMP PM helper and formats selected return data into `debugfs_buf`. `zynqmp_pm_debugfs_api_write()` parses a single write buffer, extracts up to five arguments, dispatches the request, and returns either the write length or an errno. `zynqmp_pm_debugfs_api_read()` returns the current `debugfs_buf`.

## Control flow and integration
`zynqmp_pm_api_debugfs_init()` creates `/sys/kernel/debug/zynqmp-firmware/pm` with mode `0660`; writes trigger PM operations and reads retrieve the last formatted result. `zynqmp_pm_api_debugfs_exit()` removes the tree. The header `zynqmp-debug.h` makes these calls no-ops when debug support is not reachable, letting the core firmware driver call init/exit conditionally without preprocessor spread.

## State and persistence behavior
Runtime state is the debugfs root dentry and one global `debugfs_buf`. The buffer is overwritten on each write and read by any opener, so it is not per-file or per-caller state. Firmware and hardware own the actual power, reset, pinctrl, clock, and ioctl side effects triggered by commands.

## Dependencies and integration points
The file depends on debugfs, user-copy helpers, string parsing, and `linux/firmware/xlnx-zynqmp.h` PM APIs. It integrates with the core ZynqMP firmware driver via `zynqmp_pm_api_debugfs_init/exit()` and is built only under `CONFIG_ZYNQMP_FIRMWARE_DEBUG`.

## Risks and test signals
Risks are significant because debugfs writes can power down nodes, alter clocks, assert resets, change pinctrl, and issue IOCTLs. There is no locking around the global response buffer, parsing invalid numeric arguments silently as zero can issue unintended default operations, and name matching uses prefix length rather than token equality. Test signals include debugfs file creation/removal, successful `PM_GET_API_VERSION` and `PM_GET_CHIPID`, permission checks, concurrent read/write behavior, and negative tests for invalid API names, oversized writes, and firmware errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/xilinx/zynqmp-debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/xilinx/zynqmp-debug.h -->
# sources/distributed-fs/ceph-client/drivers/firmware/xilinx/zynqmp-debug.h

## Purpose
`zynqmp-debug.h` declares the ZynqMP firmware debugfs init/exit hooks and supplies no-op inline stubs when the debug object is not built or reachable.

## Important APIs
The exported internal hooks are `zynqmp_pm_api_debugfs_init()` and `zynqmp_pm_api_debugfs_exit()`. Under `IS_REACHABLE(CONFIG_ZYNQMP_FIRMWARE_DEBUG)` they are real functions implemented in `zynqmp-debug.c`; otherwise they are static inline empty functions.

## Control flow and integration
The header lets core firmware code call debug init/exit unconditionally while kbuild decides whether calls resolve to the real debugfs implementation or compile away. This keeps debug support optional without changing the call site.

## State and persistence behavior
The header stores no state. When debug support is enabled, state is owned by `zynqmp-debug.c`; when disabled, there are no side effects.

## Dependencies and integration points
It depends on Kconfig reachability for `CONFIG_ZYNQMP_FIRMWARE_DEBUG` and is included by ZynqMP firmware code that wants optional debugfs support.

## Risks and test signals
Risks are limited to configuration mismatch: using `IS_REACHABLE()` is important for built-in/module combinations. Test signals are successful builds with debug enabled and disabled, no unresolved symbols in modular configurations, and debugfs tree absence when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/xilinx/zynqmp-debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/xilinx/zynqmp-ufs.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/xilinx/zynqmp-ufs.c

## Purpose
`zynqmp-ufs.c` exports ZynqMP/Versal firmware helpers for UFS bring-up. It reads secure firmware-managed registers to check M-PHY and SRAM readiness, sets SRAM bypass control, and reads UFS calibration values from eFuse cache.

## Important APIs and functions
`zynqmp_pm_is_mphy_tx_rx_config_ready(bool *is_ready)` reads the PMC IOU SLCR TX/RX config-ready register and reports whether any readiness bits in `GENMASK(3,0)` are set. `zynqmp_pm_is_sram_init_done(bool *is_done)` reads the SRAM CSR and checks bit 0. `zynqmp_pm_set_sram_bypass()` reads SRAM CSR, clears external-load-done, sets bypass, and writes bits 2:1 back through `zynqmp_pm_sec_mask_write_reg()`. `zynqmp_pm_get_ufs_calibration_values(u32 *val)` reads the UFS calibration eFuse cache offset.

## Control flow and integration
All helpers are thin exported wrappers around secure register read or masked-write firmware APIs. They use hard-coded PM register node ids for PMC IOU SLCR and eFuse cache plus local offsets/masks. The boolean query helpers validate output pointers before firmware access.

## State and persistence behavior
The file stores no private state. It reads or modifies firmware-controlled hardware register state. `zynqmp_pm_set_sram_bypass()` has a persistent hardware side effect until changed by firmware/hardware reset or another control path.

## Dependencies and integration points
The file depends on `linux/firmware/xlnx-zynqmp.h` for secure register helpers and on module exports for UFS host/PHY drivers. It is built under `CONFIG_ZYNQMP_FIRMWARE` with the core firmware object.

## Risks and test signals
Risks include register-node/offset drift across SoCs, treating any TX/RX ready bit as ready rather than requiring all lanes, missing null validation in `zynqmp_pm_get_ufs_calibration_values()`, and side effects from masked SRAM writes. Test signals include exported symbol resolution by UFS drivers, successful secure register reads on supported platforms, expected behavior when firmware denies access, and UFS initialization paths observing readiness/calibration values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/xilinx/zynqmp-ufs.c -->
