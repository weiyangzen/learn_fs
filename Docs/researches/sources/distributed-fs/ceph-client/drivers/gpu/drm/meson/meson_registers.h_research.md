# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_registers.h

Purpose: Central Meson DRM VPU register map and bitfield header. It names register offsets for VPP, VIU, OSD, VD input, VENC, HDMI routing, RDMA, gamma/TCON/LCD, AFBC decoders, blend units, and memory arbitration, and provides `_REG()` and `writel_bits_relaxed()` helpers.

Important APIs, types, and functions: `_REG(reg)` converts Meson register numbers to byte offsets by shifting left by two. `writel_bits_relaxed(mask, val, addr)` performs a read-modify-write. The remainder is macro definitions: VPP/VPP2 scaling/blend/color registers, VIU OSD/VD registers, matrix/HDR registers, AFBC and MAFBC registers, ENCI/ENCP/ENCL/ENCT encoder timing registers, VPU mux/HDMI setting bits, RDMA registers/control bits, LCD/gamma/TCON registers, and G12A blend-source controls.

Control flow: No runtime flow in the header, but it controls almost every MMIO access in this subset. Encoder files use ENCI/ENCP/ENCL/VPU HDMI constants, plane/overlay files use OSD/VD/VPP/blend constants, AFBCD uses OSD1_AFBCD and VPU_MAFBC constants, and RDMA uses channel register constants.

State and persistence: All macros represent persistent hardware state. Many registers are write-once-until-mode-change, while interrupt/status/reset registers have side effects. `writel_bits_relaxed()` is non-atomic with respect to concurrent MMIO users unless callers serialize externally.

Dependencies and integration points: Includes `<linux/io.h>` and assumes Linux bit macros are available through consumers. It is the source of truth for register numbers shared across Meson DRM modules.

Risks: A wrong offset or bit definition affects hardware globally. Duplicate numeric aliases exist for hardware overlays, such as `VPU_HDMI_FMT_CTRL` and `VPU_VDIN_ASYNC_HOLD_CTRL`, requiring context-aware use. The read-modify-write helper can race if used on registers touched by interrupt handlers or other display paths. The file is large and includes blocks not used by this subset, so changes should be scoped carefully.

Test signals: Broad hardware smoke tests are needed: primary/overlay scanout, HDMI/CVBS/DSI output, scaling, AFBC decode, RDMA replay, suspend/resume, and SoC-specific register paths. Compile-time references catch only spelling, not semantic bit errors.
