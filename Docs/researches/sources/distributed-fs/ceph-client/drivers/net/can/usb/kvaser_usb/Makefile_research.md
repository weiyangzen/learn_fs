# sources/distributed-fs/ceph-client/drivers/net/can/usb/kvaser_usb/Makefile

Purpose: defines the Kbuild composition for the Kvaser USB CAN driver module. It builds `kvaser_usb.o` when `CONFIG_CAN_KVASER_USB` is enabled.

Important APIs/types/functions: no C APIs are declared here. The build variables are `obj-$(CONFIG_CAN_KVASER_USB) += kvaser_usb.o` and `kvaser_usb-y = kvaser_usb_core.o kvaser_usb_devlink.o kvaser_usb_leaf.o kvaser_usb_hydra.o`.

Control flow: Kbuild compiles the common core, devlink support, Leaf/Usbcan protocol implementation, and Hydra protocol implementation into one module. Product ID dispatch in `kvaser_usb_core.c` selects the appropriate ops table at runtime.

State and persistence behavior: no runtime state or persistence. Its only effect is compile-time object inclusion.

Dependencies/integration points: integrates with the kernel CAN USB driver menu through `CONFIG_CAN_KVASER_USB`. The object list is an important integration point because `kvaser_usb_core.c` references `kvaser_usb_leaf_dev_ops`, `kvaser_usb_hydra_dev_ops`, and `kvaser_usb_devlink_ops` defined in the companion objects.

Risks: omitting one object would cause link failures or remove support for a Kvaser device family. Adding a new Kvaser protocol family requires updating this file as well as the core ID/ops mapping.

Test signals: build coverage with `CONFIG_CAN_KVASER_USB=m` or `=y` is the main signal; runtime tests should confirm both Leaf/Usbcan and Hydra devices still bind from the single module.
