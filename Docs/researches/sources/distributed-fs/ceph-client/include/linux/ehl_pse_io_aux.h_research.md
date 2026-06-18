# sources/distributed-fs/ceph-client/include/linux/ehl_pse_io_aux.h

Purpose: small auxiliary-device contract for Intel Elkhart Lake PSE I/O subdevices.

Important APIs/types/functions: device name constants `EHL_PSE_IO_NAME`, `EHL_PSE_GPIO_NAME`, `EHL_PSE_TIO_NAME`, and `struct ehl_pse_io_data` carrying a memory resource plus IRQ.

Control flow: parent PSE I/O driver creates auxiliary devices identified by these names and passes `ehl_pse_io_data`; child drivers bind by name and consume the resource/IRQ for GPIO or PPS TIO functionality.

State/persistence: no persistent state. Runtime state is resource assignment from firmware/platform enumeration.

Dependencies/integration: depends on `struct resource` from `linux/ioport.h`, the auxiliary bus model, Intel PSE platform drivers, GPIO, and time/PPS related child drivers.

Risks/test signals: risks are mismatched child names, overlapping memory resources, invalid IRQ propagation, and ABI drift between parent and child drivers. Test auxiliary-device registration, probe/remove, resource start/size, IRQ handling, and disabled child-driver cases.
