# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn32/dcn32_hpo_dp_link_encoder.h

Purpose: Declares DCN3.2-specific HPO DP link encoder field-mask list and constructor.

Important APIs and types: `DCN3_2_HPO_DP_LINK_ENC_MASK_SH_LIST` lists the fields needed by inherited DCN31 link encoder code, excluding the DCN31 RDPCSTX mask composition. `dcn32_hpo_dp_link_enc_is_in_alt_mode` and `hpo_dp_link_encoder32_construct` are declared.

Control flow: resource code uses this mask list when building DCN32 register metadata, then constructs a DCN32 function table over the DCN31 concrete object.

State and persistence: no state in the header. It defines metadata contracts for register field generation.

Dependencies and integration: includes `link_encoder.h` but uses `struct dcn31_hpo_dp_link_encoder` in prototypes, so includers must have the DCN31 definition available or rely on prior declarations.

Risks and test signals: the duplicate prototype for `dcn32_hpo_dp_link_enc_is_in_alt_mode` is harmless but noisy. Compile coverage should ensure include ordering provides the DCN31 struct, and register tests should validate field masks match DCN32 hardware headers.
