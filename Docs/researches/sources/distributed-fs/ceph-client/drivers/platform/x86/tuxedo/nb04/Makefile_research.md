# sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/nb04/Makefile

Purpose: Kbuild recipe for the TUXEDO NB04 WMI AB module. It composes `tuxedo_nb04_wmi_ab.o` from `wmi_ab.o` and `wmi_util.o`.

Important APIs and control flow: no runtime APIs. `obj-$(CONFIG_TUXEDO_NB04_WMI_AB)` gates the composite object, while `tuxedo_nb04_wmi_ab-y` lists the constituent objects.

State and dependencies: build state is entirely driven by `CONFIG_TUXEDO_NB04_WMI_AB`. The composition ties the virtual HID LampArray implementation to the WMI method helper layer.

Risks and test signals: omitting `wmi_util.o` would leave unresolved WMI wrapper symbols, while a wrong composite name would break the documented module name. Test by building the option as a module and checking symbol resolution with `modpost`.
