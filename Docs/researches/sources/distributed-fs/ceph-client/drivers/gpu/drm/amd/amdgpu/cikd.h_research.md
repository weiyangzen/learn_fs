# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cikd.h

Purpose: defines CIK-generation register offsets, packet constructors, command opcodes, bit masks, display offsets, memory-type constants, SDMA packet fields, VCE command ids, and raster/backend mapping masks shared by CIK AMDGPU blocks.

Important APIs and definitions: memory type masks for `MC_SEQ_MISC0`, display CRTC/HPD/audio endpoint offsets, SRBM selector field helpers, PM4 packet helpers (`PACKET0`, `PACKET2`, `PACKET3`, `PACKET3_COMPUTE`), a large set of `PACKET3_*` opcode ids and field helpers, SDMA instance offsets and `SDMA_PACKET()`, SDMA opcodes/subopcodes for NOP/COPY/WRITE/IB/FENCE/TRAP/SEMAPHORE/POLL/COND_EXEC/FILL/PTE/TIMESTAMP/SRBM_WRITE, VCE command ids, LDS/private base helpers, KFD SDMA queue offset, and raster-config field masks.

Control flow: no executable control flow. The macros are consumed by ring emitters and register programming code to generate correct command stream words and MMIO offsets. `cik_sdma.c` uses SDMA definitions extensively; GFX and VM paths use PM4 packet definitions; `cik.c` and display code use register offsets and masks.

State and persistence: stateless compile-time definitions. The values encode hardware ABI contracts; changing them changes command streams and MMIO programming.

Dependencies and integration points: included by CIK common, IH, SDMA, GFX, and related blocks. It bridges generated/ASIC register headers and driver code that needs hand-authored packet/register constants.

Risks: any incorrect opcode, shift, mask, or offset can corrupt command streams, hang rings, or program the wrong register. Some macros assume a `REG_SET` helper exists from other headers. The file uses a broad include guard name `CIK_H`, which can conflict conceptually with `cik.h`'s `__CIK_H__` but not textually. Because these are raw hardware constants, review should compare against ASIC documentation or known-good upstream headers.

Test signals: compile of all CIK ring emitters, packet decoder tests where available, SDMA/GFX ring tests, VM flush behavior, VCE command submission, display register programming, and hardware smoke tests under graphics/compute/video workloads.
