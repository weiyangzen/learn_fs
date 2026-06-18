# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/Kconfig

## Purpose
`Kconfig` declares the Intel Touch Host Controller HID driver menu and the selectable core THC, QuickSPI, and QuickI2C modules. It controls whether the PCI/ACPI THC hardware support and HID-over-SPI/I2C transport drivers are built.

## Important APIs, types, and functions
`CONFIG_INTEL_THC_HID` is a tristate core option depending on `X86_64`, `PCI`, and `ACPI`, and selecting `SGL_ALLOC`. `CONFIG_INTEL_QUICKSPI` and `CONFIG_INTEL_QUICKI2C` are tristate child options that depend on `INTEL_THC_HID`.

## Control flow and integration points
There is no runtime control flow. These symbols feed the kernel build system and gate compilation of `intel-thc.o`, `intel-quickspi.o`, and `intel-quicki2c.o` in the adjacent Makefile. The help text documents THC as a PCH IP block with SPI, I2C, and DMA/sequencer components.

## State and persistence behavior
Kconfig choices persist only in the kernel build configuration. They determine module availability, not runtime device state.

## Dependencies
The menu depends on x86_64 and PCI. The core depends on ACPI and selects scatter-gather allocation support. QuickSPI/QuickI2C depend on the core THC support and the source files' external HID-over-SPI/I2C and Intel THC helper APIs.

## Risks and edge cases
Incorrect dependencies can allow impossible builds, such as transport modules without ACPI/PCI THC support. Selecting `SGL_ALLOC` in the core is needed by THC DMA helpers; removing it could break link or runtime allocation paths. Help text and symbol names must stay aligned with Makefile targets.

## Test signals
Run config/build matrix checks for built-in, module, and disabled combinations; verify transport options disappear when `INTEL_THC_HID` is disabled; and build all three modules under `allmodconfig` and minimal x86_64 PCI/ACPI configs.
