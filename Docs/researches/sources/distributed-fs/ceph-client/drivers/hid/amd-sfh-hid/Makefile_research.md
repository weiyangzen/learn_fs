# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/Makefile

## Purpose

This Makefile builds the AMD SFH HID module from the transport, PCI, descriptor, and SFH 1.1 source files.

## Important APIs, Types, and Functions

`obj-$(CONFIG_AMD_SFH_HID) += amd_sfh.o` defines the module/composite target. `amd_sfh-objs` includes `amd_sfh_hid.o`, `amd_sfh_client.o`, `amd_sfh_pcie.o`, `hid_descriptor/amd_sfh_hid_desc.o`, and the SFH 1.1 files `amd_sfh_init.o`, `amd_sfh_interface.o`, and `amd_sfh_desc.o`. `ccflags-y += -I $(src)/` makes local headers visible to subdirectory files.

## Control Flow

Kbuild links the listed objects into `amd_sfh.o` whenever `CONFIG_AMD_SFH_HID` is enabled. The module entry point comes from `module_pci_driver()` in `amd_sfh_pcie.c`.

## State and Persistence Behavior

The file has no runtime state, but the object list defines which code paths are always present in the driver. SFH 1.1 support is not optional once the driver is built.

## Dependencies and Integration Points

It depends on the parent HID Makefile routing and the Kconfig symbol. The include path supports headers referenced with local subdirectory paths.

## Risks and Test Signals

The key risk is omitting an object that supplies callbacks installed through `amd_mp2_ops`, such as descriptor operations or SFH 1.1 initialization. Build tests should verify both built-in and module configurations, plus clean builds that catch missing generated include paths.
