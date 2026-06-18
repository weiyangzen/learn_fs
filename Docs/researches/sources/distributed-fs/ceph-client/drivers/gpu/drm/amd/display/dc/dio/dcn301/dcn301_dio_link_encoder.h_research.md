# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn301/dcn301_dio_link_encoder.h

## Purpose
This header defines DCN301 link encoder register lists, mask/shift additions, and construction prototypes. It parallels DCN30 while adding DCN301-specific DPCS mask fields.

## Important APIs, Types, and Macros
`LE_DCN301_REG_LIST(id)` enumerates DIG backend, TMDS, DP DPHY/link/MST/secondary/stream/fast-training registers. `LINK_ENCODER_MASK_SH_LIST_DCN301(mask_sh)` extends DCN20 with `TMDS_SYNC_DCBAL_EN`. `DPCS_DCN301_MASK_SH_LIST(mask_sh)` includes HDMI FRL mode, 10-bit data swap, 18-bit data-order invert, PHY boost, and TX clock enable.

The header declares `dcn301_link_encoder_construct` and the shared `enc3_hw_init`.

## Control Flow and State
There is no executable flow. The macros become static register binding data used by the C implementation and resource initialization. Hardware state is reached through the generated register and mask tables.

## Dependencies and Integration Points
It includes `dcn20/dcn20_link_encoder.h` and integrates with DCN301 resource construction, shared DCN30 AUX initialization, and common DCN10/DCN20 link functions.

## Risks and Test Signals
Register-list drift is the main risk, especially FRL/data-swap fields that differ from DCN30. Test signals include compile-time register generation, HDMI FRL-related path coverage if applicable, TMDS link behavior, DP link training, FEC, and AUX transactions.
