<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mei_aux.h -->
# sources/distributed-fs/ceph-client/include/linux/mei_aux.h

## Purpose
This header defines the auxiliary-bus wrapper used to expose Intel MEI-related auxiliary devices.

## Important APIs, types, and functions
`struct mei_aux_device` embeds `struct auxiliary_device` and carries IRQ number, MMIO BAR resource, extended operational memory resource, and `slow_firmware` timeout hint. `auxiliary_dev_to_mei_aux_dev()` converts from auxiliary device to wrapper.

## Control flow
MEI parent code creates an auxiliary device, fills resources and flags, and registers it on the auxiliary bus. Auxiliary drivers recover the wrapper with the conversion macro and use the IRQ/resource metadata during probe.

## State and persistence
State is device-model runtime metadata and resource descriptors. The header stores no global state.

## Dependencies and integration points
It depends on the Linux auxiliary bus and resource structures. It integrates MEI with auxiliary consumers such as graphics/PXP-related devices.

## Risks and test signals
Risks include resource lifetime errors, slow firmware timeouts not being honored, invalid IRQs, and incorrect container conversion. Test auxiliary probe/remove, resource mapping, IRQ setup, and slow-firmware timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mei_aux.h -->
