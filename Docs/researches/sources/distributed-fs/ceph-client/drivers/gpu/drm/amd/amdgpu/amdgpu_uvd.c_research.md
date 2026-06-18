# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_uvd.c

## Purpose

`amdgpu_uvd.c` implements legacy UVD video decode support: firmware selection/loading, firmware BO allocation, suspend/resume save and restore, per-file decode handle tracking, command submission validation/patching, kernel-generated create/destroy messages, power management, and IB self-tests. It covers pre-VCN decode hardware and compatibility quirks such as 256 MB address segment restrictions on older chips.

## Important APIs And Functions

`amdgpu_uvd_sw_init()` selects firmware by ASIC, requests and validates it, derives firmware version and maximum session handles, allocates per-instance VCPU BOs, initializes handle slots, determines 64-bit address support and context-buffer support, and allocates a shared message IB BO. `amdgpu_uvd_sw_fini()` destroys the scheduler entity, frees saved VCPU snapshots, VCPU BOs, rings, message BO, and firmware.

`amdgpu_uvd_prepare_suspend()`, `amdgpu_uvd_suspend()`, and `amdgpu_uvd_resume()` handle VCPU BO preservation. Resume either restores saved BO contents or reloads firmware/zeros the rest and forces ring fence completion. RAS ATHUB events and DPC recovery are treated specially because they can corrupt VCPU memory.

The CS parser is built around `struct amdgpu_uvd_cs_ctx`. `amdgpu_uvd_cs_packets()` walks packet0/type2 command streams. `amdgpu_uvd_cs_pass1()` validates/forces buffer placement for older non-64-bit UVD. `amdgpu_uvd_cs_pass2()` patches virtual addresses to real GPU offsets, enforces buffer sizes, 256 MB segment limits, valid command ids, and message-before-other-command ordering. `amdgpu_uvd_cs_msg()` validates create/decode/destroy messages and per-file handles. `amdgpu_uvd_cs_msg_decode()` computes minimum DPB/image/context sizes for H264, VC1, MPEG2, MPEG4, MJPEG, and H265.

`amdgpu_uvd_get_create_msg()` and `amdgpu_uvd_get_destroy_msg()` synthesize firmware messages for ring tests and cleanup, then submit through `amdgpu_uvd_send_msg()`. `amdgpu_uvd_ring_begin_use/end_use()` ungate/gate clocks and power with delayed idle work. `amdgpu_uvd_ring_test_ib()` validates IB execution. `amdgpu_uvd_used_handles()` counts active sessions.

## Dependencies And Integration

The file depends on firmware loading, AMDGPU BO/TTM placement, VM mapping lookup, CS parsing, ring/job submission, scheduler entities, dma-fence, RAS state, DPM/powergating, and hardware register packet definitions from `cikd.h` and `uvd_4_2_d.h`. It integrates with file close through `amdgpu_uvd_free_handles()` and with ring setup through `amdgpu_uvd_entity_init()`.

## State, Risks, And Tests

Persistent runtime state lives in `adev->uvd`: firmware pointer/version, max handles, per-instance VCPU BOs, message BO, atomic handle array plus owning `drm_file`, idle work, context-buffer mode, and decode image width. Risks include malformed command streams causing out-of-bounds reads if length checks miss a case, integer overflow or divide-by-zero in decode-size math for invalid dimensions, handle leaks/collisions across files, BO placement failures, stale saved BOs after reset, and powergating races around active fences.

Test signals include firmware selection for each supported ASIC, old/new firmware version handling, CS parser rejection of invalid packet types/registers/commands/alignment, decode message buffer-size validation, create/decode/destroy handle transitions, file-close cleanup, suspend/resume with active and inactive sessions, RAS-triggered resume behavior, 256 MB segment crossing tests, idle clock gating, and ring/IB self-tests.
