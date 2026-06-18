# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga_overlay.h

## Purpose

`svga_overlay.h` defines legacy VMware SVGA video-overlay escape formats, FourCC identifiers, stream register update/flush payloads, and packed FIFO escape structures.

## Important APIs, Types, and Functions

- `VMWARE_FOURCC_YV12`, `VMWARE_FOURCC_YUY2`, `VMWARE_FOURCC_UYVY` and `SVGAOverlayFormat`: supported overlay video formats.
- `SVGA_VIDEO_COLORKEY_MASK`: color-key bit mask.
- `SVGA_ESCAPE_VMWARE_VIDEO`, `_SET_REGS`, and `_FLUSH`: overlay escape command IDs.
- `SVGAEscapeVideoSetRegs` and `SVGAEscapeVideoFlush`: non-packed logical payloads with stream ID and register/value items.
- `SVGAFifoEscapeCmdVideoBase`, `SVGAFifoEscapeCmdVideoFlush`, `SVGAFifoEscapeCmdVideoSetRegs`, and `SVGAFifoEscapeCmdVideoSetAllRegs`: packed FIFO escape payload layouts.

## Control Flow

There is no executable logic. Runtime overlay code constructs SET_REGS escapes with one or more register/value items to update stream state, then emits FLUSH escapes when needed. The all-register payload uses `SVGA_VIDEO_NUM_REGS` from `svga_reg.h`.

## State and Persistence Behavior

Overlay stream state persists in the virtual device/host overlay unit. The header defines message formats for mutating that state but stores none itself.

## Dependencies and Integration Points

- Includes `svga_reg.h` for video register IDs/counts and base types.
- Integrated by vmwgfx overlay support and the base SVGA escape FIFO command path.

## Risks and Edge Cases

- Several structs use one-element trailing arrays for variable numbers of register updates. Callers must allocate enough bytes for the actual item count.
- Packed FIFO structures must match host expectations exactly.
- Overlay support is legacy; modern display paths may not exercise it, increasing regression risk.
- Color-key values should be masked to 24 bits.

## Test Signals

- Overlay command construction tests should cover single-register, all-register, and flush payload sizes.
- Size/offset checks should cover packed FIFO escape structs.
- Functional tests should verify YV12/YUY2/UYVY stream setup, color keying, and destination screen selection where overlay support is available.
