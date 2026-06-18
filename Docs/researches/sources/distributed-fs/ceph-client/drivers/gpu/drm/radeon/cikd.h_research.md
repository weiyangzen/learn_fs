# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cikd.h

## Purpose
`cikd.h` is the main CIK ASIC hardware definition header for the Radeon driver. It maps large portions of CIK register space and packet encodings: power management, thermal/fan control, PCIe, SMC, memory controller, VM, command processor, RLC, SDMA, UVD/VCE media blocks, ATC, interrupts, and PM4/SDMA packet formats.

## Important APIs, types, and definitions
- Golden/config constants: `BONAIRE_GB_ADDR_CONFIG_GOLDEN`, `HAWAII_GB_ADDR_CONFIG_GOLDEN`, render-backend bitmap widths, and DIDT/SMC/DPM register fields.
- Power, thermal, fan, clock, and PCIe definitions: `GENERAL_PWRMGT`, `CG_THERMAL_*`, `CG_FDO_*`, SPLL controls, and PCIe link-control fields.
- Core register definitions: `SRBM_GFX_CNTL`, `SRBM_STATUS`, `SRBM_SOFT_RESET`, VM L2/context registers, memory-controller aperture/timing registers, GRBM indexing, scratch registers, CP queue/HQD registers, and RLC power-gating/safe-mode fields.
- PM4 packet helpers: `PACKET0`, `PACKET2`, `PACKET3`, `PACKET3_COMPUTE`, packet decoders, and many `PACKET3_*` opcodes/field helpers.
- SDMA definitions: two-engine offset constants, SDMA microcode/control/ring/IB registers, `SDMA_PACKET`, and SDMA opcodes for copy, write, IB, fence, trap, semaphore, poll, constant fill, PTE/PDE generation, timestamp, and SRBM writes.
- UVD/VCE/ATC/IH definitions support media engines and address-translation/PASID plumbing.

## Control flow and integration points
The file contains no functions, but it controls how many CIK driver files construct MMIO accesses and command packets. `cik_sdma.c` directly uses SDMA register and opcode definitions from this header. Command processor setup, VM management, power management, reset, media, and interrupt code use the broader register map and packet helpers.

## State and persistence behavior
All persistent state represented here is hardware state. The macros encode addresses and bitfields for registers whose values persist across command submissions and often across runtime power transitions until explicitly reset. Packet macros create command-stream words that alter GPU state when consumed by CP or SDMA engines.

## Dependencies and constraints
Consumers need Radeon utility macros such as `REG_SET` and standard fixed-width integer handling. Register values are ASIC-specific and must match CIK hardware documentation. Field helpers generally shift without full semantic validation, so call sites must mask, range-check, and respect block-specific ordering/alignment rules.

## Risks and test signals
Any incorrect address, bit mask, packet opcode, or shift can cause hard-to-debug hardware failures: failed init, broken power management, GPU hangs, VM faults, media engine failure, or corrupted command streams. Test signals include CIK boot/probe, modeset, suspend/resume, power-management transitions, VM fault tests, command submission, SDMA tests, UVD/VCE playback/encode, and register readback against known-good traces.
