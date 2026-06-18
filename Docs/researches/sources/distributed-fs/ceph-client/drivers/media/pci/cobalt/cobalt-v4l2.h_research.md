<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-v4l2.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-v4l2.h

Purpose: Declares Cobalt V4L2 node lifecycle functions.

Important APIs/types: `cobalt_nodes_register(struct cobalt *cobalt)` initializes and registers video and ALSA stream nodes. `cobalt_nodes_unregister(struct cobalt *cobalt)` unregisters video devices and exits ALSA devices.

Control flow: Called from PCI probe after hardware/subdevices are initialized and from remove/error paths before lower-level resources are freed.

State/persistence: No header state. Functions initialize or release state embedded in `struct cobalt_stream`.

Dependencies/integration: Bridges the main driver lifecycle with the V4L2/ALSA stream layer.

Risks: Lifecycle callers must preserve ordering: subdevices and PCI resources must exist during register, and active users must be quiesced before unregister completes.

Test signals: Compile/link checks and Cobalt probe/remove node creation/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-v4l2.h -->
