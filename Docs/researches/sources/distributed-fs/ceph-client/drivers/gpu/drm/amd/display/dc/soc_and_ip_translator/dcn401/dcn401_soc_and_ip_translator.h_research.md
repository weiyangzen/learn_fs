<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/dcn401/dcn401_soc_and_ip_translator.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/dcn401/dcn401_soc_and_ip_translator.h

## Purpose

This header declares the DCN401 SoC/IP translator constructor and reusable bounding-box update helpers.

## Important APIs, Types, And Functions

- `dcn401_construct_soc_and_ip_translator`.
- `dcn401_get_soc_bb`.
- `dcn401_update_soc_bb_with_values_from_clk_mgr`.
- `dcn401_update_soc_bb_with_values_from_vbios`.
- `dcn401_update_soc_bb_with_values_from_software_policy`.

## Control Flow

The header contains declarations only. It enables generic factory code and newer DCN translator implementations to call DCN401 update stages.

## State And Persistence Behavior

No state is stored here. The declared helpers populate caller-owned DML2 bounding-box structures from runtime DC state.

## Dependencies And Integration Points

Includes `core_types.h`, `dc.h`, `clk_mgr.h`, `soc_and_ip_translator.h`, and DML2 SoC parameter types. It is included by the generic translator factory and by the DCN42 translator to reuse VBIOS/software-policy code.

## Risks And Edge Cases

Because these helpers are reusable across revisions, changing their signatures or semantics can break DCN42 and any future translator that inherits DCN401 update behavior. FPU use must remain aligned with the Makefile flags and caller contexts.

## Test Signals

Build coverage verifies declarations across generic, DCN401, and DCN42 translation units. Functional validation comes from matching DML2 SoC outputs for DCN401 and DCN42 when shared update layers are exercised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/dcn401/dcn401_soc_and_ip_translator.h -->
