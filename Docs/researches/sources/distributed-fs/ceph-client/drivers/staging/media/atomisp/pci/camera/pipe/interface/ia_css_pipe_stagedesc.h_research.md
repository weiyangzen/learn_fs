# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/interface/ia_css_pipe_stagedesc.h

Purpose: declares helpers that convert binaries, firmware blobs, or SP functions into CSS pipeline stage descriptors.

Important APIs/types/functions: `ia_css_pipe_get_generic_stage_desc()`, `ia_css_pipe_get_firmwares_stage_desc()`, and `ia_css_pipe_get_sp_func_stage_desc()` fill `ia_css_pipeline_stage_desc` fields for binary-backed, firmware-backed, and SP-function-backed stages.

Control flow: no direct logic in the header. Callers use these helpers while assembling CSS pipelines after binary descriptor lookup.

State and persistence: stage descriptors are caller-owned runtime objects. The helpers do not allocate persistent state.

Dependencies and integration: depends on CSS firmware info, frame, binary, and pipeline-common types.

Risks and test signals: descriptor correctness is crucial because later pipeline execution trusts stage fields. Tests should validate binary, firmware, and SP-only stage assembly, including multi-output arrays and null vf/in frames.
