<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumo_smc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumo_smc.c

## Purpose
`sumo_smc.c` implements Sumo/Palm SMU mailbox and RCU helper routines used by Sumo DPM. It sends service requests to the firmware, initializes M3 arbiter parameter tables, notifies firmware about alternate VDDNB policy, initializes graphics power gating, configures boost timer and TDP limits, toggles boost state, and reads the running firmware version.

## Important APIs and functions
- `sumo_send_msg_to_smu` is the internal mailbox routine. It waits for `INT_DONE`, writes `GFX_INT_REQ` with `SERV_INDEX(id) | INT_REQ`, waits for request/ack/done bits, then clears `INT_REQ`.
- `sumo_initialize_m3_arb` writes default, UVD, and fullscreen-3D M3 arbiter parameter sets into RCU/MCU parameter space when dynamic M3 arbiter support is enabled.
- `sumo_smu_notify_alt_vddnb_change` writes policy bits to `RCU_ALTVDDNB_NOTIFY` and sends the alt-VDDNB service request if the feature and firmware version support it.
- `sumo_smu_pg_init` sends the graphics power-gating initialization service request.
- `sumo_enable_boost_timer` derives a timer period from XCLK and the LCLK prescaler, writes boost/throttle/GNB/TDP margins, and sends SMU service id 20.
- `sumo_set_tdp_limit` updates 12-bit per-level TDP fields across `RCU_SclkDpmTdpLimit01`, `23`, and `47` for levels 0, 1, 2, 3, 4, and boost level 7.
- `sumo_boost_state_enable` clears or sets `RCU_GPU_BOOST_DISABLE` bit 0; `sumo_get_running_fw_version` reads `RCU_FW_VERSION`.

## Control flow and integration points
`sumo_dpm_setup_asic` initializes M3 arbiter data and reads firmware version. `sumo_gfx_powergating_initialize` calls `sumo_smu_pg_init` multiple times while staging RCU power-gating control fields. `sumo_dpm_enable` calls `sumo_enable_boost_timer` when boost is enabled. Runtime state changes call alt-VDDNB notifications around NBPS1 transitions, TDP programming for levels, and boost enable/disable when entering or leaving boost-capable states.

## State and persistence behavior
The file persists state in RCU/SMU hardware registers and firmware-visible parameter tables. M3 arbiter arrays are copied from `pi->sys_info`; boost and TDP values come from BIOS-derived `sumo_power_info`. Mailbox state is transient but firmware service effects persist until later SMU commands or reset.

## Dependencies and constraints
The implementation includes `radeon.h`, `sumod.h`, `sumo_dpm.h`, and `ppsmc.h`. It depends on `sumo_get_pi`, Radeon MMIO accessors, RCU accessors, `radeon_get_xclk`, `udelay`, `rdev->usec_timeout`, family IDs, and firmware version `>= 0x00010C00` for alt VDDNB on Sumo/Sumo2. The timeout loops do not return errors, so callers cannot distinguish success from late/missing firmware acknowledgement.

## Risks and test signals
Risks include silent SMU mailbox timeout, incorrect service IDs, bad TDP level-to-register mapping, boost timer overflow/scaling mistakes, firmware-version gating errors, and register alias confusion around RCU/MCU addresses. Test signals include SMC firmware version logging, successful DPM enable with power-gating init, boost entry/exit, battery/performance NBPS1 transitions, TDP limit readback, and absence of hangs in mailbox wait paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumo_smc.c -->
