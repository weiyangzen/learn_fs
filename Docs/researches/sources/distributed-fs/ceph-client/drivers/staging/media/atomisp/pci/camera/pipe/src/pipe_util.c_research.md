# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/src/pipe_util.c

Purpose: implements small CSS pipe helpers used by descriptor and pipeline code.

Important APIs/types/functions: `ia_css_pipe_util_pipe_input_format_bpp()` delegates to `ia_css_util_input_format_bpp()` using the pipe stream format and `pixels_per_clock == 2`. `ia_css_pipe_util_create_output_frames()` nulls each output frame slot. `ia_css_pipe_util_set_output_frames()` assigns one output slot after asserting the index is in range.

Control flow: functions are straight-line wrappers around assertions and assignment.

State and persistence: mutates only caller-provided frame arrays. No persistent state.

Dependencies and integration: depends on CSS pipe/frame public APIs and format utility code. Used before binary descriptor selection and stage descriptor assembly.

Risks and test signals: null pipe/stream and out-of-range indices are assertion-only failures. Tests should include bpp mapping for supported atomisp input formats and output array initialization before stage creation.
