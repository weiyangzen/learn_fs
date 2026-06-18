<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_dsi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_dsi.h

## Purpose
Declares Keem Bay DSI data structures, MIPI/DSI/D-PHY constants, register helper inlines, configuration structs, and the DSI entry points used by the platform and CRTC code.

## Important APIs, types, and functions
Important types include `struct kmb_dsi`, `struct mipi_ctrl_cfg`, `struct mipi_tx_ctrl_cfg`, `struct mipi_tx_frame_cfg`, `struct mipi_tx_frame_section_cfg`, datatype parameter structs, and D-PHY/DSI enums. Inline helpers are `kmb_write_mipi()`, `kmb_read_mipi()`, `kmb_write_bits_mipi()`, `kmb_set_bit_mipi()`, and `kmb_clr_bit_mipi()`. Prototypes cover host bridge init, mode set, MMIO mapping, clock init, encoder init, and unregister.

## Control flow
The header has no complex flow beyond MMIO access helpers. `kmb_write_bits_mipi()` performs read-modify-write masking for arbitrary bit fields; set/clear helpers manipulate single bit offsets.

## State and persistence
The `kmb_dsi` structure persists per DSI instance and owns encoder base, platform device, host/device pointers, bridge pointer, MIPI MMIO, clocks, and system clock value.

## Dependencies and integration points
Includes DRM encoder and MIPI DSI definitions. The constants must match `kmb_dsi.c` and `kmb_regs.h`; the public prototypes are consumed by `kmb_drv.c` and `kmb_crtc.c`.

## Risks
`kmb_write_bits_mipi()` uses `(1 << num_bits) - 1`, which is unsafe for 32-bit widths but current callers use smaller fields. The large enum surface is hardware-contract sensitive. Header-level constants hardcode default 24 MHz clocks, 24 bpp, and default lane rate.

## Test signals
Build coverage catches signature drift. Runtime validation is provided by DSI clock init, mode set, bridge attach, and D-PHY programming tests in the C file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_dsi.h -->
