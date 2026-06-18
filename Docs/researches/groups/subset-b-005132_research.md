# subset-b-005132 research

Grouped research for the platform/x86 AMD, Apple, Fujitsu-Siemens, and ASUS files assigned to `subset-b-005132`. Each section is source-tree aligned and can be split into its mapped per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/sps.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/sps.c

## Purpose
`sps.c` implements Static Power Slider support for the AMD Platform Management Framework (PMF). It bridges Linux platform profiles to AMD firmware/APMF power-limit programming so user-visible profile choices such as performance, balanced, and low-power become concrete SPL, SPPT, FPPT, STT, and PMF PPT limits. It supports both the original PMF interface, which stores full per-source/per-mode power-limit tables, and PMF IF v2, which maps source/profile pairs to APTS granular state indexes.

## Important APIs, Types, and Functions
The file uses `struct amd_pmf_dev` from `pmf.h`, static table caches `config_store`, `config_store_v2`, and `apts_config_store`, and APMF/PMF helper types such as `struct amd_pmf_static_slider_granular`, `struct amd_pmf_static_slider_granular_v2`, and `struct amd_pmf_apts_granular`. `amd_pmf_init_sps()` is the entry point that initializes the balanced profile, reads firmware defaults, applies initial limits, and registers a `platform_profile` device. `amd_pmf_set_sps_power_limits()` converts the current profile to PMF power mode and dispatches either legacy or v2 limit programming. `amd_pmf_update_slider()` is the legacy get/set command dispatcher for SPL, FPPT, SPPT, SPPT_APU_ONLY, STT_MIN, and STT skin temperature limits. `amd_pmf_update_sps_power_limits_v2()` maps legacy profile modes to v2 `POWER_MODE_BEST_PERFORMANCE`, `BALANCED`, or `BEST_POWER_EFFICIENCY` indexes, then calls `amd_pmf_update_slider_v2()`.

The platform profile callbacks are `amd_pmf_profile_probe()`, `amd_pmf_hidden_choices()`, `amd_pmf_profile_get()`, and `amd_pmf_profile_set()`. They advertise low-power, balanced, and performance as visible choices, hide quiet and balanced-performance, and update firmware on every set. Debug-only dump helpers produce table diagnostics when `CONFIG_AMD_PMF_DEBUG` is enabled.

## Control Flow
Initialization starts in `amd_pmf_init_sps()`. It sets `dev->current_profile` to `PLATFORM_PROFILE_BALANCED`, checks `APMF_FUNC_STATIC_SLIDER_GRANULAR`, loads either legacy defaults via `apmf_get_static_slider_granular()` or v2 defaults via `apmf_get_static_slider_granular_v2()` plus `apts_get_static_slider_granular_v2()` for every APTS state, then immediately applies balanced limits through `amd_pmf_set_sps_power_limits()`. Finally it registers the platform profile provider with `devm_platform_profile_register()`.

Runtime updates are initiated by `amd_pmf_profile_set()`. It stores the requested profile in `pmf->current_profile`, optionally emits an OS power-slider update to the EC through `apmf_os_power_slider_update()`, then optionally updates static-slider limits. `amd_pmf_get_pprof_modes()` normalizes Linux profile choices into PMF modes; unsupported profiles return `-EOPNOTSUPP`. `amd_pmf_power_slider_update_event()` combines AC/DC source and PMF mode into the APMF flag bits expected by firmware.

## State and Persistence
State is volatile kernel state. Firmware defaults are cached globally in static table stores, while the live selected profile is per-device in `pmf->current_profile`. The driver writes hardware/firmware limits immediately through `amd_pmf_send_cmd()` and does not persist user profile choice across reboot. On module/device reprobe, the balanced profile and firmware default tables are reloaded.

## Dependencies and Integration Points
The file depends on PMF core helpers in `pmf.h`, APMF function availability checks, power-source detection through `amd_pmf_get_power_source()`, fixed-point conversion through `fixp_q88_fromint()`, and Linux `platform_profile` registration. Firmware commands are sent by `amd_pmf_send_cmd()` using command IDs defined outside this file. It integrates with the OS platform-profile subsystem and with firmware/EC power-slider notification.

## Risks and Test Signals
Risk centers on firmware table shape and profile mapping. v2 paths trust firmware-provided APTS indexes; invalid or out-of-range indexes would lead to programming from `apts_config_store.val[idx]` without local bounds checking. Legacy `amd_pmf_update_slider()` ignores command return values, so partial firmware programming failures may not propagate. The global static caches also assume one active PMF device or compatible tables across devices. Useful tests include platform profile registration, profile switching under AC and DC, validation of the APMF update flag for each profile/source pair, suspend/resume profile retention at the PMF core level, and debugfs or trace validation that all expected `SET_*` commands are issued with firmware-derived values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/sps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/tee-if.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/tee-if.c

## Purpose
`tee-if.c` implements the AMD PMF Smart PC policy engine interface to AMDTEE. It loads a platform policy binary from firmware memory, opens a trusted application session, initializes the policy builder TA, periodically invokes policy enactment, and applies returned actions to PMF firmware limits, BIOS outputs, or synthetic input events.

## Important APIs, Types, and Functions
The exported PMF entry points are `amd_pmf_init_smart_pc()`, `amd_pmf_deinit_smart_pc()`, `amd_pmf_tee_init()`, `amd_pmf_tee_deinit()`, `amd_pmf_start_policy_engine()`, and `amd_pmf_invoke_cmd_enact()`. Shared-memory command setup is centralized in `amd_pmf_prepare_args()`. `amd_pmf_invoke_cmd_init()` sends the policy binary to the TA, while `amd_pmf_invoke_cmd()` is the delayed-work callback that repeatedly calls `amd_pmf_invoke_cmd_enact()`. `amd_pmf_apply_policies()` interprets TA actions and programs PMF command IDs such as `SET_SPL`, `SET_SPPT`, `SET_FPPT`, `SET_STT_LIMIT_APU`, `SET_P3T`, and PMF PPT variants.

The file uses TEE core types `struct tee_context`, `struct tee_ioctl_invoke_arg`, `struct tee_param`, and TEE shared memory, plus PMF TA protocol structures such as `struct ta_pmf_shared_memory`, `struct ta_pmf_init_table`, `struct ta_pmf_enact_table`, and `struct ta_pmf_enact_result`. Debug builds expose module parameters `pb_actions_ms` and `pb_side_load` and a debugfs policy-binary sideload path.

## Control Flow
`amd_pmf_init_smart_pc()` first checks BIOS Smart PC advertisement with `apmf_check_smart_pc()`. It initializes delayed work, asks firmware to expose the DRAM address with `amd_pmf_set_dram_addr()`, maps the policy resource with `devm_ioremap_resource()`, copies the policy into a devm buffer, rejects all-`0xff` policy buffers, allocates `prev_data`, then tries each UUID in `amd_pmf_ta_uuid`. For each UUID it opens AMDTEE context/session/shared memory through `amd_pmf_tee_init()` and starts the policy engine. On success, it enables callback buffering state and registers an input device for TA system-state events.

`amd_pmf_start_policy_engine()` validates the policy cookie and length, adjusts `dev->policy_sz` to the real policy length plus header padding, invokes TA initialization, marks `smart_pc_enabled`, and schedules periodic enactment after a startup delay. Each periodic enactment clears shared memory, populates TA inputs, invokes the TA command, and, when the TA returns success with actions, applies each action. Duplicate power-limit writes are suppressed by comparing against `dev->prev_data`.

## State and Persistence
Policy binary contents are copied into `dev->policy_buf`, shared with the TA through `dev->fw_shm_pool`, and tracked by `dev->policy_sz`. Runtime state includes `dev->tee_ctx`, `dev->session_id`, `dev->shbuf`, `dev->prev_data`, `dev->smart_pc_enabled`, `dev->cb_flag`, and the delayed work item. None of this persists across boot. The TA's output affects live firmware power limits and BIOS output values immediately. In debug mode, policy sideload replaces the devm policy buffer and restarts the policy engine.

## Dependencies and Integration Points
This file integrates with AMDTEE through the Linux TEE client API, PMF core firmware command helpers, PMF sensor/input population helpers, APMF Smart PC resource setup, input subsystem key events (`KEY_SLEEP`, `KEY_SUSPEND`, `KEY_SCREENLOCK`), and debugfs for policy sideloading. BIOS output actions are delegated to `amd_pmf_smartpc_apply_bios_output()`.

## Risks and Test Signals
Important risks include policy-size validation mistakes, TA ABI drift, repeated delayed-work scheduling after error paths, and action-count trust. The code validates cookie presence and minimum sizes, but action array bounds depend on TA-provided structures. `amd_pmf_update_bios_output()` converts an action index to `bios_idx` without checking `amd_pmf_get_bios_output_idx()` for `-EINVAL`; current callers only pass BIOS output cases, but this assumption should remain protected. Deinit unregisters the input device with `input_unregister_device()` even though it was devm-allocated, which is a lifetime pattern worth regression testing. Test signals include successful Smart PC enablement, no policy path returning `-EINVAL`, periodic enactment cadence, duplicate-action suppression, suspend/shutdown cleanup via `cancel_delayed_work_sync()`, debugfs sideload failure handling, and validation that input events are emitted for TA system-state actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/tee-if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/wbrf.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/wbrf.c

## Purpose
`wbrf.c` provides AMD ACPI WBRF, the Wi-Fi Band RFI mitigation interface. It lets producer devices publish active frequency ranges to BIOS, lets consumer devices retrieve the active range list, and provides a blocking notifier chain so consumers such as graphics drivers can react when producer frequency bands change.

## Important APIs, Types, and Functions
The exported API consists of `acpi_amd_wbrf_add_remove()`, `acpi_amd_wbrf_supported_producer()`, `acpi_amd_wbrf_supported_consumer()`, `amd_wbrf_retrieve_freq_band()`, `amd_wbrf_register_notifier()`, and `amd_wbrf_unregister_notifier()`. Internal helper `wbrf_record()` formats input ranges into the ACPI `_DSM` package for add/remove actions. `struct amd_wbrf_ranges_out` mirrors the packed firmware output buffer for retrieval, while public input/output uses `struct wbrf_ranges_in_out` and `struct freq_band_range` from `linux/acpi_amd_wbrf.h`.

## Control Flow
Producers first check support using `acpi_amd_wbrf_supported_producer()`, which requires an ACPI companion and checks `_DSM` function bit `WBRF_RECORD`. To publish a range update, `acpi_amd_wbrf_add_remove()` obtains the ACPI companion, calls `wbrf_record()`, and broadcasts `WBRF_CHANGED` on success. `wbrf_record()` validates that `in->num_of_ranges` matches the number of non-zero start/end range entries, builds an ACPI package containing range count, action, and start/end integer pairs, evaluates the WBRF record `_DSM`, and requires an integer zero result.

Consumers check support with `acpi_amd_wbrf_supported_consumer()`, register a notifier, and retrieve active ranges with `amd_wbrf_retrieve_freq_band()`. Retrieval evaluates the `_DSM` retrieve function with an empty string parameter, validates returned buffer length, copies it into the packed local representation, then transfers count and band list into caller storage.

## State and Persistence
This file keeps only the global blocking notifier chain `wbrf_chain_head`. Frequency-band state is cached by firmware/BIOS through `_DSM`, not by this driver. Consumers that register late are expected to call retrieve to obtain the current BIOS-cached state.

## Dependencies and Integration Points
The implementation depends on ACPI companion devices, `acpi_check_dsm()`, `acpi_evaluate_dsm()`, the AMD WBRF GUID, and Linux blocking notifier chains. The expected integration is between Wi-Fi or other radio producers and RFI-sensitive consumers, with comments identifying amdgpu as a current consumer.

## Risks and Test Signals
Risk points include malformed ACPI buffers, mismatched range counts, and firmware returning non-integer or non-zero status. Retrieval checks maximum and minimum buffer length but copies the full fixed `band_list` to the caller regardless of returned count; callers must honor `num_of_ranges`. Tests should cover support probing without ACPI companion, add/remove with empty, mismatched, and valid range lists, notifier delivery only after successful firmware recording, retrieve zero-entry and multi-entry buffers, and invalid buffer lengths from mocked ACPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/wbrf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/x3d_vcache.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/x3d_vcache.c

## Purpose
`x3d_vcache.c` is a small platform driver for AMD 3D V-Cache performance optimization. It exposes a sysfs control that switches firmware between frequency-preferred and cache-preferred modes through an ACPI `_DSM` method.

## Important APIs, Types, and Functions
The driver binds ACPI ID `AMDI0101` and registers a platform driver named `amd_x3d_vcache`. Module parameter `x3d_mode` selects the initial mode, defaulting to `frequency`. `struct amd_x3d_dev` stores the device, ACPI handle, mutex, and current mode. `amd_x3d_mode_switch()` is the core ACPI `_DSM` writer. `amd_x3d_mode_show()` and `amd_x3d_mode_store()` implement the `amd_x3d_mode` sysfs attribute. `amd_x3d_resume_handler()` reapplies the stored mode after resume.

## Control Flow
`amd_x3d_probe()` obtains the ACPI handle, verifies `_DSM` function `DSM_SET_X3D_MODE`, allocates state, initializes the mutex, stores driver data, parses the initial module parameter with `match_string()`, and calls `amd_x3d_mode_switch()`. Runtime sysfs writes use `sysfs_match_string()` to convert `frequency` or `cache` to the mode index and then call the same switch function. Resume reads the current in-kernel mode under the mutex and writes it back to firmware.

## State and Persistence
The only persistent-in-memory state is `curr_mode`, protected by `lock`. The selected mode is not persisted by this driver across reboot. Firmware receives the selected mode through ACPI `_DSM`, and resume reapplies the last in-kernel selection because firmware may reset during sleep.

## Dependencies and Integration Points
The file depends on ACPI `_DSM`, platform-driver matching, sysfs device groups, PM sleep callbacks, and standard kernel mutex helpers. It does not integrate with cpufreq or scheduler logic directly; it delegates actual optimization behavior entirely to firmware.

## Risks and Test Signals
`amd_x3d_mode_switch()` treats any non-NULL `_DSM` response as success and does not validate returned object type or status payload. It updates `curr_mode` after `_DSM` evaluation but before checking any firmware-level semantic result. Tests should cover invalid module parameters, sysfs accepted values and rejected values, ACPI absence, `_DSM` absence, resume reapplication, and concurrent sysfs access. A firmware mock that returns an error object would be useful to decide whether stricter result validation is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/x3d_vcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amilo-rfkill.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amilo-rfkill.c

## Purpose
`amilo-rfkill.c` provides WLAN rfkill support for specific Fujitsu-Siemens Amilo laptop models whose radios are controlled through legacy keyboard-controller commands or fixed I/O ports.

## Important APIs, Types, and Functions
The driver defines two rfkill operation implementations: `amilo_a1655_rfkill_set_block()` sends command `A1655_WIFI_COMMAND` through i8042, and `amilo_m7440_rfkill_set_block()` writes paired values to ports `0x118f` and `0x118e` and verifies them. `amilo_rfkill_id_table` maps DMI system matches to the correct `struct rfkill_ops`. `amilo_rfkill_probe()` allocates and registers the rfkill device, and init/exit functions register a simple platform driver/device only on matching DMI systems.

## Control Flow
Module init first checks the DMI table. If unsupported, it exits with `-ENODEV`. On supported systems it registers `amilo_rfkill_driver`, then creates a platform device named after `KBUILD_MODNAME`. Probe resolves the first matching DMI entry, allocates an `RFKILL_TYPE_WLAN` rfkill device with the model-specific operations pointer stored in `driver_data`, and registers it. User rfkill changes call the selected `.set_block` callback. Remove unregisters and destroys the rfkill object; module exit unregisters both platform device and driver.

## State and Persistence
The driver has two global pointers, `amilo_rfkill_pdev` and `amilo_rfkill_dev`, for the singleton platform device and rfkill device. Radio state is not cached locally and is driven directly into hardware on each rfkill set. There is no persistence beyond the platform firmware/hardware latch state.

## Dependencies and Integration Points
Dependencies are DMI matching, platform devices, the rfkill subsystem, i8042 locking/commands for A1655/L1310-class systems, and raw port I/O for M7440-class systems. The driver is intentionally narrow and does not rely on ACPI.

## Risks and Test Signals
The code uses legacy raw hardware access. Incorrect DMI matches could write to unrelated I/O ports or send unintended i8042 commands, so DMI specificity is critical. The M7440 path validates writes by reading back the ports, while the A1655 path relies on `i8042_command()` return status. Tests are mostly hardware or emulation based: DMI non-match should avoid registration; DMI match should create one WLAN rfkill; block/unblock should call the correct hardware path; M7440 readback mismatch should return `-EIO`; unregister should destroy the singleton without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amilo-rfkill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/apple-gmux.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/apple-gmux.c

## Purpose
`apple-gmux.c` drives Apple's gmux controller used on dual-GPU Macs. It provides gmux register access across classic PIO, indexed I/O, and T2-era MMIO variants; registers a platform backlight device when gmux owns panel brightness; integrates with `vga_switcheroo` for display/DDC muxing and discrete-GPU power control; handles ACPI notifications/GPEs; and exposes a debugfs port access interface.

## Important APIs, Types, and Functions
`struct apple_gmux_data` stores register resources, access config, backlight device, switcheroo state, ACPI/GPE data, completion state, and debugfs selection. `struct apple_gmux_config` selects read/write methods, switcheroo handler, resource type, version format, and gmux variant name. Accessors are grouped as `gmux_pio_*`, `gmux_index_*`, and `gmux_mmio_*`, with generic wrappers `gmux_read8()`, `gmux_write8()`, `gmux_read32()`, and `gmux_write32()`.

Backlight integration uses `gmux_get_brightness()`, `gmux_update_status()`, and `gmux_bl_ops`. Switcheroo integration uses `gmux_switchto()`, `gmux_switch_ddc()`, `gmux_set_power_state()`, and `gmux_get_client_id()`. Interrupt handling uses `gmux_notify_handler()`, `gmux_clear_interrupts()`, and GPE enable/disable logic. `gmux_probe()` and `gmux_remove()` own device lifetime.

## Control Flow
Probe is PNP-driven for `GMUX_ACPI_HID`. It rejects a second singleton instance, calls `apple_gmux_detect()` to identify the gmux type, allocates state, selects a config, requests and maps I/O or MMIO resources, reads the version, and optionally registers the `gmux_backlight` device depending on ACPI video backlight ownership. It obtains the ACPI handle, optionally reads `GMGP` and installs a notify handler plus GPE, determines whether the external port is fully switchable by scanning PCI Thunderbolt devices, sets the global `apple_gmux_data`, enables interrupts, reads initial switch state, registers the `vga_switcheroo` handler, and initializes debugfs.

Switch requests update cached display/DDC/external state then write gmux switch registers. Discrete power changes write the gmux power sequence and wait up to 200 ms for a power interrupt completion if a GPE is available. Suspend disables interrupts; resume reenables interrupts, rewrites switch state, and reapplies discrete-off state if needed.

## State and Persistence
The driver keeps a singleton global `apple_gmux_data` because the switcheroo callbacks do not carry per-device context. Runtime state includes selected mux owners, external switchability, discrete power state, selected debugfs port, and completion state. Hardware register values persist according to gmux/firmware behavior, but the driver rewrites cached switch and power state on resume. Backlight brightness is stored in gmux hardware and synchronized through the backlight core.

## Dependencies and Integration Points
The file integrates with PNP, ACPI video/backlight policy, `apple-gmux.h` detection and register constants, port/MMIO I/O APIs, PCI bus scanning, `vga_switcheroo`, debugfs, and ACPI GPE/notify handling. It directly affects GPU power rails and display routing.

## Risks and Test Signals
Risks are high because the driver controls display routing and discrete GPU power. Indexed/MMIO access relies on polling loops that return boolean readiness but callers do not surface timeout failures. The singleton global constrains multi-device assumptions. Debugfs permits raw gmux port writes and is intentionally powerful. T2 MMIO interrupt clearing requires ACPI `GMSP(0)` to avoid floods. Test signals include correct gmux type detection, resource request failures, backlight registration only when selected by ACPI policy, switcheroo registration and GPU classification, DDC switching on pre-retina configs, Thunderbolt external-port forcing, power-change completion timeout warnings, suspend/resume state restoration, and debugfs 1-byte/4-byte access validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/apple-gmux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/asus-armoury.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/asus-armoury.c

## Purpose
`asus-armoury.c` exposes ASUS Armoury-style BIOS/WMI settings through the firmware attributes class. It covers gaming-laptop controls that do not fit existing subsystems, including mini-LED modes, GPU MUX mode, dGPU/eGPU controls, APU memory reservation, charging and boot options, panel options, and ROG power tunables.

## Important APIs, Types, and Functions
`struct asus_armoury_priv` stores the firmware-attributes device/kset, eGPU mutex, AC/DC `struct rog_tunables`, and selected WMI device IDs for mini-LED and GPU MUX variants. `struct rog_tunables` stores current AC/DC values and a pointer to DMI-provided `struct power_limits`. The main WMI helpers are `armoury_has_devstate()`, `armoury_get_devstate()`, `armoury_set_devstate()`, `armoury_attr_uint_store()`, and `armoury_attr_uint_show()`. `asus_fw_attr_add()` creates the firmware-attributes device and conditionally creates per-feature sysfs groups. `init_rog_tunables()` matches the DMI power-limit table from `asus-armoury.h` and initializes AC/DC default values.

Feature-specific handlers include mini-LED mode mapping, `gpu_mux_mode_current_value_store()`, `dgpu_disable_current_value_store()`, `egpu_enable_current_value_store()`, APU memory show/store, and generated macro-based attributes for charge mode, boot sound, MCU powersave, panel overdrive, panel HD mode, automatic brightness, and ROG power tunables.

## Control Flow
Module init obtains the ASUS WMI ACPI device UID and rejects the legacy `ASUSWMI` DCTS path because this driver requires DSTS-style state access. It initializes DMI-based ROG tunables, then creates the firmware attributes device. Attribute creation always starts with top-level `pending_reboot`, detects which mini-LED and GPU MUX WMI IDs are present, creates their groups, then iterates `armoury_attr_groups`. A group is created only if its WMI device is present; power tunables are further gated by AC power-limit availability and non-zero max values.

Writes flow through `armoury_set_devstate()` either directly or via `armoury_attr_uint_store()`, which parses decimal input, enforces bounds, sends WMI, updates cached tunable state if requested, notifies sysfs, and signals pending reboot for BIOS settings such as GPU MUX and panel HD mode. eGPU/dGPU/MUX operations enforce sequencing under `egpu_mutex` and reject combinations known to break GPU state. eGPU enablement may trigger PCI bus rescan.

## State and Persistence
`fw_attrs.pending_reboot` is runtime kernel state exposed through sysfs and uevents; it is set when the driver knows BIOS changes need reboot but is not persistent across module reload. ROG tunable values are cached separately for AC and DC and selected dynamically by `power_supply_is_system_supplied()`. Actual settings are persisted, if at all, by ASUS firmware after WMI calls. The driver allocates AC/DC tunable structures at init and frees them at exit.

## Dependencies and Integration Points
The file depends on `asus-wmi` exported namespace, WMI management GUIDs and device IDs, the firmware attributes class, DMI power-limit data from `asus-armoury.h`, power-supply state, PCI rescanning, sysfs/kobject uevents, and ASUS platform data definitions. It shares the ASUS notebook WMI event GUID as its module alias but exposes configuration rather than hotkeys.

## Risks and Test Signals
Risk areas include firmware side effects, GPU state sequencing, DMI power-limit correctness, and generated sysfs contract drift. `armoury_set_devstate()` includes a safety block for known-dangerous APU memory values `0x100` and `0x101`. eGPU activation carefully checks connection, MUX state, return codes, and rescans PCI, but still depends on model-specific firmware behavior. The mini-LED show path reads WMI into `mode` but then uses `FIELD_GET(ASUS_MINI_LED_MODE_MASK, 0)`, which always extracts from zero and looks like a logic bug; tests should catch current-value reporting for nonzero modes. Test signals include group presence by WMI feature bit, each attribute's possible/default/min/max files, AC/DC tunable switching, pending reboot uevents, eGPU enable/disable result handling, dGPU disable rejection when MUX is in dGPU mode, and cleanup removing all conditionally created groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/asus-armoury.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/asus-armoury.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/asus-armoury.h

## Purpose
`asus-armoury.h` is the companion header for `asus-armoury.c`. It defines the firmware-attributes sysfs macro framework, declares generic integer WMI show/store helpers, defines ROG power-limit data structures, and contains the large DMI table that maps ASUS board names to AC/DC tunable limits.

## Important APIs, Types, and Macros
The header declares `armoury_attr_uint_store()` and `armoury_attr_uint_show()` for macro-generated sysfs handlers. Low-level macros such as `__ASUS_ATTR_RO`, `__ASUS_ATTR_RO_AS`, `__ASUS_ATTR_RW`, `__WMI_STORE_INT`, and `ASUS_WMI_SHOW_INT` build `struct kobj_attribute` definitions. Group macros including `ASUS_ATTR_GROUP_BOOL_RO`, `ASUS_ATTR_GROUP_BOOL_RW`, `ASUS_ATTR_GROUP_ENUM_INT_RO`, `ASUS_ATTR_GROUP_BOOL`, `ASUS_ATTR_GROUP_ENUM`, `ASUS_ATTR_GROUP_INT_VALUE_ONLY_RO`, and `ASUS_ATTR_GROUP_ROG_TUNABLE` generate firmware-attributes-compatible directories with `current_value`, `possible_values`, `display_name`, `type`, and, for tunables, `default_value`, `min_value`, `max_value`, and `scalar_increment`.

`struct power_limits` stores min/default/max values for CPU package limits, APU/platform limits, Nvidia dynamic boost, Nvidia thermal target, and Nvidia TGP. `struct power_data` pairs AC and DC `power_limits` and records whether a model requires fan-curve handling. `power_limits[]` is a static DMI match table keyed primarily by `DMI_BOARD_NAME`.

## Control Flow
This header does not execute code independently; its macros expand into static functions, attributes, and attribute groups in `asus-armoury.c`. ROG tunable macros call `get_current_tunables()` at show/store time so AC/DC limits follow power-source state. The DMI table is consumed by `init_rog_tunables()`, which calls `dmi_first_match(power_limits)`, reads the selected `struct power_data`, allocates AC/DC tunable stores, and seeds defaults from `_def` values or `_max` when no default is specified.

## State and Persistence
The header defines static const model data rather than mutable state. The DMI table is compiled into the module and persists for the lifetime of the loaded code. The generated attributes store mutable current values in `struct rog_tunables` allocated by the C file; firmware persistence depends on ASUS WMI behavior.

## Dependencies and Integration Points
The macros assume `enum_type_show()`, `int_type_show()`, `get_current_tunables()`, and the generic armoury integer helpers exist in the including C file. They depend on sysfs/kobject types, DMI matching, and ASUS WMI device IDs supplied by included platform headers. The DMI table is the model policy boundary for safe power tuning; it prevents exposing tunables when no model-specific limits exist.

## Risks and Test Signals
Macro-generated sysfs code is compact but easy to break with naming mismatches because each macro synthesizes function and symbol names. ROG tunable stores reject equal min/max values as unsupported and rely on `u8` limits, so model values must fit that range. The DMI table is large and model-specific; incorrect board names, missing DC data, or missing max values directly affect attribute visibility. Tests should compile-check every generated attribute group, validate that group names match the firmware-attributes ABI, verify model-specific DMI matches for representative FA/GA/GU/GV/GX/RC boards, confirm default fallback to max, and check that absent limits suppress the corresponding power tunable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/asus-armoury.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/asus-laptop.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/asus-laptop.c

## Purpose
`asus-laptop.c` is the legacy ACPI ATKD ASUS laptop support driver. It exposes hotkey events, vendor backlight, LED controls, wireless/GPS rfkill, ambient-light controls, display switching, and Pegatron Lucid tablet extras for systems using ACPI IDs `ATK0100` and `ATK0101`.

## Important APIs, Types, and Functions
`struct asus_laptop` is the central per-device state: ACPI device/handle, platform device, backlight, input devices, LED descriptors, rfkill descriptors, cached wireless/light/LEDD state, model name, DSDT header, and event counters. `struct asus_led` wraps LED class devices and work items. `struct asus_rfkill` wraps rfkill devices and control IDs. ACPI helpers `write_acpi_int_ret()`, `write_acpi_int()`, and `acpi_check_handle()` are used throughout.

Major subsystems are initialized by `asus_platform_init()`, `asus_backlight_init()`, `asus_input_init()`, `asus_led_init()`, `asus_rfkill_init()`, `pega_accel_init()`, and `pega_rfkill_init()`. Sysfs handlers expose `infos`, `wlan`, `bluetooth`, `wimax`, `wwan`, `display`, `ledd`, `ls_value`, `ls_level`, `ls_switch`, and `gps`. ACPI notifications are handled by `asus_acpi_notify()`.

## Control Flow
Module init registers a base platform driver and the ACPI platform driver, then requires that at least one ACPI device probe succeeded. Probe allocates `struct asus_laptop`, sets ACPI name/class, applies DMI adjustments, initializes ACPI state by calling `INIT`, `BSTS`, and `CWAP`, detects RSTS support, detects Pegatron Lucid features, creates the platform device/sysfs group, conditionally registers vendor backlight when ACPI video policy selects vendor backlight, then registers input, LEDs, rfkill, Pegatron accelerometer/rfkill, and ACPI notify handler.

Runtime ACPI notifications generate netlink events with per-event counters, normalize brightness ranges to a single up/down event, update backlight state for brightness events, emit accelerometer uevents for Pegatron orientation changes, or report sparse-keymap input events. Sysfs writes generally parse integers and call corresponding ACPI methods. LED writes are deferred to a single-thread workqueue to avoid ACPI calls in unsafe contexts. Remove unwinds notify, backlight, rfkill, LED, input, accelerometer, platform device, and allocations.

## State and Persistence
The driver caches mutable state in `struct asus_laptop`: `ledd_status`, `light_level`, `light_switch`, wireless status fallback bits, Pegatron accelerometer readings, event counters, and module-parameter-derived initial settings. Actual hardware state is controlled through ACPI methods such as `WLED`, `BLED`, `GSMC`, `WMXC`, `SPLV`, `SDSP`, `ALSC`, `ALSL`, `SDON`, and `SDOF`. Module parameters set boot-time behavior but are not runtime persistent.

## Dependencies and Integration Points
The file integrates with ACPI platform-device matching, ACPI video backlight policy, input sparse keymaps, LED class devices, backlight core, rfkill, platform sysfs, DMI, and ACPI netlink events. It is separate from newer ASUS WMI drivers and covers older ATKD firmware interfaces.

## Risks and Test Signals
Risks include fragile ACPI firmware behavior, many optional methods, and legacy raw assumptions. `asus_sysfs_is_visible()` guards sysfs files by probing ACPI methods, which is important because many models expose only a subset. LED unregister is called for all LED structs even if not registered, matching common classdev tolerance but still worth testing. `asus_laptop_get_info()` allocates the ACPI output buffer and model string; allocation and cleanup paths are important. Test signals include successful probe on ATK0100/ATK0101 only, no device causing module init failure, sysfs visibility per ACPI method, brightness event handling with and without vendor backlight, rfkill setup for WLAN/Bluetooth/WWAN/WiMAX/GPS, Pegatron accelerometer polling and fake first report, ACPI notify input mapping, and orderly cleanup on each probe failure label.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/asus-laptop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/asus-nb-wmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/asus-nb-wmi.c

## Purpose
`asus-nb-wmi.c` is the ASUS notebook WMI hotkey driver. It supplies DMI-specific quirks, a large WMI event keymap, optional i8042 filtering, and key filtering for the shared ASUS WMI core driver.

## Important APIs, Types, and Functions
The file defines module parameters `wapf` and `tablet_mode_sw`, global quirk pointer `quirks`, and `atkbd_reports_vol_keys`. `asus_i8042_filter()` observes PS/2 keyboard scancodes to detect volume keys already reported by atkbd and optionally filters E1 extended codes on affected models. `asus_nb_wmi_quirks()` selects the default or DMI-specific `struct quirk_entry`, applies module parameter overrides, and attaches quirks to the shared `struct asus_wmi_driver`.

The DMI table maps many ASUS models to quirk structures controlling WAPF, WMI backlight behavior, display-toggle suppression, USB charging register, forced ALS writes, tablet switch mode, ignored fan, WLAN event remapping, and Armoury-key behavior. `asus_nb_wmi_keymap[]` maps WMI event codes to Linux input keys or ignores known duplicate/status events. `asus_nb_wmi_key_filter()` suppresses brightness events handled by ACPI video, suppresses duplicate volume keys when atkbd reports them, and rewrites WLAN console events according to quirks.

## Control Flow
Module init calls `asus_wmi_register_driver()` with `asus_nb_wmi_driver`. The shared ASUS WMI core calls `detect_quirks`, sets up the keymap and input device, and dispatches events through the key filter. DMI matching uses `dmi_check_system()` and `dmi_matched()` to update the global `quirks` pointer. The i8042 filter is available to the shared driver to watch raw keyboard traffic; when it sees E0 volume scancodes, later WMI volume events are ignored.

## State and Persistence
State is module-global and runtime-only: selected `quirks`, effective `wapf`, optional tablet switch override, and `atkbd_reports_vol_keys`. No user settings are persisted by this file. DMI quirks are static compiled data.

## Dependencies and Integration Points
The implementation depends on the shared ASUS WMI core (`asus-wmi.h`), sparse keymap semantics, DMI, i8042 filtering, ACPI video brightness-key ownership, and the ASUS notebook WMI event GUID. It is primarily an adapter that configures and constrains shared WMI behavior for notebook models.

## Risks and Test Signals
Risk is concentrated in quirk correctness and duplicate input suppression. Incorrect DMI matches can change WAPF radio behavior, tablet mode detection, or event remapping. The i8042 filter uses static state for E0/E1 prefix tracking and must avoid consuming unrelated keyboard data; it ignores AUX data explicitly. Tests should cover representative DMI quirk selection, module parameter overrides, brightness-key suppression when ACPI video handles keys, volume duplicate suppression after observed atkbd scancodes, WLAN event remapping for Zenbook Duo and ROG Z13 quirks, tablet mode override behavior, and clean unregister through `asus_wmi_unregister_driver()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/asus-nb-wmi.c -->
