# Group Research: group_1746_spdk_sources_virtualization_spdk_lib_nvme_nvme_c_sources_virtualiza_2871a8fb2223

Scope: `Docs/research_subset_a.md` subset A, SPDK NVMe library files under `sources/virtualization/spdk/lib/nvme/`.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme.c

## Purpose

`nvme.c` is the top-level SPDK NVMe library entry point for driver initialization, controller probing/connection, controller detach orchestration, transport-ID parsing/comparison, synchronous admin completion waiting, and common request helpers. It bridges public APIs such as `spdk_nvme_probe()`, `spdk_nvme_connect()`, and `spdk_nvme_detach()` to transport-specific controller construction and controller initialization in `nvme_ctrlr.c`.

## Main Responsibilities

- Owns the global NVMe driver object:
  - `g_spdk_nvme_driver`, stored in an SPDK shared memzone named `spdk_nvme_driver`.
  - `g_spdk_nvme_pid`, process-local PID used for multi-process request ownership.
  - `g_nvme_attached_ctrlrs`, per-process attached controller list.
  - `g_spdk_nvme_driver->shared_attached_ctrlrs`, shared PCIe controller list.

- Initializes shared driver state with `nvme_driver_init()`:
  - Primary process reserves and initializes shared memory.
  - Secondary process waits for primary initialization.
  - Initializes a robust process-shared mutex where supported.
  - Opens PCI hotplug event listener and generates a default extended host ID.

- Handles controller probe/connect:
  - `spdk_nvme_probe()` / `spdk_nvme_probe_ext()` create an async probe context and poll it synchronously.
  - `spdk_nvme_probe_async_ext()` starts a scan without waiting for all controllers to finish initialization.
  - `spdk_nvme_probe_poll_async()` advances controller init and frees the probe context when finished.
  - `spdk_nvme_connect()` / `spdk_nvme_connect_async()` provide direct-connect style construction with caller-supplied controller options.

- Handles detach:
  - `spdk_nvme_detach()` performs blocking detach.
  - `spdk_nvme_detach_async()` appends individual controller detach jobs to a detach context.
  - `spdk_nvme_detach_poll_async()` polls all outstanding detach jobs and frees the detach context when complete.
  - Actual destruction is delegated to `nvme_ctrlr_destruct_async()` / `nvme_ctrlr_destruct_poll_async()`.

- Provides blocking completion helpers:
  - `nvme_completion_poll_cb()` records command completion into `nvme_completion_poll_status`.
  - `nvme_wait_for_completion_poll()` polls a qpair or poll group, checks timeout, checks PCIe CSTS validity, and returns `-EAGAIN`, `0`, `-EIO`, or `-ECANCELED`.
  - `nvme_wait_for_adminq_completion()` wraps admin queue polling with controller admin timeout.

- Provides non-fast-path user-buffer copy request allocation:
  - `nvme_allocate_request_user_copy()` allocates a DMA buffer, optionally copies host-to-controller payload, and restores controller-to-host data in `nvme_user_copy_cmd_complete()` before invoking the user callback.

- Implements transport ID and host ID parsing:
  - `spdk_nvme_transport_id_parse()`
  - `spdk_nvme_host_id_parse()`
  - `spdk_nvme_transport_id_compare()`
  - `spdk_nvme_transport_id_parse_trtype()`
  - `spdk_nvme_transport_id_parse_adrfam()`
  - `spdk_nvme_transport_id_populate_trstring()`
  - `spdk_nvme_trid_populate_transport()`

## Probe and Connection Flow

The central probe path is:

1. Caller enters `spdk_nvme_probe_ext()` or `spdk_nvme_probe_async_ext()`.
2. `nvme_driver_init()` ensures global shared driver state exists.
3. `nvme_probe_ctx_init()` initializes callback pointers and tail queues.
4. `nvme_probe_internal()` validates transport availability, locks the global driver, and calls `nvme_transport_ctrlr_scan()`.
5. For each found device, `nvme_ctrlr_probe()` either:
   - Reuses an existing controller matching transport ID and host NQN, increments the process ref count, and calls `attach_cb()`, or
   - Constructs a new transport controller and places it on `probe_ctx->init_ctrlrs`.
6. `spdk_nvme_probe_poll_async()` repeatedly calls `nvme_ctrlr_poll_internal()` for initializing controllers.
7. When a controller reaches `NVME_CTRLR_STATE_READY`, it is moved to either the shared PCIe list or per-process list, ref-counted for the current process, and delivered to `attach_cb()`.

The direct-connect path uses the same machinery but sets `direct_connect=true` and, when options are supplied, uses `nvme_connect_probe_cb()` to copy caller options into the controller opts used during construction.

## Detach Flow

Detach is ref-count aware and multi-process aware:

1. `nvme_ctrlr_detach_async()` locks the global driver and checks `nvme_ctrlr_get_ref_count()`.
2. If the current process holds the last reference:
   - Allocates `nvme_ctrlr_detach_ctx`.
   - Drops this process ref.
   - Sends I/O message detach notification through `nvme_io_msg_ctrlr_detach()`.
   - Starts `nvme_ctrlr_destruct_async()`.
3. If other processes still reference the controller:
   - Only drops this process ref and returns no destruction context.
4. Completion removes the controller from the shared/per-process attached list in `nvme_ctrlr_detach_async_finish()`.

## Transport ID Parsing Details

The parser accepts whitespace-separated `key:value` or `key=value` entries. Recognized transport ID keys include:

- `trtype`
- `adrfam`
- `traddr`
- `trsvcid`
- `priority`
- `subnqn`

It silently ignores application/custom keys such as `hostaddr`, `hostsvcid`, `hostnqn`, `ns`, and `alt_traddr`. Unknown keys are logged but do not cause a hard parse failure unless token parsing itself fails.

`spdk_nvme_transport_id_compare()` normalizes PCI addresses for PCIe comparisons. For IPv4/IPv6 fabrics addresses it uses `spdk_net_compare_address()` rather than raw string comparison, while other address families use case-insensitive string comparison for `traddr`/`trsvcid` and exact string comparison for `subnqn`.

## State, Concurrency, and Multi-Process Behavior

- Uses a process-private init mutex to serialize first-time global driver setup.
- Uses `g_spdk_nvme_driver->lock` as a robust process-shared mutex protecting shared controller lists and driver initialization state.
- PCIe controllers are considered shared across processes; other transports are stored per process.
- Attach callbacks are invoked after dropping the global driver lock so users can safely call APIs that may reacquire the lock, including detach.
- Request timeout handling is per active process and skips admin commands submitted by other processes.

## Important Dependencies

- `nvme_internal.h` for controller/qpair/request internals.
- `nvme_io_msg.h` for cross-process controller update/detach messages.
- `spdk/env.h` for memzones, timing, allocation, and process role.
- `spdk/net.h` for address comparison.
- Transport hooks through `nvme_transport_ctrlr_scan()`, `nvme_transport_ctrlr_construct()`, and related transport dispatch.

## Error Handling and Risks

- Timeout handling marks pending completion status as timed out so callback-side cleanup can free memory later.
- `nvme_wait_for_completion_poll()` treats invalid PCIe CSTS reads as internal device errors.
- Secondary processes fail initialization if the primary process has not started or does not initialize within the global timeout.
- Transport ID parsing has mixed behavior: malformed token/length failures return `-EINVAL`, while unknown keys are logged but parsing continues.
- Detach depends on process ref counts and robust shared locking; incorrect ref ownership elsewhere can prevent destruction or prematurely destruct a shared controller.

## Filesystem/Virtualization Relevance

This file is part of the user-space NVMe storage substrate used by SPDK applications and virtualized storage stacks. It provides controller discovery, attach, detach, and address parsing needed by higher-level block-device and NVMe-oF integrations.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_auth.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_auth.c

## Purpose

`nvme_auth.c` implements NVMe-oF DH-HMAC-CHAP authentication for SPDK NVMe qpairs. It provides digest and Diffie-Hellman group lookup APIs, DH-HMAC-CHAP key transformation and response calculation, OpenSSL-backed DH key generation/secret derivation, and the qpair authentication state machine used for fabrics connections.

Most functional code is compiled only when `SPDK_CONFIG_HAVE_EVP_MAC` is enabled. The digest/group name lookup helpers are always present.

## Main Responsibilities

- Defines supported DH-HMAC-CHAP hash digests:
  - SHA-256
  - SHA-384
  - SHA-512

- Defines supported DH groups:
  - `null`
  - `ffdhe2048`
  - `ffdhe3072`
  - `ffdhe4096`
  - `ffdhe6144`
  - `ffdhe8192`

- Exposes digest/group mapping helpers:
  - `spdk_nvme_dhchap_get_digest_id()`
  - `spdk_nvme_dhchap_get_digest_name()`
  - `spdk_nvme_dhchap_get_dhgroup_id()`
  - `spdk_nvme_dhchap_get_dhgroup_name()`
  - `spdk_nvme_dhchap_get_digest_length()`

- Implements DH-HMAC-CHAP cryptographic helpers:
  - Parse DHHC-1 formatted CHAP keys from SPDK key objects.
  - Validate key size and CRC32 checksum.
  - Transform keys according to DH-HMAC-CHAP hash/NQN rules.
  - Generate host DH public keys.
  - Derive DH shared secrets from peer public keys.
  - Calculate CHAP response values with HMAC.

- Implements fabrics qpair authentication:
  - `nvme_fabric_qpair_authenticate_async()`
  - `nvme_fabric_qpair_authenticate_poll()`
  - `spdk_nvme_qpair_authenticate()`

## Authentication State Machine

The state machine is stored in `qpair->auth.state` and driven by `nvme_fabric_qpair_authenticate_poll()`:

1. `NVME_QPAIR_AUTH_STATE_NEGOTIATE`
   - Sends `AUTH_negotiate` with allowed digest and DH group lists.
   - Moves to `AWAIT_NEGOTIATE`.

2. `NVME_QPAIR_AUTH_STATE_AWAIT_NEGOTIATE`
   - Waits for Authentication Send completion.
   - Issues Authentication Receive for challenge.
   - Moves to `AWAIT_CHALLENGE`.

3. `NVME_QPAIR_AUTH_STATE_AWAIT_CHALLENGE`
   - Waits for challenge receive completion.
   - Validates message type, transaction ID, sequence number, hash length, DH group, DH value length, and policy allow-lists.
   - Sends DH-HMAC-CHAP reply.
   - Moves to `AWAIT_REPLY`.

4. `NVME_QPAIR_AUTH_STATE_AWAIT_REPLY`
   - Waits for reply send completion.
   - Issues receive for `success1`.
   - Moves to `AWAIT_SUCCESS1`.

5. `NVME_QPAIR_AUTH_STATE_AWAIT_SUCCESS1`
   - Validates controller success response.
   - If bidirectional authentication is enabled with `dhchap_ctrlr_key`, sends `success2`.
   - Otherwise enters `DONE`.

6. `NVME_QPAIR_AUTH_STATE_AWAIT_SUCCESS2` / `AWAIT_FAILURE2`
   - Waits for final send completion and then enters `DONE`.

7. `NVME_QPAIR_AUTH_STATE_DONE`
   - Cleans fabric poll resources and invokes auth cleanup.

A reentrancy guard, `auth->flags.in_auth_poll`, prevents recursive polling.

## Message Construction and Validation

- `nvme_auth_send_negotiate()` builds a common `AUTH_negotiate` message with a single DH-HMAC-CHAP descriptor.
- `nvme_auth_check_message()` validates expected message IDs and handles `AUTH_failure1` from the controller.
- `nvme_auth_check_challenge()` validates the DH-HMAC-CHAP challenge payload.
- `nvme_auth_send_reply()` computes the host response and optionally a controller challenge for bidirectional authentication.
- `nvme_auth_check_success1()` verifies controller response when a controller key is configured.
- `nvme_auth_send_failure2()` sends a terminal failure message when protocol/payload validation fails.

All auth send/receive commands use `nvme_auth_submit_request()`, which reuses `qpair->reserved_req` and `qpair->fabric_poll_status->dma_data`.

## Cryptographic Flow

`nvme_auth_get_key()` reads a key from `struct spdk_key` and expects the `DHHC-1:%02x:<base64>:` format. It:

1. Extracts the hash ID.
2. Decodes the base64 secret.
3. Requires decoded size of 36, 52, or 68 bytes, representing 32/48/64-byte keys plus a 4-byte CRC.
4. Validates CRC32.
5. Calls `nvme_auth_transform_key()`.

`nvme_auth_transform_key()` either copies raw key material for hash `NONE` or computes an HMAC over the NQN plus the literal NVMe-over-Fabrics string using the requested digest.

`spdk_nvme_dhchap_calculate()` computes the DH-HMAC-CHAP response over:

- Augmented challenge value.
- Sequence number.
- Transaction ID.
- Secure channel concatenation byte.
- Role string, such as `HostHost` or `Controller`.
- Local and remote NQNs with a zero terminator between them.

If a DH group is not `null`, `spdk_nvme_dhchap_generate_dhkey()`, `spdk_nvme_dhchap_dhkey_get_pubkey()`, and `spdk_nvme_dhchap_dhkey_derive_secret()` use OpenSSL EVP_PKEY/DHX APIs to generate and derive the shared secret.

## State, Memory, and Secret Handling

- Authentication allocates `struct nvme_completion_poll_status` and a 4096-byte DMA buffer per qpair auth attempt.
- Sensitive temporary key buffers are zeroed with `spdk_memset_s()`.
- `spdk_key_dup()` is used while holding the controller lock, then key references are released with `spdk_keyring_put_key()`.
- The file logs public keys and DH secret dumps through auth debug logging macros, which is useful for debugging but sensitive if debug log collection is enabled in production-like environments.

## Important Dependencies

- OpenSSL EVP MAC, EVP PKEY, DHX, RAND, BIGNUM, and OSSL_PARAM APIs.
- SPDK key/keyring abstractions.
- SPDK base64, CRC32, endian, and secure memset utilities.
- NVMe-oF fabric authentication structures from SPDK internal/public headers.
- Common completion polling from `nvme.c`.

## Error Handling and Risks

- Missing host DH-HMAC-CHAP key returns `-ENOKEY`.
- Secure channel concatenation is explicitly unsupported and returns `-EINVAL`.
- Protocol validation failures generally send `failure2` if possible and complete with `-EACCES`.
- Unsupported/disallowed digest or DH group is treated as authentication failure.
- OpenSSL allocation or crypto operation failures generally return `-EIO`, `-EINVAL`, `-ENOMEM`, or `-ENOBUFS`.
- Bidirectional authentication requires a host key; controller-key-only configurations are rejected elsewhere in controller key setup.

## Filesystem/Virtualization Relevance

This file secures NVMe-oF controller/qpair connections used by SPDK storage applications. In virtualized storage deployments, this authentication path protects remote block-device attachment and controller access.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_auth.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_ctrlr.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_ctrlr.c

## Purpose

`nvme_ctrlr.c` is the core SPDK NVMe controller lifecycle implementation. It manages controller options, admin and I/O queue pairs, initialization/reset/destruction state machines, namespace discovery, asynchronous event handling, multi-process ownership, keep-alive, controller memory regions, namespace management commands, firmware/boot partition operations, and controller metadata accessors.

It is the main controller orchestration layer between public `spdk_nvme_ctrlr_*` APIs and transport-specific operations.

## Main Responsibilities

- Controller option defaults and ABI-compatible option copying.
- I/O qpair allocation, connect, disconnect, reconnect, and free.
- Controller register access wrappers for CAP, VS, CC, CSTS, CMB, PMR, boot partition registers, and NSSR.
- Controller initialization state machine through `nvme_ctrlr_process_init()`.
- Controller reset/disconnect/reconnect flows.
- Controller destruction and shutdown notification.
- Identify Controller, Identify Namespace, Active Namespace List, Namespace ID Descriptor List, and I/O command set specific identify flows.
- Supported log page and feature discovery.
- Asynchronous Event Request setup and event dispatch.
- ANA log allocation, retrieval, parsing, and namespace ANA state updates.
- Per-process controller tracking for SPDK multi-process operation.
- Public controller APIs for namespace attach/detach/create/delete/format, firmware update, CMB/PMR, boot partitions, security send/receive, and authentication.

## Controller Initialization State Machine

The central initialization function is `nvme_ctrlr_process_init()`. It advances `ctrlr->state` through transport setup and NVMe controller bring-up. Major phases are:

1. Optional PCIe init delay.
2. Connect admin qpair.
3. Read version register `VS`.
4. Read capability register `CAP`.
5. Read controller configuration `CC` and determine whether disabling is required.
6. If enabled, wait for `CSTS.RDY`, clear `CC.EN`, and wait for disabled.
7. Enable controller:
   - Select page size.
   - Select command set.
   - Validate arbitration mechanism.
   - Program `CC.EN = 1`.
8. Wait for `CSTS.RDY = 1`.
9. Reset admin queue transport state.
10. Identify Controller.
11. Configure Asynchronous Event Requests.
12. Configure keep-alive.
13. Identify NVM/ZNS/KV I/O command set specific controller data.
14. Set number of I/O queues.
15. Discover active namespaces.
16. Identify namespaces.
17. Identify namespace descriptor lists.
18. Identify namespace I/O command set specific data.
19. Discover supported log pages and features.
20. Set Host Behavior Support feature if needed.
21. Configure doorbell buffer if supported.
22. Set Host ID if needed.
23. Run transport ready hook.
24. Enter `NVME_CTRLR_STATE_READY`.

The state machine uses async register operations and async admin commands, then polls admin completions from wait states. It tracks per-state timeouts using SPDK ticks and avoids recursive admin completion processing when already in admin completion context.

## Controller Options

`spdk_nvme_ctrlr_get_default_ctrlr_opts()` populates defaults with ABI-size checks:

- I/O queue count, size, and request count.
- CMB submission queue preference.
- Interrupt enablement.
- Arbitration configuration.
- Keep-alive timeout.
- Transport retry and ACK timeout settings.
- Host NQN and host identifiers.
- Command set selection.
- Admin timeout and admin queue size.
- NVMe/TCP header/data digest settings.
- Fabrics connect timeout.
- ANA and changed namespace log read controls.
- TLS PSK and DH-HMAC-CHAP keys/digest/group allow-lists.

The default host NQN and extended host ID come from the global driver object initialized in `nvme.c`.

## I/O Qpair Lifecycle

Key public APIs:

- `spdk_nvme_ctrlr_get_default_io_qpair_opts()`
- `spdk_nvme_ctrlr_alloc_io_qpair()`
- `spdk_nvme_ctrlr_connect_io_qpair()`
- `spdk_nvme_ctrlr_disconnect_io_qpair()`
- `spdk_nvme_ctrlr_reconnect_io_qpair()`
- `spdk_nvme_ctrlr_free_io_qpair()`

Qpair allocation validates:

- Controller is ready.
- Queue priority is compatible with selected arbitration.
- User-provided SQ/CQ buffers are large enough.
- Delayed command submission is not used with interrupts.

The controller maintains:

- `active_io_qpairs`
- Per-process `allocated_io_qpairs`
- `free_io_qids` bit array

Freeing a qpair handles completion-context deletion deferral, disconnect polling for async qpairs, poll group removal, queued request aborting for local qpairs, qid release, and transport deletion.

## Reset, Disconnect, and Failure Handling

- `nvme_ctrlr_fail()` marks the controller failed, optionally removed, sets error state, and disconnects adminq.
- `spdk_nvme_ctrlr_fail()` wraps it with controller locking.
- `nvme_ctrlr_disconnect()` starts reset/disconnect:
  - Marks resetting/disconnecting.
  - Disables keep-alive.
  - Aborts queued aborts and AERs.
  - Marks adminq local failure.
  - Disconnects adminq.
- `spdk_nvme_ctrlr_reset()` performs synchronous reset by disconnecting, processing admin completions until disconnect, reconnecting, and polling reinitialization.
- `spdk_nvme_ctrlr_reconnect_async()` sets state back to init and intentionally leaves the controller lock held until `spdk_nvme_ctrlr_reconnect_poll_async()` completes.
- `spdk_nvme_ctrlr_reconnect_poll_async()` reinitializes the controller, reconnects non-fabrics qpairs where possible, marks foreign qpairs for owner-process reset handling, removes inactive namespaces, and emits controller update messages if needed.

Subsystem reset is exposed through `spdk_nvme_ctrlr_reset_subsystem()` and writes NSSR only when supported.

## Identify and Namespace Discovery

Namespace objects are stored in an RB tree ordered by NSID.

Active namespace discovery uses `nvme_active_ns_ctx`:

- For old/quirked controllers, it synthesizes all namespaces from `1..NN`.
- Otherwise it issues one or more Active Namespace List identify commands.
- It handles multi-page namespace lists by reallocating the list buffer and continuing from the last returned NSID.
- It swaps controller namespace state by clearing removed namespaces and marking new/existing namespaces as pending identify.

Namespace identify flow:

- `nvme_ctrlr_identify_namespaces()` identifies all pending namespaces.
- `nvme_ctrlr_identify_id_desc_namespaces()` retrieves namespace ID descriptor lists when supported.
- `nvme_ctrlr_identify_namespaces_iocs_specific()` retrieves ZNS, KV, or NVM-specific namespace data when supported.

The code treats some namespace identify failures as non-fatal when they indicate namespaces became inactive during discovery.

## Command Set Specific Handling

Controller-level I/O command set data:

- `nvme_ctrlr_identify_iocs_nvm_specific()`
- `nvme_ctrlr_identify_iocs_zns_specific()`
- `nvme_ctrlr_identify_iocs_kv_specific()`

ZNS-specific behavior includes:

- Reading ZNS controller identify data.
- Computing `max_zone_append_size`.
- Reading the ZNS Command Effects log page.
- Setting `SPDK_NVME_CTRLR_ZONE_APPEND_SUPPORTED` when Zone Append is supported.

The controller command set is selected during enable based on CAP.CSS and caller options, with fallbacks for buggy targets.

## Log Pages, Features, ANA, and AERs

Supported log pages:

- Mandatory log pages are marked directly.
- Command Effects Log is marked if controller LPA says CSES.
- ANA log is marked when CMIC indicates ANA reporting.
- FDP logs are marked when FDP is advertised.
- Intel vendor log pages are discovered through Intel log page directory for PCIe Intel devices unless disabled by quirks.

ANA handling:

- `nvme_ctrlr_alloc_ana_log_page()` sizes buffers based on active namespace count and ANA group count.
- `nvme_ctrlr_update_ana_log_page()` fetches the ANA log page synchronously through the admin queue.
- `nvme_ctrlr_parse_ana_log_page()` copies each variable-sized descriptor before passing it to a callback.
- `nvme_ctrlr_update_ns_ana_states()` updates namespace ANA group/state.

AER handling:

- `nvme_ctrlr_configure_aer()` configures requested async event notices.
- `nvme_ctrlr_construct_and_submit_aer()` submits AER commands.
- `nvme_ctrlr_async_event_cb()` queues events to every active process and resubmits AERs unless removed/destructed.
- `nvme_ctrlr_process_async_event()` handles namespace attribute changes and ANA changes.
- Namespace change processing can use Changed Namespace List log or fall back to full active namespace rediscovery.

## Multi-Process Tracking

The controller maintains `active_procs`, each with:

- PID and primary/secondary flag.
- Active request queue.
- Per-process allocated I/O qpairs.
- Async event queue.
- Timeout callbacks and AER callbacks.
- Process-local PCI device handle.

Important functions:

- `nvme_ctrlr_add_process()`
- `nvme_ctrlr_remove_process()`
- `nvme_ctrlr_cleanup_process()`
- `nvme_ctrlr_remove_inactive_proc()`
- `nvme_ctrlr_proc_get_ref()`
- `nvme_ctrlr_proc_put_ref()`
- `nvme_ctrlr_get_ref_count()`

Inactive process cleanup uses `kill(pid, 0)` and `ESRCH` detection, then frees outstanding requests, async events, and qpairs owned by the dead process.

## Destruction and Shutdown

`nvme_ctrlr_destruct_async()` prepares destruction by:

- Marking controller destructed.
- Processing admin completions.
- Aborting queued aborts and AERs.
- Freeing active I/O qpairs.
- Freeing doorbell and command-set-specific data.
- Starting shutdown notification through `nvme_ctrlr_shutdown_async()`.

`nvme_ctrlr_shutdown_async()` reads CC, sets shutdown notification or disables the controller depending on options, and then `nvme_ctrlr_shutdown_poll_async()` polls CSTS.SHST until complete or timeout.

`nvme_ctrlr_destruct_poll_async()` completes shutdown, invokes detach callback, disconnects adminq, clears namespaces, frees qid bit arrays, ANA buffers, and calls transport destruct.

## Public Controller Utility APIs

The file exposes many controller metadata and operation APIs, including:

- Controller data/register access:
  - `spdk_nvme_ctrlr_get_data()`
  - `spdk_nvme_nvm_ctrlr_get_data()`
  - `spdk_nvme_ctrlr_get_regs_*()`
  - `spdk_nvme_ctrlr_get_num_ns()`
  - `spdk_nvme_ctrlr_get_ns()`
  - `spdk_nvme_ctrlr_get_pci_device()`
  - `spdk_nvme_ctrlr_get_numa_id()`
  - `spdk_nvme_ctrlr_get_id()`
  - `spdk_nvme_ctrlr_get_max_xfer_size()`
  - `spdk_nvme_ctrlr_get_max_sges()`
  - `spdk_nvme_ctrlr_get_flags()`
  - `spdk_nvme_ctrlr_get_transport_id()`

- Namespace management:
  - `spdk_nvme_ctrlr_attach_ns()`
  - `spdk_nvme_ctrlr_detach_ns()`
  - `spdk_nvme_ctrlr_create_ns()`
  - `spdk_nvme_ctrlr_delete_ns()`
  - `spdk_nvme_ctrlr_format()`

- Firmware and boot partitions:
  - `spdk_nvme_ctrlr_update_firmware()`
  - `spdk_nvme_ctrlr_read_boot_partition_start()`
  - `spdk_nvme_ctrlr_read_boot_partition_poll()`
  - `spdk_nvme_ctrlr_write_boot_partition()`

- Controller memory:
  - `spdk_nvme_ctrlr_reserve_cmb()`
  - `spdk_nvme_ctrlr_map_cmb()`
  - `spdk_nvme_ctrlr_unmap_cmb()`
  - `spdk_nvme_ctrlr_enable_pmr()`
  - `spdk_nvme_ctrlr_disable_pmr()`
  - `spdk_nvme_ctrlr_map_pmr()`
  - `spdk_nvme_ctrlr_unmap_pmr()`

- Security/auth:
  - `spdk_nvme_ctrlr_security_receive()`
  - `spdk_nvme_ctrlr_security_send()`
  - `spdk_nvme_ctrlr_authenticate()`
  - `spdk_nvme_ctrlr_set_keys()`

## Important Dependencies

- `nvme_internal.h` for controller, namespace, qpair, state, and request internals.
- `nvme_io_msg.h` for controller update messaging.
- Transport dispatch functions for qpair/controller construction, connect/disconnect, register access, CMB/PMR, memory domains, and readiness.
- Admin command constructors from companion command files.
- SPDK environment APIs for DMA/shared allocation, virtual-to-physical translation, ticks, delays, PCI handling, and bit arrays.

## Error Handling and Risks

- The initialization state machine is broad and timeout-driven; incorrect timeout or state transition behavior can stall probe/reset.
- Several operations deliberately treat optional feature failures as non-fatal, such as Host ID setting and Intel log page discovery.
- Namespace discovery handles active namespace changes but may clear namespace state when identify returns inactive/invalid errors.
- Multi-process cleanup assumes process liveness can be detected with `kill(pid, 0)`.
- Some reset/reconnect paths intentionally hold controller locks across async-style phases; callers must respect API contract.
- Boot partition write uses controller fields as operation state, so concurrent boot partition writes on one controller would conflict.
- Debug/error handling often logs and continues for optional device features, reflecting real-world controller quirks.

## Filesystem/Virtualization Relevance

This file is central to SPDK’s user-space NVMe controller model. It supplies the controller lifecycle and namespace surface that higher-level block devices, NVMe-oF initiators, virtualized storage backends, and filesystem-adjacent storage tooling rely on for discovery, queue setup, reset recovery, namespace changes, and secure/admin operations.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_ctrlr.c -->