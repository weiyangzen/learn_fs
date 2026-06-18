# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-decon5433.h

## Purpose
This header defines register offsets and bitfield helpers for Exynos543x DECON display controller variants, including Exynos5430, Exynos5433, internal, and TV register differences. It is a hardware ABI map for DECON timing, windows, blending, interrupts, QoS, update/trigger, clock gating, and CRC control.

## Important APIs, Types, and Functions
The file exports macros for core register offsets such as `DECON_VIDCON0`, `DECON_VIDOUTCON0`, `DECON_WINCONx(n)`, `DECON_VIDOSDx*`, `DECON_SHADOWCON`, window buffer address registers, `DECON_VIDINTCON*`, `DECON_BLENDCON`, `DECON_UPDATE`, timing registers, trigger registers, CRC registers, and clock-gate registers. Bitfield macros cover `VIDCON0` enable/reset/status, output interface and interlace flags, window burst length, BPP modes, alpha/blending flags, shadow protection, interrupt status, update triggers, timing fields, CRC enable, and blending coefficients.

## Control Flow
The header has no executable flow. DECON driver code includes it to compose register values during mode set, atomic plane updates, shadow protection, vblank/framdone IRQ setup, trigger/update firing, and CRC reads.

## State and Persistence Behavior
The macros describe persistent MMIO state in DECON hardware. Window configuration, framebuffer addresses, alpha/blend settings, trigger mode, and timing registers remain programmed until changed or reset. Shadow-protection and update bits control when buffered register writes become active.

## Dependencies and Integration Points
Consumers are Exynos543x DECON drivers and related Exynos plane/CRTC code. The header depends on Linux bit helpers such as `GENMASK` from the including context. It integrates with display timing programming, framebuffer DMA address programming, blending, interrupt handling, QoS tuning, and optional TV/internal output paths.

## Risks
Register maps are SoC-specific; using Exynos5433 offsets on Exynos7 or FIMD hardware will program the wrong registers. Several macros take window numbers with implicit assumptions, including `n - 1` for key registers, so window 0 misuse can underflow offsets. BPP mode definitions include overlapping values for 25/32 bpp modes, so callers must pair them with format-specific semantics. Trigger and shadow bits are safety-critical for atomic updates because premature update can show partial framebuffer state.

## Test Signals
Build DECON543x users, verify mode set timing registers, window enable/disable, framebuffer base/end/size programming, alpha and pixel blending, shadow protection, vblank/framdone interrupts, trigger/update behavior, CRC enable/readback, and QoS/clock-gate settings on Exynos543x hardware or register-level tests.
