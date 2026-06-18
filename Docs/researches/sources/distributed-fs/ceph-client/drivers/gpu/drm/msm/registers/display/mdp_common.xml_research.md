# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/mdp_common.xml

## Purpose
This XML file holds shared RNN definitions used by Qualcomm MDP display register databases. It avoids duplicating common pixel-format, component, alpha, fetch, coordinate, and packing definitions between MDP generations, especially MDP4 and MDP5.

## Important APIs, Types, And Data
The key exported enums are `mdp_chroma_samp_type`, `mdp_fetch_type`, `mdp_mixer_stage_id`, `mdp_alpha_type`, `mdp_component_type`, `mdp_bpc`, `mdp_bpc_alpha`, and `mdp_fetch_mode`. Inline bitsets `reg_wh` and `reg_xy` encode common 16-bit width/height and x/y register layouts. `mdp_unpack_pattern` defines four 8-bit unpack elements for source pixel unpack registers. These types are referenced by `mdp5.xml` fields such as `SRC_SIZE`, `SRC_XY`, `SRC_FORMAT`, `SRC_UNPACK`, blending controls, and pixel extension arrays.

## Control Flow, State, And Integration
The file has no runtime execution. During generation, `gen_header.py` imports it first, registers its enums and inline bitsets, and lets later files use them as field types. The state described is reusable hardware register encoding, not persistent driver state. Because inline bitsets are expanded into register-specific macros, changes here affect every imported register database that references the shared names.

## Risks And Test Signals
Any enum value drift can silently corrupt generated field programming across multiple display generations. The risk is high for `mdp_mixer_stage_id` because stage IDs encode z-order and are split across legacy low bits and MDP5 extension bits. Test signals include successful RNN parsing, no unknown-type errors when generating MDP headers, generated macros matching expected names, and display composition tests that exercise scaling, alpha blending, YUV formats, and source unpacking.
