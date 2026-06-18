# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/interface/ia_css_pipe_util.h

Purpose: declares small CSS pipe utility helpers for input-format bit depth and output-frame array handling.

Important APIs/types/functions: `ia_css_pipe_util_pipe_input_format_bpp()` derives bits per pixel from a pipe's stream config. `ia_css_pipe_util_create_output_frames()` initializes a frame pointer array, and `ia_css_pipe_util_set_output_frames()` assigns a frame at a checked output index.

Control flow: no direct header control flow. Implementations are simple wrappers used by pipe descriptor and pipeline assembly code.

State and persistence: no stored state; helpers mutate caller-provided frame pointer arrays.

Dependencies and integration: depends on CSS pipe/frame public types and integrates with binary/stage descriptor code.

Risks and test signals: index bounds rely on assertions. Tests should cover all input formats, two-pixels-per-clock cases, and output arrays sized to `IA_CSS_BINARY_MAX_OUTPUT_PORTS`.
