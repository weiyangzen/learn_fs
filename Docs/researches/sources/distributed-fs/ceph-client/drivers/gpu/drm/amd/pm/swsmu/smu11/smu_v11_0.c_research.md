# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/smu_v11_0.c

## Purpose

`smu_v11_0.c` is the common SMU11 support layer for AMDGPU SWSMU devices. It handles MP1 firmware loading/status, PowerPlay table discovery, common SMU table allocation/freeing, VBIOS boot clock extraction, SMU message register setup, DPM clock and power-limit helpers, GFXOFF, fan control, thermal/SMU interrupts, BACO/BAMACO, mode resets, PCIe link reporting, and deep-sleep/ULV feature toggles. ASIC-specific SMU11 policy files, such as `vangogh_ppt.c`, bind these helpers through their `pptable_funcs`.

## Important APIs, Types, and Functions

The file exports common routines including `smu_v11_0_init_microcode`, `smu_v11_0_load_microcode`, `smu_v11_0_check_fw_status`, `smu_v11_0_setup_pptable`, `smu_v11_0_init_smc_tables`, `smu_v11_0_fini_smc_tables`, `smu_v11_0_init_power`, `smu_v11_0_get_vbios_bootup_values`, `smu_v11_0_notify_memory_pool_location`, `smu_v11_0_set_driver_table_location`, `smu_v11_0_set_tool_table_location`, `smu_v11_0_set_allowed_mask`, `smu_v11_0_system_features_control`, `smu_v11_0_init_max_sustainable_clocks`, `smu_v11_0_get_current_power_limit`, `smu_v11_0_set_power_limit`, fan helpers, `smu_v11_0_register_irq_handler`, BACO helpers, reset helpers, DPM frequency helpers, and `smu_v11_0_init_msg_ctl`.

Important local helpers include `smu_v11_0_set_pptable_v2_0`, `smu_v11_0_set_pptable_v2_1`, `smu_v11_0_atom_get_smu_clockinfo`, `smu_v11_0_get_max_sustainable_clock`, `smu_v11_0_set_irq_state`, `smu_v11_0_irq_process`, and `convert_to_vddc`.

Key state structures are `struct smu_context`, `struct amdgpu_device`, `struct smu_table_context`, `struct smu_power_context`, `struct smu_dpm_context`, `struct smu_baco_context`, `struct smu_msg_ctl`, `struct smu_table`, and `struct smu_feature`.

## Control Flow

Firmware bring-up requests an SMC firmware blob based on the MP1 IP version unless an SR-IOV VF uses PSP-managed firmware for selected SMU11 variants. PSP load mode registers the firmware in `adev->firmware.ucode`; direct loading writes the firmware words into MP1 SRAM, toggles MP1 reset, and polls `MP1_FIRMWARE_FLAGS.INTERRUPTS_ENABLED` until firmware is alive.

PowerPlay table setup prefers a driver-provided soft PPTABLE from the SMC firmware header when a v2 firmware header and nonzero `pp_table_id` are present. Otherwise it falls back to the VBIOS `powerplayinfo` ATOM table, then records `power_play_table` and size in `smu->smu_table`.

Table initialization allocates driver PPTABLE, max sustainable clocks, and optional overdrive copies based on `tables[SMU_TABLE_*].size`; finalization frees all common SMU tables, metrics/watermark/config/ECC buffers, DPM contexts, power-state objects, and resets cache timestamps and sizes.

Runtime control mostly routes high-level requests into SMU messages. Frequency helpers map common clocks to ASIC-specific IDs and send `GetMinDpmFreq`, `GetMaxDpmFreq`, `SetSoftMinByFreq`, `SetSoftMaxByFreq`, `SetHardMinByFreq`, and `SetHardMaxByFreq`. Power-limit helpers map AC/DC power source to firmware encoding and pack source/controller/limit fields into `GetPptLimit` and `SetPptLimit` parameters. GFXOFF helpers gate on MP1 IP version and `PP_GFXOFF_MASK` before sending allow/disallow messages.

Interrupt control programs THM thermal thresholds, clears/enables THM interrupt bits, configures MP1 software interrupts, and registers THM high/low, SMUIO GPIO19 CTF, and MP1 SMU-to-host interrupt IDs. Processing schedules delayed software CTF work, powers off on hardware CTF, updates AC/DC state and ACK work, and counts/logs thermal throttling.

BACO enter/exit handles ASIC-specific sequences: newer Navi-family variants use `EnterBaco` message parameters for BACO/BAMACO, Arcturus writes a different THM BACO register, RAS/XGMI conditions select different firmware parameters, and exit clears BIOS scratch registers then polls BACO exit status.

## State and Persistence Behavior

Persistent driver state includes `adev->pm.fw`, `adev->pm.fw_version`, `adev->firmware.fw_size`, boot values under `smu_table.boot_values`, allocated table pointers, DPM contexts, `smu_power.power_context`, `smu_baco.state`, `smu->current_power_limit`, user overdrive/fan profile fields, `adev->pm.ac_power`, and `smu->hard_min_uclk_req_from_dal`.

Hardware state is changed through MP1 SRAM/SMN registers, MP1 C2P message registers, SMUIO voltage telemetry registers, THM fan/thermal/BACO registers, PCIe link registers, BIOS scratch registers, and SMU firmware-managed DPM, feature, PPT, and BACO state. Many writes persist until reset, suspend/resume, BACO exit, or later SMU messages.

## Dependencies

The file depends on AMDGPU core objects, ATOMBIOS/VBIOS helpers, firmware loader APIs, SOC15 register helpers, SMU common helpers (`smu_cmn_*`), SMU message ops (`smu_msg_v1_ops`), THM/MP/SMUIO generated register headers, RAS state, IRQ infrastructure, delayed/workqueue APIs, and kernel allocation/time/reboot helpers.

## Integration Points

ASIC-specific SMU11 PPT files call these helpers through `pptable_funcs`, especially for firmware status, table lifecycle, power context, IRQs, memory/table address notification, GFXOFF, power limits, VBIOS boot values, resets, and message control initialization. Display code consumes max sustainable clocks and display clock voltage requests. Runtime PM and reset code use BACO/BAMACO and mode-reset helpers. Sysfs/hwmon paths consume fan, power, and DPM helpers.

## Risks and Edge Cases

Firmware header version handling is strict; malformed or unsupported SMC firmware tables cause PPTABLE setup failures. Direct firmware loading skips the first and last firmware dwords and assumes MP1 SRAM semantics. Many clock values convert from 10 kHz to MHz or kHz, so unit mistakes can overconstrain DPM. Power-limit parameters truncate the limit to 16 bits. Fan tach/PWM code guards zero divisors but still depends on THM register availability and ASIC fan wiring. BACO paths vary by MP1 IP version, RAS, SR-IOV, and runtime PM mode; incorrect selection can leave the ASIC in an unresponsive state. Hardware CTF interrupt handling calls `orderly_poweroff(true)`, so false positives are severe.

## Test Signals

Build coverage should include all SMU11 ASIC-specific policy users. Runtime signals include firmware request/load success, `check_fw_status` passing, VBIOS and driver PPTABLE selection logs, successful SMU table transfer, sysfs DPM level reads/writes, fan PWM/RPM reads/writes, thermal interrupt registration and throttling logs, AC/DC transition handling, GFXOFF allow/disallow behavior, BACO enter/exit, mode1/mode2 reset, suspend/resume table reinitialization, and PCIe link reporting.
