# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn401/dcn401_dsc.c

## Purpose

`dcn401_dsc.c` is the DCN4.01 DSC hardware backend. It mirrors the DCN20 preparation model but uses a DCN401-specific register map, interrupt-control layout, state readback, forwarding-status wait, and object type. It still relies on shared DSC config/PPS/RC helpers.

## Important APIs, Types, And Functions

The file exports `dsc401_construct`, `dsc401_read_state`, `dsc401_validate_stream`, `dsc401_set_config`, `dsc401_enable`, `dsc401_disable`, `dsc401_disconnect`, `dsc401_wait_disconnect_pending_clear`, and `dsc401_set_fgcg`. It also defines `dsc401_get_single_enc_caps` and a private register writer.

## Control Flow

Construction installs `dcn401_dsc_funcs`. Validation and set-config call shared `dsc_prepare_config`; set-config then writes DCN401 registers. The writer programs debug, DSCCIF input format/BPC, slice count and ICH fields, RC buffer model size, DCN401 interrupt-control register 0, PPS config registers 0-22, and range parameters. Enable/disable manage `DSC_CLOCK_EN` and DSCRM forwarding. Disconnect clears forwarding; wait polls `DSCRM_DSC_FORWARD_EN_STATUS`.

## State, Dependencies, Risks, And Test Signals

Runtime state is in `struct dcn401_dsc::reg_vals` and MMIO registers. `dsc401_read_state` fills additional fields such as block prediction, line buffer depth, version minor, RC buffer size, and simple422 state. Dependencies include `dcn401_dsc.h`, `reg_helper`, DRM DSC helpers, `dscc_types.h`, and `rc_calc.h`. Risks include divergent register names, commented-out DSCCIF size programming, changed status-poll semantics, and shared DCN20 reg-state compatibility. Tests should cover register programming, disconnect wait, readback, FGCg, and packed PPS.
