## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_dpi_regs.h

### Purpose

`mtk_dpi_regs.h` defines the DPI/DP-INTF register offsets and bit fields used by `mtk_dpi.c`. It names enable/reset/interrupt bits, output settings, timing generator registers, color limit and conversion fields, embedded sync fields, matrix selection, and test pattern controls.

### Important APIs, types, and functions

The header is macro-only. Major groups are `DPI_EN`, `DPI_RET`, `DPI_INTEN/INTSTA`, `DPI_CON`, `DPI_OUTPUT_SETTING`, `DPI_SIZE`, `DPI_DDR_SETTING`, horizontal/vertical timing registers, background/status/checksum registers, interlace/3D timing extensions, Y/C limit registers, YUV422 and embedded sync fields, matrix selection, frequency/edge bits, and `DPI_PATTERN0`.

### Control flow

There is no runtime control flow. `mtk_dpi.c` combines these masks with SoC-specific `mtk_dpi_conf` masks and shifts to program timing, polarity, bit depth, channel order, color conversion, DDR/edge behavior, input/output pixel packing, and test patterns.

### State and persistence behavior

The header owns no state. It describes persistent DPI hardware registers whose values remain until rewritten or reset: enable, reset, timing, output packing, color conversion, limits, DDR mode, interrupts, checksum, embedded sync, and pattern generator.

### Dependencies

The macros assume standard `BIT()`, `GENMASK()`, and related bit helpers are available through including files. Semantically it depends on `mtk_dpi.c` and MediaTek display hardware manuals.

### Integration points

All DPI bridge and component programming is expressed through this header. SoC variants in `mtk_dpi.c` choose different masks for the same conceptual fields, especially DP-INTF wide masks and channel-swap/input-2P bits.

### Risks

Many masks are unshifted legacy constants, while the driver also shifts config masks in several places; changing masks without checking call sites can double-shift or under-mask writes. DPI and DP-INTF reuse some registers with different bit positions. Incorrect DDR or channel swap definitions can produce wrong colors or broken output timing without compile-time failures.

### Test signals

Build coverage plus hardware readback while setting modes, RGB/YUV bus-format tests, interrupt/status behavior if enabled by future code, test-pattern debugfs output, and DP-INTF modes using 16-bit masks are useful validation signals.
