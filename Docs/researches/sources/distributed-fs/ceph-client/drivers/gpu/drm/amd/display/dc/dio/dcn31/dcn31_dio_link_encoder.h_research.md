# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h

## Purpose
This header defines DCN31 link encoder register/mask extensions and public APIs for DIO PHY muxing, mappable DP/DPIA flows, USB-C alt-mode checks, and max-link-cap derivation.

## Important APIs, Types, and Macros
`LE_DCN31_REG_LIST(id)` extends DCN3 with `DP_DPHY_INTERNAL_CTRL` and DIO link control registers A-F. `LINK_ENCODER_MASK_SH_LIST_DCN31(mask_sh)` includes FEC fields, TMDS control, AUX DPHY fields, and DIO link encoder selection fields. `DPCS_DCN31_REG_LIST(id)` and `DPCS_DCN31_MASK_SH_LIST(mask_sh)` define extensive RDPCSTX/RDPCSPIPE PHY, PLL, FIFO, DP alt-mode, fuse, and interrupt fields. `DPCS_DCN314_REG_LIST(id)` provides a related reduced PHY register list for DCN314 resources.

Public APIs include full and minimal constructors, `dcn31_link_encoder_set_dio_phy_mux`, DP SST/MST enable, disable, `dcn31_link_encoder_is_in_alt_mode`, `dcn31_link_encoder_get_max_link_cap`, and `enc31_hw_init`.

## Control Flow and State
The header defines contracts only. Runtime users program DIO mux, AUX, DP PHY/FEC, and alt-mode state through the listed registers and function prototypes.

## Dependencies and Integration Points
It includes `dcn30/dcn30_dio_link_encoder.h`. DCN32, DCN35, and DCN401 reuse DCN31 DIO mux and alt-mode APIs, so this header is a cross-generation link-routing dependency.

## Risks and Test Signals
The field surface is large and ASIC-sensitive; incorrect PHY or alt-mode fields can break USB-C lane detection, DP training, or power sequencing. Test signals include all DCN31-family builds, HPO mux programming, FEC status, USB-C DP Alt Mode detection, DP lane limiting, AUX init, and DP PHY training across transmitters A-F.
