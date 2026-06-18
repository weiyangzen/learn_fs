# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/Makefile

## Purpose

This Makefile builds the Amlogic C3 ISP driver aggregate object from device, params, stats, capture, core, and resizer implementation files.

## Important APIs, Types, And Symbols

- `c3-isp-objs` includes `c3-isp-dev.o`, `c3-isp-params.o`, `c3-isp-stats.o`, `c3-isp-capture.o`, `c3-isp-core.o`, and `c3-isp-resizer.o`.
- `obj-$(CONFIG_VIDEO_C3_ISP) += c3-isp.o` gates the aggregate driver object.

## Control Flow

Kbuild links all component objects into one `c3-isp` module or built-in object when `VIDEO_C3_ISP` is enabled.

## State And Persistence

There is no runtime state in this file. It determines build composition only.

## Dependencies And Integration Points

The object list corresponds to the shared data structures and prototypes in `c3-isp-common.h`: device probing, core subdev, resizers, capture nodes, stats node, and params node are all separate implementation units linked together.

## Risks

Omitting one component causes unresolved symbols for the registration, ISR, or pre-configuration functions declared in the common header. Adding a new shared entry point requires updating this object list if it lives in a new source file.

## Test Signals

Targeted module builds should produce `c3-isp.ko` without unresolved symbols. Link errors involving `c3_isp_captures_*`, `c3_isp_stats_*`, `c3_isp_params_*`, `c3_isp_core_*`, or `c3_isp_resizers_*` implicate this Makefile or matching source files.
