<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/regsnv04.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/regsnv04.h

## Purpose
Defines legacy NV04 framebuffer register addresses and selected bitfields used by older framebuffer code.

## Important APIs, Types, And Functions
Exports constants for `NV04_PFB_BOOT_0`, memory type/amount fields, RAM width, and `NV04_PFB_CFG0`. There are no functions or data objects.

## Control Flow
This header has no runtime flow. Including code uses the symbolic constants when reading or masking MMIO registers.

## State And Persistence
No driver state is stored. The constants describe persistent hardware register ABI.

## Dependencies And Integration Points
Integrates with early Nouveau framebuffer implementations and any code that decodes NV04-class PFB boot/configuration registers.

## Risks And Edge Cases
Incorrect masks or shifts would misdecode memory type, width, or amount on old GPUs. This file does not validate chipset applicability.

## Test Signals
Boot logs and VRAM sizing on NV04-era hardware are the relevant signals, together with compiler checks for include users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/regsnv04.h -->
