# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/core_types.h

## Purpose

`core_types.h` defines the central internal Display Core resource and state model. It ties streams, planes, pipes, links, bandwidth/DML output, clocks, encoders, writeback, MALL/FAMS, and HWSS block sequences into the `dc_state` object used for validation and commits.

## Important APIs, Types, And Functions

Major types include `resource_funcs`, `resource_pool`, `stream_resource`, `plane_resource`, `link_resource`, `link_config`, `pipe_update_flags`, `pixel_rate_divider`, `p_state_switch_method`, `dsc_padding_params`, `pipe_ctx`, `link_enc_cfg_context`, `resource_context`, DCE/DCN bandwidth outputs, `bw_context`, `dc_dmub_cmd`, `dc_state`, `replay_context`, `dc_bounding_box_max_clk`, and `memory_qos`. `resource_funcs` is the resource-manager vtable for validation, DML pipe population, link encoder assignment, pipe acquisition/release, writeback population, MALL/mcache programming, DSC resource attachment, and encoder switching.

## Control Flow

Validation starts from a prospective `dc_state`, uses `resource_funcs` to acquire resources, populate DML pipe inputs, validate bandwidth/global/planes, assign encoders, and calculate watermarks/DLG. Commit/HWSS paths consume `pipe_ctx` entries, per-pipe update flags, cached DML/RQ/DLG/TTU registers, and block sequences. Reference counting on `dc_state` manages lifetime as current and candidate contexts move through validation and commit.

## State And Persistence Behavior

`dc_state` is the persistent in-memory description of a requested display state: stream arrays, phantom stream/plane arrays, resource context, PowerPlay display config, DML/DML2 bandwidth context, clock manager pointer, pending block sequence, DMUB commands, refcount, performance parameters, and power source. `pipe_ctx` persists per-pipe mappings and cached programming data. `resource_pool` persists hardware objects owned by the DC instance.

## Dependencies And Integration Points

The header includes broad DC, DCE, DCN, DML, DML2, hardware, DMUB, link, audio, DPP, DWB, HUBP, MPC, panel, and power-management headers. It is the integration point between resource management, bandwidth validation, HWSS, link services, color, writeback, mcache/MALL, and clock management.

## Risks And Edge Cases

This is a high-blast-radius header; layout or semantic changes affect nearly every DC subsystem. `pipe_ctx` links (`top_pipe`, `bottom_pipe`, ODM neighbors) must remain consistent during splits/merges. Resource reference counts and acquisition bitmaps can leak or double-assign hardware. Large bandwidth/DML fields must not be stack-copied casually. Phantom/SubVP and mcache/FAMS state adds additional hidden coupling to commit ordering.

## Test Signals

Full AMDGPU DC builds catch type drift. Functional tests should cover multi-stream, MPO, ODM, MPC combine, DSC, writeback, DP HPO, link encoder reassignment, phantom/SubVP, MALL/mcache, cursor, and power-source changes. Resource leak checks, validation status, pipe topology dumps, DML outputs, block sequence counts, and refcount warnings are useful signals.
