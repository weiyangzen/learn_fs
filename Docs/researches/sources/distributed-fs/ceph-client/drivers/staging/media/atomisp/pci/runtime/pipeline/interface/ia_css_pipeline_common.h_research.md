# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/pipeline/interface/ia_css_pipeline_common.h

Purpose: shared pipeline stage function enumeration.

Important definitions: `enum ia_css_pipeline_stage_sp_func` values `RAW_COPY`, `BIN_COPY`, `ISYS_COPY`, and `NO_FUNC`; `IA_CSS_PIPELINE_NUM_STAGE_FUNCS` is 3, excluding `NO_FUNC`.

Control flow/state: no state. The enum lets stage descriptors and stage records distinguish SP-only copy/isys functions from normal ISP binary/firmware stages.

Dependencies/integration: consumed by pipeline creation, debug graph dump, and SP pipeline setup.

Risks: `IA_CSS_PIPELINE_NUM_STAGE_FUNCS` must stay synchronized with functional enum values. `NO_FUNC` is a sentinel and should not be counted as an executable SP function.

Test signals: switch/default handling for every enum, stage add validation for no binary/firmware/no func, and debug graph skipping SP funcs.
