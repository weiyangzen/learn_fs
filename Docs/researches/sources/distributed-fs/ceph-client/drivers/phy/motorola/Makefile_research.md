# sources/distributed-fs/ceph-client/drivers/phy/motorola/Makefile

Purpose: This Makefile maps Motorola PHY Kconfig symbols to their driver objects.

Important APIs/types/functions: It has two object rules: `obj-$(CONFIG_PHY_CPCAP_USB) += phy-cpcap-usb.o` and `obj-$(CONFIG_PHY_MAPPHONE_MDM6600) += phy-mapphone-mdm6600.o`.

Control flow: Kbuild expands each `obj-*` line based on the resolved tristate symbol. Built-in symbols put objects into the built-in archive; module symbols produce loadable modules.

State and persistence: No runtime state exists. The persistent input is the kernel configuration, and the output is build-system membership.

Dependencies and integration points: It depends on the surrounding `drivers/phy` Kbuild hierarchy including the Motorola directory. It integrates directly with the two Kconfig entries in the same directory.

Risks: A symbol/object mismatch would silently omit a driver or break builds. Because both entries are one-object drivers, rename churn needs synchronized updates in this file, Kconfig help text, module aliases, and source filenames.

Test signals: A targeted build with `CONFIG_PHY_CPCAP_USB=m` or `CONFIG_PHY_MAPPHONE_MDM6600=m` should emit the corresponding `.ko`; built-in configs should include the object in the kernel image.
