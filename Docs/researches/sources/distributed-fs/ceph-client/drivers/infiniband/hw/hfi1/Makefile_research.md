<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/Makefile

## Purpose

This Makefile defines the object composition for the HFI1 kernel module or built-in object. It gathers the many HFI1 implementation units under `hfi1.o` when `CONFIG_INFINIBAND_HFI1` is enabled.

## Important APIs, types, and functions

The key build variable is `obj-$(CONFIG_INFINIBAND_HFI1) += hfi1.o`. The `hfi1-y` list includes core files such as `affinity.o`, `aspm.o`, `chip.o`, `device.o`, `driver.o`, interrupt and PCIe support, receive and transmit paths, IPOIB integration, MAD handling, SDMA, TID RDMA, user contexts, verbs, and QP/RC/UC/UD logic. Conditional additions include `debugfs.o` under `CONFIG_DEBUG_FS` and `fault.o` only when both fault-injection Kconfig symbols and debugfs support are enabled. `CFLAGS_trace.o = -I$(src)` gives generated trace code access to local headers, and `MVERSION` can define `HFI_DRIVER_VERSION_BASE` for `driver.o`.

## Control Flow

During kbuild, the HFI1 Kconfig symbol selects whether this directory emits `hfi1.o`. Kbuild compiles every object in `hfi1-y`, optionally appends debugfs/fault objects, applies per-object CFLAGS, and links them into the final HFI1 module or built-in object.

## State and Persistence

There is no runtime state in the Makefile. Its persistent effect is the build graph: which source files are compiled and which preprocessor flags are visible to specific objects.

## Dependencies and Integration Points

This file integrates HFI1 with Linux kbuild, debugfs, fault injection, tracing include paths, and external module version injection through `MVERSION`. It must stay aligned with source filenames and with Kconfig symbols that guard optional code.

## Risks

Missing an object from `hfi1-y` can compile cleanly only until a referenced symbol is needed, or worse can drop a feature path from the module. Adding optional code without matching Kconfig guards can break minimal builds. `CFLAGS_driver.o` quoting is sensitive because it feeds a C string macro. Trace include paths must remain correct for generated trace headers.

## Test Signals

Build `CONFIG_INFINIBAND_HFI1` as both module and built-in, with and without `CONFIG_DEBUG_FS`, `CONFIG_FAULT_INJECTION`, and `CONFIG_FAULT_INJECTION_DEBUG_FS`. Check that `modinfo hfi1` or built-in version strings reflect `MVERSION` when supplied and that trace compilation still finds local headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/Makefile -->
