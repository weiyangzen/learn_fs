<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource_fpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource_fpu.h

## Purpose

`dcn42_resource_fpu.h` declares the FPU-only DCN42 z-state support decision helper.

## Important APIs, Types, And Functions

- Include guard `_DCN42_RESOURCE_FPU_H_`.
- Includes `core_types.h`.
- Declares `void dcn42_decide_zstate_support(struct dc *dc, struct dc_state *context);`.

## Control Flow

No executable control flow is present. The header exposes a helper implemented in the paired C file so non-FPU resource code can call it inside `DC_FP_START`/`DC_FP_END`.

## State And Persistence Behavior

The header itself stores no state. The declared function mutates the bandwidth context in `struct dc_state`.

## Dependencies And Integration Points

It integrates `dcn42_resource.c` with the FPU compilation unit. Consumers must call the helper only with floating-point access enabled, matching kernel AMDGPU display FPU rules.

## Risks And Edge Cases

The main risk is misuse from a non-FPU-safe context. Signature drift between this header and the implementation would break the resource validation path at build time.

## Test Signals

Compiler coverage verifies declaration consistency. Runtime z-state validation on DCN42 confirms the call path is entered only inside the FPU guard and produces expected Z8 decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource_fpu.h -->
