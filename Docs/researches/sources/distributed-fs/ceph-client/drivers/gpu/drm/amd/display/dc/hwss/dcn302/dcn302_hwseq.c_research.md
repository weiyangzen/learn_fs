# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn302/dcn302_hwseq.c

## Purpose
Implements DCN 3.0.2-specific power-gating register control for DPP, HUBP, and DSC blocks.

## Important APIs, Types, and Functions
Exports `dcn302_dpp_pg_control`, `dcn302_hubp_pg_control`, and `dcn302_dsc_pg_control`. Each accepts `struct dce_hwseq *hws`, an instance index, and `bool power_on`. It uses register helper macros over domain PG config/status registers and `DC_IP_REQUEST_CNTL` for DSC.

## Control Flow
DPP and HUBP functions compute `power_gate` and expected `pwr_status`, honor debug disable flags, skip if the first PG config register is absent, switch over instance 0-4, update the domain power gate bit, and wait for PG FSM status. DSC additionally enables `IP_REQUEST_EN` around domain 16-20 programming and restores it afterward.

## State and Persistence Behavior
Mutates hardware PG control/status state and temporarily changes `DC_IP_REQUEST_CNTL.IP_REQUEST_EN`. No software state is retained.

## Dependencies and Integration Points
Called through private HWSS hooks patched by `dcn302_init.c` after inheriting DCN30 tables. Depends on register definitions in the DCN302 register table and debug flags `disable_dpp_power_gate`, `disable_hubp_power_gate`, and `disable_dsc_power_gate`.

## Risks and Test Signals
Risks include wrong domain-to-instance mapping, timeout waiting for PG FSM, leaving IP request enabled/disabled incorrectly, and unsupported instances breaking into debugger. Test with plane power gating on/off for all supported pipes, DSC enable/disable, debug flags, suspend/resume, and systems with missing PG registers.
