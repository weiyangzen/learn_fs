# sources/distributed-fs/ceph-client/drivers/media/pci/intel/Kconfig

Purpose: is the top-level Intel media PCI Kconfig menu fragment. It sources IPU3, IPU6, and IVSC submenus and declares the `IPU_BRIDGE` helper library.

Important APIs/types/functions: `IPU_BRIDGE` is tristate, depends on ACPI and I2C, and documents support for Windows-shipped systems needing synthetic firmware nodes for IPU camera sensors.

Control flow: Kconfig inclusion controls which Intel IPU drivers and bridge helper are available.

State and persistence: no runtime state.

Dependencies/integration: connects `ipu-bridge.c` to consumers such as ipu3-cio2 and atomisp, while sourcing additional Intel media driver families.

Risks and test signals: bridge must be selectable for drivers that call its exported symbols. Test Kconfig combinations where IPU3 is built with bridge built-in/module/off and where ACPI or I2C are unavailable.
