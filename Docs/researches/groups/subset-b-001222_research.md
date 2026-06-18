# subset-b-001222 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-ops.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-ops.c

## Purpose

`ccp-ops.c` is the command execution layer for the AMD Cryptographic Coprocessor. It translates high-level `struct ccp_cmd` requests into CCP hardware operations for AES, AES-CMAC, AES-GCM, XTS-AES, 3DES, SHA/HMAC, RSA, passthrough DMA/bitwise operations, and ECC. It also owns the common scatterlist, DMA scratch-buffer, local storage block, endian conversion, and command completion/error propagation mechanics used by those engines.

## Important APIs, Types, And Functions

The only exported function here is `ccp_run_cmd()`, which dispatches by `cmd->engine`. Core helpers include `ccp_init_sg_workarea()`, `ccp_update_sg_workarea()`, `ccp_init_dm_workarea()`, `ccp_init_data()`, `ccp_prepare_data()`, `ccp_process_data()`, `ccp_copy_to_sb()`, and `ccp_copy_from_sb()`. Operation handlers include `ccp_run_aes_cmd()`, `ccp_run_aes_cmac_cmd()`, `ccp_run_aes_gcm_cmd()`, `ccp_run_xts_aes_cmd()`, `ccp_run_des3_cmd()`, `ccp_run_sha_cmd()`, `ccp_run_rsa_cmd()`, `ccp_run_passthru_cmd()`, `ccp_run_passthru_nomap_cmd()`, and the ECC math helpers. SHA initial constants are stored as big-endian arrays and copied into CCP local storage with hardware byte-swap passthrough.

## Control Flow

Each handler validates command sizes, key lengths, IVs, buffer presence, and version support, then allocates DMA-visible workareas or maps scatterlists. Key and context material is copied into CCP storage-block slots, usually with 256-bit byte swapping to match engine endian requirements. Data is processed in looped chunks chosen from the current source and destination DMA scatterlist entries; short or split entries are staged through a DMA pool buffer. Hardware submission is performed through `cmd_q->ccp->vdata->perform` callbacks. After each chunk, workarea cursors are advanced and final state such as IV, digest, authentication tag, RSA output, or ECC coordinates is copied back to caller buffers.

## State And Persistence Behavior

The file maintains no persistent device state of its own except per-command job IDs generated from `ccp->current_id` on version 3 devices. Most state is transient stack or allocated DMA workarea state. The handlers mutate caller-provided contexts: AES/XTS IVs, SHA contexts or final digests, GCM tags, RSA/ECC result buffers, and `cmd->engine_error`. Local storage block contents persist only for the lifetime of a submitted job and are allocated by the command queue.

## Dependencies And Integration Points

This layer depends on `ccp-dev.h` for queue/device structures and hardware action callbacks, Linux scatterlist/DMA APIs, crypto constants for AES/DES/SHA, and `linux/ccp.h` command layouts. It is reached from the CCP device queueing path and is sensitive to hardware version data such as `rsamax`, storage-block layout, and supported callbacks like `des3`.

## Risks And Test Signals

Risks include DMA mapping lifetime bugs, scatterlist cursor mistakes around DMA-merged entries, incorrect endian conversion or storage-block offsets, in-place detection using only first-entry virtual addresses, command-buffer leaks on error paths, GCM tag validation mistakes, and SNP/KVM-visible crypto regressions from engine-specific validation changes. Test signals include crypto selftests for AES modes, CMAC, GCM auth failure, SHA/HMAC including zero-length input, RSA sizes up to hardware maximum, passthrough alignment cases, ECC success/error bits, DMA API debug, IOMMU enabled boots, and hardware command error propagation through `cmd->engine_error`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/dbc.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/dbc.c

## Purpose

`dbc.c` implements the AMD Secure Processor Dynamic Boost Control misc-device interface. It lets privileged userspace authenticate and exchange DBC nonce, UID, and parameter messages with PSP firmware, using either platform-access mailbox commands or the PSP extended mailbox path depending on advertised capability.

## Important APIs, Types, And Functions

The external lifecycle functions are `dbc_dev_init()` and `dbc_dev_destroy()`. The user entry point is `dbc_ioctl()` on `/dev/dbc`. `send_dbc_cmd()` abstracts transport selection and maps PSP firmware status codes to Linux errors through `error_codes`. `send_dbc_nonce()` retries once on `-EAGAIN`, and `send_dbc_parameter()` chooses get/set firmware commands based on `dbc_user_param.msg_index`.

## Control Flow

Probe allocates one page for `union dbc_buffer`, initializes transport-specific header, result, payload, and payload-size pointers, probes availability with a nonce command, then registers a mode `0600` misc device. Each ioctl obtains the master PSP, serializes with `ioctl_mutex`, copies the fixed-size user structure into the shared payload area, sets payload size, sends the relevant firmware message, and copies the payload back to userspace.

## State And Persistence Behavior

Persistent state is `struct psp_dbc_device` stored in `psp->dbc_data`, including the command page and transport-selection fields. Firmware authentication state may survive driver initialization; `-EACCES` from the initial nonce is treated as already authenticated. The command buffer is reused across ioctls under a mutex.

## Dependencies And Integration Points

DBC depends on PSP master selection, `psp_extended_mailbox_cmd()`, `psp_send_platform_access_msg()`, `uapi/linux/psp-dbc.h`, and platform feature probing in `psp-dev.c`. It must initialize after platform access because non-extended transport uses the platform-access mailbox.

## Risks And Test Signals

Risks include stale shared-buffer contents, incorrect firmware-status translation, transport mismatch when capability bits are wrong, and fixed-size user-copy assumptions diverging from UAPI structures. Test by checking `/dev/dbc` permissions, exercising nonce/UID/get/set parameter ioctls on both transports, forcing PSP status errors, and verifying concurrent ioctl serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/dbc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/dbc.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/dbc.h

## Purpose

`dbc.h` defines the private Dynamic Boost Control device state shared between the DBC implementation and PSP initialization code.

## Important APIs, Types, And Functions

`struct psp_dbc_device` records the owning `device`, `psp_device`, a page-sized `union dbc_buffer`, ioctl mutex, misc device, and transport abstraction pointers. `union dbc_buffer` overlays a `struct psp_request` for platform access with `struct psp_ext_request` for extended mailbox. It declares `dbc_dev_init()` and `dbc_dev_destroy()`.

## Control Flow

The header has no executable control flow. Its fields let `dbc.c` use one ioctl path while switching between platform-access and extended-mailbox command layouts during initialization.

## State And Persistence Behavior

The structure persists as `psp->dbc_data` until PSP teardown. Its payload and result pointers point into the selected union member and must remain consistent with `use_ext`.

## Dependencies And Integration Points

It includes DBC UAPI definitions, misc-device support, platform-access request definitions, and `psp-dev.h`. It is private to the CCP/PSP driver tree.

## Risks And Test Signals

Risks are layout and aliasing mistakes between the two mailbox formats. Compile coverage with both platform-access and extended DBC capability paths, plus ioctl tests that confirm payload size and status fields are written to the expected header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/dbc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/hsti.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/hsti.c

## Purpose

`hsti.c` exposes PSP security-reporting attributes through sysfs and can populate missing HSTI/security bits by issuing a platform-access query to PSP firmware.

## Important APIs, Types, And Functions

The exported objects are `psp_security_attr_group` and `psp_init_hsti()`. The `security_attribute_show()` macro creates read-only attributes such as `fused_part`, `boot_integrity`, `debug_lock_on`, `tsme_status`, and RPMC/HSP/ROM armor flags. `psp_populate_hsti()` sends `PSP_CMD_HSTI_QUERY` and merges the returned HSTI bits into `psp->capability.raw`.

## Control Flow

During PSP initialization, `psp_init_hsti()` optionally calls `psp_populate_hsti()` if the platform feature says HSTI is available. The sysfs group is visible only when `psp->capability.security_reporting` is true. If TSME is enabled, initialization logs whether SME is redundant or TSME is active.

## State And Persistence Behavior

Security state is cached in `psp->capability`. The sysfs attributes are read-only views of that cached capability register. No background updates occur after initialization.

## Dependencies And Integration Points

It depends on `platform-access.c` for the HSTI query, `cc_platform_has()` for SME reporting, and `sp-pci.c` for attaching the attribute group to PCI devices.

## Risks And Test Signals

Risks include exposing attributes before data is valid, shifting returned HSTI bits into the wrong capability region, and failing PSP init on transient HSTI query errors. Test by inspecting sysfs visibility on devices with and without security reporting, validating each bit against firmware documentation, and checking logs on TSME/SME systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/hsti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/hsti.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/hsti.h

## Purpose

`hsti.h` declares the PSP security sysfs group and initialization helper used by the PSP and PCI glue code.

## Important APIs, Types, And Functions

It exports `psp_security_attr_group` and declares `psp_init_hsti(struct psp_device *psp)`.

## Control Flow

There is no runtime control flow in the header. Consumers include the header to attach the sysfs group and to populate HSTI state during PSP initialization.

## State And Persistence Behavior

The header defines no storage. State lives in `psp->capability` and sysfs registration owned elsewhere.

## Dependencies And Integration Points

It relies on `struct psp_device` being visible to translation units that include it through `psp-dev.h` or equivalent includes.

## Risks And Test Signals

Risk is limited to declaration drift from `hsti.c`. Build tests with `CONFIG_CRYPTO_DEV_SP_PSP` and sysfs attribute group registration cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/hsti.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/platform-access.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/platform-access.c

## Purpose

`platform-access.c` implements AMD PSP platform-access mailbox and doorbell transports. It provides serialized firmware message submission for platform services such as HSTI, DBC, and other PSP platform commands.

## Important APIs, Types, And Functions

Exported APIs are `psp_check_platform_access_status()`, `psp_send_platform_access_msg()`, and `psp_ring_platform_doorbell()`, plus lifecycle functions `platform_access_dev_init()` and `platform_access_dev_destroy()`. Helpers `check_recovery()` and `wait_cmd()` poll command-response registers and ready bits.

## Control Flow

Initialization allocates `struct psp_platform_access_device`, stores version register offsets from PSP vdata, and initializes mailbox and doorbell mutexes. `psp_send_platform_access_msg()` locks the mailbox, rejects recovery state, waits for readiness, writes the physical request-buffer address to low/high registers, writes the command field, waits for completion, verifies the address registers still match, and returns either success or `-EIO` with firmware status captured in the request header. The doorbell path similarly serializes, writes a small command/status field, rings the button register, waits, and returns the PSP result.

## State And Persistence Behavior

State persists in `psp->platform_access_data` and consists mainly of MMIO offsets and mutexes. Request buffers are owned by callers; this file only writes their physical address to PSP registers. Hardware command-response registers carry transient command state.

## Dependencies And Integration Points

It depends on PSP master lookup, `linux/psp-platform-access.h` request formats, bitfield helpers, MMIO polling, and register offsets supplied by `sp-pci.c`. DBC and HSTI call into this transport.

## Risks And Test Signals

Risks include mailbox contention with firmware/BIOS users, stale address-register verification failures, timeout handling, and confusing `-EIO` transport errors with firmware-level request failures. Test with platform-access consumers, concurrent command submission, induced PSP busy/recovery states, and dynamic debug hex dumps for request/response payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/platform-access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/platform-access.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/platform-access.h

## Purpose

`platform-access.h` defines the private state for PSP platform-access support and declares its init/destroy functions.

## Important APIs, Types, And Functions

`struct psp_platform_access_device` stores device and PSP pointers, `platform_access_vdata`, separate mailbox and doorbell mutexes, and an opaque data pointer. It declares `platform_access_dev_init()` and `platform_access_dev_destroy()`.

## Control Flow

The header itself has no control flow. It provides the shared layout used by platform-access setup, teardown, and message-sending code.

## State And Persistence Behavior

Instances persist as `psp->platform_access_data`. The mutexes protect serialized access to PSP hardware command registers.

## Dependencies And Integration Points

It includes platform-access UAPI/private request definitions and `psp-dev.h`, binding this state to PSP subdevice initialization.

## Risks And Test Signals

Risks are field-layout drift and missing cleanup of initialized mutexes. Build coverage plus probe/remove tests on PSP devices with platform-access vdata validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/platform-access.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/psp-dev.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/psp-dev.c

## Purpose

`psp-dev.c` is the central AMD Platform Security Processor subdevice driver. It initializes PSP capability state, mailbox access, interrupts, and optional subdevices for SEV, TEE, SFS, platform access, DBC, and HSTI.

## Important APIs, Types, And Functions

Global `psp_master` tracks the selected master PSP. Public functions include `psp_dev_init()`, `psp_dev_destroy()`, `psp_mailbox_command()`, `psp_extended_mailbox_cmd()`, `psp_set_sev_irq_handler()`, `psp_clear_sev_irq_handler()`, `psp_get_master_device()`, `psp_restore()`, `psp_pci_init()`, and `psp_pci_exit()`. `psp_irq_handler()` fans PSP interrupts to the registered SEV handler. `psp_get_capability()` reads and validates the feature register.

## Control Flow

`psp_dev_init()` allocates `struct psp_device`, attaches PSP vdata and MMIO registers, initializes the mailbox mutex, reads capability bits, disables/clears interrupts, requests the PSP IRQ, selects the master device through bus callbacks, initializes supported subdevices, and finally enables interrupts. Mailbox commands serialize on `psp->mailbox_mutex`, check ready state, write optional command-buffer addresses, trigger the command register, and poll for completion. Teardown destroys subdevices, frees the IRQ, and clears master state.

## State And Persistence Behavior

Per-device state lives in `sp->psp_data`. Capability bits are cached in `psp->capability`; subdevice pointers store owned feature modules. The master pointer is derived from `sp_get_psp_master_device()` and cached in `psp_pci_init()` for SEV PCI setup.

## Dependencies And Integration Points

It integrates with `sp-dev.c` for IRQ allocation and master selection, with `sev-dev.c`, `tee-dev.c`, `sfs.c`, `platform-access.c`, `dbc.c`, and `hsti.c` for subdevice lifecycles, and with PSP register offsets supplied by PCI/platform vdata.

## Risks And Test Signals

Risks include partially initialized subdevices on mid-probe failures, capability misreads on systems whose BIOS blocks register access, interrupt enable ordering, and shared mailbox races with consumers. Test by probing devices with different capability combinations, suspend/restore TEE ring reinit, subdevice init failures, IRQ delivery to SEV commands, and module unload/remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/psp-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/psp-dev.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/psp-dev.h

## Purpose

`psp-dev.h` defines the private PSP core structures, capability bit layout, mailbox command IDs, extended mailbox request format, and PSP core function prototypes.

## Important APIs, Types, And Functions

Key types are `union psp_cap_register`, `struct psp_device`, `enum psp_cmd`, `struct psp_ext_req_buffer_hdr`, `struct psp_ext_request`, and `enum psp_sub_cmd`. It declares master lookup, mailbox functions, and SEV IRQ handler registration helpers. `psp_device` holds MMIO base, mailbox mutex, subdevice pointers, interrupt callback, and capability state.

## Control Flow

The header has no executable flow, but its definitions shape all PSP subdevice command paths: standard mailbox commands use `enum psp_cmd`, while DBC/SFS use extended subcommands and `struct psp_ext_request`.

## State And Persistence Behavior

The `psp_device` object persists for the life of an SP device. Its subdevice pointers are nullable feature state and must be cleared during teardown.

## Dependencies And Integration Points

It depends on Linux PSP/platform-access headers and `sp-dev.h`. It is included across PSP subdrivers and the PCI glue.

## Risks And Test Signals

Risks include bitfield layout assumptions for the hardware capability register and packed request layout drift from firmware. Build and runtime tests across PSP generations, with feature bits decoded in sysfs and subdevices initialized conditionally, validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/psp-dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/sev-dev-tio.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/sev-dev-tio.c

## Purpose

`sev-dev-tio.c` implements the low-level SEV-TIO firmware interface used to connect PCIe devices to SNP/TDISP flows. It manages Scatter List Address buffers, SPDM request/response objects, firmware-owned page transitions, and TIO device lifecycle commands.

## Important APIs, Types, And Functions

Public functions include `sev_tio_init_locked()`, `sev_tio_continue()`, `sev_tio_dev_create()`, `sev_tio_dev_connect()`, `sev_tio_dev_disconnect()`, `sev_tio_dev_reclaim()`, and `sev_tio_cmd_buffer_len()`. Internal command buffer structures cover TIO status, init, device create/connect/disconnect/measure/cert/reclaim. SLA helpers include `make_sla()`, `sla_buffer_map()`, `sla_buffer_unmap()`, `sla_alloc()`, `sla_free()`, `sla_expand()`, and SPDM helpers `spdm_ctrl_alloc()`, `spdm_ctrl_init()`, and `spdm_ctrl_free()`.

## Control Flow

TIO initialization queries firmware status, validates the returned status structure, and issues `SEV_CMD_TIO_INIT` when firmware says TIO is enabled but not initialized. Device create allocates a firmware-owned device context SLA and a firmware page, then sends `TIO_DEV_CREATE`. Connect allocates request, response, scratch, and output buffers, fills an SPDM control structure, and calls `sev_tio_do_cmd()`. If firmware returns SPDM-request status, the function prepares DOE payload lengths and returns a PCI DOE feature code so the higher TSM layer can exchange SPDM messages and call `sev_tio_continue()`. Reclaim frees firmware pages, sends reclaim, frees SLA buffers, and clears context state.

## State And Persistence Behavior

Per-device state is stored in `struct tsm_dsm_tio`: SLA addresses, vmapped request/response headers, current command replay buffer, PSP return code, firmware data page, and PCI IDE stream pointers. SLA buffers may be hypervisor-owned or firmware-owned; freeing firmware-owned buffers requires SNP reclaim before releasing pages. Output and scratch buffers can be expanded when firmware requests larger buffers.

## Dependencies And Integration Points

It depends on SEV command submission from `sev-dev.c`, SNP RMP helpers, PCI DOE constants, Linux TSM and PCI IDE types from `sev-dev-tio.h`, and AMD SEV firmware command definitions. `sev-dev-tsm.c` drives its SPDM continuation loop.

## Risks And Test Signals

Risks include page-state leaks when reclaim fails, vmap/unmap mismatches for scatter SLAs, firmware-owned buffer expansion errors, SPDM header length validation gaps, and deadlocks if locked SEV command paths call reclaim paths that also lock. Test with SEV-TIO-capable firmware, DOE CMA and secure-session exchanges, buffer expansion responses, connect/disconnect/reclaim failure injection, and RMP/page-leak diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/sev-dev-tio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/sev-dev-tio.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/sev-dev-tio.h

## Purpose

`sev-dev-tio.h` defines shared SEV-TIO data structures used by the PSP TIO firmware interface and the PCI TSM/IDE integration layer.

## Important APIs, Types, And Functions

Important types are packed `struct sla_addr_t`, `struct tsm_spdm`, `struct tsm_dsm_tio`, `struct tio_dsm`, `struct spdm_dobj_hdr`, and `struct sev_tio_status`. It declares TIO lifecycle functions and constants such as `SEV_TIO_MAX_COMMAND_LENGTH`, `TIO_IDE_MAX_TC`, and SPDM data object IDs.

## Control Flow

The header has no executable flow. Its structures allow `sev-dev-tio.c` to store firmware/SLA command state and `sev-dev-tsm.c` to drive PCI TSM connect/disconnect operations.

## State And Persistence Behavior

`struct tsm_dsm_tio` is the persistent per-PCI-device TIO state: firmware context, SPDM buffers, current command continuation data, and IDE stream handles. `struct sev_tio_status` caches firmware-advertised buffer limits and capabilities.

## Dependencies And Integration Points

It includes PCI TSM, PCI IDE, generic TSM, and SEV UAPI headers. It also forward-couples to `struct sev_device` through `struct tio_dsm`.

## Risks And Test Signals

Risks include packed bitfield and firmware ABI layout drift, undersized command replay buffer, and SPDM object length mismatches. Compile-time layout checks in implementation plus TIO firmware status validation and PCI TSM connect tests are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/sev-dev-tio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/sev-dev-tsm.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/sev-dev-tsm.c

## Purpose

`sev-dev-tsm.c` connects SEV-TIO firmware operations to the Linux PCI TSM framework. It probes eligible PF0 PCI devices, establishes SPDM sessions over DOE, configures PCI IDE streams, and tears those streams down during disconnect.

## Important APIs, Types, And Functions

The external functions are `sev_tsm_init_locked()` and `sev_tsm_uninit()`. `sev_tsm_ops` provides `.probe`, `.remove`, `.connect`, and `.disconnect` callbacks. Helpers include `sev_tio_spdm_cmd()`, IDE stream setup/enable/register/teardown functions, `tio_pf0_probe()`, `dsm_create()`, `dsm_connect()`, and `dsm_disconnect()`.

## Control Flow

Initialization calls `sev_tio_init_locked()`, registers a TSM device, copies TIO status, and stores `sev->tsmdev`/`sev->tio_status`. TSM probe constructs a PF0 object for devices that qualify. Connect verifies the DOE mailbox supports secure session, allocates an IDE stream for traffic class 0, creates the firmware TIO device context, programs IDE stream identifiers and default stream settings, runs `TIO_DEV_CONNECT`, loops through SPDM DOE exchanges until firmware succeeds, enables/registers IDE streams, and unwinds on errors. Disconnect attempts normal then forced firmware disconnect, reclaims TIO context, disables/unregisters streams, and frees IDE state.

## State And Persistence Behavior

The `struct tio_dsm` allocated at probe owns the per-device TIO state. Stream state is mirrored in PCI IDE structures and in firmware device context buffers. The SEV device stores the registered `tsm_dev` and a cached copy of TIO status until uninit.

## Dependencies And Integration Points

It depends on the Linux PCI TSM framework, PCI DOE, PCI IDE namespace, PSP/SEV TIO helpers, IOMMU/SEV platform initialization, and PCI root-port topology helpers. It is invoked from SNP initialization when firmware and IOMMU both support SEV-TIO.

## Risks And Test Signals

Risks include incomplete unwind ordering around IDE stream enable/register, assumptions that traffic class 0 is always present, DOE mailbox mismatch, forced root-port CFG/TEE settings, and disconnect during shutdown/restart. Test with TSM-capable PF0 devices, DOE CMA and secure-session traffic, IDE stream enable/register failure injection, connect/disconnect cycles, and system shutdown forced disconnect paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/sev-dev-tsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/sev-dev.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/sev-dev.c

## Purpose

`sev-dev.c` implements the AMD Secure Encrypted Virtualization and SEV-SNP PSP firmware interface. It registers `/dev/sev`, exposes platform ioctls, submits SEV/SNP/TIO firmware commands, manages SEV/SNP platform initialization and shutdown, handles SNP firmware-owned page transitions, maintains persistent INIT_EX storage, and exports helper APIs to KVM and other kernel users.

## Important APIs, Types, And Functions

External APIs include `sev_dev_init()`, `sev_dev_destroy()`, `sev_platform_init()`, `sev_platform_shutdown()`, `sev_do_cmd()`, `__sev_do_cmd_locked()`, SEV guest helpers, `snp_alloc_firmware_page()`, `snp_free_firmware_page()`, `snp_alloc_hv_fixed_pages()`, `snp_free_hv_fixed_pages()`, `sev_get_snp_policy_bits()`, and `sev_issue_cmd_external_user()`. Major internal areas are command buffer sizing, INIT/INIT_EX/NV file handling, SNP platform data and feature discovery, RMP firmware-page helpers, legacy SEV command bounce descriptors, ioctl handlers, firmware update, panic shutdown, and TIO initialization.

## Control Flow

`sev_dev_init()` validates CPU SEV support, allocates a two-page command buffer, registers the SEV IRQ callback, and creates `/dev/sev`. PCI init obtains firmware API/version state and optionally downloads firmware. `sev_platform_init()` serializes on `sev_cmd_mutex`, initializes SNP first when supported, then legacy SEV unless deferred. SNP init builds an optional reserved-memory/HV-fixed range list, prepares RMP state, executes `SNP_INIT[_EX]`, flushes caches, runs `SNP_DF_FLUSH`, registers panic shutdown, and may initialize SEV-TIO. Command submission copies caller data into a physical scratch command buffer, prepares SNP legacy buffer state when needed, writes command-buffer registers, triggers PSP, waits by interrupt or panic-safe polling, records PSP status, persists INIT_EX NV state for mutating commands, reclaims buffers, and copies results back. Ioctls validate access mode, copy user data, perform state transitions such as temporary INIT/SHUTDOWN, and return firmware status through `struct sev_issue_cmd`.

## State And Persistence Behavior

Global state includes `sev_cmd_mutex`, `misc_dev`, `psp_dead`, `psp_timeout`, `sev_es_tmr`, `sev_init_ex_buffer`, and the HV-fixed page list. Per-device `struct sev_device` stores firmware API/build, command buffers, platform status, SNP initialized state, SNP feature/status caches, waitqueue state, and TIO registration. INIT_EX data can persist to a root-opened file path. SNP page ownership state persists in the RMP and can force leaking pages if reclaim fails. HV-fixed pages may become non-returnable until reboot after SNP INIT_EX.

## Dependencies And Integration Points

This file integrates with PSP master/device state, SEV UAPI ioctls, KVM exported SEV guest APIs, x86 SNP/RMP helpers, AMD IOMMU SNP support, firmware loading, panic notifiers, PCI TSM/TIO helpers, cache flush/WBINVD operations, misc devices, and root filesystem file I/O for INIT_EX. `sev-dev-tio.c` supplies TIO command sizing and TSM initialization.

## Risks And Test Signals

Risks are high: command-buffer active flags can remain set on early preparation errors, SNP RMP transitions can leak or strand pages, panic shutdown must avoid mutex and notifier deadlocks, ioctl user-copy size limits must match firmware expectations, INIT_EX persistence can fail after successful firmware mutations, and TIO/SNP initialization ordering can lose state if probe deferral is misconfigured. Test signals include `/dev/sev` platform ioctl suites, KVM SEV/SEV-ES/SNP guest launch/teardown, SNP kexec and panic paths, firmware update/version logs, RMP page-state stress, INIT_EX file persistence, negative PSP status injection, and lockdep around nested reclaim commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/sev-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/sev-dev.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/sev-dev.h

## Purpose

`sev-dev.h` defines the private SEV device state, command-response register bit masks, misc-device reference wrapper, and SEV/SNP helper prototypes used by PSP, TIO, and KVM-facing code.

## Important APIs, Types, And Functions

It defines `struct sev_misc_dev` and `struct sev_device`. `sev_device` contains PSP/MMIO references, SEV vdata, interrupt wait state, firmware API/build fields, primary and backup command buffers, SNP initialized flag, SEV/SNP cached platform status, SNP feature info, and TIO state. It declares core lifecycle, locked command submission, PCI init/exit, HV-fixed page allocation, TSM init/uninit, and TIO command length lookup.

## Control Flow

No executable flow lives here. The header establishes the shared state contract used by `sev-dev.c`, `psp-dev.c`, `sev-dev-tio.c`, and `sev-dev-tsm.c`.

## State And Persistence Behavior

The state model is persistent per PSP device. Command-buffer flags track nested firmware command use, while SNP/TIO fields represent platform state that may outlive individual file descriptors.

## Dependencies And Integration Points

It includes SEV UAPI, misc-device, waitqueue, DMA, interrupt, and capability headers. The declared functions are consumed by PSP init, KVM SEV support, SFS HV-fixed allocation, and TIO integration.

## Risks And Test Signals

Risks include structure field misuse across files and stale cached platform status. Compile coverage with PSP/SEV/TIO configurations and runtime tests that initialize, shut down, and reinitialize SEV/SNP validate the shared state contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/sev-dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/sfs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/sfs.c

## Purpose

`sfs.c` implements AMD PSP Seamless Firmware Servicing support through `/dev/sfs`. It sends PSP extended mailbox commands to query firmware versions and load SFS update packages from the kernel firmware store.

## Important APIs, Types, And Functions

Lifecycle functions are `sfs_dev_init()` and `sfs_dev_destroy()`. User entry is `sfs_ioctl()`. Firmware command helpers are `send_sfs_cmd()`, `send_sfs_get_fw_versions()`, and `send_sfs_update_package()`. `sfs_misc_init()` registers a shared misc device with reference counting.

## Control Flow

Initialization allocates a 2 MiB command buffer through the SNP HV-fixed page allocator, marks it uncacheable, stores it in `psp->sfs_data`, and registers `/dev/sfs` mode `0600`. `SFSIOCFWVERS` initializes the first page to `0xc7`, sends `PSP_SFS_GET_FW_VERSIONS`, and copies the version blob plus status fields back to userspace. `SFSIOCUPDATEPKG` copies a bounded payload name from userspace, requests `amd/<payload>`, checks the aligned package size against the fixed 2 MiB buffer, copies firmware bytes into the SFS buffer, sends `PSP_SFS_UPDATE`, and returns firmware status.

## State And Persistence Behavior

The 2 MiB command buffer persists for the PSP device lifetime and may become HV-fixed during SNP init. It is mapped uncacheable until destroy restores write-back caching. The misc device is process-shared and protected by a global ioctl mutex.

## Dependencies And Integration Points

SFS depends on PSP extended mailbox commands, firmware loader paths under `amd/`, SEV SNP HV-fixed page allocation, memory attribute changes, and SFS UAPI structures. PSP init enables it when capability bit `sfs` is present.

## Risks And Test Signals

Risks include uncacheable mapping cleanup failure, HV-fixed page lifetime leaks, accepting malformed payload names, firmware package alignment mistakes, and concurrent ioctl buffer reuse. Test `/dev/sfs` permissions, firmware-version query, update with maximum and oversized payloads, missing firmware files, SNP-enabled initialization, and remove/unload memory attribute restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/sfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/sfs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/sfs.h

## Purpose

`sfs.h` defines the private structures for PSP Seamless Firmware Servicing support.

## Important APIs, Types, And Functions

It defines `struct sfs_misc_dev`, packed `struct sfs_command`, and `struct sfs_device`. The command layout embeds `struct psp_ext_req_buffer_hdr`, a one-page status/extended buffer, and a flexible SFS payload buffer. It declares `sfs_dev_init()` and `sfs_dev_destroy()`.

## Control Flow

The header contains no executable flow. Its layout is consumed by `sfs.c` to cast the 2 MiB command buffer into an extended mailbox request plus payload area.

## State And Persistence Behavior

`struct sfs_device` persists as `psp->sfs_data` and owns the HV-fixed page and misc-device reference.

## Dependencies And Integration Points

It includes SFS UAPI, PSP SEV/platform-access definitions, memory attribute helpers, and `psp-dev.h`.

## Risks And Test Signals

Risks include packed flexible-array layout drift and mismatch with PSP extended command expectations. Build tests and live SFS firmware-version queries validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/sfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/sp-dev.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/sp-dev.c

## Purpose

`sp-dev.c` is the common AMD Secure Processor core used by both PCI and platform bus frontends. It tracks SP devices, multiplexes shared interrupts between CCP and PSP subdevices, initializes/destroys CCP and PSP feature blocks, and provides module entry/exit.

## Important APIs, Types, And Functions

Public functions include `sp_alloc_struct()`, `sp_init()`, `sp_destroy()`, `sp_suspend()`, `sp_resume()`, `sp_restore()`, `sp_request_ccp_irq()`, `sp_request_psp_irq()`, `sp_free_ccp_irq()`, `sp_free_psp_irq()`, and `sp_get_psp_master_device()`. Static state includes `sp_units`, `sp_unit_lock`, and `sp_ordinal`. `sp_irq_handler()` calls registered CCP and PSP handlers when both subdevices share an IRQ.

## Control Flow

Bus probes allocate and populate `struct sp_device`, then call `sp_init()`. The core appends the device to the global list, initializes CCP if vdata exists, then initializes PSP if vdata exists. IRQ request helpers either install a shared top-level handler or request a subdevice-specific IRQ. Suspend/resume delegate to CCP, while restore first restores PSP TEE state then resumes CCP. Module init registers the PCI driver on x86 or platform driver on arm64; x86 PSP PCI post-init starts SEV firmware setup.

## State And Persistence Behavior

The global SP list persists while devices are bound and is protected by a rwlock. Each `sp_device` stores subdevice data pointers, IRQ handlers, master-selection callbacks, and bus-specific data. Ordinals monotonically assign device names.

## Dependencies And Integration Points

It depends on bus frontends `sp-pci.c` and `sp-platform.c`, CCP and PSP subdevice APIs, kernel module initialization, and KVM SEV built-in init when configured.

## Risks And Test Signals

Risks include shared IRQ lifetime races, ignoring subdevice init errors in `sp_init()`, master lookup under write lock, and partial teardown ordering between CCP/PSP. Test with devices that have CCP-only, PSP-only, shared IRQ, and separate IRQ layouts; suspend/resume/restore; and module unload or PCI remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/sp-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/sp-dev.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/sp-dev.h

## Purpose

`sp-dev.h` defines the common Secure Processor device model, version-data structures, feature flags, and cross-file APIs for CCP and PSP subdevices.

## Important APIs, Types, And Functions

Key structures are `ccp_vdata`, `sev_vdata`, `tee_vdata`, `platform_access_vdata`, `psp_vdata`, `sp_dev_vdata`, and `sp_device`. It defines cache attributes, platform feature bits, the `PSP_FEATURE()` macro, bus init/exit prototypes, common SP lifecycle/IRQ helpers, and conditional CCP/PSP stubs for disabled configs.

## Control Flow

The header has no executable control flow, but its vdata pointers drive whether `sp_init()` creates CCP and/or PSP subdevices and which MMIO offsets those subdevices use.

## State And Persistence Behavior

`struct sp_device` persists per bound device and carries bus-specific data, MMIO base, IRQ state, master-selection callbacks, and CCP/PSP subdevice pointers.

## Dependencies And Integration Points

It is included by SP core, PCI/platform frontends, PSP, SEV, TEE, and CCP code. It abstracts hardware generation differences through static vdata tables.

## Risks And Test Signals

Risks include incorrect register offsets in vdata, function-pointer misuse when configs are disabled, and structure field assumptions across bus frontends. Compile matrix coverage and probe tests for all supported PCI IDs/ACPI/OF matches are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/sp-dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/sp-pci.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/sp-pci.c

## Purpose

`sp-pci.c` is the PCI frontend for AMD Secure Processor/CCP devices. It matches AMD PCI IDs, maps BARs, allocates MSI-X/MSI interrupts, selects a PSP master device, provides PSP firmware/security sysfs attributes, and supplies generation-specific vdata.

## Important APIs, Types, And Functions

Public entry points are `sp_pci_init()` and `sp_pci_exit()`. Probe/remove/shutdown/PM handlers are `sp_pci_probe()`, `sp_pci_remove()`, `sp_pci_shutdown()`, `sp_pci_suspend()`, `sp_pci_resume()`, and `sp_pci_restore()`. IRQ helpers are `sp_get_msix_irqs()`, `sp_get_msi_irq()`, and `sp_free_irqs()`. Master selection uses `psp_set_master()`, `psp_get_master()`, and `psp_clear_master()`. Static vdata tables define SEV, TEE, platform-access, PSP, and SP device register layouts by PCI ID.

## Control Flow

Probe allocates `sp_device` and PCI-private state, enables the PCI device with managed resources, maps memory BARs, chooses MSI-X or MSI, sets bus mastering and DMA mask, installs PSP master callbacks, stores driver data, and calls `sp_init()`. Remove destroys subdevices and frees interrupts. Shutdown destroys subdevices without a separate IRQ-free path. PM delegates into common SP suspend/resume/restore. Sysfs attribute visibility reads PSP registers and hides all-ones inaccessible values.

## State And Persistence Behavior

`sp_dev_master` tracks the lexicographically earliest PCI PSP device by domain/bus/slot/function. Per-device `struct sp_pci` stores MSI-X vectors. Static vdata tables are immutable hardware descriptors.

## Dependencies And Integration Points

It integrates with PCI core, DMA mask setup, MSI/MSI-X APIs, common SP core, CCP hardware vdata from `ccp-dev.h`, PSP security HSTI attributes, SEV/TEE/platform-access register layouts, and module PCI device tables.

## Risks And Test Signals

Risks include wrong vdata for a PCI ID, master selection changes on hotplug/remove, sysfs reads from inaccessible PSP registers, IRQ fallback behavior, and shutdown/remove cleanup asymmetry. Test all listed PCI IDs where possible, MSI-X one-vector and two-vector paths, MSI fallback, firmware sysfs visibility, multi-socket master selection, suspend/restore, and device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/sp-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/sp-platform.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/sp-platform.c

## Purpose

`sp-platform.c` is the ACPI/OF platform-bus frontend for AMD CCP/SP devices, mainly non-PCI environments such as ARM64 Seattle.

## Important APIs, Types, And Functions

Public functions are `sp_platform_init()` and `sp_platform_exit()`. Driver callbacks are `sp_platform_probe()`, `sp_platform_remove()`, and optional PM suspend/resume handlers. Helpers include `sp_get_acpi_version()` and `sp_get_irqs()`. `struct sp_platform` tracks DMA coherency and IRQ count.

## Control Flow

Probe allocates common and platform-private state, selects vdata from OF or ACPI match, maps resource 0, checks DMA support and coherency, sets `sp->axcache`, configures a 48-bit DMA mask, obtains one or two IRQs, stores driver data, and calls `sp_init()`. Remove calls `sp_destroy()`. PM delegates to common SP suspend/resume.

## State And Persistence Behavior

Per-device platform state persists in `sp->dev_specific`. Coherency determines the AXCACHE attribute used by CCP hardware operations. There is no PSP vdata in this platform table, so this path is CCP-focused.

## Dependencies And Integration Points

It depends on platform device resources, ACPI ID `AMDI0C00`, OF compatible `amd,ccp-seattle-v1a`, DMA attribute APIs, common SP core, and CCP platform vdata.

## Risks And Test Signals

Risks include incorrect DMA coherency handling, missing second IRQ on platforms that need it, unsupported DMA silently failing probe, and vdata mismatch between ACPI and OF. Test ACPI and DT probe, coherent and non-coherent DMA operation, single/shared IRQ versus dual IRQ, suspend/resume, and remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/sp-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/tee-dev.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/tee-dev.c

## Purpose

`tee-dev.c` implements the AMD PSP Trusted Execution Environment ring-buffer interface. It initializes a shared command ring with PSP firmware and exports a kernel API for submitting TEE commands through the PSP master device.

## Important APIs, Types, And Functions

Public APIs are `tee_dev_init()`, `tee_dev_destroy()`, `tee_restore()`, `psp_tee_process_cmd()`, and `psp_check_tee_status()`. Ring helpers include `tee_alloc_ring()`, `tee_free_ring()`, `tee_alloc_cmd_buffer()`, `tee_init_ring()`, `tee_destroy_ring()`, `tee_submit_cmd()`, and `tee_wait_cmd_completion()`. Static `psp_dead` disables further TEE use after fatal timeout/error.

## Control Flow

Initialization allocates a ring of 32 `tee_ring_cmd` entries, sends `PSP_CMD_TEE_RING_INIT` with the physical ring address, retries once by destroying a busy ring after hibernate-like conditions, and stores state in `psp->tee_data`. Command submission locks the ring, waits for an empty entry, rejects if PSP is dead, writes command ID/state/payload, advances the write pointer, rings firmware through the write-pointer MMIO register, then waits for firmware to mark the command completed. The response payload and status are copied back and the entry flag is marked copied.

## State And Persistence Behavior

Persistent state is `struct psp_tee_device` and its `ring_buf_manager`: ring virtual address, physical address, size, mutex, and write pointer. Firmware owns the read pointer register and updates command state in-place. Fatal command timeout or destroy/init failure sets `psp_dead` until driver reload.

## Dependencies And Integration Points

It depends on PSP mailbox commands, TEE register offsets in `tee_vdata`, `linux/psp-tee.h` command IDs, PSP master lookup, and PSP restore during PCI restore.

## Risks And Test Signals

Risks include ring full handling under concurrency, cache coherency of firmware-updated ring entries, timeout disabling all TEE operations, copying more than `MAX_BUFFER_SIZE`, and ring reinitialization after hibernate. Test with TEE clients using `psp_tee_process_cmd()`, concurrent submissions, forced full ring, hibernate restore, firmware busy response, and timeout injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/tee-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/tee-dev.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/tee-dev.h

## Purpose

`tee-dev.h` describes the host/AMD Secure Processor TEE ring-buffer ABI and declares TEE device lifecycle functions.

## Important APIs, Types, And Functions

It defines `struct tee_init_ring_cmd`, `struct ring_buf_manager`, `struct psp_tee_device`, `enum tee_cmd_state`, `enum cmd_resp_state`, and packed `struct tee_ring_cmd`. Constants include `TEE_DEFAULT_CMD_TIMEOUT`, `TEE_DEFAULT_RING_TIMEOUT`, `MAX_BUFFER_SIZE`, and `MAX_RING_BUFFER_ENTRIES`. It declares `tee_dev_init()`, `tee_dev_destroy()`, and `tee_restore()`.

## Control Flow

There is no executable flow. The declared ring-entry states are used by `tee-dev.c` and PSP firmware to coordinate command lifecycle.

## State And Persistence Behavior

The ring manager stores host-maintained write pointer and firmware-visible ring address. Each ring entry stores command state, PSP status, payload, and driver response flag.

## Dependencies And Integration Points

It depends on Linux device/mutex types and PSP TEE command IDs from public headers included by the implementation. The ABI is shared with firmware, so packing and 1024-byte entry size are significant.

## Risks And Test Signals

Risks include structure size/layout drift, incorrect state transitions, and buffer-size mismatch with callers. `BUILD_BUG_ON(sizeof(struct tee_ring_cmd) != 1024)` plus live TEE command round trips are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/tee-dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccree/Makefile

## Purpose

This Makefile builds the Arm CryptoCell/CCREE crypto driver object composition under `drivers/crypto/ccree`.

## Important APIs, Types, And Functions

It declares `obj-$(CONFIG_CRYPTO_DEV_CCREE) := ccree.o` and composes `ccree-y` from core modules: driver, buffer manager, request manager, cipher, hash, AEAD, and SRAM manager. Optional objects are added for `CONFIG_CRYPTO_FIPS`, `CONFIG_DEBUG_FS`, and `CONFIG_PM`.

## Control Flow

Kbuild links the listed objects into `ccree.o` when CCREE support is enabled. Feature-specific files are included only when the corresponding kernel config symbols are set.

## State And Persistence Behavior

The Makefile has no runtime state. Its persistent effect is build composition and conditional inclusion of FIPS, debugfs, and power-management code.

## Dependencies And Integration Points

It integrates with Linux Kbuild and the CCREE source files in the same directory. Configuration symbols determine whether the driver and optional support paths are compiled.

## Risks And Test Signals

Risks include missing object entries when new CCREE source files are added or feature objects being omitted under their configs. Test by building with `CONFIG_CRYPTO_DEV_CCREE`, with and without `CONFIG_CRYPTO_FIPS`, `CONFIG_DEBUG_FS`, and `CONFIG_PM`, and checking link coverage for the resulting `ccree.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/Makefile -->
