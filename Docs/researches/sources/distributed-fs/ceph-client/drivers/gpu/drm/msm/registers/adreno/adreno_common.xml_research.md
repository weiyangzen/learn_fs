# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/adreno_common.xml

## Purpose
`adreno_common.xml` is the shared Adreno rnndb fragment for cross-generation enums, inline bitsets, and common CP/register definitions. It is imported by most generation-specific Adreno XML files and generates `adreno_common.xml.h`, which is included directly by `adreno_gpu.h`.

## Important definitions
The file imports `freedreno_copyright.xml`, defines a `chip` enum with bare generation values `A2XX` through `A8XX`, and provides common rendering enums: draw primitive mode, compare function, stencil op, blend factor/op, surface endian, dither mode, depth format, copy-control mode, ROP code, render mode, MSAA sample count, shader thread/instruction modes, color swap, tessellation spacing, A5xx+ address and line modes, A6xx texture prefetch commands, and `adreno_pipe`.

It defines three inline bitsets. `adreno_rb_stencilrefmask` packs stencil reference, mask, and write-mask bytes. `adreno_reg_xy` packs X/Y coordinates plus `WINDOW_OFFSET_DISABLE`. `adreno_cp_protect` packs common protected-register region fields with base address, mask length, trap-write, and trap-read bits.

The `AXXX` 32-bit domain defines 71 common CP and scratch/event registers. Important groups include ringbuffer registers (`CP_RB_BASE`, `CP_RB_CNTL`, read/write pointer registers, write pointer delay/base), queue threshold and availability registers, scratch mask/address/registers, micro-engine state (`CP_ME_RDADDR`, `CP_ME_CNTL`, `CP_ME_STATUS`, ME RAM access), interrupt control/status/ack, CSQ/IB status, bin mask/select, indirect buffer base/size registers, CP status, and ME event source/address/data registers for VS, PS, CF, NRT, and VS fetch-done events.

## Control flow and generation behavior
The XML is a foundational import for generation-specific files. The Makefile passes XML inputs through `gen_header.py`, and `adreno_common.xml.h` is generated as part of the Adreno header set. Runtime control flow appears in the C driver through generated constants included by `adreno_gpu.h`; CP ringbuffer setup, interrupt handling, scratch register use, event programming, and protected register setup use these names and bit masks.

## State and persistence
The source itself is static. The generated constants describe persistent hardware state while the GPU is running: CP ringbuffer base/control and pointers, interrupt enables/status, scratch registers, protected register windows, event write addresses/data, and command processor status. Those hardware states persist until rewritten, reset, or power-cycled.

## Dependencies and integration points
This file is the dependency root for the generation-specific XML files in this work item. `a6xx_descriptors.xml`, `a6xx_enums.xml`, `a6xx_gmu.xml`, `a6xx_perfcntrs.xml`, `a7xx_enums.xml`, `a7xx_perfcntrs.xml`, `a8xx_descriptors.xml`, and `a8xx_enums.xml` all import it directly or rely on types it defines. Generated `adreno_common.xml.h` is included by `adreno_gpu.h`, so the common register and enum surface reaches the broader msm Adreno driver.

## Risks
Because this file is shared across generations, changes have a wide blast radius. Wrong CP ringbuffer or interrupt register definitions can break GPU submission, interrupt handling, or hang recovery. Misdefined blend/depth/stencil/MSAA enums can corrupt rendering across multiple generations. The common `adreno_cp_protect` layout differs from `a6x_cp_protect`, so protected-register programming must use the correct bitset for the target generation/path. Comments note limited confidence for some behavior, such as A5xx+ line mode and A6xx texture prefetch commands, so those areas should be validated on hardware before broadening use.

## Test signals
Build signals include XML validation, generated `adreno_common.xml.h`, and successful compilation of `adreno_gpu.h` consumers. Runtime signals include successful ringbuffer initialization/submission, CP interrupts and acknowledgments, scratch register reads/writes, protected register fault behavior, draw mode/depth/stencil/blend correctness under CTS/deqp, line rendering with and without MSAA, and stable hang recovery/state capture.
