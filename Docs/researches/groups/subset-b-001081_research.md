# Research: subset-b-001081

Grouped research for TPM transport, platform, virtual-device, and resource-manager files under `sources/distributed-fs/ceph-client/drivers/char/tpm`. Each section preserves the exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_crb_ffa.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_crb_ffa.c

## Purpose
Implements the Arm FF-A TPM CRB start-method companion used by the generic CRB driver when a TPM service is exposed as an FF-A partition. It does not own the command buffer itself; it sends standardized direct-request messages to notify the secure service that CRB command or locality control fields changed.

## Important APIs, Types, And Functions
Exports `tpm_crb_ffa_init()` and `tpm_crb_ffa_start()`. Internal state is `struct tpm_crb_ffa`, holding the `ffa_device`, negotiated ABI version, a message mutex, and either direct-message v1 or v2 payload storage. `tpm_crb_ffa_to_linux_errno()`, `__tpm_crb_ffa_try_send_receive()`, `__tpm_crb_ffa_send_receive()`, `tpm_crb_ffa_get_interface_version()`, `tpm_crb_ffa_probe()`, and `tpm_crb_ffa_remove()` implement status mapping, retry, version negotiation, and FF-A driver lifetime.

## Control Flow
`tpm_crb_ffa_init()` registers the FF-A driver for built-in configurations and returns `-ENOENT` until probe completes, or `-ENODEV` after failed probe. Probe rejects partitions without direct receive support, allocates the singleton, selects 32-bit mode for AArch32 services, and verifies the service ABI via `CRB_FFA_GET_INTERFACE_VERSION`. `tpm_crb_ffa_start()` serializes on `msg_data_lock` and sends `CRB_FFA_START` with request type and locality. Message send retries `-EBUSY` until `busy_timeout_ms` expires.

## State And Persistence
State is a singleton pointer, negotiated major/minor version, and reusable FF-A message buffers. Nothing is persistent across driver unload; TPM command state lives in the CRB memory owned by the CRB driver and secure service.

## Dependencies And Integration Points
Depends on `linux/arm_ffa.h`, FF-A direct request/response operations, and the CRB driver through exported symbols declared in `tpm_crb_ffa.h`. It matches the TPM FF-A service UUID and translates service status codes to Linux errno values.

## Risks And Edge Cases
Only one FF-A TPM service instance is supported. The global singleton uses `ERR_PTR(-ENODEV)` to remember failed probe states. ABI compatibility checks are strict on major version and unusual on minor-version comparison, so version policy should be reviewed with DEN0138 changes. Timeout behavior depends on the module parameter and secure service returning `-EBUSY` consistently.

## Test Signals
Useful signals include FF-A service discovery, direct-request v1/v2 paths, AArch32 mode selection, busy retry timeout, incompatible ABI versions, duplicate service probe, CRB command start and locality start paths, and CRB driver retry behavior when `tpm_crb_ffa_init()` returns `-ENOENT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_crb_ffa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_crb_ffa.h -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_crb_ffa.h

## Purpose
Provides the small integration contract between the generic TPM CRB driver and the optional Arm FF-A CRB start-method driver.

## Important APIs, Types, And Functions
Declares `tpm_crb_ffa_init()` and `tpm_crb_ffa_start()` when `CONFIG_TCG_ARM_CRB_FFA` is reachable, otherwise supplies no-op inline stubs returning success. It also defines `CRB_FFA_START_TYPE_COMMAND` and `CRB_FFA_START_TYPE_LOCALITY_REQUEST`.

## Control Flow
The header lets CRB code call initialization and start notifications unconditionally while compile-time configuration determines whether real FF-A work occurs. Request-type constants select whether the secure TPM service should process a CRB command or a locality request.

## State And Persistence
The header owns no state. The real state resides in `tpm_crb_ffa.c`; stub builds intentionally persist no FF-A status.

## Dependencies And Integration Points
Used by CRB code that needs to support ACPI TPM2 FF-A start methods without hard-linking to the FF-A implementation in disabled configurations.

## Risks And Edge Cases
No-op stubs mean callers must rely on platform detection to avoid silently treating an unavailable FF-A start method as initialized. Constants must remain synchronized with the FF-A ABI documentation and `tpm_crb_ffa.c`.

## Test Signals
Build matrix coverage with FF-A enabled, module-only, built-in, and disabled configurations; CRB start-method tests for both command and locality request qualifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_crb_ffa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_ftpm_tee.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_ftpm_tee.c

## Purpose
Implements a TPM 2.0 class device backed by Microsoft-compatible firmware TPM trusted application running in a GP-compliant OP-TEE environment.

## Important APIs, Types, And Functions
The TPM operation is `ftpm_tee_tpm_op_send()`, registered in `ftpm_tee_tpm_ops` with `TPM_OPS_AUTO_STARTUP`. Probe and removal are shared by both platform and TEE-client bindings through `ftpm_tee_probe_generic()` and `ftpm_tee_remove_generic()`. `ftpm_tee_match()` selects OP-TEE GP contexts, and module init registers both the platform and TEE client drivers.

## Control Flow
Probe allocates private state, opens a TEE context, opens a session to the fTPM TA UUID, allocates one shared memory buffer sized for command plus response, allocates a TPM chip, marks it TPM2 and synchronous, and registers it. Send validates command length, copies the TPM command into shared memory offset zero, invokes `FTPM_OPTEE_TA_SUBMIT_COMMAND`, reads the response from the second half of shared memory, validates the TPM header length against minimum, TA limit, and caller buffer, then copies it back.

## State And Persistence
Per-device state stores the TEE context, session id, shared memory handle, and TPM chip pointer. Persistent TPM NV state is owned by the TA/TEE implementation, not this driver.

## Dependencies And Integration Points
Depends on the Linux TEE client API, `tpm_chip_alloc()`, `tpm_chip_register()`, OF compatible `microsoft,ftpm`, and the OP-TEE fTPM TA UUID. Shutdown closes the TEE session and context for platform devices.

## Risks And Edge Cases
Shared memory is reused for all commands and assumes synchronous TPM core serialization. TA return values are passed back directly when invocation succeeds but TA status is nonzero. Response length is trusted only after header validation, but malformed short responses fail with `-EIO`. Probe must clean up partially opened TEE contexts and sessions in the correct order.

## Test Signals
OP-TEE TA discovery, platform and tee-client probe paths, command and response size limit tests, malformed response headers, TA invocation failure, removal/shutdown cleanup, and TPM2 startup/self-test through the TPM core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_ftpm_tee.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_ftpm_tee.h -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_ftpm_tee.h

## Purpose
Defines the fTPM OP-TEE command ids, shared-buffer limits, and private per-device structure used by `tpm_ftpm_tee.c`.

## Important APIs, Types, And Functions
Key definitions are `FTPM_OPTEE_TA_SUBMIT_COMMAND`, `FTPM_OPTEE_TA_EMULATE_PPI`, `MAX_COMMAND_SIZE`, `MAX_RESPONSE_SIZE`, and `struct ftpm_tee_private` containing the TPM chip, TEE session, TEE context, and shared memory object.

## Control Flow
The header has no executable flow, but it fixes the memory layout assumption used by the send path: command bytes at offset zero and response bytes at `MAX_COMMAND_SIZE`.

## State And Persistence
`struct ftpm_tee_private` is runtime state only. TA-side persistent TPM state is not represented in this header.

## Dependencies And Integration Points
Includes TEE, TPM, and UUID kernel headers. It is private to the fTPM TEE driver and mirrors the TA command ABI.

## Risks And Edge Cases
Command and response size constants must remain compatible with the TA. `FTPM_OPTEE_TA_EMULATE_PPI` is defined but unused by the current driver, so PPI behavior is not surfaced here.

## Test Signals
Compile coverage, shared memory size validation, and ABI compatibility checks with the matching OP-TEE fTPM TA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_ftpm_tee.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_i2c_atmel.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_i2c_atmel.c

## Purpose
Supports Atmel AT97SC3204T I2C TPMs whose protocol sends raw TPM command buffers over I2C and later reads raw TPM responses, without the normal TIS locality/status register model.

## Important APIs, Types, And Functions
Defines `struct priv_data` with a cached short response buffer and length. TPM class operations are `i2c_atmel_send()`, `i2c_atmel_recv()`, `i2c_atmel_read_status()`, `i2c_atmel_cancel()`, and `i2c_atmel_req_canceled()`.

## Control Flow
Probe checks `I2C_FUNC_I2C`, allocates a TPM chip and private data, sets conservative default timeouts, and registers the chip. Send writes the complete command with `i2c_master_send()` and treats partial sends as errors. Status polling attempts an I2C read; failed reads mean not ready, successful reads cache the response prefix and return `ATMEL_STS_OK`. Recv uses the cached TPM header to determine response length, copies cached data when complete, or re-reads the expected response length.

## State And Persistence
Private state caches the latest response prefix until recv consumes it. There is no explicit locality, cancellation, or persistent software state.

## Dependencies And Integration Points
Integrates with the TPM core through `TPM_OPS_AUTO_STARTUP` and standard send/status/recv callbacks. Device matching is through I2C id `tpm_i2c_atmel` or OF compatible `atmel,at97sc3204t`.

## Risks And Edge Cases
The hardware has no known probe command, so registration relies on TPM startup detecting invalid devices. Cancellation is unsupported. Cached short responses depend on the header being present in the first read. Re-reading after partial cache assumes the device leaves the completed response readable until the next command.

## Test Signals
Full and partial response reads, failed-read polling behavior, partial I2C send errors, timeout handling, small response fast path, OF/I2C matching, and suspend/resume through TPM PM helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_i2c_atmel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_i2c_infineon.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_i2c_infineon.c

## Purpose
Implements the legacy Infineon SLB9635/SLB9645 I2C TPM protocol using TIS-like register semantics over vendor-specific I2C transfers.

## Important APIs, Types, And Functions
Global `struct tpm_inf_dev tpm_dev` stores the single supported client, locality, chip type, adapter limit, command buffer, and chip. Low-level helpers are `iic_tpm_read()`, `iic_tpm_write_generic()`, `iic_tpm_write()`, and `iic_tpm_write_long()`. TIS operations include `request_locality()`, `release_locality()`, `tpm_tis_i2c_status()`, `get_burstcount()`, `wait_for_stat()`, `recv_data()`, `tpm_tis_i2c_recv()`, and `tpm_tis_i2c_send()`.

## Control Flow
Probe enforces a single client and full I2C functionality, then initializes a TPM chip with TIS timeouts. Initialization requests locality zero, reads `TPM_DID_VID`, identifies SLB9635 or SLB9645, and registers the chip. Reads either use combined transfer for SLB9645 or split address/data messages for SLB9635, with retries, guard sleeps, and adapter-limit fallback. Send requests locality, enters command-ready state, writes FIFO data in burst chunks, verifies `DATA_EXPECT`, writes `GO`, and leaves response polling to core. Recv reads header, validates expected length, drains remaining data, checks for leftover data, resets ready, sleeps for cleanup, and releases locality.

## State And Persistence
Uses global singleton state for client, locality, adapter-limit fallback, and chip pointer. TPM persistent state remains in hardware.

## Dependencies And Integration Points
Depends on raw `__i2c_transfer()` under adapter segment lock, TPM class callbacks, I2C/OF IDs for Infineon TPMs, and TPM PM helpers.

## Risks And Edge Cases
Singleton state prevents multiple devices. Split-transfer timing and guard sleeps are chip-specific. Locality release happens on recv and error paths, so missing recv after send could hold locality. Adapter quirk fallback changes transfer chunking after `-EOPNOTSUPP`. Vendor ID byte order is easy to misinterpret.

## Test Signals
SLB9635 split protocol, SLB9645 combined protocol, I2C NAK retry, adapter block-size fallback, locality timeout, burstcount timeout, malformed response sizes, leftover data detection, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_i2c_infineon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_i2c_nuvoton.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_i2c_nuvoton.c

## Purpose
Supports Nuvoton/Winbond WPCT301, NPCT501, and NPCT6xx TPMs over their I2C FIFO register protocol, including optional data-available interrupt acceleration.

## Important APIs, Types, And Functions
Private data contains IRQ number, interrupt counter, and read waitqueue. Important helpers are `i2c_nuvoton_read_buf()`, `i2c_nuvoton_write_buf()`, `i2c_nuvoton_read_status()`, `i2c_nuvoton_write_status()`, `i2c_nuvoton_wait_for_stat()`, `i2c_nuvoton_recv_data()`, `i2c_nuvoton_recv()`, `i2c_nuvoton_send()`, `i2c_nuvoton_int_handler()`, and `get_vid()`.

## Control Flow
Probe validates VID/DID/RID, allocates chip/private state, marks TPM2 when matched by data, sets default timeouts, optionally requests a level-low IRQ, and registers the chip. Send retries command setup, writes `COMMAND_READY`, waits for readiness, writes FIFO chunks constrained by burst count and 32-byte I2C block size, verifies `EXPECT`, writes `GO`, computes ordinal duration, and waits for data availability. Recv retries up to five times, optionally uses response-retry status, reads an initial burst containing the TPM header, validates expected length, drains remaining bytes, checks for leftover data, and returns ready state.

## State And Persistence
State is per-chip IRQ/read queue metadata and transient FIFO buffer contents. Persistent TPM state is hardware-owned.

## Dependencies And Integration Points
Uses SMBus block I/O helpers, optional OF match data for TPM2, TPM core timeouts/duration calculation, TPM PM helpers, and I2C device-tree interrupt registration.

## Risks And Edge Cases
The IRQ only signals data availability and is disabled in the handler, so missed re-enable or spurious interrupts can force timeouts. `get_vid()` has a firmware-revision fallback that reads FIFO offset as an alternate ID. Send keeps `count` outside the retry loop, so retry logic must be evaluated carefully if a partial write path fails late. Level-low IRQs cannot be shared.

## Test Signals
Polling and IRQ modes, VID fallback path, response retry, malformed response length, burstcount zero timeout, command duration timeout, TPM2 match data, interrupt disable/re-enable behavior, and PM suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_i2c_nuvoton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_ibmvtpm.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_ibmvtpm.c

## Purpose
Implements IBM Power virtual TPM support over VIO CRQ queues and hypervisor calls, registering a TPM chip backed by an RTCE DMA buffer.

## Important APIs, Types, And Functions
Core operations are `tpm_ibmvtpm_send()`, `tpm_ibmvtpm_recv()`, `tpm_ibmvtpm_status()`, and `tpm_ibmvtpm_req_canceled()`. CRQ lifecycle helpers include `ibmvtpm_send_crq()`, `ibmvtpm_crq_send_init()`, `ibmvtpm_crq_get_version()`, `ibmvtpm_crq_get_rtce_size()`, `ibmvtpm_crq_send_init_complete()`, `ibmvtpm_reset_crq()`, `ibmvtpm_crq_get_next()`, `ibmvtpm_crq_process()`, and `ibmvtpm_interrupt()`.

## Control Flow
Probe allocates a TPM chip, driver state, one CRQ page, maps it for DMA, registers or resets the hypervisor CRQ, requests the VIO IRQ, enables interrupts, initializes waitqueues and locks, sends init/version/RTCE-size CRQs, waits for RTCE buffer allocation, sets TPM2 flag for compatible `IBM,vtpm20`, and registers the chip. Send waits for any in-flight command, copies the command into RTCE buffer under lock, marks processing, sends a CRQ pointing to the DMA handle, and retries once after `H_CLOSED` by resuming CRQ. Interrupt processing walks CRQ responses, handles init negotiation, allocates/maps RTCE buffer, records version, records response length, clears processing, and wakes waiters. Recv copies the RTCE response and clears it.

## State And Persistence
Runtime state includes CRQ ring index, DMA mappings, RTCE buffer and size, response length, version, waitqueues, spinlock, and processing flag. Persistent vTPM state is owned by the hypervisor/server side.

## Dependencies And Integration Points
Depends on Power VIO, `plpar_hcall_norets()` Hcalls, DMA mapping, IRQ handling, and TPM core registration. PM hooks send prepare-to-suspend and re-enable/init CRQ on resume.

## Risks And Edge Cases
Command completion races with Hcall return, so `tpm_processing_cmd` is set before sending CRQ. Error paths must unmap DMA and free pages exactly once. `tpm_ibmvtpm_send()` returns zero even after some CRQ send failures after clearing the processing flag, which is worth scrutiny. Probe waits only one second for RTCE buffer response.

## Test Signals
CRQ init handshake, version and RTCE-size responses, DMA mapping failure, H_CLOSED retry on send, suspend/resume, interrupt-driven command completion, TPM2 compatible matching, and cleanup after partial probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_ibmvtpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_ibmvtpm.h -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_ibmvtpm.h

## Purpose
Defines IBM vTPM CRQ message layout, device runtime state, and message constants shared by the IBM VIO vTPM implementation.

## Important APIs, Types, And Functions
Key types are `struct ibmvtpm_crq`, `struct ibmvtpm_crq_queue`, and `struct ibmvtpm_dev`. Constants define CRQ page size, init commands, valid markers, response bit, and vTPM message ids for get version, TPM command, RTCE buffer size, and suspend preparation.

## Control Flow
The header encodes the ring and CRQ command protocol consumed by `tpm_ibmvtpm.c`; responses are distinguished by `VTPM_MSG_RES` and valid bytes.

## State And Persistence
`struct ibmvtpm_dev` tracks the VIO device, CRQ ring, DMA handles, RTCE buffer, locks, waitqueues, response length, version, and command-processing flag.

## Dependencies And Integration Points
Depends on VIO and DMA types via the C file includes. The packed, aligned CRQ layout must match the hypervisor register/memory protocol.

## Risks And Edge Cases
Field endian annotations are part of the ABI. Changing constants or packing can break hypervisor communication. RTCE buffer is declared `void __iomem *` though allocated with `kmalloc()`, which can complicate static analysis.

## Test Signals
CRQ byte layout validation, endian conversion tests, ring index wrap, and ABI compatibility with IBM Power hypervisor vTPM devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_ibmvtpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_infineon.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_infineon.c

## Purpose
Implements legacy Infineon SLD9630/SLB9635 TPM access over PNP-discovered I/O ports or MMIO, using Infineon's vendor-layer framing and WTX wait-extension protocol.

## Important APIs, Types, And Functions
Global `struct tpm_inf_dev tpm_dev` stores resource type and register locations. Low-level accessors are `tpm_data_in/out()` and `tpm_config_in/out()`. Transport helpers include `empty_fifo()`, `wait()`, `wait_and_send()`, `tpm_wtx()`, `tpm_wtx_abort()`, `tpm_inf_send()`, and `tpm_inf_recv()`. PNP lifecycle is `tpm_inf_pnp_probe()`, `tpm_inf_pnp_remove()`, and `tpm_inf_resume()`.

## Control Flow
Probe obtains I/O or memory resources, requests/remaps them, reads vendor/product/version through config registers, programs data-register base, activates the device, disables reset/low-power/IRQ control, allocates a TPM chip, and registers it. Send clears FIFO, waits for transmit FIFO empty, emits vendor-layer header, data header, and command bytes. Recv reads a four-byte vendor header, handles data frames by copying out the TPM payload, acknowledges or aborts WTX packets up to a maximum, and reports error frames.

## State And Persistence
Global state records the active resource mapping and data/config offsets. `number_of_wtx` counts WTX packets during a receive. Hardware configuration is reprogrammed on resume.

## Dependencies And Integration Points
Uses PNP IDs `IFX0101`/`IFX0102`, port I/O or MMIO accessors, TPM core callbacks, and TPM PM helpers.

## Risks And Edge Cases
The driver is singleton and global-state based. WTX handling can loop until the maximum is reached, then aborts. Receive code assumes vendor frame sizes and shifts payload in place. Resource cleanup differs for port and MMIO paths and must match probe branch. Cancellation is effectively unsupported.

## Test Signals
PNP port and MMIO resource discovery, vendor/product ID reads, WTX grant and abort behavior, malformed vendor frames, FIFO drain timeout, resume reconfiguration, and conflict with generic `tpm_tis` on IFX IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_infineon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_loongson.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_loongson.c

## Purpose
Registers a TPM 2.0 device backed by the Loongson security engine MFD interface.

## Important APIs, Types, And Functions
Defines `struct tpm_loongson_cmd` for the engine command header and TPM callbacks `tpm_loongson_send()` and `tpm_loongson_recv()`. `tpm_loongson_probe()` initializes the engine and TPM chip.

## Control Flow
Probe obtains `SE_ENGINE_TPM` from the parent Loongson security engine, initializes command id and data offset, allocates a TPM chip, marks it TPM2 and IRQ-capable, stores the engine as chip drvdata, and registers the chip. Send bounds-checks the engine buffer, sets data length, copies the TPM command into the engine data buffer, and calls `loongson_se_send_engine_cmd()`. Recv copies the returned data buffer according to `command_ret->data_len`.

## State And Persistence
Runtime state is owned mostly by `struct loongson_se_engine`: command headers, return headers, data buffer, buffer size, and offset. TPM persistent state lives in the security engine.

## Dependencies And Integration Points
Depends on `linux/mfd/loongson-se.h`, platform device binding `tpm_loongson`, and the TPM core.

## Risks And Edge Cases
There is minimal validation of response format beyond buffer length. The driver assumes the engine command path is synchronous enough for TPM core send/recv ordering. It sets IRQ flag but does not implement status/interrupt callbacks, relying on the engine command completion semantics.

## Test Signals
Engine initialization failure, command-size boundary, response-size boundary, TPM2 startup, command timeout behavior in the MFD engine, and platform-device binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_loongson.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_nsc.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_nsc.c

## Purpose
Supports legacy National Semiconductor TPMs discovered through Super I/O index registers and exposed as a two-byte I/O-port command/data interface.

## Important APIs, Types, And Functions
Private state is `struct tpm_nsc_priv` with base port. Helpers include `wait_for_stat()`, `nsc_wait_for_ready()`, `tpm_nsc_send()`, `tpm_nsc_recv()`, `tpm_nsc_cancel()`, `tpm_nsc_status()`, `tpm_read_index()`, and `tpm_write_index()`.

## Control Flow
Module init probes Super I/O IDs at default and alternate bases, registers a platform driver/device, enables the DPM module, requests the two-port region, allocates a TPM chip, and registers it. Send writes a cancel command as a hardware workaround, waits for ready and input-buffer states, enters normal mode, writes command bytes, and terminates with EOC. Recv waits for F0, checks normal mode, reads bytes until F0/EOC, validates the TPM header size, and returns the response length.

## State And Persistence
State is a platform device pointer and per-chip I/O base. Super I/O configuration persists in hardware while the module is loaded.

## Dependencies And Integration Points
Requires port I/O, platform device registration, TPM core callbacks, and TPM PM suspend/resume helpers.

## Risks And Edge Cases
The driver manually calls remove logic from module exit before unregistering the platform device, so lifetime assumptions are old-style. Back-to-back commands require the cancel workaround. Timeouts are long and polling-based. It reads up to caller `count` before knowing exact response size.

## Test Signals
Super I/O ID detection, base address extraction, region conflict, send/recv mode transitions, cancel behavior, response size validation, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_nsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_ppi.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_ppi.c

## Purpose
Adds the ACPI Physical Presence Interface sysfs group under TPM devices, exposing firmware-mediated TPM operation requests, responses, transition actions, and supported operation policy.

## Important APIs, Types, And Functions
The public entry point is `tpm_add_ppi()`. Sysfs handlers include version, request show/store, transition action, response, TCG operations, and vendor-specific operations. `tpm_eval_dsm()` wraps ACPI DSM evaluation, and `cache_ppi_operations()` fills a global operation cache protected by `tpm_ppi_lock`.

## Control Flow
`tpm_add_ppi()` checks for an ACPI handle and PPI DSM version function, caches the firmware version string, and appends the `ppi` attribute group to the TPM chip. Request show calls DSM GETREQ and supports two- or three-integer packages, printing parameterized request 23 specially. Request store chooses SUBREQ or SUBREQ2, formats argv4 differently for PPI version compatibility, evaluates DSM, and maps firmware return codes. Operation show paths lazily cache GETOPR results for request ids 0..255 and print human-readable policy strings.

## State And Persistence
The kernel caches the PPI version in `chip->ppi_version` and operation policies in global `ppi_operations_cache`. Submitted requests and responses persist in firmware/BIOS variables outside the driver.

## Dependencies And Integration Points
Depends on ACPI DSM GUID `3DDDFAA6-361B-4EB4-A424-8D10089D1653`, TPM chip ACPI handles, sysfs attribute groups, and firmware PPI versions 1.0 through 1.3.

## Risks And Edge Cases
Firmware returns vary widely, so handlers accept legacy buffer/package argument forms. The operation cache is global, not per-chip, which can be wrong on systems with multiple TPM ACPI handles. Sysfs buffers can be filled with many operation lines, so bounds rely on `sysfs_emit_at()`.

## Test Signals
PPI versions 1.0, 1.1, 1.2, and 1.3; request 23 with parameter; malformed DSM packages; denied and BIOS-failure responses; operation cache population; absence of PPI DSM; and multi-TPM ACPI scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_ppi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_svsm.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_svsm.c

## Purpose
Implements an AMD SVSM vTPM driver for SEV-SNP guests, forwarding TPM commands to a Secure VM Service Module using the SVSM vTPM protocol.

## Important APIs, Types, And Functions
Private state is `struct tpm_svsm_priv` with one page-sized contiguous buffer. TPM callback `tpm_svsm_send()` uses `svsm_vtpm_cmd_request_fill()`, `snp_svsm_vtpm_send_command()`, and `svsm_vtpm_cmd_response_parse()`. Probe and remove are `tpm_svsm_probe()` and `tpm_svsm_remove()`.

## Control Flow
Probe allocates private state and one page buffer, allocates a managed TPM chip, stores private state on the chip device, marks the chip synchronous, probes TPM2 capabilities, registers the chip, and logs TPM version. Send formats command plus SVSM header into the internal physically contiguous buffer, performs the SVSM call in place, and parses the response back into the caller buffer.

## State And Persistence
Runtime state is the one-page command/response buffer. vTPM persistent state is owned by the SVSM.

## Dependencies And Integration Points
Depends on `linux/tpm_svsm.h`, `asm/sev.h`, a platform device named `tpm-svsm`, and TPM core registration.

## Risks And Edge Cases
The maximum buffer is one page; oversized TPM commands rely on the SVSM helper to reject them. The same buffer is reused for command and response. The driver is registered with `module_platform_driver_probe()`, so runtime unbind is intentionally unsupported and remove is exit-only.

## Test Signals
SEV-SNP guest discovery, one-page command limit, malformed SVSM responses, TPM2 probe, module unload, and SVSM call error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_svsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis.c

## Purpose
Provides the memory-mapped/PNP/platform front-end for the generic TPM TIS FIFO core.

## Important APIs, Types, And Functions
Defines `struct tpm_info` resource/IRQ input and `struct tpm_tis_tcg_phy` containing `tpm_tis_data` plus MMIO base. PHY operations are `tpm_tcg_read_bytes()` and `tpm_tcg_write_bytes()`. Probe paths include `tpm_tis_pnp_init()`, `tpm_tis_plat_probe()`, `tpm_tis_force_device()`, and shared `tpm_tis_init()`.

## Control Flow
Initialization checks whether an ACPI `MSFT0101` TPM2 device should be handled by CRB instead, maps the memory resource, selects IRQ use based on module parameter and device data, enables iTPM workaround if forced or ACPI HID `INTC0102`, then calls `tpm_tis_core_init()`. Module init may create a forced x86 platform device at `0xFED40000`, registers the platform driver, and optionally the PNP driver. Remove unregisters the TPM chip and delegates hardware cleanup to the core.

## State And Persistence
State is per-device mapped MMIO and `tpm_tis_data`; module parameters `interrupts`, `itpm`, `force`, and `hid` affect probe behavior. No persistent data is stored in software.

## Dependencies And Integration Points
Depends on ACPI TPM2 table interpretation, PNP IDs, OF compatibles, platform resources, and `tpm_tis_core_init()`. It integrates with TPM PM by using `tpm_tis_resume()`.

## Risks And Edge Cases
`MSFT0101` devices with non-memory-mapped ACPI TPM2 start methods must be left to CRB. Forced probing can conflict with firmware-described devices. PREEMPT_RT flush reads reduce latency spikes but add MMIO reads. PNP IDs overlap with older vendor drivers such as Infineon.

## Test Signals
PNP and platform probing, forced x86 probe, ACPI TPM2 CRB handoff, MMIO read/write modes, iTPM workaround selection, IRQ module parameter behavior, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_core.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_core.c

## Purpose
Implements the transport-independent TPM TIS/PTP FIFO state machine used by MMIO, SPI, I2C, and platform-specific PHY front-ends.

## Important APIs, Types, And Functions
Exports `tpm_tis_core_init()`, `tpm_tis_remove()`, and `tpm_tis_resume()`. Main callbacks are `tpm_tis_status()`, `tpm_tis_recv()`, `tpm_tis_send()`, `tpm_tis_ready()`, `tpm_tis_request_locality()`, and `tpm_tis_relinquish_locality()`. Important helpers include `wait_for_tpm_stat()`, `wait_startup()`, `check_locality()`, `get_burstcount()`, `recv_data()`, `tpm_tis_send_data()`, IRQ probing/handler helpers, timeout/duration override helpers, `probe_itpm()`, and `tpm_tis_clkrun_enable()`.

## Control Flow
Core init allocates a TPM chip, installs default maximum timeouts, stores PHY ops, reads vendor ID, applies vendor quirks, maps Intel Bay Trail CLKRUN control when needed, waits for access-valid, reads and disables interrupt capabilities, requests locality zero, probes TPM version, reads revision, detects iTPM behavior, bootstraps the chip, optionally validates/probes IRQ operation, and registers the TPM chip. Send acquires FIFO readiness, writes all but the last byte in burst chunks while checking `DATA_EXPECT`, writes the last byte, verifies CRC when available, writes `GO`, and waits for data availability in IRQ mode. Recv reads header and body by burst count, validates expected length, checks for leftover data, verifies CRC, and retries recoverable reads with `RESPONSE_RETRY`.

## State And Persistence
`struct tpm_tis_data` stores locality, locality reference count, IRQ, interrupt mask, waitqueues, quirk flags, unhandled IRQ counters, manufacturer id, CLKRUN mapping, PHY ops, RNG quality, and polling delays. Hardware state includes locality ownership, interrupt enable/status, FIFO contents, and TPM status bits.

## Dependencies And Integration Points
Depends on PHY callbacks from `tpm_tis_core.h`, TPM core startup/bootstrap/registration, TPM1/TPM2 capability helpers, DMI for interrupt-storm diagnostics, ACPI handles from front-ends, and platform PM.

## Risks And Edge Cases
Locality reference counting must balance across nested TPM core operations. IRQs are probed by causing a TPM command and disabled if unconfirmed; interrupt storms force polling and schedule IRQ freeing outside interrupt context. Vendor quirks alter cancellation, timeouts, durations, and status-valid retry behavior. Invalid `TPM_STS` values dump stack for misuse forensics. CLKRUN manipulation is x86/Bay Trail specific and reference-counted.

## Test Signals
FIFO send/recv with burst boundaries, TPM1 and TPM2 startup, locality nesting, IRQ probe success/failure, interrupt storms, response retry, CRC-enabled PHYs, vendor timeout overrides, iTPM detection, ST/Winbond cancellation quirks, Bay Trail CLKRUN, and resume interrupt re-enable/self-test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_core.h -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_core.h

## Purpose
Defines the shared TIS register layout, status bits, interrupt bits, quirks, private data, PHY interface, inline endian-aware register helpers, and exported core entry points.

## Important APIs, Types, And Functions
Key types are `enum tis_access`, `enum tis_status`, `enum tis_int_flags`, `enum tis_defaults`, `enum tpm_tis_flags`, `struct tpm_tis_data`, `enum tpm_tis_io_mode`, and `struct tpm_tis_phy_ops`. Inline helpers wrap PHY reads/writes for 8/16/32-bit little-endian access and optional CRC verification.

## Control Flow
The header defines address macros such as `TPM_ACCESS(l)`, `TPM_STS(l)`, `TPM_DATA_FIFO(l)`, `TPM_DID_VID(l)`, and `TPM_RID(l)` that all PHY front-ends use. `is_bsw()` provides an x86 Bay Trail check for CLKRUN handling.

## State And Persistence
`struct tpm_tis_data` is the persistent runtime object for each TIS chip while the driver is bound, carrying chip pointer, locality state, IRQ bookkeeping, waitqueues, PHY ops, and timing details.

## Dependencies And Integration Points
Included by MMIO, SPI, I2C, SynQuacer, and core TIS files. Exports `tpm_tis_core_init()`, `tpm_tis_remove()`, and, under PM, `tpm_tis_resume()`.

## Risks And Edge Cases
Address macros encode locality shifts differently from some bus-specific protocols, so front-ends must translate carefully. PHY ops promise little-endian data; violating that breaks core register interpretation. `is_bsw()` depends on x86 CPU model definitions.

## Test Signals
Build coverage across all TIS PHYs, endian conversion tests for 16/32-bit helpers, CRC callback behavior, locality address calculation, and PM conditional declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_i2c.c

## Purpose
Implements the native TCG PTP TPM 2.0 I2C transport as a PHY under the generic TIS core.

## Important APIs, Types, And Functions
`struct tpm_tis_i2c_phy` stores the I2C client, guard-time settings, and I/O buffer. Key helpers are `tpm_tis_i2c_address_to_register()`, `tpm_tis_i2c_retry_transfer_until_ack()`, `tpm_tis_i2c_sanity_check_read()`, `tpm_tis_i2c_read_bytes()`, `tpm_tis_i2c_write_bytes()`, `tpm_tis_i2c_verify_crc()`, and `tpm_tis_i2c_init_guard_time()`.

## Control Flow
Probe allocates PHY and buffer, sets default cancellation semantics, reads I2C interface capability to derive guard time, selects locality zero, enables data checksum, and calls `tpm_tis_core_init()` in polling mode. Reads write the register selector, read data in I2C block chunks, retry and sanity-check reserved-zero bits. Writes send register plus data chunks. CRC verification reads `TPM_DATA_CSUM` and compares reflected CCITT CRC with the command or response bytes.

## State And Persistence
Per-device state tracks guard-time requirements for read/write sequences, min/max guard delay, and a reusable I/O buffer. Locality is forced to zero through `TPM_LOC_SEL`.

## Dependencies And Integration Points
Depends on I2C block transfer limits, CRC-CCITT, OF matches for Infineon/Nuvoton/TCG I2C TPMs, and the TIS core PHY contract.

## Risks And Edge Cases
Register translation must map TIS core addresses into native I2C register addresses. Guard-time interpretation is vendor-specific and required after ACK and NACK sequences. Reserved-zero sanity failures trigger retries and protect against bus corruption. Enabling checksum means all command/response paths depend on CRC register correctness.

## Test Signals
Guard-time capability parsing, register translation, large FIFO chunking, NACK retries, reserved-zero sanity failures, CRC mismatch, locality selection, checksum enable, and TIS core registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_i2c_cr50.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_i2c_cr50.c

## Purpose
Implements the Google Cr50/Ti50 I2C TPM protocol, which is TIS-like but requires special transaction timing, four-byte status accesses, interrupt-based readiness, and custom burst handling.

## Important APIs, Types, And Functions
Private state is `struct tpm_i2c_cr50_priv_data` with IRQ, completion, and write buffer. Key functions are `tpm_cr50_i2c_read()`, `tpm_cr50_i2c_write()`, `tpm_cr50_request_locality()`, `tpm_cr50_release_locality()`, `tpm_cr50_i2c_tis_status()`, `tpm_cr50_i2c_get_burst_and_status()`, `tpm_cr50_i2c_tis_send()`, `tpm_cr50_i2c_tis_recv()`, and `tpm_cr50_i2c_probe()`.

## Control Flow
Probe checks I2C support, allocates a TPM2 chip and private state, optionally marks firmware-power-managed, requests a falling-edge IRQ with `IRQF_NO_AUTOEN`, requests locality zero, reads DID/VID, validates Cr50/Ti50 IDs, releases locality, and registers. I2C reads send the register address, wait for IRQ or fallback delay, then read data. Writes prepend register address, send, then wait for readiness. Send waits for command-ready, writes FIFO chunks based on burst count minus address byte, verifies `DATA_EXPECT` clears, and writes four-byte `GO`. Recv reads the first full burst, derives expected length, drains remaining bursts, and checks `DATA_AVAIL` clears.

## State And Persistence
State is per-chip IRQ/completion and temporary write buffer. Locality handling locks the I2C adapter segment between request and release, effectively serializing TPM access.

## Dependencies And Integration Points
Matches ACPI `GOOG0005` and OF `google,cr50`, integrates directly with TPM class ops rather than `tpm_tis_core`, and uses firmware-power-managed device property.

## Risks And Edge Cases
All four status bytes must be accessed together. No IRQ mode falls back to fixed 20 ms delays. Locality request returns while holding the I2C bus lock until release, so error paths must unlock. Burst count must stay within 63-byte max minus address overhead. The error path condition around aborting pending transactions should be checked against status semantics.

## Test Signals
IRQ and no-IRQ modes, Cr50 and Ti50 IDs, locality lock/unlock on failures, four-byte status accesses, burst chunk boundaries, TPM2 startup, firmware-power-managed property, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_i2c_cr50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_spi.h -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_spi.h

## Purpose
Defines the SPI PHY structure and exported helper/probe functions shared by the generic TIS SPI driver and the Cr50 SPI specialization.

## Important APIs, Types, And Functions
Defines `struct tpm_tis_spi_phy` with embedded `tpm_tis_data`, SPI device pointer, flow-control callback, completion, wake timing, and I/O buffer. Declares `tpm_tis_spi_init()`, `tpm_tis_spi_transfer()`, `cr50_spi_probe()`, and optional `tpm_tis_spi_resume()`.

## Control Flow
The inline `to_tpm_tis_spi_phy()` converts from core data to SPI PHY. Conditional stubs allow the generic SPI driver to compile without Cr50 support.

## State And Persistence
The PHY struct persists for the lifetime of an SPI TPM device and carries both generic SPI transaction state and Cr50-specific wake/ready fields used by the specialized implementation.

## Dependencies And Integration Points
Included by `tpm_tis_spi_main.c` and `tpm_tis_spi_cr50.c`, and depends on the TIS core interface.

## Risks And Edge Cases
The flow-control callback is mandatory for transfers; front-ends must initialize it. Conditional stubs mean device IDs can resolve to `-ENODEV` when Cr50 support is disabled.

## Test Signals
Build matrix with and without `CONFIG_TCG_TIS_SPI_CR50`, SPI probe dispatch for generic and Cr50 IDs, and resume declaration under PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_spi_cr50.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_spi_cr50.c

## Purpose
Specializes the TIS SPI PHY for Google Cr50 firmware timing, wake, ready-IRQ, and firmware-version behavior.

## Important APIs, Types, And Functions
`struct cr50_spi_phy` wraps `tpm_tis_spi_phy` with access-delay tracking, mutex, last-access timestamp, and IRQ confirmation state. Important functions are `cr50_spi_irq_handler()`, `cr50_ensure_access_delay()`, `cr50_wake_if_needed()`, `cr50_spi_flow_control()`, `tpm_tis_spi_cr50_transfer()`, `cr50_print_fw_version()`, `cr50_spi_probe()`, and `tpm_tis_spi_resume()`.

## Control Flow
Probe allocates Cr50 PHY, sets custom flow control, initializes wake and access-delay state, requests an optional rising-edge ready IRQ, initializes the generic SPI TIS layer in polling IRQ mode, prints firmware version from `TPM_CR50_FW_VER`, and marks the chip firmware-power-managed by default. Transfers take a mutex, ensure required inter-transaction delay or IRQ confirmation, wake Cr50 by toggling chip select after sleep, delegate to `tpm_tis_spi_transfer()`, then update last access. Resume resets wake timing before calling core resume.

## State And Persistence
Runtime state tracks when Cr50 may sleep, whether ready IRQs are confirmed, current access delay policy, and the embedded SPI/TIS core state. TPM persistent state remains in the device firmware.

## Dependencies And Integration Points
Depends on the generic SPI TIS transfer engine, Cr50 OF/SPI dispatch in `tpm_tis_spi_main.c`, TPM core resume, and the firmware-power-managed property.

## Risks And Edge Cases
Ready IRQ is used only after confirmation; otherwise fixed delays are used. Jiffies wrap can cause harmless extra delays but is acknowledged. Flow control waits until bit 0 is set and times out with `-EBUSY`. Wake toggling assumes asserting chip select is sufficient after sleep.

## Test Signals
Cr50 SPI with and without IRQ, IRQ confirmation fallback, inter-transaction delay, wake-after-sleep behavior, flow-control timeout, firmware-version readout, firmware-power-managed property, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_spi_cr50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_spi_main.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_spi_main.c

## Purpose
Implements the generic native SPI TPM TIS/PTP PHY and SPI driver dispatch layer.

## Important APIs, Types, And Functions
Exports `tpm_tis_spi_transfer()` and `tpm_tis_spi_init()`. Transfer helpers are `tpm_tis_spi_flow_control()`, `tpm_tis_spi_transfer_half()`, `tpm_tis_spi_transfer_full()`, `tpm_tis_spi_read_bytes()`, and `tpm_tis_spi_write_bytes()`. Probe dispatch uses `tpm_tis_spi_probe()`, `tpm_tis_spi_driver_probe()`, and device-id/of-match function pointers.

## Control Flow
Generic probe allocates the SPI PHY, sets standard flow control, enables `SPI_TPM_HW_FLOW` for half-duplex controllers, chooses device IRQ if present, initializes completion, and calls `tpm_tis_spi_init()`. Full-duplex transfer locks the SPI bus, sends a four-byte TPM SPI header with chip-select held, performs flow control by clocking one-byte reads until ready, transfers up to 64 data bytes, and repeats. Half-duplex transfer builds one SPI message with command, address, and data phases so capable controllers can manage hardware flow control. Driver probe dispatches to Cr50 or generic probe based on OF/SPI id data.

## State And Persistence
Per-device state stores SPI device, flow-control callback, completion, wake-after timestamp, and reusable I/O buffer. No persistent TPM state is stored.

## Dependencies And Integration Points
Integrates with `tpm_tis_core_init()` through PHY ops, SPI controller flags, OF compatibles, ACPI `SMO0768`, and optional Cr50 probe.

## Risks And Edge Cases
Full-duplex flow control requires bus lock and explicit chip-select deactivation on error. Half-duplex controllers depend on controller-level `SPI_TPM_HW_FLOW`. Maximum SPI frame is 64 bytes, so large FIFO transfers are chunked. Probe dispatch must handle missing id match data cleanly.

## Test Signals
Full-duplex and half-duplex controllers, flow-control timeout, chunked reads/writes, error cleanup deasserting chip select, IRQ and no-IRQ modes, generic device IDs, Cr50 dispatch, and PM resume callback wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_spi_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_synquacer.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_synquacer.c

## Purpose
Provides a Socionext SynQuacer MMIO TPM front-end for the generic TIS core, using byte-wise 16/32-bit accesses required by the platform controller.

## Important APIs, Types, And Functions
Defines `struct tpm_tis_synquacer_info` and `struct tpm_tis_synquacer_phy`. PHY ops are `tpm_tis_synquacer_read_bytes()` and `tpm_tis_synquacer_write_bytes()`, wired through `tpm_tcg_bw`. Probe and init are `tpm_tis_synquacer_probe()` and `tpm_tis_synquacer_init()`.

## Control Flow
Probe obtains the MMIO resource, disables IRQ support by setting `irq = -1`, maps the resource, and calls `tpm_tis_core_init()`. Read operations perform byte reads for 8-, 16-, and 32-bit modes in little-endian result order. Writes perform byte writes; 32-bit writes occur in descending byte order due to SynQuacer SPI-controller limitations.

## State And Persistence
State is per-device mapped MMIO base plus embedded `tpm_tis_data`. The TPM core owns locality, timeout, and chip registration state.

## Dependencies And Integration Points
Matches OF `socionext,synquacer-tpm-mmio` and ACPI `SCX0009`, uses TIS core PM resume, and does not use interrupts.

## Risks And Edge Cases
Byte order and write order are platform-specific; using generic MMIO helpers could break hardware. IRQ support is absent, so all waits are polling. 16-bit writes return `-EINVAL`, matching core expectations that writes are 8 or 32 bit.

## Test Signals
OF and ACPI probe, byte-wise 32-bit DID/VID reads, descending 32-bit writes, polling-mode TIS commands, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_synquacer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_vtpm_proxy.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_vtpm_proxy.c

## Purpose
Implements `/dev/vtpmx`, a factory for virtual TPM proxy devices where a userspace process emulates TPM hardware through an anonymous server-side file descriptor while clients use normal `/dev/tpm*` nodes.

## Important APIs, Types, And Functions
`struct proxy_dev` stores chip, flags, waitqueue, buffer mutex, state flags, request/response lengths, shared buffer, and registration work. Server-side file ops are `vtpm_proxy_fops_read()`, `vtpm_proxy_fops_write()`, `vtpm_proxy_fops_poll()`, and release. TPM callbacks are `vtpm_proxy_tpm_op_send()`, `vtpm_proxy_tpm_op_recv()`, `vtpm_proxy_tpm_op_status()`, `vtpm_proxy_tpm_req_canceled()`, and `vtpm_proxy_request_locality()`. Control path is `vtpmx_ioc_new_dev()`.

## Control Flow
Module init creates a workqueue and registers misc device `vtpmx`. A privileged `VTPM_PROXY_IOC_NEW_DEV` allocates proxy state and TPM chip, creates an anonymous server file, marks it opened, sets TPM2 flag if requested, queues TPM chip registration work, and returns fd/major/minor/tpm number to userspace. TPM core send copies a request into the proxy buffer and wakes the server. Server read blocks until request is available, copies it out, and marks waiting-for-response. Server write copies a response back, clears wait state, and wakes TPM core. Device release stops registration work, unregisters the chip if needed, and frees state.

## State And Persistence
State is in-memory per proxy device: open/registered/wait-response/driver-command flags, request/response buffer, and work item. No persistent TPM data is stored by the driver; userspace emulator owns persistence.

## Dependencies And Integration Points
Uses miscdevice, anon inode files, waitqueues, TPM core registration, TPM locality commands, user ABI `linux/vtpm_proxy.h`, and CAP_SYS_ADMIN for device creation.

## Risks And Edge Cases
The server fd lifetime controls device lifetime. Locality-setting commands are blocked from clients unless issued by the driver command path. Close races with chip registration are handled by work flushing and open-state wakeups. Buffer state is protected by mutex, but status reads check `resp_len` without locking. Userspace protocol errors surface as TPM command timeouts or `-EIO`.

## Test Signals
`VTPM_PROXY_IOC_NEW_DEV` permission and ABI fields, TPM1/TPM2 mode, request/response round trips, poll readiness, server close while client waits, close during registration work, locality command filtering, malformed response sizes, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_vtpm_proxy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpmrm-dev.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpmrm-dev.c

## Purpose
Implements file operations for the TPM resource-manager character device, giving each open file its own TPM2 transient-object/session space.

## Important APIs, Types, And Functions
Defines `struct tpmrm_priv`, embedding generic `file_priv` and `struct tpm_space`. Implements `tpmrm_open()`, `tpmrm_release()`, and exported `tpmrm_fops`.

## Control Flow
Open obtains the containing `tpm_chip` from the inode cdev, allocates per-file private state, initializes a TPM2 space with `TPM2_SPACE_BUFFER_SIZE`, and calls `tpm_common_open()` with that space. Release retrieves the private container, calls `tpm_common_release()`, deletes the TPM2 space from the chip, frees memory, and returns success. Read/write/poll delegate directly to common TPM file helpers.

## State And Persistence
Each open resource-manager fd owns a `tpm_space` that virtualizes TPM2 handles for the lifetime of the file. No durable state is kept after release.

## Dependencies And Integration Points
Depends on `tpm-dev.h`, common TPM file operations, and TPM2 space management helpers `tpm2_init_space()` and `tpm2_del_space()`.

## Risks And Edge Cases
Allocation or space initialization failure aborts open. Release must delete the space after common release while the chip reference is still available. The file is meaningful only for TPM2-capable chips, enforced by higher TPM core registration logic.

## Test Signals
Multiple concurrent opens with isolated spaces, open failure injection, resource cleanup on release, read/write/poll behavior through common helpers, and TPM2 transient handle virtualization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpmrm-dev.c -->
