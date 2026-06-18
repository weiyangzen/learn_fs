# sources/distributed-fs/ceph-client/lib/pldmfw/Makefile

## Purpose
Builds the PLDM firmware update helper object when `CONFIG_PLDMFW` is selected.

## APIs, Control Flow, and State
The single build rule is `obj-$(CONFIG_PLDMFW) += pldmfw.o`. There is no runtime code or state; control flow is Kbuild conditional inclusion based on kernel configuration.

## Dependencies, Integration, Risks, and Tests
Depends on the parent Kbuild including this directory and the `CONFIG_PLDMFW` symbol being defined by kernel configuration. Risks include missing Kconfig selection causing drivers that need PLDM firmware flashing to fail link, or stale object naming if source files change. Test signals are allmodconfig/build coverage, driver configurations selecting `PLDMFW`, and link checks for `pldmfw_flash_image()`.
