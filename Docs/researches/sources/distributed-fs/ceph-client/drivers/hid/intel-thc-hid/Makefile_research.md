# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/Makefile

## Purpose
`Makefile` maps the THC Kconfig symbols to kernel objects. It builds the shared Intel THC core and the QuickSPI/QuickI2C transport modules with their PCI, HID, and protocol components.

## Important APIs, types, and functions
`obj-$(CONFIG_INTEL_THC_HID)` builds `intel-thc.o` from `intel-thc-dev.o`, `intel-thc-dma.o`, and `intel-thc-wot.o`. `obj-$(CONFIG_INTEL_QUICKSPI)` builds `intel-quickspi.o` from `pci-quickspi.o`, `quickspi-hid.o`, and `quickspi-protocol.o`. `obj-$(CONFIG_INTEL_QUICKI2C)` builds `intel-quicki2c.o` from `pci-quicki2c.o`, `quicki2c-hid.o`, and `quicki2c-protocol.o`. `ccflags-y` adds the shared `intel-thc` include path.

## Control flow and integration points
There is no runtime control flow. The Makefile composes module boundaries: QuickSPI and QuickI2C import symbols from the core THC module namespace, and the include path lets transport code include `intel-thc-dev.h`, `intel-thc-dma.h`, and related headers.

## State and persistence behavior
The file affects build artifacts only. It does not define runtime state.

## Dependencies
It depends on Kconfig symbols and on source file layout under `intel-thc`, `intel-quickspi`, and `intel-quicki2c`. It also assumes the exported THC helper namespace is available to the transport modules.

## Risks and edge cases
Object list drift can omit a required protocol or HID file from a module. Include-path changes can break local header resolution. If the core is built-in and transports are modules, namespace imports and symbol exports must remain valid.

## Test signals
Build each symbol as `y`, `m`, and `n`; inspect module dependencies with `modinfo`; and run link checks for namespace imports and unresolved symbols.
