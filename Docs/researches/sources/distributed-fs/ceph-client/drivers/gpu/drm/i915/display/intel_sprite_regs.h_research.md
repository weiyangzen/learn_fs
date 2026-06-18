# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sprite_regs.h

Purpose: defines MMIO register addresses and bitfields used by legacy sprite plane code. It covers three families: G4x/ILK/SNB DVS registers, IVB/HSW/BDW sprite registers, and VLV/CHV SP registers including CHV pipe-B sprite CSC registers.

Important definitions: DVS macros include `DVSCNTR`, `DVSSTRIDE`, `DVSPOS`, `DVSSIZE`, key registers, `DVSSURF`, `DVSSCALE`, and G4x/ILK gamma registers. IVB macros include `SPRCTL`, `SPRSTRIDE`, `SPRPOS`, `SPRSIZE`, key/surface/offset/scaler/gamma registers. VLV/CHV macros include `_VLV_SPR()`, `SPCNTR`, `SPSTRIDE`, `SPPOS`, `SPSIZE`, key/surface/tile/constant-alpha/CLRC/gamma registers, plus `SPCSC*` CSC coefficient and clamp registers.

Control flow and integration: `intel_sprite.c` composes control words and register payloads from these macros before calling `intel_de_write*()` or `intel_de_read()`. Field helpers such as `REG_FIELD_PREP`, `REG_BIT`, `_MMIO_PIPE`, and VLV base offsets make the register programming readable and constrain bit placement.

State and persistence: this header itself stores no state, but it defines all persistent hardware state touched by the sprite commit paths: enable bits, pixel formats, YUV order/range, rotation, tiling, source/destination keying, offsets, live surface, gamma, and CSC. It is therefore part of the hardware contract.

Risks and tests: risks are incorrect field widths, wrong pipe/plane address calculations, and family-specific bit reuse such as HSW `SPROFFSET` sharing an IVB tile offset address. Test signals are plane enable/disable, supported pixel formats, tiling, YUV conversion, gamma, color keying, scaling, CHV pipe-B CSC, and error-state capture matching live MMIO.
