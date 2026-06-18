# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn21/dcn21_link_encoder.h

## Purpose
Defines the DCN2.1 link encoder structure, register/mask extensions, and public constructor/DP-enable prototypes.

## Important APIs, Types, And Functions
`struct dcn21_link_encoder` embeds `struct dcn10_link_encoder` and adds `struct dpcssys_phy_seq_cfg`. `DPCS_DCN21_MASK_SH_LIST` extends DCN2 masks with fuse, DP-alt, vreg, EQ, DCO, and soft-reset fields. `DPCS_DCN21_REG_LIST` adds PHY control and DMCU DP-alt block registers. `LINK_ENCODER_MASK_SH_LIST_DCN21` extends link encoder masks and adds xbar/fuse/scratch registers. Exports `dcn21_link_encoder_enable_dp_output()` and constructor.

## Control Flow
No executable flow. Macros provide register descriptors for the implementation and inherited link helpers.

## State And Persistence
The concrete structure persists link encoder state plus PHY sequence configuration. Hardware state is represented by the listed PHY and link registers.

## Dependencies And Integration Points
Includes `dcn20/dcn20_link_encoder.h` and participates in DCN2.1 resource construction and link training.

## Risks
Macro `LINK_ENCODER_MASK_SH_LIST_DCN21(mask_sh)` references `id` inside the body for `SRI(...)` entries even though the macro signature has no `id`; this relies on expansion context or may be a latent macro bug. PHY field compatibility with inherited DCN20 helpers is critical.

## Test Signals
Compile all macro users, instantiate DCN2.1 link encoders, and run DP/HDMI link training, USB-C alt-mode, and PHY fuse/EQ programming tests.
