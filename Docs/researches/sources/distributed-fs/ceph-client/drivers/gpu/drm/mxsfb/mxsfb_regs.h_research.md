# sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/mxsfb_regs.h

## Purpose
This header defines register offsets and bitfield macros for classic MXS/i.MX LCDIF/eLCDIF display controllers.

## Important APIs, Types, And Data
Offsets cover `LCDC_CTRL`, `CTRL1`, V3/V4 transfer count/current/next buffers, VDCTRL timing registers, CRC/debug registers, and overlay `AS_*` registers. Macros encode reset/clock-gate/run bits, bus width, word length, byte packaging, frame-done IRQ bits, CTRL2 outstanding request settings, transfer dimensions, sync polarity/width/period, wait counts, valid-data count, debug sync bits, overlay alpha/format/color-key/enable fields, and min/max resolution.

## Control Flow, State, And Integration
The file is a macro-only hardware contract consumed by `mxsfb_drv.c` and `mxsfb_kms.c`. The KMS path combines these macros with mode, format, and SoC devdata to program volatile controller state. `REG_SET` and `REG_CLR` describe the set/clear alias registers used throughout reset, IRQ, and enable paths.

## Risks And Test Signals
The risk surface is direct hardware programming accuracy. V3 and V4 offsets differ, so callers must use `mxsfb_devdata` for variant-dependent addresses. Width/mask macros assume callers pass values in range. Test signals include compile coverage, register dumps for known modes, IRQ clear/enable behavior, overlay enable/disable validation, and scanout stability under underflow-prone modes.
