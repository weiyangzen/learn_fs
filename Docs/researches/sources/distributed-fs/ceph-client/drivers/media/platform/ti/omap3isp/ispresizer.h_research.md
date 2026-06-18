# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispresizer.h

## Purpose
Declares the OMAP3 ISP resizer data model, pad numbering, coefficient container, scaling ratio/luma helper structures, input-source enum, and exported lifecycle/IRQ/query APIs used by the broader ISP driver.

## Important APIs, Types, and Functions
`struct isp_res_device` is the central state object containing the V4L2 subdevice, two media pads, active pad formats, input/output `isp_video` nodes, memory address/crop offset, current ratio, stream state, crop state, waitqueue, stopping atomic, and spinlock. `struct isprsz_coef`, `struct resizer_ratio`, and `struct resizer_luma_yenh` describe hardware programming inputs. Public prototypes cover init/cleanup, entity registration, ISR hooks, suspend/resume, busy check, and max-rate calculation.

## Control Flow
This header does not execute control flow, but its layout defines the contract consumed by `ispresizer.c` and the ISP core. The resizer transitions between `RESIZER_INPUT_NONE`, `RESIZER_INPUT_VP`, and `RESIZER_INPUT_MEMORY`, and exposes sink/source pads `RESZ_PAD_SINK` and `RESZ_PAD_SOURCE` to media graph code.

## State and Persistence
All state is in-memory kernel driver state. The `crop.request` value stores the user-facing crop, while `crop.active` stores the hardware-mangled crop that satisfies resizer equations. `addr_base` and `crop_offset` are volatile DMA programming aids for memory input.

## Dependencies and Integration Points
Depends on Linux spinlocks/types and forward declarations from the ISP stack. It embeds `struct isp_video` and V4L2/media structures through included ISP headers, so ABI drift in video or media entity state affects this structure.

## Risks and Edge Cases
Bitfield `applycrop` and `state` are touched in streaming/IRQ paths and require the spinlock discipline implemented in the C file. Pad constants must stay aligned with entity initialization and subdev callbacks. Adding fields to `struct isp_res_device` requires checking initialization and cleanup paths.

## Test Signals
Compile coverage across OMAP3 ISP configs should catch declaration drift. Runtime evidence comes from correct registration of two video nodes and one scaler subdevice, valid pad link setup, suspend/resume behavior, and no races when changing crop while streaming.
