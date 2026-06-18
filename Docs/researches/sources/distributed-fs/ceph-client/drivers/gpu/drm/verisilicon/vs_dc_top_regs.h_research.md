<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_dc_top_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_dc_top_regs.h

## Purpose
`vs_dc_top_regs.h` defines top-level VeriSilicon DC reset, IRQ, and chip-identity register offsets.

## Important APIs, Types, and Functions
Macros include `VSDC_TOP_RST`, `VSDC_TOP_IRQ_ACK`, `VSDC_TOP_IRQ_VSYNC(n)`, `VSDC_TOP_IRQ_EN`, `VSDC_TOP_CHIP_MODEL`, `VSDC_TOP_CHIP_REV`, and `VSDC_TOP_CHIP_CUSTOMER_ID`.

## Control Flow
`vs_hwdb.c` reads identity registers, `vs_dc.c` reads IRQ ACK/status, and `vs_crtc.c` toggles VSYNC IRQ enable bits using these definitions.

## State and Persistence Behavior
The file describes persistent MMIO register state and contains no software state.

## Dependencies and Integration Points
It depends on Linux bit macros and is included by DC, CRTC, DRM IRQ, and hardware database code.

## Risks
IRQ ACK/status semantics must match hardware. Identity offsets drive supported-format and display-count selection; wrong values reject or misconfigure hardware.

## Test Signals
Hardware probe logs, IRQ enable/readback checks, and identity table matching validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_dc_top_regs.h -->
