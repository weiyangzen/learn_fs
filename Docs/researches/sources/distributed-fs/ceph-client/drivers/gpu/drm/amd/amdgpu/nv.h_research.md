# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nv.h

## Purpose
`nv.h` declares the Navi common IP block and the few cross-file helper entry points exported by `nv.c`.

## Important APIs, Types, And Functions
It includes `nbio_v2_3.h`, declares `nv_common_ip_block`, `nv_grbm_select()`, `nv_set_virt_ops()`, and `cyan_skillfish_reg_base_init()`.

## Control Flow
There is no header control flow. Other AMDGPU files include it to install `nv_common_ip_block`, select GRBM queues through `nv_grbm_select()`, initialize virtualization ops, or call Cyan Skillfish register-base setup.

## State And Persistence
No state is defined in the header. The declared functions mutate `adev` state in their implementations.

## Dependencies And Integration Points
It depends on the NBIO 2.3 header and AMDGPU device type definitions from included contexts. `cyan_skillfish_reg_base_init()` is declared here for a platform-specific integration point outside this source pair.

## Risks
The direct include of `nbio_v2_3.h` reflects Navi baseline assumptions; other NBIO versions are included by implementation files. A declaration without a local definition, such as `cyan_skillfish_reg_base_init()`, requires link coverage in the wider tree.

## Test Signals
Compile/link success, common IP block registration, GRBM queue selection behavior, SR-IOV virt ops installation, and Cyan Skillfish builds are the relevant signals.
