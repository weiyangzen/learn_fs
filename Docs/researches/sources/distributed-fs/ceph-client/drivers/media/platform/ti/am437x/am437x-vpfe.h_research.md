# sources/distributed-fs/ceph-client/drivers/media/platform/ti/am437x/am437x-vpfe.h

## Purpose
Defines the AM437x VPFE driver's internal data model for subdevice integration, CCDC configuration, supported formats, vb2 buffers, and the main device state.

## Important APIs, Types, And Functions
Key enums describe pin polarity, hardware interface type, CCDC pixel format, frame format, pixel order, and buffer type. `struct vpfe_hw_if_param` stores endpoint interface type, sync polarities, and bus width. `struct vpfe_subdev_info` and `struct vpfe_config` describe the single remote subdevice and async connection. `struct ccdc_params_raw`, `struct ccdc_params_ycbcr`, `struct ccdc_config`, and `struct vpfe_ccdc` model CCDC hardware programming. `struct vpfe_fmt` maps V4L2 fourcc to mbus code and bits-per-pixel. `struct vpfe_device` is the top-level driver state.

Inline helpers compute maximum bit positions for gamma/data-size settings and include the CCDC register header.

## Control Flow
The header has no executable flow beyond inline helpers. Its structures are populated by device-tree parsing, async bind, V4L2 format/input/std ioctls, CCDC programming helpers, vb2 queue callbacks, IRQ handling, and PM context save/restore.

## State And Persistence
Defines all important in-memory state: V4L2/video objects, notifier, current subdevice/input, selected standard, IRQ, current/next buffers, current format and crop, active format list, vb2 queue, DMA queue/lock, field offset, CCDC config/register context, stopping flag, and capture-stop completion.

## Dependencies And Integration Points
Depends on Linux AM437x VPFE UAPI definitions, clocks, completions, I/O, I2C, V4L2 core, vb2 V4L2, vb2 DMA-contig, and local register definitions. It is shared only by the AM437x implementation.

## Risks
The `VPFE_MAX_SUBDEV` and `VPFE_MAX_INPUTS` constants are one, but several structures look general; future expansion needs careful array and async-notifier auditing. Register context sizing depends on `VPFE_REG_END`. State fields are shared across ioctl, vb2, IRQ, and PM paths, so lock discipline in the C file is critical.

## Test Signals
Compile-time coverage catches structure/API drift. Runtime validation is through the C file: graph binding, format negotiation, capture IRQs, buffer completion, and suspend/resume context restore.
