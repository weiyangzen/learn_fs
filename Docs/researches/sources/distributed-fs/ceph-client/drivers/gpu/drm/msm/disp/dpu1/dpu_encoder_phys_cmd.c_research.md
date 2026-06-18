# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_encoder_phys_cmd.c

## Purpose
Implements command-mode physical encoders for DSI-style panels. It configures CTL/INTF/PP routing, tear-check, command-mode interface compression/widebus flags, external TE connection, vblank emulation through read-pointer IRQs, and kickoff/PP-done synchronization.

## Important APIs, Types, and Functions
The public entry is `dpu_encoder_phys_cmd_init`. The vtable populated by `dpu_encoder_phys_cmd_init_ops` includes `enable`, `disable`, `control_vblank_irq`, `wait_for_commit_done`, `wait_for_tx_complete`, `prepare_for_kickoff`, `trigger_start`, IRQ enable/disable, `restore`, idle power-collapse preparation, and line count. Key helpers are `_dpu_encoder_phys_cmd_update_intf_cfg`, `dpu_encoder_phys_cmd_tearcheck_config`, `_dpu_encoder_phys_cmd_pingpong_config`, `_dpu_encoder_phys_cmd_wait_for_idle`, `_dpu_encoder_phys_cmd_wait_for_ctl_start`, and `_dpu_encoder_phys_cmd_handle_ppdone_timeout`.

## Control Flow and State
Mode set stores IRQ indexes from CTL, PP or INTF TE, and INTF underrun caps. Enable sets split config, programs CTL command-mode topology, binds PP to INTF on DPU 5+, programs command compression/widebus flags, configures tearcheck, and marks `DPU_ENC_ENABLED`. Kickoff preparation waits for previous PP done, resets pending state on timeout, disables autorefresh, and reconnects TE after kickoff. `pending_kickoff_cnt`, `pending_ctlstart_cnt`, `pending_vblank_cnt`, wait queues, and `vblank_refcount` are the key volatile state. Timeout handling snapshots display state, unregisters read-pointer IRQ after selected failures, signals frame error or panel-dead after repeated failures, and requests CTL reset through `enable_state`.

## Dependencies and Integration Points
Uses `dpu_core_irq_register_callback`, PP/INTF tearcheck ops, CTL `setup_intf_cfg`, `bind_pingpong_blk`, encoder frame/vblank/underrun callbacks, tracepoints, `dpu_kms_get_clk_rate("vsync")`, DSC helpers, widebus helpers, and display snapshots. DPU core major version decides whether TE lives on INTF or PP.

## Risks and Test Signals
Risks center on IRQ refcount imbalance, failing to unregister callbacks after timeout, invalid TE source when `has_intf_te` changes by SoC, and stale `pending_kickoff_cnt` causing commit stalls. Tests should cover command-mode panel commits, autorefresh disable, external TE reconnect, split master/slave paths, PP-done timeout recovery, CTL-start wait, DSC command mode, and line-count reads with both PP TE and INTF TE generations.
