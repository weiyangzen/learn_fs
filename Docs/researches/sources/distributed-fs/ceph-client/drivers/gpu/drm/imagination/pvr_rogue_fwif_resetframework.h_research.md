# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_resetframework.h

Purpose: This header defines the small firmware reset-framework command payload used to preserve or restore compute queue/control-stream registers through reset/context recovery paths.

Important APIs/types/functions: `rogue_fwif_rf_registers` contains a union for either `cdmreg_cdm_cb_base` or `cdmreg_cdm_ctrl_stream_base`, plus `cdmreg_cdm_cb_queue` and `cdmreg_cdm_cb`. `rogue_fwif_rf_cmd` wraps those registers and requires `fw_registers` to be the last member of the containing structure. `ROGUE_FWIF_RF_CMD_SIZE` exposes the payload size.

Control flow: No executable code. The data is prepared by the host or firmware reset framework and then consumed as a block of CDM state registers.

State and persistence behavior: Instances represent persistent reset recovery state in FW-shared memory. The union reflects two mutually exclusive CDM modes: user-mode queue base or control-stream base.

Dependencies and integration points: Includes Linux `bits`/`types` and `pvr_rogue_fwif_shared.h` for shared alignment/types. It integrates with compute context reset, hard context switching, and firmware register replay.

Risks: Adding fields after `fw_registers` violates the documented size/copy assumption. Choosing the wrong union interpretation can restore an invalid CDM queue/control-stream state.

Test signals: Compute HWR/reset tests, context store/resume tests, CDM user-mode queue vs control-stream submissions, and compile/build coverage.
