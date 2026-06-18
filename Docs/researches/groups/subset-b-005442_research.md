# subset-b-005442 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/ctl.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/ctl.c

## Purpose

`ctl.c` implements the Thunderbolt control channel and the common configuration read/write/reset command helpers. It owns ring allocation, DMA-backed control-frame buffers, CRC conversion, outstanding request matching, synchronous and asynchronous request completion, hotplug/event dispatch, and error translation from Thunderbolt configuration errors to Linux errnos.

## Important APIs, Types, and Functions

The central private type is `struct tb_ctl`, which holds the NHI pointer, TX/RX rings, a DMA pool for frames, preposted RX packets, the outstanding request queue, default timeout, domain index, and the event callback installed by the domain. The public lifecycle APIs are `tb_ctl_alloc()`, `tb_ctl_start()`, `tb_ctl_stop()`, and `tb_ctl_free()`.

`tb_cfg_request_alloc/get/put()`, `tb_cfg_request()`, `tb_cfg_request_cancel()`, and `tb_cfg_request_sync()` manage refcounted `struct tb_cfg_request` objects. Standard command helpers include `tb_cfg_ack_notification()`, `tb_cfg_ack_plug()`, `tb_cfg_reset()`, `tb_cfg_read_raw()`, `tb_cfg_write_raw()`, `tb_cfg_read()`, `tb_cfg_write()`, and `tb_cfg_get_upstream_port()`.

Internal helpers such as `check_header()`, `check_config_address()`, `decode_error()`, `parse_header()`, `tb_cfg_print_error()`, `tb_ctl_tx()`, `tb_ctl_rx_callback()`, `tb_cfg_match()`, and `tb_cfg_copy()` provide packet validation, CRC handling, route/sequence matching, and result decoding.

## Control Flow

Allocation creates a coherent frame pool, a TX ring on control HopID 0, an RX ring with a small pool of preallocated receive packets, and initializes the request list. Starting the channel starts TX first, then RX, submits all RX packets, and marks the control channel running. Stopping clears `running`, stops RX/TX rings, warns if requests are still queued, and reinitializes the queue.

Transmit flow allocates a `ctl_pkg`, copies host-endian dwords to big endian, appends a CRC32C-derived checksum, assigns SOF/EOF to the package type, and queues the frame. The TX completion callback frees the package and DMA buffer.

Receive flow validates frame size, strips and verifies the checksum for normal packet classes, converts data to CPU endian, dispatches async errors and event/XDomain/ICM notifications to the domain callback, then tries to match the packet against active requests. A matching request copies the response, schedules completion work, and is later dequeued and refcount-released from `tb_cfg_request_work()`.

Synchronous requests queue an async request and wait on a completion. Timeout calls `tb_cfg_request_cancel()`, schedules the work item, waits until the request is inactive, stores the timeout error, then flushes the work before returning.

## State and Persistence Behavior

The file maintains volatile in-kernel state only. `struct tb_ctl` persists for the domain lifetime and owns rings, DMA pool, RX packet buffers, and outstanding request list. `struct tb_cfg_request` persists until its kref reaches zero; while queued it stores a back pointer to the control channel, request/response buffers, matching callbacks, and completion result.

No filesystem state is persisted. Hardware-visible side effects are real Thunderbolt control-channel operations: configuration reads and writes, reset packets, and event acknowledgments. Retried reads/writes use sequence values `0..3` and short sleeps between timeouts to avoid stale replies colliding with a new attempt.

## Dependencies and Integration Points

The file depends on NHI ring APIs (`tb_ring_alloc_*`, `tb_ring_start/stop/free`, `tb_ring_tx/rx`), DMA pools, workqueues, wait queues, mutexes, CRC32C, endian conversion helpers, Thunderbolt message structures from `tb_msgs.h`, and tracepoints from `trace.h`.

It is the transport used by higher-level switch, port, ICM, DMA-port, and domain code. Domain callbacks receive events through the `event_cb` function pointer. Config helpers are consumed throughout the Thunderbolt driver through `tb_sw_read/write()`, `tb_port_read/write()`, and lower-level safe-mode access paths.

## Risks and Edge Cases

The request cancellation path deliberately schedules the request work even if RX completion races with timeout. Correctness depends on the active flag, cancel flag, and kref serialization around request lookup. `tb_ctl_stop()` only warns about dangling requests and reinitializes the queue; callers must stop after outstanding work is drained or canceled.

`tb_cfg_match()` treats any error packet as a match. This ensures errors complete requests, but an unrelated asynchronous error must be filtered earlier by `tb_async_error()`. Unknown error packets may still terminate the first active request.

Raw read/write response sizes are derived from `length`; callers must respect maximum control packet payload size. `tb_ctl_tx()` rejects frames larger than `TB_FRAME_SIZE - 4`, but raw helper stack objects assume the message structs are large enough for the requested data.

`tb_ctl_start()` sets `running = true` after submitting RX frames without holding `request_queue_lock`. Enqueue checks are locked, but lifecycle callers rely on domain-level locking to serialize start/stop with request issuance.

## Test Signals

Useful tests include config read/write success, Thunderbolt error response mapping, timeout and retry behavior, stale reply after timeout, async event delivery, checksum mismatch drops, invalid frame size drops, stop during in-flight request, and request cancel races. Fault injection should cover DMA pool allocation failure, ring allocation failure, `tb_ring_tx()` failure, callback-initiated traffic, and suspended/runtime-resumed domain transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/ctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/ctl.h -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/ctl.h

## Purpose

`ctl.h` is the private interface for the Thunderbolt control channel and configuration command layer. It exposes the opaque `struct tb_ctl`, request lifecycle APIs, synchronous and asynchronous request helpers, packet result metadata, route header helpers, and standard configuration operations used by the rest of the driver.

## Important APIs, Types, and Functions

`event_cb` is the domain callback type for control-channel events. `struct tb_cfg_result` records the route and port that responded, whether the error was a Linux errno or a Thunderbolt configuration error, and the raw `enum tb_cfg_error` for Thunderbolt errors. `struct ctl_pkg` wraps a received or transmitted control packet with its DMA-backed `ring_frame`.

`struct tb_cfg_request` is the reusable request object. It stores request and response buffers, packet types, expected response size, multipacket count, matching/copy callbacks, completion callback, flags, work item, result, and queue linkage. `TB_CFG_REQUEST_ACTIVE` and `TB_CFG_REQUEST_CANCELED` define request state bits.

The header exports control lifecycle functions, request refcounting and cancellation functions, `tb_cfg_request_sync()`, route helpers `tb_cfg_get_route()` and `tb_cfg_make_header()`, event acknowledgment helpers, raw config read/write, translated config read/write, reset, and upstream-port discovery.

## Control Flow

Higher layers allocate a control channel with `tb_ctl_alloc()`, start it when the domain is ready, and stop/free it during suspend or teardown. Standard config operations allocate a `tb_cfg_request`, fill the packet metadata and callbacks, submit through `tb_cfg_request_sync()`, then release the request.

The header deliberately separates generic request transport from common configuration commands. Callers that need custom matching, such as ICM or DMA safe-mode mailbox access, can fill `struct tb_cfg_request` directly and still use the shared queue, timeout, and completion machinery.

## State and Persistence Behavior

This header defines volatile request and transport contracts. It does not define persistent storage. Persistence-like effects occur only through functions declared here when callers write router or port configuration space, reset devices, acknowledge hotplug notifications, or drive firmware mailboxes over the control channel.

`tb_cfg_make_header()` and `tb_cfg_get_route()` preserve route information across packet headers. The warning in `tb_cfg_make_header()` is important because route high bits are not a full 32-bit field in the wire header.

## Dependencies and Integration Points

The header depends on kernel krefs, Thunderbolt public types, NHI definitions, and message ABI structures from `tb_msgs.h`. It is included by the control-channel implementation, ICM firmware manager, DMA-port mailbox implementation, and other Thunderbolt files that need low-level config-space access.

Request matching and copy function pointers are the main extension point. They allow strict config packet validation for normal requests and relaxed validation for safe-mode DMA mailbox traffic or multipacket ICM responses.

## Risks and Edge Cases

Because `struct tb_cfg_request` stores pointers to caller-owned request and response buffers, those buffers must outlive the request until completion or cancellation is fully flushed. Synchronous helpers satisfy this with stack buffers and `tb_cfg_request_sync()`, but asynchronous users must manage lifetime carefully.

`response_size` and `npackets` are trusted by request-specific copy callbacks. Incorrect values can under-copy, over-copy, or cause unrelated packets to be accepted. Custom match functions must be strict enough to reject stale replies from timed-out requests.

The route helpers warn but do not fail on overflow. Callers should not ignore route construction warnings when adding new packet formats or wider route uses.

## Test Signals

Header-level validation should come from build coverage across all Thunderbolt objects, plus tests or static checks for request lifetime, callback signatures, route round trips, and packet size assumptions. Any changes to `struct tb_cfg_request` should be tested against normal config requests, ICM requests, DMA-port safe-mode requests, and asynchronous NVM authentication requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/ctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/debugfs.c

## Purpose

`debugfs.c` exposes Thunderbolt/USB4 diagnostic and debug controls under debugfs. It can dump switch, port, path, counter, sideband, retimer, DROM, and service state; optionally write raw config and sideband registers; and optionally drive USB4 lane margining operations for ports and retimers.

## Important APIs, Types, and Functions

Public entry points are `tb_debugfs_init/exit()`, `tb_switch_debugfs_init/remove()`, `tb_xdomain_debugfs_init/remove()`, `tb_service_debugfs_init/remove()`, and `tb_retimer_debugfs_init/remove()`.

Register helpers include `validate_and_copy_from_user()`, `parse_line()`, `regs_write()`, `port_regs_show()`, `switch_regs_show()`, `path_show()`, `counters_show()`, `counters_write()`, `sb_regs_show()`, `port_sb_regs_show()`, and `retimer_sb_regs_show()`. `port_sb_regs` and `retimer_sb_regs` enumerate USB4 sideband registers and their supported byte widths.

When `CONFIG_USB4_DEBUGFS_MARGINING` is enabled, `struct tb_margining` tracks lane margining capabilities, current settings, result buffers, lane selection, BER contour, software dwell time, error-counter mode, voltage/time mode, and Gen4 eye selection. Margining file operations expose `caps`, `lanes`, `mode`, `run`, `results`, `test`, `margin`, `eye`, and software-only tuning attributes.

## Control Flow

Initialization creates a global `thunderbolt` debugfs root. Each switch creates a directory named after the device, a switch `regs` file, an optional `drom` blob, and per-port directories for active ports. Port directories expose config registers, path tables, counters, sideband registers for USB4 ports, and optional margining files. Retimers get sideband and optional margining entries under a retimer-specific directory.

Show paths acquire runtime PM on the target device, take the domain mutex, read config or sideband registers, format data as offset-relative tables, then release the mutex and runtime PM reference. Write paths copy at most one page from userspace, parse one line at a time, taint the kernel for raw hardware writes, and write registers under the same runtime PM and domain lock.

Margining allocation reads link generation, asymmetric width capability, and USB4 margining capabilities, then creates only the files supported by the device. Running a margining operation validates lane settings, temporarily disables CL states on the downstream switch if present, clears prior results, executes software or hardware margining through USB4 helpers, restores CL states, and stores raw results for later reads.

## State and Persistence Behavior

The file keeps a global debugfs root and per-device dentries. It also stores `struct tb_margining` objects in USB4 port or retimer state while debugfs entries exist. Result arrays persist until the next margining run, explicit result clear, or device removal.

Most reads are observational, but writes can change live hardware configuration, clear counters, alter sideband registers, and run margining tests. These operations are not persisted by this file, but some hardware effects can persist until reset, link retraining, or firmware action. `add_taint(TAINT_USER)` marks raw user-triggered hardware writes.

## Dependencies and Integration Points

The file depends on debugfs, seq_file, uaccess, runtime PM, the Thunderbolt domain mutex, config-space helpers (`tb_sw_read/write`, `tb_port_read/write`), USB4 sideband helpers, USB4 margining helpers, CL-state helpers, retimer objects, XDomain objects, and DROM blobs populated by EEPROM/NVM code.

It integrates with switch/port discovery and removal through the public init/remove hooks. Service drivers such as `dma_test.c` create their own directories under service debugfs directories.

## Risks and Edge Cases

Raw debugfs write support is intentionally dangerous and compile-time gated. Misuse can desynchronize driver state from hardware; the taint marker documents that risk. The parser accepts only numeric fields in expected short or long formats and stops silently when lines no longer parse.

In `sb_regs_write()`, the size check uses `bytes_read > sb_regs->size` instead of `sb_reg->size`. Since `sb_regs` points to the first table element, writes to later registers may be checked against the first register's size, which is a bug signal for sideband write validation.

Several user-buffer handlers set `buf[count - 1] = '\0'` after copying a page-sized bounded buffer. Zero `count` is rejected by `validate_and_copy_from_user()`, so underflow is avoided, but inputs larger than one page are truncated.

Margining division uses capability-derived step counts. If firmware reports zero voltage or time steps, result formatting can divide by zero. Link state can change between allocation and run; `validate_margining()` rechecks RX2 asymmetric width but other capability assumptions remain cached.

## Test Signals

Tests should cover debugfs creation/removal for switches, ports, retimers, services, and XDomains; register table reads with partial access failures; raw write parsing under `CONFIG_USB4_DEBUGFS_WRITE`; counter clearing; sideband write size validation; runtime PM failure paths; and device removal while files are open.

Margining tests need hardware or mocked USB4 helpers for software/hardware modes, lane selection, RX2 asymmetry, Gen4 eye selection, CL disable/enable restoration, interrupted runs, result clearing, and unsupported capability combinations. Static analysis should flag the sideband size-check bug and any unchecked debugfs lookup references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/dma_port.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/dma_port.c

## Purpose

`dma_port.c` implements the DMA configuration based mailbox used to access switch flash/NVM and power operations through the NHI/DMA port. It is designed to work even when a switch is in safe mode, where normal validation and functionality are limited.

## Important APIs, Types, and Functions

`struct tb_dma_port` records the owning switch, NHI port number, mailbox capability base, and a temporary data buffer. Public APIs are `dma_port_alloc()`, `dma_port_free()`, `dma_port_flash_read()`, `dma_port_flash_write()`, `dma_port_flash_update_auth()`, `dma_port_flash_update_auth_status()`, and `dma_port_power_cycle()`.

Internal helpers include `dma_find_port()`, `dma_port_read()`, `dma_port_write()`, `dma_port_wait_for_completion()`, `dma_port_request()`, `dma_port_flash_read_block()`, `dma_port_flash_write_block()`, and `status_to_errno()`. The mailbox uses `MAIL_DATA`, `MAIL_IN`, and `MAIL_OUT` registers, with command/status bitfields for flash read, flash write, flash update authentication, and power cycle.

## Control Flow

Allocation probes candidate NHI ports 3, 5, and 7 by reading port type at config offset 2. If it finds `TB_TYPE_NHI`, it allocates a `tb_dma_port` and uses capability base `0x3e`.

Read and write helpers construct raw control-channel config packets using custom relaxed match/copy callbacks. They do not enforce the normal config-address validation because safe-mode switches expose only restricted behavior. Mailbox requests write a command to `MAIL_IN`, poll until `MAIL_IN_OP_REQUEST` clears, read `MAIL_OUT`, and convert status to errno.

Flash reads and writes are block oriented through `tb_nvm_read_data()` and `tb_nvm_write_data()`. A flash read submits a read command for a dword address and then reads up to 16 dwords from `MAIL_DATA`. A flash write writes the data block first, then submits a write command, using the CSS bit for the CSS magic address range.

Authentication and power-cycle operations submit short mailbox commands with a 150 ms completion wait. Authentication status is read later from `MAIL_OUT` because authenticating a root switch can reset the host controller before a normal synchronous result is observable.

## State and Persistence Behavior

The only kernel state is the allocated DMA-port object. Persistent hardware effects are significant: flash writes update the non-active NVM region, CSS writes update the authentication header area, update-auth can swap active/non-active firmware regions after validation, and power-cycle resets the switch.

`dma_port_flash_update_auth_status()` consumes no local state; it interprets the current mailbox output register and returns `1` when the last status belongs to the update-auth command. `dma_port_flash_write()` enforces `DMA_PORT_CSS_MAX_SIZE` for CSS writes but otherwise delegates alignment and retry handling to the NVM helpers.

## Dependencies and Integration Points

The file depends on `ctl.h` request transport, switch routing from `tb.h`, config-space definitions from `tb_regs.h`, delay/jiffies helpers, and NVM block helpers (`tb_nvm_read_data()` and `tb_nvm_write_data()`). EEPROM/DROM code uses it to copy host-router DROM from NVM when EFI data is unavailable.

It integrates with firmware update flows through NVM read/write/authenticate operations and with safe-mode recovery where the normal switch functionality is not available.

## Risks and Edge Cases

The relaxed response matching accepts packets by route/type/size only and does not verify sequence, address, or error packet details. That is intentional for safe mode but increases stale-response risk if callers issue overlapping requests to the same route. The broader control-channel layer warns that callers should serialize messages for a given switch.

`dma_port_wait_for_completion()` polls with 50 ms request timeouts and ignores timeout reads until the overall deadline. A controller that repeatedly times out on reads may delay failure until the full mailbox timeout.

Address and dword count fields are masked into fixed-width bitfields. Large addresses or block sizes outside what `tb_nvm_*` passes could be truncated. CSS writes are specially bounded, but non-CSS write sizes depend on the common NVM helper respecting the 16-dword mailbox limit.

## Test Signals

Validation should cover NHI port discovery on ports 3/5/7, safe-mode reads that would fail normal validation, mailbox completion polling, status-to-errno mapping, flash read/write retries, CSS size rejection, update-auth asynchronous status, and power-cycle request behavior. Fault tests should inject config read/write timeouts, access/auth errors in `MAIL_OUT`, and route removal during mailbox polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/dma_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/dma_port.h -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/dma_port.h

## Purpose

`dma_port.h` declares the Thunderbolt DMA-port mailbox interface used for switch NVM flash access and switch power/authentication operations. It hides the concrete `struct tb_dma_port` implementation from callers and exposes a small API for allocation, flash reads/writes, authentication, authentication status, and power cycling.

## Important APIs, Types, and Functions

The header forward-declares `struct tb_switch` and `struct tb_dma_port`. It defines `DMA_PORT_CSS_ADDRESS` as the magic CSS write address and `DMA_PORT_CSS_MAX_SIZE` as the maximum CSS write size. Public functions are `dma_port_alloc()`, `dma_port_free()`, `dma_port_flash_read()`, `dma_port_flash_write()`, `dma_port_flash_update_auth()`, `dma_port_flash_update_auth_status()`, and `dma_port_power_cycle()`.

## Control Flow

Callers allocate a DMA port for a switch, use the returned object for block-oriented NVM operations, then release it. Flash reads target the active region; flash writes target the non-active region except CSS writes, which use the fixed CSS address. Authentication is split into request and later status polling so root-switch resets can be handled by higher layers.

## State and Persistence Behavior

The header itself stores no state. The object returned by `dma_port_alloc()` represents a mailbox endpoint for one switch. Calls can produce persistent hardware effects: non-active NVM contents can change, firmware authentication can trigger active image swap, and `dma_port_power_cycle()` can reset the switch.

## Dependencies and Integration Points

The header includes `tb.h` for switch definitions and size macros. It is consumed by EEPROM/DROM and NVM update code that needs safe-mode-compatible flash access without exposing mailbox register details.

## Risks and Edge Cases

The API does not expose locking requirements, so callers must rely on the surrounding Thunderbolt domain lock and control-channel serialization. Address and size semantics are hardware-specific; callers must pass byte addresses and sizes acceptable to the NVM helpers and mailbox implementation.

Because authentication status is separate from authentication start, callers must handle controller reset or disappearance between calls and must not assume `dma_port_flash_update_auth()` returning success means the image was accepted.

## Test Signals

Build coverage should ensure all users include the header cleanly. Functional tests should allocate/free on switches with and without DMA capability, read flash data, reject oversize CSS writes, write non-active flash blocks, start authentication, poll status, and power-cycle a test switch or mocked mailbox.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/dma_port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/dma_test.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/dma_test.c

## Purpose

`dma_test.c` is a Thunderbolt service driver that exposes an XDomain DMA traffic test through debugfs. It registers a `dma_test` property directory/service, binds to matching XDomain services, allocates TX/RX rings and XDomain paths on demand, sends or receives bounded 4 KiB frames, and reports packet, CRC, overflow, speed, width, and configuration errors.

## Important APIs, Types, and Functions

`struct dma_test` holds the bound service, parent XDomain, TX/RX rings and HopIDs, configured packet counts, expected link speed/width, actual packet counters, CRC/overflow counters, last result, error code, completion, lock, and debugfs directory. `struct dma_test_frame` wraps a frame buffer and `ring_frame`.

Core helpers are `dma_test_start_rings()`, `dma_test_stop_rings()`, `dma_test_free_rings()`, `dma_test_submit_rx()`, `dma_test_submit_tx()`, `dma_test_rx_callback()`, `dma_test_tx_callback()`, `dma_test_set_bonding()`, `dma_test_validate_config()`, `dma_test_check_errors()`, and `test_store()`.

Debugfs attributes expose `lanes`, `speed`, `packets_to_receive`, `packets_to_send`, `status`, and write-only `test`. Module lifecycle is handled by `dma_test_init()` and `dma_test_exit()`; service lifecycle by `dma_test_probe()` and `dma_test_remove()`.

## Control Flow

Module init allocates a 4 KiB pattern buffer, fills it with an incrementing data pattern, creates and registers the `dma_test` property directory, then registers the Thunderbolt service driver. Probe allocates private state, initializes its mutex and completion, stores drvdata, and creates debugfs files.

Writing `1` to `test` resets counters, validates that at least one direction is configured and bidirectional runs use equal packet counts, applies requested lane bonding, creates TX/RX rings, allocates XDomain HopIDs, enables paths, starts rings, submits RX buffers first, submits TX frames, waits for RX completion if needed, stops and frees rings, checks expected speed/width and counters, and stores pass/fail status.

RX callbacks unmap and free buffers, count received packets, record descriptor CRC/overflow flags, and complete the run when the expected number arrives. TX callbacks unmap and free transmitted buffers. The suspend hook relies on interruptible completion waits returning so an in-progress debugfs write can unwind and tear down rings.

## State and Persistence Behavior

Per-service state persists for the service lifetime. Test configuration and last-result counters persist until the service is removed or another run overwrites them. Rings, HopIDs, DMA mappings, and packet buffers are transient and should be fully released after each run.

No disk state is persisted. Hardware state changes include temporary XDomain DMA paths and optional lane-bonding configuration. Paths are disabled in `dma_test_stop_rings()` even when buffer submission or wait fails after ring startup.

## Dependencies and Integration Points

The file depends on Thunderbolt service registration, property directories, XDomain path allocation/enable/disable helpers, NHI ring allocation, DMA mapping APIs, completions, debugfs, module lifecycle, and service driver matching through `TB_SERVICE("dma_test", 1)`.

It integrates with `domain.c` through the Thunderbolt service bus and with the debugfs infrastructure through the service debugfs directory.

## Risks and Edge Cases

`dma_test_submit_rx()` and `dma_test_submit_tx()` return immediately on allocation or DMA mapping failure but do not clean up frames already submitted in the same loop. Later `dma_test_stop_rings()` stops rings, which should cancel queued frames and run callbacks, but this depends on ring stop semantics for partially submitted buffers.

`dma_test_submit_tx()` increments `packets_sent` before checking the return value of `tb_ring_tx()`, and it ignores any `tb_ring_tx()` failure. If TX submission can fail after ring setup, the result may misreport packets and leak the frame unless the ring takes ownership.

The generated pattern writes through a `u32 *` while incrementing a `u64` value, so the actual pattern uses truncated 32-bit values rather than full 64-bit chunks. The current driver never validates received payload contents, only packet counts and descriptor errors.

Removal deletes debugfs under the lock but does not actively stop an in-progress test outside the debugfs call path. The debugfs write holds the same lock, so removal waits, but long receive waits can delay removal until interrupt or completion.

## Test Signals

Tests should cover service registration/probe/remove, debugfs validation bounds, send-only, receive-only, and loopback send+receive runs, invalid mismatched packet counts, lane bonding enable/disable failures, speed/width mismatch reporting, RX descriptor CRC/overflow flags, interruptible wait during suspend, allocation failures after partial submissions, and repeated runs with no stale rings or HopIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/dma_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/domain.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/domain.c

## Purpose

`domain.c` implements the Thunderbolt bus and domain core. It registers the `thunderbolt` bus type, matches Thunderbolt services to service drivers, exposes domain sysfs attributes, allocates and tears down `struct tb` domains, coordinates control-channel lifecycle with connection-manager operations, handles suspend/resume/runtime PM transitions, and provides authorization/path-management wrappers.

## Important APIs, Types, and Functions

Service bus helpers include `match_service_id()`, `tb_service_match()`, `tb_service_probe()`, `tb_service_remove()`, and `tb_service_shutdown()`. Domain sysfs attributes are `boot_acl`, `deauthorization`, `iommu_dma_protection`, and `security`.

Public domain lifecycle APIs include `tb_domain_alloc()`, `tb_domain_add()`, `tb_domain_remove()`, `tb_domain_suspend_noirq()`, `tb_domain_resume_noirq()`, `tb_domain_suspend()`, `tb_domain_freeze_noirq()`, `tb_domain_thaw_noirq()`, `tb_domain_complete()`, `tb_domain_runtime_suspend()`, `tb_domain_runtime_resume()`, `tb_domain_init()`, and `tb_domain_exit()`.

Authorization and path APIs include `tb_domain_disapprove_switch()`, `tb_domain_approve_switch()`, `tb_domain_approve_switch_key()`, `tb_domain_challenge_switch_key()`, `tb_domain_disconnect_pcie_paths()`, `tb_domain_approve_xdomain_paths()`, `tb_domain_disconnect_xdomain_paths()`, and `tb_domain_disconnect_all_paths()`.

## Control Flow

`tb_domain_alloc()` allocates `struct tb` plus connection-manager private data, assigns a domain id, creates an ordered workqueue, allocates the control channel with `tb_domain_event_cb()`, initializes the embedded device, and sets bus/type/groups. `tb_domain_add()` starts the control channel under `tb->lock`, calls connection-manager `driver_ready`, adds the domain device, starts the connection manager, releases the lock to allow event processing, and enables runtime PM/autosuspend.

Control-channel events enter `tb_domain_event_cb()`. XDomain request/response packets are delegated to XDomain handling when enabled; other events are passed to `cm_ops->handle_event()`.

Removal locks the domain, stops connection-manager activity, stops control traffic, flushes the ordered workqueue, calls optional `deinit`, and unregisters the device. The device release frees the control channel, workqueue, ida id, mutex, and `struct tb`.

Suspend/freezing stop the control channel after optional connection-manager noirq hooks. Resume/thaw restart it before optional resume hooks. Runtime suspend calls optional connection-manager runtime suspend and then stops control traffic; runtime resume starts control traffic then calls the resume hook.

Authorization wrappers enforce connection-manager capability and parent authorization before approving a switch. Secure challenge approval generates a random challenge, asks firmware/device for a response, computes HMAC-SHA256 using the switch key, uses `crypto_memneq()` for comparison, and approves only on match.

## State and Persistence Behavior

Domain state persists in `struct tb`: NHI, control channel, ordered workqueue, device model object, security level, boot ACL capacity, domain lock, root switch, and connection-manager private data. The bus registration and domain ida are global.

Sysfs `boot_acl` can persist policy into firmware-managed preboot ACL storage through connection-manager callbacks. Switch authorization, key approval, challenge approval, and path disconnect/approval can change controller and topology state but are not stored by this file itself.

## Dependencies and Integration Points

The file depends on the Linux driver core, bus types, sysfs attributes, runtime PM, IDA, workqueues, crypto SHA256/HMAC helpers, random bytes, the Thunderbolt control channel, XDomain support, NVM/ACPI/debugfs initialization, and connection-manager operations in `struct tb_cm_ops`.

It is the integration point between low-level NHI probing, firmware/software connection managers, switch/device objects, XDomain services, debugfs, ACPI, NVM, and sysfs userspace policy.

## Risks and Edge Cases

`boot_acl_store()` carefully bounds input length and requires exactly `nboot_acl` comma-separated fields, but it calls `pm_runtime_get_sync()` without checking negative return. Similar patterns elsewhere assume runtime PM resume success or tolerate later command failures.

Domain start holds `tb->lock` across control-channel start because events may arrive immediately. Any connection-manager `driver_ready` or `start` implementation must avoid lock inversions with work queued back to the same ordered workqueue.

Runtime resume starts the control channel before the connection manager resumes. If resume hook fails, the control channel remains started; callers need to handle the partially resumed state.

Authorization wrappers require parent authorization but trust `sw->key` and firmware callbacks for secure operations. Challenge approval returns `-EKEYREJECTED` on HMAC mismatch and must be tested with malformed or missing keys.

## Test Signals

Tests should cover bus registration/unregistration, service matching by all match flags, probe/remove/shutdown dispatch, domain allocation failure unwind, add failure at driver_ready/device_add/start stages, event callback routing, sysfs boot ACL show/store parsing, suspend/resume/freeze/thaw/runtime PM sequencing, switch approval parent checks, secure challenge success/failure, and disconnect-all behavior across PCIe and XDomain paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/domain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/eeprom.c

## Purpose

`eeprom.c` reads and parses Thunderbolt/USB4 DROM data for switches. It supports legacy bit-banged EEPROM access, host DROM copies from EFI properties, DROM copies from active NVM through the DMA port, and USB4 router DROM reads. Parsed DROM entries populate switch identity, vendor/device names, port disable/link metadata, dual-link relationships, and USB4 product IDs.

## Important APIs, Types, and Functions

Low-level EEPROM helpers are `tb_eeprom_ctl_read/write()`, `tb_eeprom_active()`, `tb_eeprom_transfer()`, `tb_eeprom_out()`, `tb_eeprom_in()`, `tb_eeprom_get_drom_offset()`, and `tb_eeprom_read_n()`. Integrity helpers are `tb_crc8()` and `tb_crc32()`.

DROM ABI structures include `struct tb_drom_header`, `struct tb_drom_entry_header`, `struct tb_drom_entry_generic`, `struct tb_drom_entry_port`, and `struct tb_drom_entry_desc`. Public APIs are `tb_drom_read_uid_only()` and `tb_drom_read()`.

Copy/parse helpers include `tb_drom_copy_efi()`, `tb_drom_copy_nvm()`, `usb4_copy_drom()`, `tb_drom_bit_bang()`, `tb_drom_parse_v1()`, `usb4_drom_parse()`, `tb_drom_parse()`, `tb_drom_parse_entries()`, `tb_drom_parse_entry_generic()`, and `tb_drom_parse_entry_port()`.

## Control Flow

For non-root switches, `tb_drom_read()` reads the DROM through USB4 DROM access or legacy EEPROM bit banging, then parses it. For root switches, USB4 hosts read UID and DROM via USB4 helpers; non-USB4 hosts first try EFI property `ThunderboltDROM`, then DMA-port NVM copy, and finally minimal UID-only read.

Bit-banged reads enable EEPROM access through plug-events capability control bits, send SPI-like read opcode and offset bytes, read each byte by toggling clock/data bits, then disable access. DROM copy functions allocate `sw->drom`, wire it to the debugfs blob when enabled, and free it on copy or parse failure.

Parsing validates total size, dispatches by `device_rom_revision`, checks UID CRC8 for v1 DROM, warns but continues on data CRC32 mismatch, then walks variable-length entries. Generic entries set vendor/device names or USB4 product IDs. Port entries mark ports disabled and, for lane ports, set link number and dual-link partner.

## State and Persistence Behavior

The parsed DROM persists in `sw->drom` for the switch lifetime and may be exposed as a debugfs blob. Parsed fields persist in `struct tb_switch`, including UID, vendor/device IDs, names, disabled port flags, link numbers, and dual-link pointers.

The file does not write persistent storage, but it reads persistent EEPROM/NVM/firmware data. The warning in `tb_eeprom_active()` is operationally important: leaving bit-banging enabled can prevent controller reprobe, so successful paths must disable access after use.

## Dependencies and Integration Points

The file depends on switch/port config-space helpers, plug-events capability definitions, DMA-port flash reads, USB4 DROM/UID helpers, EFI/device properties, CRC32C, debugfs blob fields, and switch structures from `tb.h`.

It feeds switch discovery and debugfs. `tb_drom_read_uid_only()` is used during resume to verify switch identity without trusting cached `sw->drom`.

## Risks and Edge Cases

`tb_eeprom_read_n()` does not use a single cleanup exit after enabling EEPROM access. If `tb_eeprom_out()` or `tb_eeprom_in()` fails, it returns immediately without disabling bit-banging, matching the file's own warning as a risk.

`tb_drom_read_uid_only()` casts `data + 1` to `u64 *`, which may be unaligned on architectures that fault on unaligned access. The kernel often tolerates this on x86, but portable code would use `get_unaligned_le64()` or similar.

CRC32 mismatch only warns and continues. That improves compatibility with bad DROMs but can propagate corrupted names or port metadata. Port entries referring to port numbers within `max_port_number` but invalid dual-link partners are trusted.

Host DROM fallback behavior can leave root switches with only UID populated when full DROM copy is unavailable. Callers must tolerate absent vendor/device names and absent port metadata.

## Test Signals

Tests should cover EFI DROM copy, DMA-port NVM DROM copy, USB4 DROM read, legacy bit-banged read, UID-only read, CRC8 failure, CRC32 warning path, size mismatch, variable-entry overrun detection, unknown DROM revision fallback, extra port entries beyond max port, disabled port entries, dual-link port metadata, and failure cleanup that disables EEPROM access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/icm.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/icm.c

## Purpose

`icm.c` implements the firmware-based internal Thunderbolt connection manager. It detects supported Intel controller generations, starts or communicates with ICM firmware, sends ICM command packets over the control channel, handles firmware topology and XDomain events, manages switch authorization and secure keys, coordinates suspend/runtime-resume rescans, exposes boot ACL operations, and proxies selected USB4 router operations including NVM authentication.

## Important APIs, Types, and Functions

`struct icm` is the connection-manager private state embedded after `struct tb`. It stores request serialization, delayed rescan work, optional upstream PCIe port and vendor capability for PCIe2CIO, safe-mode/runtime-PM/NVM-upgrade flags, protocol version, cached asynchronous NVM auth reply, RTD3 veto state, and generation-specific operation pointers.

Transport helpers include `icm_match()`, `icm_copy()`, `icm_request()`, PCIe2CIO helpers (`pcie2cio_read/write()`), and firmware start/reset helpers (`icm_firmware_running()`, `icm_firmware_reset()`, `icm_firmware_start()`, `icm_firmware_init()`, `icm_driver_ready()`).

Generation-specific implementations cover Falcon Ridge (`icm_fr_*`), Alpine Ridge (`icm_ar_*`), Titan Ridge (`icm_tr_*`), Ice Lake (`icm_icl_*`), and newer TGL/ADL/RPL/MTL/Maple Ridge support. Public entry is `icm_probe()`, which returns a populated `struct tb` or `NULL`.

Topology helpers include `alloc_switch()`, `add_switch()`, `update_switch()`, `remove_switch()`, `add_xdomain()`, `update_xdomain()`, and `remove_xdomain()`. Runtime/resume helpers include `icm_unplug_children()`, `icm_free_unplugged_children()`, `icm_rescan_work()`, `icm_complete()`, `icm_runtime_suspend/resume()`, and switch runtime callbacks.

## Control Flow

Probe allocates a domain with ICM private data, initializes the request lock and rescan work, switches on PCI device ID, installs generation-specific private callbacks and `tb_cm_ops`, checks support, and returns the domain to the NHI driver.

Domain add calls `icm_driver_ready()`. It starts firmware if needed, detects safe mode, validates firmware mode, optionally resets physical links via PCIe2CIO, sends `DRIVER_READY`, waits for root switch config access, records security level, protocol version, boot ACL capacity, and runtime-PM support, then later `icm_start()` allocates and adds the root switch.

ICM commands are serialized by `request_lock` and sent as `TB_CFG_PKG_ICM_CMD`; responses are matched by command code and copied by packet id. Notifications are copied into heap work items and processed on the domain ordered workqueue under `tb->lock`.

Device-connected events reconcile existing switches by UUID, route, link/depth, and dual-link physical port. Stale switches or XDomains are removed before new objects are added. Disconnected events remove matching switches or XDomains. XDomain path approval creates DMA tunnels through firmware and emits tunnel activation/deactivation notifications.

Suspend tells firmware the driver unloads and may save devices. Resume marks children unplugged, re-sends driver-ready, accepts firmware's connected events as the new truth, then delayed rescan removes still-unplugged children. RTD3 veto events hold or release a runtime PM reference on the domain.

USB4 proxy operations require protocol version 3. Synchronous operations return metadata/status/data directly. NVM_AUTH is asynchronous: it submits a request with a completion callback, stores the eventual reply in `last_nvm_auth`, and later status polling matches it by route.

## State and Persistence Behavior

Persistent in-kernel state includes the domain, root switch, switch/XDomain topology objects, ICM private flags, protocol version, boot ACL size, and cached NVM auth reply. Switch objects store route, link/depth, connection id/key, authorization state, security level, boot flag, speed/width, runtime PM capability, UUID, and unplug markers.

Firmware-visible persistent effects include approving switches, adding secure keys, challenge approval, boot ACL reads/writes, disconnecting PCIe paths, XDomain path setup/teardown, saving devices for boot ACL, USB4 router operations, and NVM authentication. Safe mode blocks normal topology creation and instead exposes a safe-mode root switch for NVM recovery.

## Dependencies and Integration Points

The file depends on the control channel, NHI firmware status/mailbox registers, PCI config access, runtime PM, workqueues, Thunderbolt switch/XDomain/device helpers, tunnel notifications, platform Apple detection, USB4 operation definitions, and connection-manager operations consumed by `domain.c`.

It integrates with `domain.c` as a `tb_cm_ops` provider; with `eeprom.c` and NVM code through USB4 switch operation proxy and NVM auth status; with `dma_test.c` and XDomain services through XDomain path approval; and with suspend/runtime PM through domain and switch callbacks.

## Risks and Edge Cases

The ICM protocol has multiple generation-specific packet formats. Reusing Falcon Ridge handlers for Alpine Ridge and Titan Ridge handlers for newer controllers is intentional but brittle if firmware semantics diverge. Topology reconciliation must handle stale UUIDs, dual-link route changes, resume events, and switches replaced by XDomain hosts.

`icm_copy()` copies responses when `packet_id < npackets` and completes when `packet_id == total_packets - 1`; it does not verify `total_packets <= npackets`, so malformed firmware can cause early completion with missing packets or ignored extra packets.

`icm_usb4_switch_op()` uses `tx_data_len` and `rx_data_len` as dword counts in copies but compares `tx_data_len < ARRAY_SIZE(request.data)`. Callers must pass lengths in dwords, not bytes, or data will be over-copied.

Asynchronous NVM auth stores only one `last_nvm_auth`. A second auth completion before status consumption frees the old reply with a warning. Concurrent auth operations on multiple switches can overwrite status.

Several runtime PM calls use `pm_runtime_get_sync()` without checking errors. Resume cleanup relies on completion signaling to avoid deadlock when removing runtime-suspended switches.

## Test Signals

Tests should cover probe selection for each PCI ID family, unsupported Apple/Falcon Ridge behavior, `start_icm` firmware start paths, safe-mode handling, driver-ready timeout, boot ACL get/set, switch approval/key/challenge success and failures, ICM request timeout/retry, multipacket topology responses, device connected/disconnected reconciliation, XDomain connected/disconnected replacement, suspend/resume rescan cleanup, RTD3 veto reference handling, USB4 proxy ops, asynchronous NVM auth status, and disconnecting PCIe/XDomain paths before NVM upgrade.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/icm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/lc.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/lc.c

## Purpose

`lc.c` implements Thunderbolt link-controller register helpers. It reads LC UUID/fuse data, locates per-port LC register blocks, resets downstream ports, marks ports or XDomain links configured, starts lane initialization after sleep, manages CLx/wake/sleep bits, connects internal xHCI on Thunderbolt 3 routers, arbitrates DisplayPort sink allocation, checks lane bonding, and forces LC power.

## Important APIs, Types, and Functions

Public functions include `tb_lc_read_uuid()`, `tb_lc_reset_port()`, `tb_lc_configure_port()`, `tb_lc_unconfigure_port()`, `tb_lc_configure_xdomain()`, `tb_lc_unconfigure_xdomain()`, `tb_lc_start_lane_initialization()`, `tb_lc_is_clx_supported()`, `tb_lc_is_usb_plugged()`, `tb_lc_is_xhci_connected()`, `tb_lc_xhci_connect()`, `tb_lc_xhci_disconnect()`, `tb_lc_set_wake()`, `tb_lc_set_sleep()`, `tb_lc_lane_bonding_possible()`, `tb_lc_dp_sink_query()`, `tb_lc_dp_sink_alloc()`, `tb_lc_dp_sink_dealloc()`, and `tb_lc_force_power()`.

Internal helpers `read_lc_desc()` and `find_port_lc_cap()` decode the LC descriptor to compute the base offset for a physical port. `tb_lc_set_port_configured()`, `tb_lc_set_xdomain_configured()`, `__tb_lc_xhci_connect()`, `tb_lc_set_wake_one()`, `tb_lc_dp_sink_from_port()`, and `tb_lc_dp_sink_available()` implement shared register updates.

## Control Flow

Most operations first reject unsupported generations or missing LC capability, then compute a per-port LC offset from `TB_LC_DESC`. The code maps logical lane adapter numbers to physical port numbers with `tb_phy_port_from_link()` and selects lane-specific bits based on odd/even port number.

Port reset sets the downstream port reset bit, sleeps for 10 ms, rereads mode, clears the bit, and writes it back. Port/XDomain configuration toggles lane configured bits and upstream bit where appropriate. Lane initialization sets the SLI bit for non-root generation 2+ switches after resume.

Wake/sleep operations iterate over all link-controller instances described by the LC descriptor and update `TB_LC_SX_CTRL` bits. Wake flags map to connect, USB4, PCIe, and DP wake bits. Sleep sets the sleep bit for every LC.

DisplayPort sink functions map the first DP IN port to sink 0 and the second to sink 1. They query allocation state, require availability or CM ownership, set allocation to CM on alloc, and clear it on dealloc for generation 3+ hardware.

## State and Persistence Behavior

The file stores no long-lived kernel state. It mutates LC hardware registers that affect link power management, reset state, wake behavior, lane initialization, internal xHCI routing, DP sink ownership, and forced power. These settings persist in hardware until changed, reset, or power-managed by firmware/hardware.

Functions that return booleans generally collapse read errors and unsupported hardware to `false`, which makes callers treat unavailable LC state as unsupported or not connected.

## Dependencies and Integration Points

The file depends on `tb_sw_read/write()`, switch/port helpers from `tb.h`, LC register definitions, generation checks, route checks, DP/USB/PCIe port type helpers, and wake flag definitions. It is used by switch setup, tunnel management, DisplayPort allocation, power management, USB3/xHCI handling, and NVM authentication force-power flows.

## Risks and Edge Cases

LC descriptor fields are trusted when computing per-port offsets. Corrupt or unexpected descriptors can point reads/writes at wrong config offsets. Several void functions ignore failures from their internal setters, so cleanup paths may silently leave LC state configured.

`tb_lc_dp_sink_query()` returns `!tb_lc_dp_sink_available()`: because availability returns `0` when available and negative otherwise, this maps any error to `false`, but also makes the logic easy to misread.

DP sink ownership treats allocation values `0` and CM-owned as available. If firmware or BIOS uses other ownership values, allocation correctly returns `-EBUSY`, but deallocation also requires the same availability check and may refuse to clear a sink not considered CM-owned.

Generation gating is conservative. Some operations return success without doing anything on older generations, so callers must not interpret success as proof that hardware state changed.

## Test Signals

Tests should cover LC descriptor parsing, per-port offset calculation for odd/even lanes, generation gating, downstream port reset sequencing, configured/unconfigured port bits, XDomain bits, lane initialization on resumed devices, CLx support reads, USB plugged/xHCI connected checks, xHCI connect/disconnect, wake flag combinations, sleep over multiple LCs, lane bonding checks, DP sink query/alloc/dealloc ownership values, force power, and read/write error propagation versus boolean collapse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/lc.c -->
