# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_osdep.h

## Purpose
`iavf_osdep.h` is the Linux OS abstraction header for shared iavf code. It provides type/header dependencies, MMIO access macros, memory wrapper structs, an allocation macro, and a debug macro expected by shared AdminQ and hardware helper code.

## Important APIs, Types, And Functions
The header includes Linux networking, PCI, TCP, VLAN, Ethernet, type, and non-atomic 64-bit I/O support. `wr32`, `rd32`, `wr64`, and `rd64` perform MMIO access relative to `struct iavf_hw::hw_addr`. `iavf_flush` reads `IAVF_VFGEN_RSTAT` to force posted MMIO writes to complete.

`struct iavf_dma_mem` records a coherent DMA allocation as virtual address, physical/DMA address, and size. `struct iavf_virt_mem` records a normal zeroed allocation as virtual address and size. `iavf_allocate_dma_mem` maps the shared-code signature to the Linux implementation `iavf_allocate_dma_mem_d`. `iavf_debug` gates `pr_info` output on `hw->debug_mask` and prefixes messages with PCI bus/device/function.

## Control Flow
This header has no standalone control loop. Its macros are invoked by shared AdminQ and main-driver code during hardware register access, queue setup, RSS programming, AdminQ setup/shutdown, and diagnostics. The memory structs are filled and freed by implementations in `iavf_main.c`.

## State And Persistence Behavior
No persistent state is stored by this header. It defines the shape of memory tracking objects and the register access model used to mutate hardware state. The debug macro reads `debug_mask` from the hardware struct; the memory wrappers carry allocation metadata until freed.

## Dependencies And Integration Points
It depends on `IAVF_VFGEN_RSTAT` being visible from register headers through include order. It integrates with `iavf_prototype.h` and AdminQ/shared code by presenting the OS-dependent names expected by Intel shared driver sources. The actual allocation/free functions live in `iavf_main.c`.

## Risks
MMIO macros assume `hw_addr` is valid and mapped; use after remove/unmap would be fatal. The 64-bit I/O include selects low-first non-atomic helpers for 32-bit kernels, so ordering assumptions must match hardware expectations. `iavf_allocate_dma_mem` ignores one shared-code parameter by design; changing shared signatures could silently break the macro. `iavf_debug` logs with `pr_info`, so broad debug masks can produce high log volume.

## Test Signals
Compile coverage across 32-bit and 64-bit configurations, AdminQ DMA allocation/free tests, reset/probe/remove register access under fault injection, and debug-mask toggling through ethtool message levels are the main signals.
