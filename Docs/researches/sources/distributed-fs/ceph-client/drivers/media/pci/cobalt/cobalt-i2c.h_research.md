<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-i2c.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-i2c.h

Purpose: Declares Cobalt I2C adapter lifecycle functions.

Important APIs/types: `cobalt_i2c_init(struct cobalt *cobalt)` registers all hardware I2C adapters. `cobalt_i2c_exit(struct cobalt *cobalt)` unregisters them.

Control flow: Called during Cobalt PCI probe before subdevice creation and during remove/error unwind after subdevice/node cleanup.

State/persistence: No header state. The implementation initializes `cobalt->i2c_adap[]` and `cobalt->i2c_data[]`.

Dependencies/integration: Interfaces the Cobalt core with Linux I2C and downstream ADV subdevice probes.

Risks: The header exposes all-or-nothing init/exit even though `ignore_err` can leave some adapters absent.

Test signals: Compile/link checks and subdevice probe paths requiring the adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-i2c.h -->
