# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn20/dcn20_link_encoder.h

Purpose: Declares the DCN20 link encoder extension over the DCN10 base, including AUX, UNIPHY, DPCS, FEC, MPLL, and USB-C alt-mode fields.

Important APIs/types/functions: `DCN2_AUX_REG_LIST()`, `UNIPHY_MASK_SH_LIST()`, `DPCS_MASK_SH_LIST()`, `DPCS_DCN2_MASK_SH_LIST()`, and `LINK_ENCODER_MASK_SH_LIST_DCN20()` define DCN2 register coverage. `struct mpll_cfg` models PLL parameters by link rate. `struct dpcssys_phy_seq_cfg` holds lane enables, fuse/SRAM/calibration flags, and selected MPLL config. `struct dcn20_link_encoder` embeds `struct dcn10_link_encoder`.

Control flow: Header declarations only; C code consumes these structures during construction, DP enable, and FEC/AUX operations.

State/persistence: Adds persistent `phy_seq_cfg` to the embedded DCN10 encoder state. Register metadata remains via the inherited `dcn10_link_encoder`.

Dependencies/integration: Includes `dcn10/dcn10_link_encoder.h`, making DCN20 a structural extension rather than an independent implementation.

Risks: Very large field macro lists are error-prone and shared by later generations. The disabled `#if 0` fields in `dpcssys_phy_seq_cfg` document intended PHY sequencing but are not active, so direct PHY programming remains incomplete.

Test signals: Compile-time field coverage, resource register initialization, FEC field access, USB-C alt-mode fields, and MPLL config selection for RBR/HBR/HBR2/HBR3.
