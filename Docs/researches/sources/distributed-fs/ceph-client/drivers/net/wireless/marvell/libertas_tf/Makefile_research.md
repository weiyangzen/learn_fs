# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/Makefile

## Purpose
Defines object composition for the Libertas thinfirm kernel modules.

## Important Rules
`libertas_tf-objs := main.o cmd.o` builds the thinfirm core. `libertas_tf_usb-objs += if_usb.o` builds USB transport support. `obj-$(CONFIG_LIBERTAS_THINFIRM)` and `obj-$(CONFIG_LIBERTAS_THINFIRM_USB)` connect those modules to Kconfig symbols.

## Control Flow And State
No runtime behavior. Build state is controlled entirely by Kconfig symbol expansion.

## Dependencies And Integration
Integrates with `Kconfig` and the kernel kbuild system. The USB object depends on exported/visible thinfirm core symbols and headers.

## Risks And Test Signals
Risks include object list drift when adding source files and missing core linkage for USB. Test signals are successful builds for `libertas_tf.ko` and `libertas_tf_usb.ko`.
