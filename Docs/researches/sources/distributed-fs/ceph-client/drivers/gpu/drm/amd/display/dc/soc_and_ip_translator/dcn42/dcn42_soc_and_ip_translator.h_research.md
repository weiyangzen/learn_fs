<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/dcn42/dcn42_soc_and_ip_translator.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/dcn42/dcn42_soc_and_ip_translator.h

## Purpose

This header declares the DCN42 SoC/IP translator constructor and the DCN42 SoC bounding-box getter.

## Important APIs, Types, And Functions

- `dcn42_construct_soc_and_ip_translator(struct soc_and_ip_translator *soc_and_ip_translator)`.
- `dcn42_get_soc_bb(struct dml2_soc_bb *soc_bb, const struct dc *dc, const struct dml2_configuration_options *config)`.

## Control Flow

The header has no executable flow. It exposes DCN42 translator functions to the generic translator factory and any direct DML2 integration code.

## State And Persistence Behavior

No state is stored here. The declared implementation populates caller-owned DML2 structures from DC runtime state.

## Dependencies And Integration Points

Includes core DC types, `dc.h`, `clk_mgr.h`, DML top SoC parameter types, and the generic `soc_and_ip_translator` definition. It is consumed by `soc_and_ip_translator.c`.

## Risks And Edge Cases

The include path uses `dml_top_soc_parameter_types.h` directly while DCN401 uses the `dml2_0/dml21/inc/...` path; include path changes can break one header but not the other. Signature changes must stay synchronized with the generic function table.

## Test Signals

Build coverage confirms include paths and declarations. Runtime validation is indirect through successful creation of a DCN42 translator and correct `get_soc_bb`/`get_ip_caps` callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/dcn42/dcn42_soc_and_ip_translator.h -->
