
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_reg.h

## Purpose
Defines legacy Nouveau hardware register offsets, bit masks, object classes, FIFO commands, display registers, AUX channel registers, framebuffer registers, graph registers, timer registers, and NV50-era register-block descriptions used by low-level display, FIFO, memory, and legacy acceleration code.

## Important APIs, Types, and Functions
This header is entirely preprocessor definitions. Major groups include NV04/NV10/NV40 framebuffer boot/tile/Z compression registers, RAMHT context fields, DMA object class IDs, USER channel register layouts, PMC interrupt/enable registers, PBUS/PCI/ROM fields, PTIMER registers, PGRAPH interrupt/context/clip/format registers, FIFO DMA command encodings, NV50 PMC/PCONNECTOR/AUX/PBUS/PFB/PDISPLAY blocks, CRTC/DAC/SOR/display-user register definitions, SOR PWM definitions, DP control bits, and cursor user registers.

## Control Flow
The header implements no control flow. It provides symbolic constants that low-level code uses for direct `nvif_rd32()`/`nvif_wr32()`/MMIO programming and bitfield interpretation.

## State and Persistence
No software state is stored. The definitions correspond to persistent hardware register state and command encodings in NVIDIA GPUs.

## Dependencies and Integration Points
It is a low-level integration point for legacy register programming paths throughout the Nouveau driver, especially display, FIFO/channel, memory/tile, graph, timer, AUX, backlight, and LED/PWM code. Some definitions overlap with rules-ng imports and are documented as partial and potentially duplicated.

## Risks and Test Signals
Risks include stale or duplicated register definitions, incorrect bit masks across GPU generations, direct register access that bypasses NVIF/GSP abstractions, and accidental use of legacy definitions on unsupported hardware. Test signals are hardware-generation smoke tests, display hotplug/AUX/backlight/PWM behavior, legacy FIFO and graph init, suspend/resume register restore, and static checks for duplicate/conflicting defines when importing newer rules.
