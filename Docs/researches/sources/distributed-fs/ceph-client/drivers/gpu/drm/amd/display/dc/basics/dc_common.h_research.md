# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/dc_common.h

Purpose: declares common AMD display-core helper functions implemented by `dc_common.c`. The header exposes color-space classification, pipe-tree visibility checks, and prescale parameter construction to hardware sequencing and other display modules.

Important APIs and types: declares `is_rgb_cspace()`, `is_lower_pipe_tree_visible()`, `is_upper_pipe_tree_visible()`, `is_pipe_tree_visible()`, and `build_prescale_params()`. The declarations depend on `enum dc_color_space`, `struct pipe_ctx`, `struct dc_bias_and_scale`, and `struct dc_plane_state` from `core_types.h`.

Control flow: this header has no executable logic. It defines the public interface used by callers that need the implementation in `dc_common.c`.

State and persistence: no state is declared or persisted. The functions operate on caller-owned display state and output structures.

Dependencies and integration points: includes `core_types.h`, which makes it part of the internal display core type graph. It is included by hardware sequencing modules such as DCN10 paths that need RGB/YCbCr classification, pipe blanking visibility checks, and DPP bias/scale setup.

Risks: because the header exposes recursive visibility helpers on raw `pipe_ctx` pointers, callers must pass valid pipe nodes from a stable display state. Signature changes would ripple into hardware sequencing code. Documentation of expected pointer nullability and pipe graph assumptions is minimal, so misuse depends on code review and integration tests.

Test signals: compile all hardware sequencing users after any signature or type change. Runtime validation should come from the `dc_common.c` behavior tests: color-space enum coverage, pipe graph traversal coverage, and prescale register value checks.
