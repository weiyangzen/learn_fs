# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_0_offset.h

## Purpose
`sdma0_4_0_offset.h` defines the SDMA0 4.0 register-address map as word offsets from the SDMA0 register block base, documented in the file as base address `0x4980`. It is the address half of the SDMA0 4.0 register ABI: code combines these `mmSDMA0_*` offsets and `_BASE_IDX` selectors with AMDGPU register access helpers to read or write the right MMIO locations.

## Important APIs, Types, and Functions
There are no functions or types. The interface is 518 `mm...` macros: each register gets an offset macro and a corresponding `_BASE_IDX`, almost always `0`. The map starts with public engine controls (`UCODE_ADDR` at `0x0000`, `UCODE_DATA` at `0x0001`, VM context controls, `VF_ENABLE`, register-type metadata, power/clock/control registers, status and EDC registers), then moves through UTCL1, physical address, perf, trust/IOV, and finally queue contexts. Queue address ranges are structured: GFX registers begin at `0x0080`, PAGE at `0x00e0`, RLC0 at `0x0140`, and RLC1 at `0x01a0`. Each queue block defines ring base/read/write pointers, write-pointer polling, IB controls, doorbell, status/logging, watermarks, CSA, preempt, AQL, minor pointer update, and mid-command data/cntl registers.

## Control Flow and State
The header has no control flow. Its ordering and numeric spacing encode hardware state layout. Gaps in the sequence are meaningful reserved or unlisted hardware addresses, so consumers must not infer dense arrays except where the hardware block is explicitly repeated.

## Persistence and Dependencies
The offsets persist in compiled code wherever register access macros are expanded. They depend on matching generated headers: `sdma0_4_0_default.h` supplies reset values for the same names, and `sdma0_4_0_sh_mask.h` supplies field definitions. Downstream dependencies are AMDGPU SDMA engine setup, debugfs/register dumps, firmware load code, VM fault and UTCL1 diagnostics, power management, and queue/ring scheduling code.

## Integration Points, Risks, and Test Signals
Integration risks are high because an incorrect offset can write a valid but wrong register. `VF_ENABLE` at `0x000a`, `PHASE2_QUANTUM` at `0x004f`, and the PAGE block from `0x00e0` through `0x0129` are present in 4.0 and absent from the 4.1 offset header in this subset, so cross-version include mistakes are especially dangerous. Test signals include MMIO traces showing firmware writes to `UCODE_*`, successful ring initialization at the expected GFX/PAGE/RLC offsets, correct doorbell/rptr/wptr behavior, clean GPU reset and resume, and register dumps whose addresses match the SDMA 4.0 hardware specification.
