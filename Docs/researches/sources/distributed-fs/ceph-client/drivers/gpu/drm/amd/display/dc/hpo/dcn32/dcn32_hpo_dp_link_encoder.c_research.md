# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn32/dcn32_hpo_dp_link_encoder.c

Purpose: Provides the DCN3.2 HPO DP link encoder variant, largely reusing DCN3.1 behavior while supplying a DCN3.2 function table and alt-mode helper.

Important APIs and functions: `dcn32_hpo_dp_link_enc_is_in_alt_mode` reads `RDPCS_PHY_DPALT_DISABLE` from `RDPCSTX_PHY_CNTL6[transmitter]`. `hpo_dp_link_encoder32_construct` initializes the same `dcn31_hpo_dp_link_encoder` concrete struct but binds `dcn32_hpo_dp_link_encoder_funcs`.

Control flow: all major operations in the function table point to DCN31 implementations: PHY enable/disable, link enable/disable, test pattern, SAT table, throttled VCP, read state, and FFE. Only `is_in_alt_mode` is supplied locally.

State and persistence: base state and register metadata are initialized in the constructor. Hardware state is managed by reused DCN31 routines.

Dependencies and integration: includes DCN31 and DCN32 headers plus register helpers. Integrated by DCN32 resource construction for DP2/HPO links.

Risks and test signals: because it reuses DCN31 functions, register compatibility is assumed. Tests should verify DCN32 register tables include every field used by inherited routines and that alt-mode transmitter indexing is valid for UNIPHY A-E.
