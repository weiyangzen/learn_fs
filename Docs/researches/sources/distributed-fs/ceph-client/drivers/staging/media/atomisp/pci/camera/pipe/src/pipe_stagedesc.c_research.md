# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/src/pipe_stagedesc.c

Purpose: fills CSS pipeline stage descriptors from already selected binaries, firmware entries, or SP functions.

Important APIs/types/functions: `ia_css_pipe_get_generic_stage_desc()` validates a binary-backed stage and copies binary mode, input, output, and vf frame pointers. `ia_css_pipe_get_firmwares_stage_desc()` fills a descriptor with both binary and firmware pointers plus an explicit mode. `ia_css_pipe_get_sp_func_stage_desc()` describes a standalone SP function with optional output frame and maximum input width.

Control flow: each helper assigns all relevant descriptor fields and initializes unused fields to null or `IA_CSS_PIPELINE_NO_FUNC`. Generic stage creation logs and returns early on invalid arguments.

State and persistence: no global state. The only mutation is the caller-provided `ia_css_pipeline_stage_desc`.

Dependencies and integration: depends on CSS pipeline common structures, binary metadata, firmware info, assertions, and debug tracing. Called during pipeline construction after binary lookup.

Risks and test signals: generic stage creation assumes `out_frame` has `IA_CSS_BINARY_MAX_OUTPUT_PORTS` entries. Firmware stage creation does not validate inputs. Tests should cover invalid binary info, multi-output copy, firmware mode propagation, and SP-only stage setup.
