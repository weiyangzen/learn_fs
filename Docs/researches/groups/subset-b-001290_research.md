# Research: subset-b-001290

This grouped report covers firmware interface sources under `sources/distributed-fs/ceph-client/drivers/firmware`. Each section is source-tree aligned and wrapped with the markers consumed by the reconciliation splitter.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/psci/psci.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/psci/psci.c

## Purpose
`psci.c` is the kernel's ARM PSCI firmware frontend. It discovers PSCI via device tree or ACPI, selects the SMCCC conduit (`SMC` or `HVC`), fills the global `psci_ops` dispatch table, and wires PSCI into CPU hotplug, CPU idle, system suspend, restart, poweroff, hibernation, SMCCC discovery, and KVM hypervisor-service discovery.

## Important APIs, Types, And Functions
- Global state: `struct psci_operations psci_ops`, `invoke_psci_fn`, `psci_conduit`, `resident_cpu`, `psci_cpu_suspend_feature`, `psci_system_reset2_supported`, and `psci_system_off2_hibernate_supported`.
- Discovery entry points: `psci_dt_init()` matches `arm,psci`, `arm,psci-0.2`, and `arm,psci-1.0`; `psci_acpi_init()` uses ACPI flags to choose HVC/SMC and then probes PSCI 0.2+.
- PSCI operation implementations: `psci_0_1_cpu_suspend/off/on/migrate`, `psci_0_2_cpu_suspend/off/on/migrate`, `psci_affinity_info()`, `psci_migrate_info_type()`, `psci_migrate_info_up_cpu()`.
- Integration APIs exported or visible to other firmware/power code: `psci_tos_resident_on()`, `get_psci_0_1_function_ids()`, `psci_set_osi_mode()`, `psci_has_osi_support()`, `psci_power_state_is_valid()`, and `psci_cpu_suspend_enter()`.
- System lifecycle hooks: `psci_sys_reset()`, `psci_sys_poweroff()`, optional `psci_sys_hibernate()`, and the `platform_suspend_ops` using `SYSTEM_SUSPEND`.
- Optional debug surface: debugfs file `psci` reports PSCI/SMCCC versions, optional function availability, OSI support, state-ID format, and Trusted OS residency.

## Control Flow
Initialization starts from DT or ACPI, calls `set_conduit()` to bind `invoke_psci_fn` to `arm_smccc_smc()` or `arm_smccc_hvc()`, then calls `psci_probe()` for PSCI 0.2+. `psci_probe()` reads `PSCI_VERSION`, rejects conflicting pre-0.2 firmware, installs standard v0.2 operation IDs, registers reset and poweroff handlers, checks Trusted OS migration residency, and for PSCI 1.0+ initializes SMCCC discovery, CPU suspend feature bits, system suspend, `SYSTEM_RESET2`, `SYSTEM_OFF2`, and KVM hypervisor service discovery. PSCI 0.1 uses DT-provided function IDs and only fills operations whose properties exist.

Runtime calls funnel through `invoke_psci_fn()` and then map PSCI negative status codes to Linux errno via `psci_to_linux_errno()`. CPU idle either invokes PSCI directly for retention states or uses `cpu_suspend()` and `psci_suspend_finisher()` for context-losing states. Restart chooses `SYSTEM_RESET2` for warm/soft reboot when supported and otherwise uses `SYSTEM_RESET`; poweroff always uses PSCI 0.2 `SYSTEM_OFF`.

## State And Persistence
State is kernel-resident and initialized early: the selected conduit, PSCI function table, feature bits, and Trusted OS resident logical CPU are retained for the lifetime of the boot. There is no persistent storage, but the driver can change firmware suspend mode with `SET_SUSPEND_MODE` and can enter firmware-controlled reset/off/suspend states. `pm_power_off` and restart notifier registration make PSCI the active lifecycle backend.

## Dependencies And Integration Points
The file depends on SMCCC call helpers, OF/ACPI discovery, CPU hotplug and idle infrastructure, suspend/hibernate infrastructure, restart notifiers, debugfs, and architecture resume symbols. It also seeds `arm_smccc_version_init()` for later SMCCC users and invokes `kvm_init_hyp_services()` when PSCI/SMCCC discovery is new enough.

## Risks
Incorrect conduit selection breaks every PSCI call. PSCI 0.1 depends on firmware-provided DT function IDs and can have partial operation coverage. CPU suspend state validation is keyed off firmware feature bits; mismatched state encodings can produce failed suspend or deeper-than-expected idle. The driver deliberately avoids powering off a CPU hosting a UP Trusted OS, so bad `MIGRATE_INFO_UP_CPU` data can affect hotplug behavior. Reset/poweroff calls do not return on successful firmware action, making failures hard to recover from.

## Test Signals
Boot logs should show PSCI and SMCCC versions and conduit-related probing. Debugfs `psci` should enumerate optional PSCI functions accurately. CPU hotplug, cpuidle, system suspend, hibernation, warm reboot, cold reboot, and poweroff are the main integration tests. `psci_checker.c` provides a late-init stress test when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/psci/psci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/psci/psci_checker.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/psci/psci_checker.c

## Purpose
`psci_checker.c` is a late-init validation tool for PSCI CPU hotplug and suspend paths. It assumes PSCI is the active CPU enable method, then exercises CPU off/on sequences and cpuidle suspend states before userspace starts.

## Important APIs, Types, And Functions
- Global test state: `nb_available_cpus`, `tos_resident_cpu`, `nb_active_threads`, and two completions coordinating suspend test threads.
- PSCI validation: `psci_ops_check()` verifies `psci_ops.cpu_off`, `cpu_on`, and `cpu_suspend`; it also records the Trusted OS resident CPU when firmware reports a UP TOS.
- Hotplug tests: `down_and_up_cpus()`, `alloc_init_cpu_groups()`, `free_cpu_groups()`, and `hotplug_tests()`.
- Suspend tests: `suspend_cpu()`, `suspend_test_thread()`, and `suspend_tests()`.
- Entry point: `late_initcall(psci_checker)`.

## Control Flow
`psci_checker()` captures the number of online CPUs, validates PSCI operations, then first runs hotplug tests. The hotplug lane attempts to offline and online all CPUs, checks expected refusal for the last online CPU, and expects `-EPERM` when trying to offline the Trusted OS resident CPU. It repeats off/on testing by topology core groups.

The suspend lane pauses idle, creates one high-priority kthread per CPU with cpuidle support, then releases all threads through `suspend_threads_started`. Each thread loops through all cpuidle states except state 0 for ten cycles, arms a timer for wakeup, disables IRQs, invokes the cpuidle state's `enter()` callback through `suspend_cpu()`, and records successful, shallow, or failed entries. The main thread waits for all workers and then parks/stops them to collect return status.

## State And Persistence
All state is transient test state. The checker modifies live CPU topology during boot and pauses cpuidle while running suspend tests. It does not persist results outside kernel logs, but failed hotplug recovery can leave CPUs offline if firmware or the kernel cannot re-add them; the code warns if the offline mask is non-empty or the online CPU count differs from the initial count.

## Dependencies And Integration Points
The checker depends on PSCI global operations from `psci.c`, CPU hotplug (`remove_cpu()` and `add_cpu()`), cpuidle driver/device registration, topology core masks, scheduler priorities, timers, tick broadcast handling, and architecture idle hooks. It is intended for controlled validation and conflicts with concurrent hotplug/torture activity.

## Risks
The test is intrusive: it offlines CPUs and enters low-power states during late init. It assumes no other actor is using hotplug before userspace starts. It also assumes DT enable-method data is sensible on arm64 because there is no generic architecture check for PSCI usage. Missing or buggy cpuidle broadcast support can cause fallback to WFI and shallow-state counts.

## Test Signals
Kernel logs report start, per-group hotplug attempts, suspend cycles, per-CPU suspend results, and pass/error counts. Expected negative test signals are `-EBUSY` for the last online CPU and `-EPERM` for a TOS-resident CPU. Any positive error count, OOM, unavailable cpuidle devices, timeout, or CPU-count warning indicates firmware, topology, or kernel integration trouble.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/psci/psci_checker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/qcom/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/firmware/qcom/Kconfig

## Purpose
This Kconfig file declares the Qualcomm firmware driver menu and the build-time feature relationships for SCM, TrustZone memory allocation, QSEECOM, and the QSEECOM UEFI secure app client.

## Important Symbols
- `QCOM_SCM`: tristate core Secure Channel Manager support. It selects `QCOM_TZMEM`.
- `QCOM_TZMEM`: tristate TrustZone memory allocator support. It selects `GENERIC_ALLOCATOR`.
- `QCOM_TZMEM_MODE_GENERIC`: default allocator mode using page-aligned, non-cacheable, physically contiguous memory.
- `QCOM_TZMEM_MODE_SHMBRIDGE`: allocator mode that also creates Qualcomm Shared Memory Bridge objects; callers must then use TZMem buffers for TrustZone.
- `QCOM_QSEECOM`: bool interface driver for Qualcomm SEE/QSEECOM, depends on built-in `QCOM_SCM=y`, and selects `AUXILIARY_BUS`.
- `QCOM_QSEECOM_UEFISECAPP`: bool EFI-variable client for the QSEE `uefisecapp`, depends on QSEECOM and EFI.

## Control Flow And Integration
The choice block forces exactly one TZMem mode when `QCOM_TZMEM` is enabled. QSEECOM is limited to built-in SCM because it is initialized from SCM's probe path and registers client devices for secure applications. The UEFI secure app client becomes available only when QSEECOM can create auxiliary clients and EFI variable infrastructure exists.

## State And Persistence
There is no runtime state in Kconfig, but these options determine whether SCM and TZMem are modular or built in, whether SHM Bridge behavior is active, and whether EFI variables can be mediated through Qualcomm SEE.

## Risks
Selecting SHM Bridge changes the TrustZone buffer contract system-wide for these drivers and can break callers that pass non-TZMem buffers. The QSEECOM dependency on `QCOM_SCM=y` means modular SCM builds cannot use this interface. Misconfigured EFI/QSEECOM options can leave platforms without efivarfs access.

## Test Signals
Expected build results are `qcom-scm.o` and `qcom_tzmem.o` when SCM is enabled, plus QSEECOM objects when the bools are selected. Runtime logs from `qcom_scm_probe()`, TZMem SHM Bridge enablement, and QSEECOM probing confirm the selected configuration took effect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/qcom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/qcom/Makefile -->
# sources/distributed-fs/ceph-client/drivers/firmware/qcom/Makefile

## Purpose
The Makefile maps Qualcomm firmware configuration symbols to object files.

## Important Build Rules
- `obj-$(CONFIG_QCOM_SCM) += qcom-scm.o`
- `qcom-scm-objs += qcom_scm.o qcom_scm-smc.o qcom_scm-legacy.o`
- `obj-$(CONFIG_QCOM_TZMEM) += qcom_tzmem.o`
- `obj-$(CONFIG_QCOM_QSEECOM) += qcom_qseecom.o`
- `obj-$(CONFIG_QCOM_QSEECOM_UEFISECAPP) += qcom_qseecom_uefisecapp.o`

## Control Flow And Integration
The SCM composite object always links the main API/probe file with both modern SMCCC and legacy call transports, allowing runtime convention probing. TZMem, QSEECOM, and the UEFI client are independent objects governed by their Kconfig dependencies.

## State And Persistence
No runtime state is defined here; the file controls linkage and module composition.

## Risks
Dropping one of the SCM transport objects would break runtime fallback for platforms that require that convention. Enabling QSEECOM without the main SCM object being built in is prevented by Kconfig, not this Makefile.

## Test Signals
Build output should show the composite `qcom-scm` object containing the three SCM source objects. Link failures around SCM transport functions or QSEECOM exports point to mismatched config dependencies or object lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/qcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_qseecom.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_qseecom.c

## Purpose
`qcom_qseecom.c` is a small platform driver that turns loaded Qualcomm SEE applications into Linux auxiliary devices. It currently detects `qcom.tz.uefisecapp` and registers a `qcom_qseecom.uefisecapp` auxiliary client when the secure app is present.

## Important APIs, Types, And Functions
- `struct qseecom_app_desc` maps secure app names to auxiliary device names.
- `qseecom_client_register()` calls `qcom_scm_qseecom_app_get_id()`, allocates `struct qseecom_client`, initializes `auxiliary_device`, and registers devm cleanup.
- `qseecom_client_release()` and `qseecom_client_remove()` handle auxiliary lifetime.
- `qcom_qseecom_probe()` loops over `qcom_qseecom_apps`.
- `subsys_initcall(qcom_qseecom_init)` registers the platform driver named `qcom_qseecom`.

## Control Flow
SCM creates the parent platform device only on supported machines after QSEECOM version probing. This driver then probes that device, queries each configured secure app by name, skips absent apps with success, and creates an auxiliary device for present apps. Auxiliary client drivers match names such as `qcom_qseecom.uefisecapp` and use the stored app ID to send requests.

## State And Persistence
Per-client state is the allocated `struct qseecom_client` containing the app ID and embedded auxiliary device. The lifetime is tied to the parent platform device through `devm_add_action_or_reset()`. There is no persistent storage.

## Dependencies And Integration Points
The driver depends on `qcom_scm_qseecom_app_get_id()` from SCM, the auxiliary bus, and `linux/firmware/qcom/qcom_qseecom.h` for the client type. It is the bridge between SCM's generic QSEECOM transport and concrete auxiliary client drivers.

## Risks
Only already-loaded secure apps are discovered; firmware/bootloader load order controls device presence. Any non-`ENOENT` lookup error fails the whole probe. Auxiliary lifetime must call both `auxiliary_device_delete()` and `auxiliary_device_uninit()` to avoid leaks.

## Test Signals
A successful app discovery logs setup for the app and creates an auxiliary device matching the client driver's ID table. Absent apps should not fail probe. The UEFI secure app driver probing is the main downstream integration signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_qseecom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_qseecom_uefisecapp.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_qseecom_uefisecapp.c

## Purpose
This auxiliary driver implements EFI variable operations by talking to Qualcomm's QSEE `qcom.tz.uefisecapp` secure application. It is used on systems where EFI variables cannot be accessed directly and must be mediated by the secure execution environment.

## Important APIs, Types, And Functions
- Secure command structs: `qsee_req/rsp_uefi_get_variable`, `set_variable`, `get_next_variable`, and `query_variable_info`.
- Buffer layout helpers: `qcuefi_buf_align_fields()`, `__field_impl()`, `__reqdata_offs()`, and the array/field offset wrappers. These build contiguous, aligned request/response buffers.
- Secure app operations: `qsee_uefi_get_variable()`, `qsee_uefi_set_variable()`, `qsee_uefi_get_next_variable()`, and `qsee_uefi_query_variable_info()`.
- Global EFI wrappers: `qcuefi_get_variable()`, `qcuefi_set_variable()`, `qcuefi_get_next_variable()`, and `qcuefi_query_variable_info()` implement `struct efivar_operations`.
- Driver lifecycle: `qcom_uefisecapp_probe()`, `qcom_uefisecapp_remove()`, and the auxiliary ID `qcom_qseecom.uefisecapp`.

## Control Flow
Probe obtains the containing `qseecom_client`, creates a managed TZMem pool with 4 KiB initial size, multiplier growth, and 256 KiB cap, installs the singleton `__qcuefi`, and registers efivars. Each efivar callback locks the singleton, builds a command-specific contiguous TZMem buffer, populates UTF-16 variable names, GUIDs, attributes, and data, sends it through `qcom_qseecom_app_send()`, validates response command IDs, lengths, and offsets, converts secure app status to EFI status, and copies out data only after bounds checks.

`GET_VARIABLE` and `GET_NEXT_VARIABLE` handle EFI buffer-size negotiation by updating `data_size` or `name_size` on `EFI_BUFFER_TOO_SMALL`. `SET_VARIABLE` supports zero-length data as EFI deletion. `QUERY_VARIABLE_INFO` returns storage, remaining, and max variable sizes from the secure response.

## State And Persistence
The driver stores one global active client pointer protected by `__qcuefi_lock`, because global efivar operations do not carry per-device context. Firmware-backed EFI variables are persistent in platform storage, but this file only mediates access; it does not cache variable contents. Request buffers are allocated from TZMem and freed automatically by cleanup attributes.

## Dependencies And Integration Points
The driver depends on the QSEECOM auxiliary device, SCM's app send API, TZMem for TrustZone-safe buffers, EFI efivar registration, UTF-16 helpers, and OF/auxiliary module infrastructure. It exposes platform EFI variables to generic EFI users and efivarfs.

## Risks
The secure app is strict about contiguous aligned request and response placement; separate buffers caused missing responses or device crashes according to in-file notes. Response validation is security critical because firmware controls offsets and sizes. The singleton design allows only one active uefisecapp provider. Bad status conversion, name-size accounting, or missing NUL termination can surface as efivarfs corruption or EFI API failures.

## Test Signals
Successful probe should register efivars and allow efivarfs list/read/write/delete operations. Test edge cases include zero-size `GetVariable`, too-small buffers, long variable names near `QSEE_MAX_NAME_LEN`, `GetNextVariableName` iteration, and write/delete status mapping. Device logs with `uefisecapp error` identify secure app status failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_qseecom_uefisecapp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_scm-legacy.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_scm-legacy.c

## Purpose
`qcom_scm-legacy.c` implements the pre-SMCCC Qualcomm SCM calling convention. It supports both buffered synchronous calls and a restricted atomic register-call format.

## Important APIs, Types, And Functions
- `struct arm_smccc_args` holds up to eight SMC registers.
- `struct scm_legacy_command` and `struct scm_legacy_response` define the shared command/response buffer layout.
- Layout helpers: `scm_legacy_command_to_response()`, `scm_legacy_get_command_buffer()`, and `scm_legacy_get_response_buffer()`.
- Transport helpers: `__scm_legacy_do()` loops through `QCOM_SCM_INTERRUPTED`.
- Public internal APIs: `scm_legacy_call()` and `scm_legacy_call_atomic()`.
- Global serialization: `qcom_scm_lock`.

## Control Flow
`scm_legacy_call()` builds a page-aligned command buffer containing header, little-endian arguments, response header, and response data space. It DMA maps the buffer, invokes SMC command class `1` with a context pointer and command physical address, maps secure monitor status through `qcom_scm_remap_error()`, then polls the response header until `is_complete` is set and copies up to three little-endian return values.

`scm_legacy_call_atomic()` builds a legacy atomic ID containing service, command, register class, IRQ mask, and argument count. It passes up to five arguments directly in registers and returns up to three result registers. It assumes the command is uninterruptible, atomic, and SMP-safe.

## State And Persistence
There is no long-lived per-call state beyond the global mutex. DMA command buffers are allocated and freed for each non-atomic call. Firmware may modify secure-world state depending on the service command invoked by callers.

## Dependencies And Integration Points
The file is called by `qcom_scm.c` when runtime convention probing selects `SMC_CONVENTION_LEGACY`. It depends on SMCCC SMC helpers, DMA mapping, endianness conversion, and the shared descriptor/result definitions in `qcom_scm.h`.

## Risks
Callers must flush/invalidate any additional buffers shared with secure world; this file only maintains the command/response buffer. Atomic calls `BUG_ON()` if too many arguments are provided. Polling `is_complete` has no timeout, so broken firmware can hang. The command layout uses 32-bit little-endian fields and can truncate if callers pass unsupported wide arguments under the legacy convention.

## Test Signals
Legacy platforms should complete convention probing and secure calls without falling back to SMCCC. Tests should cover non-atomic calls with arguments/results, interrupted SMC retry, and atomic boot/power operations. Hangs in response polling or `QCOM_SCM_INTERRUPTED` loops indicate firmware transport issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_scm-legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_scm-smc.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_scm-smc.c

## Purpose
`qcom_scm-smc.c` implements the modern Qualcomm SCM SMCCC transport for ARM 32-bit and 64-bit conventions, including extended argument buffers in TZMem and Qualcomm waitqueue handling.

## Important APIs, Types, And Functions
- `struct arm_smccc_args` holds eight SMC argument registers.
- `__scm_smc_do_quirk()` invokes `arm_smccc_smc_quirk()` with the Qualcomm A6 quirk and retries `QCOM_SCM_INTERRUPTED`.
- Waitqueue helpers: `fill_wq_resume_args()`, `scm_get_wq_ctx()`, and `__scm_smc_do_quirk_handle_waitq()`.
- Call executor: `__scm_smc_do()` serializes non-atomic calls, handles waitqueue sleep/resume, and retries `QCOM_SCM_V2_EBUSY`.
- Main API: `__scm_smc_call()` builds SMCCC call values and copies overflow arguments to TZMem.

## Control Flow
`__scm_smc_call()` encodes call type, 32/64-bit convention, owner, service, and command into `a0`, places `arginfo` in `a1`, and stores the first four arguments in registers. When more than four arguments are required, it allocates a TZMem buffer from SCM's pool, writes the remaining arguments as little-endian 32-bit or 64-bit values depending on convention, and passes its physical address in the last register argument.

Atomic calls invoke once through the quirk path. Non-atomic calls take `qcom_scm_lock`, run the waitqueue-aware call loop, release the lock, and retry `QCOM_SCM_V2_EBUSY` up to 20 times with 30 ms sleeps. If firmware returns `QCOM_SCM_WAITQ_SLEEP`, the code waits on the SCM waitqueue completion and resumes the secure call with `QCOM_SCM_WAITQ_RESUME`.

## State And Persistence
The transport has only the global mutex. Extended argument buffers are temporary TZMem allocations. Waitqueue sleep state is held by secure firmware and resumed through call context IDs supplied in firmware responses.

## Dependencies And Integration Points
This transport is used by `qcom_scm.c` for `SMC_CONVENTION_ARM_32` and `SMC_CONVENTION_ARM_64`. It depends on TZMem, SCM waitqueue completion APIs in `qcom_scm.c`, SMCCC helpers, DMA-safe memory, and shared SCM descriptor/error definitions.

## Risks
All extended-argument calls require an initialized SCM TZMem pool; otherwise they fail with `-EINVAL`. Waitqueue handling depends on IRQ/completion setup in SCM probe. Long or stuck firmware waitqueues can stall callers. Atomic callers bypass busy retry and waitqueue handling, so they must only use firmware calls that are safe in atomic context.

## Test Signals
Convention probing should select ARM32 or ARM64 on modern platforms. Extended-argument users such as memory assignment and HDCP should pass arguments correctly. Waitqueue-capable firmware can be tested by commands that sleep and later wake through SCM IRQ; failures show as waitqueue timeouts, invalid context warnings, or `GET_WQ_CTX` errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_scm-smc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_scm.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_scm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_scm.h -->
# sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_scm.h

## Purpose
This private header defines SCM internal call descriptors, argument metadata, transport prototypes, service/command IDs, common SCM error codes, and the shared error remapping helper used by `qcom_scm.c`, `qcom_scm-smc.c`, and `qcom_scm-legacy.c`.

## Important APIs, Types, And Macros
- `enum qcom_scm_convention`: unknown, legacy, ARM32 SMCCC, ARM64 SMCCC.
- `enum qcom_scm_arg_types`: value, read-only buffer, read-write buffer, and buffer-value.
- `QCOM_SCM_ARGS()` encodes argument count and per-argument type tags into the `arginfo` word.
- `struct qcom_scm_desc` carries service, command, argument metadata, up to ten 64-bit args, and owner.
- `struct qcom_scm_res` carries up to three return values.
- Transport prototypes: `__scm_smc_call()`, `scm_legacy_call()`, `scm_legacy_call_atomic()`, and the `scm_smc_call()` wrapper using global convention.
- Service constants cover boot, PIL/PAS, IO, info, memory protection, OCMEM, enterprise security/ICE, HDCP, LMH, SMMU, waitqueue, GPU, and trusted OS SMC invoke.
- `qcom_scm_remap_error()` maps SCM negative status codes to Linux errno.

## Control Flow And Integration
Callers fill `qcom_scm_desc` with IDs and `QCOM_SCM_ARGS()` metadata, then transport files encode it for either modern SMCCC or legacy SMC. `qcom_scm.c` uses these constants to implement higher-level exported APIs. Waitqueue prototypes bridge the SMCCC transport back to the core SCM interrupt/completion handling.

## State And Persistence
The header declares the global `qcom_scm_convention` but owns no storage itself. Its constants define firmware state transitions performed by implementation files.

## Dependencies And Integration Points
It depends on forward declarations for `struct device` and `struct qcom_tzmem_pool`, plus public Qualcomm firmware headers for external types. It is the internal ABI between SCM implementation units.

## Risks
Incorrect `arginfo` encoding or service/command IDs can route secure calls incorrectly. `qcom_scm_remap_error()` defaults unknown errors to `-EINVAL`, which can hide firmware-specific status. The header allows up to ten arguments and three returns; call sites must respect transport-specific limits and extended-buffer behavior.

## Test Signals
Compile-time tests catch missing prototypes or constants. Runtime call-availability probes and successful high-level SCM operations validate that service IDs, command IDs, and argument metadata match firmware expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_scm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_tzmem.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_tzmem.c

## Purpose
`qcom_tzmem.c` provides a TrustZone-safe memory allocator for Qualcomm firmware drivers. It creates genalloc-backed pools over coherent DMA memory and optionally wraps each area in a Qualcomm SHM Bridge so TrustZone accepts the buffers.

## Important APIs, Types, And Functions
- Internal types: `struct qcom_tzmem_area`, `struct qcom_tzmem_pool`, and `struct qcom_tzmem_chunk`.
- Global state: `qcom_tzmem_dev`, radix tree `qcom_tzmem_chunks`, and `qcom_tzmem_chunks_lock`.
- Mode hooks: `qcom_tzmem_init()`, `qcom_tzmem_init_area()`, and `qcom_tzmem_cleanup_area()` differ between generic and SHM Bridge configurations.
- SHM Bridge exports: `qcom_tzmem_shm_bridge_create()` and `qcom_tzmem_shm_bridge_delete()`.
- Pool APIs: `qcom_tzmem_pool_new()`, `qcom_tzmem_pool_free()`, and `devm_qcom_tzmem_pool_new()`.
- Allocation APIs: `qcom_tzmem_alloc()`, `qcom_tzmem_free()`, and `qcom_tzmem_to_phys()`.
- Enable API: `qcom_tzmem_enable()`.

## Control Flow
`qcom_tzmem_enable()` records the SCM device and initializes mode-specific behavior. In SHM Bridge mode it skips blacklisted SoCs, calls `qcom_scm_shm_bridge_enable()`, and records whether bridge creation should be active. Pools are created with static, multiplier, or on-demand growth policies and optionally prefilled with coherent DMA areas. Each area is added to a `gen_pool`, tracked in the pool's area list, and optionally assigned a SHM Bridge handle.

Allocations round up to page size, allocate a chunk record, try `gen_pool_alloc()`, grow the pool if allowed, and insert a chunk record into a global radix tree keyed by virtual address. Free looks up the chunk, returns memory to the owning pool, and frees the record. Physical address translation scans owned chunks and delegates to `gen_pool_virt_to_phys()`.

## State And Persistence
The allocator maintains boot/module-lifetime global device state, per-pool area lists and gen_pools, per-allocation chunk metadata, and optional SHM Bridge handles. Memory is coherent DMA memory and is not persisted, but SHM Bridge creation/deletion changes secure firmware's view of shared memory.

## Dependencies And Integration Points
It depends on DMA coherent allocation, generic allocator, radix tree, spinlocks, device tree machine matching, and SCM SHM Bridge calls. SCM and QSEECOM/UEFI clients use it for buffers passed to TrustZone.

## Risks
`qcom_tzmem_enable()` is singleton and returns `-EBUSY` on repeated enable. Freeing a pool with outstanding chunks triggers a warning and risks leaks or use-after-free. `qcom_tzmem_to_phys()` scans all chunks and returns zero on failure; callers must treat zero as invalid. SHM Bridge mode is blacklisted for known-broken machines, but unsupported firmware or non-TZMem buffers can still fail secure calls.

## Test Signals
Pool creation should succeed in static, multiplier, and on-demand policies. Allocation/free should leave no non-empty pool warnings. SHM Bridge mode should log unsupported on blacklisted/unsupported platforms and create/delete handles on supported platforms. SCM extended-argument, QSEECOM, and EFI variable operations validate allocator integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_tzmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_tzmem.h -->
# sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_tzmem.h

## Purpose
This private header exposes only the TZMem enable hook needed by the SCM core.

## Important API
- `int qcom_tzmem_enable(struct device *dev);`

## Control Flow And Integration
`qcom_scm_probe()` calls `qcom_tzmem_enable()` before creating SCM's TZMem pool. The public allocation APIs live in `linux/firmware/qcom/qcom_tzmem.h`; this private header is for SCM/TZMem internal coordination.

## State And Persistence
No state is stored in the header. The call initializes the singleton device pointer and mode-specific allocator behavior in `qcom_tzmem.c`.

## Risks
The narrow header helps prevent arbitrary users from enabling the allocator. Calling enable more than once fails because the implementation is singleton.

## Test Signals
SCM probe failure with "Failed to enable the TrustZone memory allocator" points to this initialization path. Successful later TZMem pool creation confirms the hook worked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_tzmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/qemu_fw_cfg.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/qemu_fw_cfg.c

## Purpose
`qemu_fw_cfg.c` exposes QEMU's firmware configuration device under `/sys/firmware/qemu_fw_cfg`. It supports ACPI, device tree, and optional command-line platform-device creation, then publishes fw_cfg directory entries by selector key and by firmware-provided path name.

## Important APIs, Types, And Functions
- Global device state: `fw_cfg_rev`, register base/size, `fw_cfg_dev_base`, `fw_cfg_reg_ctrl`, `fw_cfg_reg_data`, `fw_cfg_reg_dma`, and `fw_cfg_dev_lock`.
- Register access: `fw_cfg_sel_endianness()`, `fw_cfg_read_blob()`, optional `fw_cfg_write_blob()`, and DMA helpers under `CONFIG_VMCORE_INFO`.
- Sysfs entry model: `struct fw_cfg_sysfs_entry`, `struct fw_cfg_sysfs_attribute`, `fw_cfg_sysfs_entry_ktype`, and binary `raw` attribute.
- Directory registration: `fw_cfg_register_dir_entries()`, `fw_cfg_register_file()`, `fw_cfg_build_symlink()`, and recursive kset cleanup.
- Probe/remove: `fw_cfg_do_platform_probe()`, `fw_cfg_sysfs_probe()`, `fw_cfg_sysfs_remove()`, `fw_cfg_sysfs_init()`, and `fw_cfg_sysfs_exit()`.
- Optional command line: `fw_cfg_cmdline_set()` and `fw_cfg_cmdline_get()` for `ioport=` and `mmio=`.

## Control Flow
Module init creates the top-level firmware kobject and registers a platform driver. Probe refuses a second device, creates `by_key` and `by_name`, maps IO or MMIO resources, resolves register offsets, verifies the `QEMU` signature, reads revision, creates `rev`, reads the firmware file directory, allocates one sysfs entry per file, adds metadata attributes plus a raw binary file, and best-effort builds a path-like symlink tree under `by_name`.

Reads acquire the ACPI global lock when available, serialize device access with `fw_cfg_dev_lock`, select the fw_cfg key with endian handling, skip to the requested offset by reading bytes, and copy the requested data. Optional VMCORE_INFO support writes guest vmcoreinfo through the DMA register path when supported.

## State And Persistence
The driver uses global singleton state for the one system fw_cfg device. Sysfs kobjects and the entry cache persist while the module/device is active. It does not persist host data; it reflects QEMU-provided firmware blobs and optionally writes vmcoreinfo to fw_cfg for crash dump support.

## Dependencies And Integration Points
It integrates with platform devices from ACPI, OF, or command line; sysfs/kobject infrastructure; firmware kobject; IO/MMIO mapping; ACPI global locking; crash dump/vmcoreinfo; and QEMU's fw_cfg UAPI structs. It is architecture-sensitive because default register offsets differ by architecture.

## Risks
The device is singleton and uses global state, so a second probe returns `-EBUSY`. Firmware-provided names may collide or contain awkward path components; symlink creation is best effort. Raw reads use byte skipping for offsets and can be slow. Command-line parsing must avoid resource overflow and malformed offset combinations. DMA support assumes physical addresses are acceptable because fw_cfg does not need IOMMU protection.

## Test Signals
On QEMU, `/sys/firmware/qemu_fw_cfg/rev`, `by_key/*/{size,key,name,raw}`, and `by_name` links should appear. Signature verification should reject non-QEMU devices. Reads of known fw_cfg blobs, command-line `ioport`/`mmio` registration, and vmcoreinfo write warnings are key validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/qemu_fw_cfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/raspberrypi.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/raspberrypi.c

## Purpose
`raspberrypi.c` implements the Raspberry Pi firmware property-channel driver. It provides synchronous mailbox transactions to VPU firmware, exports property-list helpers to other drivers, registers legacy hwmon/clock platform devices, and manages shared firmware handles by reference count.

## Important APIs, Types, And Functions
- `struct rpi_firmware` stores mailbox client/channel, transaction completion, and `kref` consumers.
- Mailbox helpers: `response_callback()` and `rpi_firmware_transaction()`.
- Exported property APIs: `rpi_firmware_property_list()` and `rpi_firmware_property()`.
- Clock helper: `rpi_firmware_clk_get_max_rate()`.
- Handle APIs: `rpi_firmware_find_node()`, `rpi_firmware_get()`, `rpi_firmware_put()`, and `devm_rpi_firmware_get()`.
- Driver lifecycle: `rpi_firmware_probe()`, `rpi_firmware_shutdown()`, and `rpi_firmware_remove()`.

## Control Flow
Probe allocates non-devm firmware state, configures a blocking mailbox client with callback completion, requests channel 0, initializes completion and reference count, stores driver data, prints firmware revision, and registers child hwmon/clock devices if supported/needed. Property calls allocate coherent DMA memory, build the firmware property buffer header and terminator, issue a mailbox transaction on channel 8, enforce memory barriers around firmware access, copy tag data back, validate firmware status, and free the DMA buffer.

Consumers find the firmware DT node, obtain the platform device, get the driver data, increment the kref unless zero, and later release with `rpi_firmware_put()`. Shutdown sends a reboot notification property.

## State And Persistence
Firmware handle state persists until the platform device and all consumers release references. The transaction lock serializes mailbox property access globally. Firmware properties can read and change persistent or hardware state in the VPU firmware, but the driver itself caches only handle/channel state and global child platform-device pointers.

## Dependencies And Integration Points
The driver depends on the BCM2835 mailbox framework, coherent DMA, OF platform devices, Raspberry Pi firmware tag definitions, kref lifetime management, hwmon and clock child drivers, and platform shutdown callbacks.

## Risks
Mailbox transactions have a one-second timeout; stuck firmware yields warnings and failed property calls. The transaction buffer must be 32-bit aligned and below the firmware's practical size limit. `rpi_firmware_property()` copies back tag data even when the underlying call fails, so callers should heed return codes. Global child pointers assume a single firmware device. Passing `NULL` tag data with zero size is valid but must not be dereferenced by callers.

## Test Signals
Probe should log the firmware revision date and create child platform devices when supported. Property reads such as `GET_FIRMWARE_REVISION`, `GET_THROTTLED`, and clock-rate queries validate transactions. Shutdown should send `RPI_FIRMWARE_NOTIFY_REBOOT`. Timeout warnings or firmware status errors identify mailbox or firmware issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/raspberrypi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/samsung/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/firmware/samsung/Kconfig

## Purpose
This Kconfig file declares `EXYNOS_ACPM_PROTOCOL`, the Samsung Exynos Alive Clock and Power Manager mailbox protocol driver.

## Important Symbol
- `EXYNOS_ACPM_PROTOCOL`: tristate, depends on `ARCH_EXYNOS || COMPILE_TEST` and `MAILBOX`. It provides client-driver interfaces to APM/ACPM firmware features.

## Control Flow And Integration
Selecting this option builds the composite ACPM protocol object. The help text positions ACPM as an APM firmware communication protocol for AP, AOC, and other masters.

## State And Persistence
No runtime state is stored here; the option controls availability of ACPM protocol code and downstream PMIC/DVFS operations.

## Risks
The driver requires mailbox support and Exynos-compatible firmware shared-memory layout. Enabling under `COMPILE_TEST` verifies buildability but not firmware behavior.

## Test Signals
Build output should include `acpm-protocol.o`, and runtime probing should match compatible ACPM IPC nodes such as `google,gs101-acpm-ipc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/samsung/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/samsung/Makefile -->
# sources/distributed-fs/ceph-client/drivers/firmware/samsung/Makefile

## Purpose
The Makefile builds the Samsung ACPM protocol as a composite object.

## Important Build Rules
- `acpm-protocol-objs := exynos-acpm.o`
- Adds `exynos-acpm-pmic.o` and `exynos-acpm-dvfs.o`.
- `obj-$(CONFIG_EXYNOS_ACPM_PROTOCOL) += acpm-protocol.o`

## Control Flow And Integration
The core queue/mailbox driver and PMIC/DVFS command helpers are linked together when ACPM protocol support is enabled, making the ops table in `exynos-acpm.c` able to reference both helper modules.

## State And Persistence
No runtime state; linkage only.

## Risks
Removing helper objects would break ops setup or leave clients without PMIC/DVFS operations.

## Test Signals
Successful build should produce the composite `acpm-protocol` object and resolve `acpm_pmic_*` and `acpm_dvfs_*` references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/samsung/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm-dvfs.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm-dvfs.c

## Purpose
`exynos-acpm-dvfs.c` builds ACPM DVFS commands for setting and querying firmware-managed clock rates.

## Important APIs And Functions
- `acpm_dvfs_set_xfer()` fills `struct acpm_xfer` with command buffers, channel ID, and optional response.
- `acpm_dvfs_init_set_rate_cmd()` encodes clock ID, rate in kHz, request type, and timestamp.
- `acpm_dvfs_set_rate()` sends a no-response frequency request.
- `acpm_dvfs_init_get_rate_cmd()` encodes a frequency-get request.
- `acpm_dvfs_get_rate()` sends the request and returns response rate converted from kHz to Hz.

## Control Flow
Clients call the ops installed by `exynos-acpm.c`. The helper fills a four-word command, assigns the ACPM channel, and calls `acpm_do_xfer()`. Set-rate ignores firmware response content, while get-rate expects the same command buffer to be updated and returns `xfer.rxd[1] * HZ_PER_KHZ`, or zero on transfer failure.

## State And Persistence
This file stores no persistent state. It asks ACPM firmware to change or report clock state; set-rate changes persist in firmware/hardware until later policy updates.

## Dependencies And Integration Points
It depends on the core ACPM transfer API, bitfield helpers, firmware protocol public header, and timekeeping for timestamps. It is installed into `acpm_handle.ops.dvfs_ops`.

## Risks
Rate conversion truncates to kHz for firmware and returns zero on transfer failure, which can also be a valid-looking rate sentinel to callers. Command format depends on firmware bitfield layout. The command buffer is stack-local and must remain valid only for the synchronous `acpm_do_xfer()` duration.

## Test Signals
Clock clients should be able to set rates and read back expected values through ACPM. Transfer errors from `acpm_do_xfer()` or zero get-rate responses indicate mailbox/firmware problems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm-dvfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm-dvfs.h -->
# sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm-dvfs.h

## Purpose
This private header declares ACPM DVFS helper functions used by the core ACPM ops setup.

## Important APIs
- `acpm_dvfs_set_rate(struct acpm_handle *handle, unsigned int acpm_chan_id, unsigned int id, unsigned long rate)`
- `acpm_dvfs_get_rate(struct acpm_handle *handle, unsigned int acpm_chan_id, unsigned int clk_id)`

## Control Flow And Integration
`exynos-acpm.c` assigns these functions to `acpm->handle.ops.dvfs_ops`, exposing them to ACPM protocol clients through the public firmware protocol handle.

## State And Persistence
No state is owned by the header. The implementation changes or reads firmware-managed DVFS state.

## Risks
The header is private to the composite object; public consumers should use the protocol ops rather than include this file.

## Test Signals
Build failures involving DVFS ops setup or missing prototypes point to this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm-dvfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm-pmic.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm-pmic.c

## Purpose
`exynos-acpm-pmic.c` builds ACPM PMIC commands for register read, bulk read, write, bulk write, and masked update operations.

## Important APIs, Types, And Functions
- Bitfield definitions encode channel, PMIC type, register, return code, mask, value, and function ID.
- `enum exynos_acpm_pmic_func` defines read/write/update/bulk command IDs.
- Error mapping: `acpm_pmic_linux_errmap[]` and `acpm_pmic_to_linux_err()`.
- Bulk packing helpers: `acpm_pmic_set_bulk()` and `acpm_pmic_get_bulk()`.
- Command initializers for each operation type.
- Exported internal helpers: `acpm_pmic_read_reg()`, `acpm_pmic_bulk_read()`, `acpm_pmic_write_reg()`, `acpm_pmic_bulk_write()`, and `acpm_pmic_update_reg()`.

## Control Flow
Each operation fills a four-word command with PMIC address fields and function code, uses `acpm_pmic_set_xfer()` to make the command both TX and RX, calls `acpm_do_xfer()`, and maps the firmware return field to Linux errno. Reads extract the value field; bulk reads unpack up to eight bytes from response words 2 and 3; bulk writes pack up to eight bytes into command words 2 and 3.

## State And Persistence
The file stores no state. PMIC writes and updates persist in hardware/firmware PMIC state until changed again. Command buffers are stack-local and synchronous.

## Dependencies And Integration Points
It depends on the core ACPM transfer API, bitfield helpers, timekeeping for timestamps on some commands, and the public ACPM protocol handle. `exynos-acpm.c` installs these helpers into `pmic_ops`.

## Risks
Bulk count is capped at eight bytes; larger requests return `-EINVAL`. Firmware return codes outside the known map become `-EIO`. Command fields are compact and firmware-specific, so bitfield mistakes can target wrong channels/registers. Some bulk command initializers do not set timestamps, so compatibility depends on firmware not requiring them for those functions.

## Test Signals
PMIC clients should read/write single registers, bulk transfer up to eight bytes, and perform masked updates with expected hardware effects. Firmware access errors should map to `-EACCES`; unknown firmware status should become `-EIO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm-pmic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm-pmic.h -->
# sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm-pmic.h

## Purpose
This private header declares ACPM PMIC helper functions used when wiring the public ACPM protocol ops.

## Important APIs
It declares single-register read/write/update and bulk read/write helpers, all taking `struct acpm_handle *`, ACPM channel ID, PMIC type/register/channel addressing, and operation-specific buffers or values.

## Control Flow And Integration
`exynos-acpm.c` assigns these helpers to `acpm->handle.ops.pmic_ops`, allowing public ACPM clients to perform PMIC operations without depending on this private header.

## State And Persistence
No state is stored here; implementation functions alter firmware/PMIC state.

## Risks
Callers inside the composite object must pass valid buffers and respect the implementation's eight-byte bulk limit.

## Test Signals
Build and ops-table setup validate the header. Runtime PMIC client operations validate the implementation behind these prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm-pmic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm.c

## Purpose
`exynos-acpm.c` is the Samsung Exynos ACPM mailbox protocol core. It maps firmware shared memory, initializes ACPM channels, sends synchronous messages through shared-memory queues and mailbox doorbells, and exposes a managed `acpm_handle` to client drivers.

## Important APIs, Types, And Functions
- Shared-memory descriptors: `struct acpm_shmem` and `struct acpm_chan_shmem`.
- Runtime queues and channel state: `struct acpm_queue`, `struct acpm_rx_data`, `struct acpm_chan`, and `struct acpm_info`.
- Transfer API: `acpm_do_xfer()` is the central message-send function.
- RX/sequence helpers: `acpm_get_saved_rx()`, `acpm_get_rx()`, `acpm_dequeue_by_polling()`, `acpm_prepare_xfer()`, and `acpm_wait_for_message_response()`.
- Queue setup: `acpm_chan_shmem_get_params()`, `acpm_achan_alloc_cmds()`, `acpm_channels_init()`, and `acpm_free_mbox_chans()`.
- Client handle APIs: `devm_acpm_get_by_node()` with internal `acpm_get_by_node()` and `acpm_handle_put()`.
- Probe: `acpm_probe()` maps SRAM, initializes channels, installs PMIC/DVFS ops, registers an ACPM clock platform device, and populates child OF devices.

## Control Flow
Probe resolves the `shmem` phandle, maps the SRAM region, applies match data to find channel init data, reads channel count and queue offsets from shared memory, allocates per-channel state and per-sequence RX buffers, initializes locks, and requests mailbox channel 0 for each ACPM channel. It then installs DVFS/PMIC ops into the handle and registers a platform clock device named by match data.

`acpm_do_xfer()` validates channel and message lengths, rejects interrupt mode because only polling is implemented, locks the TX queue, waits for queue slots, assigns a nonzero sequence number not already in the bitmap, records response expectations, writes the TX words into SRAM, advances TX front, sends a mailbox doorbell, marks TX done, releases the TX lock, and polls RX until the sequence bit clears or timeout expires. RX draining saves out-of-order responses in per-sequence buffers and clears bitmap bits when responses are consumed.

## State And Persistence
The driver stores mapped SRAM pointers, per-channel queue pointers, locks, sequence numbers, pending sequence bitmap, saved RX data, mailbox channels, and a public handle. Firmware/hardware state lives in shared SRAM and ACPM. Device links and module references keep the ACPM supplier alive while consumers hold handles.

## Dependencies And Integration Points
It depends on OF phandles, ioremap, Exynos mailbox messages, mailbox client APIs, shared-memory ACPM firmware layout, child platform population, and PMIC/DVFS helper modules. It exposes functionality through `linux/firmware/samsung/exynos-acpm-protocol.h`.

## Risks
Only polling completion is supported; channels requiring interrupt mode return `-EOPNOTSUPP`. Queue pointer interpretation is inverted from firmware perspective and must match shared memory layout. Sequence numbers range 1..63; bitmap handling must prevent reuse while pending. RX buffer allocation scales with channel message length and sequence count. Timeout paths can leave pending bitmap bits until subsequent cleanup behavior.

## Test Signals
Probe should map SRAM, initialize all channels, request mailboxes, and register the ACPM clock device. PMIC and DVFS operations should complete through `acpm_do_xfer()`. Timeout logs showing channel, sequence, and bitmap identify queue or firmware stalls. Device-link behavior can be tested by consumer probe/remove cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm.h -->
# sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm.h

## Purpose
This private header defines the ACPM transfer descriptor and declares the core synchronous transfer function used by PMIC and DVFS helpers.

## Important APIs And Types
- `struct acpm_xfer` contains counted TX/RX word pointers, TX/RX word counts, and ACPM channel ID.
- `struct acpm_handle` is forward declared.
- `int acpm_do_xfer(struct acpm_handle *handle, const struct acpm_xfer *xfer);`

## Control Flow And Integration
Helper modules build `acpm_xfer` structures and pass them to `acpm_do_xfer()` in `exynos-acpm.c`. Public clients use ops stored in `struct acpm_handle`, not this private header directly.

## State And Persistence
The header owns no state. `acpm_xfer` is per-call state whose buffers must remain valid for the synchronous transfer.

## Risks
The counted pointer annotations document buffer sizes but runtime validation still depends on the core checking counts against channel message length.

## Test Signals
Compile-time type checking of PMIC/DVFS helpers and successful synchronous transfers validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/smccc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/firmware/smccc/Kconfig

## Purpose
This Kconfig file declares generic ARM SMCCC support, discovery support, and optional SoC bus registration through SMCCC `ARCH_SOC_ID`.

## Important Symbols
- `HAVE_ARM_SMCCC`: base architecture support for SMC/HVC instructions.
- `HAVE_ARM_SMCCC_DISCOVERY`: depends on `ARM_PSCI_FW`, defaults yes, and enables PSCI-mediated SMCCC v1.1+ discovery.
- `ARM_SMCCC_SOC_ID`: bool SoC bus device for SMCCC SOC_ID, depends on discovery, defaults yes, and selects `SOC_BUS`.

## Control Flow And Integration
PSCI initializes SMCCC version/conduit discovery. When discovery support is enabled, `smccc.o` and `kvm_guest.o` are built; SOC_ID support adds `soc_id.o`.

## State And Persistence
No runtime state is stored in Kconfig. The symbols determine whether SMCCC global version, KVM hypervisor service discovery, TRNG device registration, and SOC bus registration are available.

## Risks
Without PSCI firmware discovery, later SMCCC features are unavailable even if firmware implements them. SOC_ID depends on firmware returning valid version and revision.

## Test Signals
Build output should include SMCCC objects when enabled. Runtime logs and sysfs SoC device attributes validate discovery and SOC_ID behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/smccc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/smccc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/firmware/smccc/Makefile

## Purpose
The Makefile maps SMCCC discovery and SOC_ID configuration to object files.

## Important Build Rules
- `obj-$(CONFIG_HAVE_ARM_SMCCC_DISCOVERY) += smccc.o kvm_guest.o`
- `obj-$(CONFIG_ARM_SMCCC_SOC_ID) += soc_id.o`

## Control Flow And Integration
Generic SMCCC discovery and KVM guest service discovery are linked together. SOC bus registration is independent but depends on discovery through Kconfig.

## State And Persistence
No runtime state; linkage only.

## Risks
Missing `kvm_guest.o` with discovery would break PSCI's call to `kvm_init_hyp_services()`. Missing `soc_id.o` only removes sysfs SoC identity.

## Test Signals
Successful link should resolve SMCCC global discovery and KVM service functions referenced by PSCI and architecture code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/smccc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/smccc/kvm_guest.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/smccc/kvm_guest.c

## Purpose
`kvm_guest.c` discovers ARM SMCCC KVM vendor hypervisor services and exposes service availability to guest code. On arm64 it can also discover target CPU implementation identity supplied by the hypervisor for errata handling.

## Important APIs And Functions
- Global bitmap `__kvm_arm_hyp_services` stores KVM service bits after init.
- `kvm_init_hyp_services()` checks the KVM hypervisor UUID, calls the KVM features function, and populates the bitmap.
- `kvm_arm_hyp_service_available()` tests service availability and is exported.
- `kvm_arm_target_impl_cpu_init()` discovers implementation CPU version/count/IDs and calls `cpu_errata_set_target_impl()` on arm64.

## Control Flow
PSCI calls `kvm_init_hyp_services()` after SMCCC discovery. The function first verifies the hypervisor UUID through `arm_smccc_hypervisor_has_uuid()`, invokes KVM feature discovery, converts four result registers into a bitmap, logs detected services, and lets architecture code initialize additional hypervisor services. The target implementation path checks required service bits, validates version major 1, allocates early memory for CPU implementation descriptors, queries each CPU, and either installs them for errata matching or frees memory on failure.

## State And Persistence
The service bitmap is `__ro_after_init`, so it becomes immutable after initialization. Target implementation data is allocated from memblock for early boot and retained if accepted by CPU errata code.

## Dependencies And Integration Points
It depends on SMCCC 1.1 invocation, hypervisor UUID discovery, PSCI version encoding macros, memblock, and architecture hypervisor/errata hooks. It is meaningful only under KVM/ARM hypervisors exposing the vendor interface.

## Risks
Feature bitmap interpretation depends on `ARM_SMCCC_KVM_NUM_FUNCS`. Unsupported target implementation versions are ignored. Failed partial CPU discovery must free memblock allocations. If the hypervisor advertises services incorrectly, downstream code may assume unavailable behavior.

## Test Signals
Under KVM, logs should show detected hypervisor services. `kvm_arm_hyp_service_available()` should match advertised feature bits. On arm64 with target implementation support, logs should show CPU count or warnings for unsupported/failed discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/smccc/kvm_guest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/smccc/smccc.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/smccc/smccc.c

## Purpose
`smccc.c` stores global ARM SMCCC discovery results and registers SMCCC-backed devices such as TRNG. It is initialized by PSCI when firmware reports SMCCC v1.1+ support.

## Important APIs And Functions
- Global state: `smccc_version`, `smccc_conduit`, `smccc_trng_available`, `smccc_soc_id_version`, and `smccc_soc_id_revision`.
- `arm_smccc_version_init()` records version/conduit, probes TRNG, and for SMCCC 1.2+ queries `ARCH_SOC_ID`.
- `arm_smccc_1_1_get_conduit()` and `arm_smccc_get_version()` are exported.
- `arm_smccc_get_soc_id_version()` and exported `arm_smccc_get_soc_id_revision()` expose SOC_ID data.
- `arm_smccc_hypervisor_has_uuid()` checks vendor hypervisor UUID.
- `smccc_devices_init()` registers `smccc_trng` if available.

## Control Flow
PSCI calls `arm_smccc_version_init()` with the discovered SMCCC version and conduit. The function probes architecture TRNG support and, when supported, uses `ARM_SMCCC_ARCH_FEATURES` to detect `ARCH_SOC_ID`, then queries version and revision. Later, a device initcall registers a simple `smccc_trng` platform device when TRNG is available.

## State And Persistence
Discovery state is stored in `__ro_after_init` globals where applicable and persists for the boot. There is no persistent storage; the values reflect firmware responses.

## Dependencies And Integration Points
It depends on SMCCC call helpers, PSCI/SMCCC version encodings, architecture random support, and platform-device registration. `soc_id.c`, KVM discovery, and hypervisor-specific drivers consume these values and helpers.

## Risks
The default version is SMCCC 1.0 until PSCI initializes it, so users must not assume discovery happened early. SOC_ID values are accepted only if the feature probe succeeds and returned values are nonnegative. Hypervisor UUID checks rely on vendor call availability.

## Test Signals
Boot logs from PSCI should report SMCCC version. Presence of the `smccc_trng` platform device, successful SOC_ID sysfs registration, and correct hypervisor UUID matching validate discovery paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/smccc/smccc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/smccc/soc_id.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/smccc/soc_id.c

## Purpose
`soc_id.c` registers a Linux SoC bus device using ARM SMCCC `ARCH_SOC_ID` data. On arm64 it can also fetch the optional firmware-provided SoC name string introduced in newer SMCCC revisions.

## Important APIs, Types, And Functions
- Bitfield macros extract JEP106 bank, JEP106 ID code, and implementation-defined SoC ID.
- Global objects: `soc_dev` and `soc_dev_attr`.
- arm64 name helpers: `str_fragment_from_reg()` and `smccc_soc_name_init()` copy registers `a1..a17` into a 136-byte NUL-terminated name buffer.
- `smccc_soc_init()` validates SMCCC/SOC_ID support, formats family/soc/revision strings, and registers `soc_device`.
- `smccc_soc_exit()` unregisters and frees state.

## Control Flow
Module init first requires SMCCC version at least 1.2 and a supported SOC_ID version. It rejects negative version or revision returns, allocates `soc_device_attribute`, formats strings such as `jep106:<bank><id>:<soc>`, optionally obtains the machine name via SMCCC 1.2 register invocation, and calls `soc_device_register()`. Exit unregisters the device and frees attributes.

## State And Persistence
The registered SoC device and attribute allocation persist while the module is loaded. String storage uses static buffers for formatted IDs and a read-only-after-init buffer for optional machine name. No data is persisted beyond sysfs exposure.

## Dependencies And Integration Points
It depends on SMCCC discovery state from `smccc.c`, SOC bus infrastructure, bitfield helpers, and arm64 SMCCC 1.2 register invocation for the optional name. The resulting sysfs SoC attributes can be used by userspace and kernel diagnostics.

## Risks
Malformed firmware name strings are ignored if not NUL-terminated within 136 bytes. Negative SOC_ID version/revision returns abort registration. Static formatted string buffers are adequate for one device but reinforce singleton behavior.

## Test Signals
On supported firmware, logs should show ID and revision, and `/sys/devices/soc0` style attributes should include `soc_id`, `family`, `revision`, and optional `machine`. Unsupported firmware should log that ARCH_SOC_ID is not implemented and skip cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/smccc/soc_id.c -->
