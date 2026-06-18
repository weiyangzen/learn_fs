# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pciercx-defs.h

## Purpose
`cvmx-pciercx-defs.h` defines 32-bit PCIe root complex configuration register offsets and field layouts. It covers selected standard and extended PCIe capability/control/status registers for an Octeon PCIe RC block.

## Important APIs, Types, and Constants
- Address macros include `CVMX_PCIERCX_CFG001`, `CFG006`, `CFG008`-`CFG011`, `CFG030`-`CFG035`, `CFG040`, `CFG066`, `CFG069`, `CFG070`, `CFG075`, `CFG448`, `CFG452`, `CFG455`, and `CFG515`. The `block_id` parameter is accepted but not used in these macros, implying callers apply block selection elsewhere.
- All exported register views are `union cvmx_pciercx_cfg*` with a raw `uint32_t u32` and an `s` struct using `__BITFIELD_FIELD` from `<uapi/asm/bitfield.h>`.
- `cfg001` maps PCI command/status-style bits such as parity/system/master-abort status, interrupt disable, bus-master enable, memory-space enable, and I/O-space enable.
- Bridge/window registers define primary/secondary/subordinate bus numbers and memory/prefetchable memory base/limit fields.
- PCIe capability/device/link/status registers expose max payload/read request size, error enables, relaxed ordering, link width/speed, ASPM, link training, hotplug/error indications, and advanced error reporting controls.
- Extended/private registers include retry timeout values, link management/error controls, filter masks, skip interval, loopback/equalization/training controls, and number of fast training sequences.

## Control Flow
The header has no functions. Consumers compute a config register offset, read a 32-bit value from the PCIe RC config access mechanism, manipulate `s` fields, and write the new `u32` back.

## State and Persistence Behavior
The modeled state lives in PCIe root-complex config registers. It controls bridge windows, bus numbering, link training, error reporting, hotplug/status signaling, and PCIe transaction attributes. Values persist until reset or reconfiguration and can affect the whole PCIe fabric under the root complex.

## Dependencies and Integration Points
- Depends on `<uapi/asm/bitfield.h>` for portable endian-aware `__BITFIELD_FIELD` declarations instead of open-coded `__BIG_ENDIAN_BITFIELD` branches.
- Intended for PCIe root-complex configuration code and any low-level Octeon PCIe bring-up path that accesses RC config space.
- Complements NPEI/PCIe-side registers in `cvmx-npei-defs.h`; the former controls NPEI packet/DMA/MSI state while this file controls PCIe RC config/link behavior.

## Risks
- The unused `block_id` argument can mislead callers into believing it selects a PCIe port; incorrect block selection must be handled by the surrounding config accessor.
- PCIe link control/status fields are timing-sensitive. Writing link disable/retrain, ASPM, payload size, read request size, or error masks at the wrong time can break enumeration or degrade performance.
- AER/status bits often have write-one-to-clear behavior in PCIe config space; raw writes can accidentally clear diagnostics.
- Since the file uses 32-bit unions, mixing it with 64-bit CSR accessors can access the wrong width.

## Test Signals
- PCIe enumeration and link-state tests should verify bus numbering, memory windows, link width/speed, payload/read request settings, and error mask behavior.
- Error-injection or link-down tests should confirm that status bits and interrupts map to expected `cfg030`/`cfg032`/`cfg034`/`cfg070` fields.
- Runtime regressions appear as PCIe link training failures, endpoint enumeration gaps, incorrect bridge windows, or unexpected AER/hotplug status clearing.
