# sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_scm.c

## Purpose
`qcom_scm.c` is the core Qualcomm Secure Channel Manager driver. It probes the SCM device, establishes clocks/interconnect/TZMem/waitqueue infrastructure, discovers the SCM calling convention, and exports secure-world services used by CPU boot, remoteproc/PAS, IOMMU and memory protection, inline encryption, HDCP, QSEECOM, QTEE, LMH, GPU, download mode, reset controllers, and Gunyah-related devices.

## Important APIs, Types, And Functions
- Driver state: `struct qcom_scm` stores device, clocks, interconnect path, waitqueue completions, reset controller, download-mode address, TZMem pool, and waitqueue count. Global `__scm` is published with release/acquire ordering.
- Convention and transport: `qcom_scm_convention`, `__get_convention()`, `qcom_scm_call()`, `qcom_scm_call_atomic()`, and `__qcom_scm_is_call_available()`.
- Boot/power APIs: `qcom_scm_set_warm_boot_addr()`, `qcom_scm_set_cold_boot_addr()`, `qcom_scm_cpu_power_down()`, `qcom_scm_set_remote_state()`, and download-mode helpers.
- PAS/remoteproc APIs: `devm_qcom_scm_pas_context_alloc()`, `qcom_scm_pas_init_image()`, `qcom_scm_pas_metadata_release()`, `qcom_scm_pas_mem_setup()`, `qcom_scm_pas_get_rsc_table()`, `qcom_scm_pas_auth_and_reset()`, `qcom_scm_pas_prepare_and_auth_reset()`, `qcom_scm_pas_shutdown()`, and `qcom_scm_pas_supported()`.
- Memory/IOMMU/security APIs: `qcom_scm_assign_mem()`, secure page-table setup, restore-sec-cfg, OCMEM lock/unlock, GPU SMMU aperture, and SMMU erratum calls.
- Storage crypto APIs: ICE key invalidation/programming and wrapped-key helpers with explicit zeroing of key buffers.
- QSEECOM/QTEE APIs: `qcom_scm_qseecom_app_get_id()`, `qcom_scm_qseecom_app_send()`, `qcom_scm_qtee_invoke_smc()`, and `qcom_scm_qtee_callback_response()`.
- Waitqueue and probe: `qcom_scm_query_waitq_count()`, `qcom_scm_get_waitq_irq()`, `qcom_scm_irq_handler()`, `qcom_scm_probe()`, and `qcom_scm_shutdown()`.

## Control Flow
Probe maps optional download-mode registers, obtains optional interconnect and clocks, registers a PAS reset controller, sets the core clock high, initializes reserved memory, enables TZMem, creates an on-demand SCM TZMem pool, discovers waitqueue count and IRQ, publishes `__scm`, probes the calling convention, applies download-mode/SDI policy, and then initializes QSEECOM, QTEE, and Gunyah watchdog platform devices.

All exported services build a `qcom_scm_desc` with service, command, owner, argument metadata, and arguments. `qcom_scm_call()` dispatches to SMCCC or legacy transport based on runtime convention; long calls often enable SCM clocks and interconnect bandwidth around the call. Shared buffers are allocated from TZMem unless a firmware contract requires plain coherent DMA, as in non-TZMem PAS metadata paths.

PAS flows authenticate and boot remote processors by initializing metadata, setting up memory, optionally retrieving resource tables from TrustZone, authenticating and resetting, then releasing metadata. Memory assignment builds aligned source VMID, memory-map, and destination permission arrays in TZMem. QSEECOM calls are serialized by a dedicated mutex and guarded by a machine allowlist before SCM creates the `qcom_qseecom` platform device.

## State And Persistence
The driver maintains boot-lifetime global SCM state, a shared TZMem pool, waitqueue completion array, download-mode state through a module parameter and hardware/SCM side effects, and SCM bandwidth vote count. It does not persist data to disk, but many calls persist changes in firmware or hardware: remote processor authentication state, memory ownership, ICE keys, secure page tables, download mode, and EFI/QSEE/QTEE side effects.

## Dependencies And Integration Points
The core depends on SMCCC transports, TZMem, device tree, clocks, interconnect, reserved memory, IRQ mapping, reset-controller framework, remoteproc resource tables, platform devices, and Qualcomm public firmware headers. It is a central integration point for storage, display, GPU, remoteproc, IOMMU, QTEE object invocation, QSEECOM secure apps, and watchdog infrastructure.

## Risks
`__scm` must not be published before the allocator and waitqueue path are ready; users rely on `qcom_scm_is_available()`. SHM Bridge behavior changes buffer validity rules. Several firmware calls have subtle contracts: PAS metadata can fail if already SHM-bridged, QSEECOM lacks reentrant/listener handling, resource-table sizes need sanity limits, and key buffers must be zeroed. Download mode may alter reboot behavior. Many calls trust firmware return values and must map SCM result registers carefully.

## Test Signals
Boot should log the selected SCM convention and probe success. Feature probes should return expected availability for PAS, ICE, HDCP, LMH, SHM Bridge, QSEECOM, and QTEE. Integration tests include remoteproc firmware boot/shutdown, SCM-mediated IO reads/writes, memory assignment owner updates, storage inline encryption key programming, efivarfs through QSEECOM, QTEE clients, waitqueue IRQ wakeups, download-mode parameter writes, and clean shutdown disabling download mode.
