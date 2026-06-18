# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vid.h

## Purpose
`vid.h` collects VI-era register offsets, PM4 packet helpers, packet opcodes, VCE/HEVC command IDs, SDMA/CRTC/DIG/audio/HPD instance offsets, and raster configuration bit helpers. It is a constants-only companion used by ring emitters, queue managers, and VI ASIC code.

## Important APIs, Types, And Functions
There are no functions or types. Important macro groups include SDMA instance offsets, display/audio/hotplug instance offsets, `PIPEID/MEID/VMID/QUEUEID`, memory type masks, PM4 packet constructors (`PACKET0`, `PACKET2`, `PACKET3`, `PACKET3_COMPUTE`), many `PACKET3_*` opcodes and field helpers, VCE and HEVC command constants, and raster backend mapping helpers for `PA_SC_RASTER_CONFIG` and `PA_SC_RASTER_CONFIG_1`.

## Control Flow
The macros are expanded by callers when building command buffers or interpreting packet headers. They do not execute directly, but they encode GPU command-processor contracts: packet type, count, opcode, destination selection, cache policy, synchronization, queue mapping, unmapping, query status, and DMA control fields.

## State And Persistence
The header owns no software state. Its constants shape persistent GPU command streams submitted to rings and IBs. Incorrect bit encodings can persist in ring buffers, MQDs, fences, or indirect buffers until consumed by hardware.

## Dependencies And Integration Points
`vid.h` is included by `vi.c` and may be used by VI-era GFX, SDMA, VCE, HEVC, KIQ, and queue-management code. It integrates with register definitions from generated ASIC headers and with common AMDGPU ring-write helpers that expect correctly packed PM4 words.

## Risks
Macro correctness is critical because the compiler cannot validate GPU packet semantics. Some helpers do not parenthesize every argument in a defensive style and several macros encode raw bit shifts; accidental signed or oversized inputs can bleed into adjacent fields. Packet count fields have hardware limits, so callers must bound counts before invoking constructors. Any opcode or field change risks hard GPU hangs rather than clean software failures.

## Test Signals
Compile coverage catches only syntax and missing macro names. Runtime signals include passing ring tests, successful fence/trap/write-data/wait-reg-mem operations, KIQ map/unmap/query flows, VCE/HEVC command submission, and GPU recovery tests that do not show bad opcode interrupts or command processor stalls.
