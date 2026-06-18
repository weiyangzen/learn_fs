# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/pipeline/interface/ia_css_pipeline.h

Purpose: declares the host-side pipeline/stage model for executing ISP binaries, firmware, and SP functions.

Important types/APIs: `ia_css_pipeline_stage`, `ia_css_pipeline`, `DEFAULT_PIPELINE`, `ia_css_pipeline_stage_desc`, lifecycle (`init`, `create`, `destroy`, `clean`), start/stop/status, stage add/finalize/get helpers, firmware/stage lookup, param usage query, SP thread map APIs, pipe I/O status accessor, and dump function.

Control flow/state: caller initializes the module, creates a pipeline with a unique `pipe_num`, maps it to an SP thread, appends stages from descriptors, finalizes stage numbers/ports, starts by sending SP events, and later requests stop/cleans.

Dependencies/integration: depends on `sh_css_internal`, public pipe types, frame structs, binary/firmware descriptors, and `ia_css_pipeline_common.h`.

Risks: pipeline and stage structs own frame pointers with allocation flags; lifetime rules are subtle. Static SP thread mapping is global and requires careful map/unmap.

Test signals: stage creation with binaries/firmware/SP funcs, automatic output/VF allocation, map/unmap boundaries, start/stop event emission, and cleanup freeing only owned frames.
