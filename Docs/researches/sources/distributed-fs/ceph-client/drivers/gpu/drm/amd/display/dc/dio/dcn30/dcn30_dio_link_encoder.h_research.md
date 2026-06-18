# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_link_encoder.h

## Purpose
This header defines the DCN30 link encoder register and mask/shift contract plus constructor and hardware-init prototypes. It gives the DCN30 implementation and later derivatives a common DIO backend register list for DIG, DP, AUX, DPCS, HPD, FEC, and PHY/alt-mode fields.

## Important APIs, Types, and Macros
`LE_DCN3_REG_LIST(id)` enumerates the DIG backend, TMDS, DP DPHY, DP link/framing, MST SAT, secondary packet, video stream, fast-training, and HBR2 pattern registers. `LINK_ENCODER_MASK_SH_LIST_DCN30(mask_sh)` extends DCN20 with TMDS DC balancer control. `DPCS_DCN3_MASK_SH_LIST(mask_sh)` adds DPCS data-order, PHY boost, TX clock enable, and USB-C DP alt-mode lane/disable fields.

The prototypes are `dcn30_link_encoder_construct`, `enc3_hw_init`, and `dcn30_link_encoder_validate_output_with_stream`.

## Control Flow and State
The header itself has no runtime flow. It shapes the static register tables consumed by `dcn30_dio_link_encoder.c` and compatible later files. State is hardware register state accessed through generated table pointers and masks.

## Dependencies and Integration Points
The header includes `dcn20/dcn20_link_encoder.h` and is included by DCN31/DCN32/DCN35/DCN401 link encoder headers or implementations. It is a foundational include for DCN3 link function-table construction.

## Risks and Test Signals
Any mismatch in register list or mask names will break compile-time generated register binding or cause runtime writes to the wrong field. Test signals include successful all-ASIC builds, DP link training, TMDS output, MST allocation, AUX init, FEC toggling, and USB-C DP alt-mode detection paths using the DPCS fields defined here.
