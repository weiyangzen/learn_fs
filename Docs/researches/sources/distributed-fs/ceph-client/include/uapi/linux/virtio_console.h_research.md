# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_console.h

Purpose: defines the virtio console and virtio serial port device ABI.

Important APIs/types/functions: feature bits include console size, multiport support, and emergency write support. `virtio_console_config` exposes columns, rows, max port count, and emergency write register. `virtio_console_control` carries per-port control messages with port ID, event, and value. Control events include device ready, port add/remove/ready, console port designation, resize, port open, and port name. `VIRTIO_CONSOLE_BAD_ID` marks an invalid port ID.

Control flow: after feature negotiation, the guest reads size and port capacity, exchanges control messages with the host over control queues, creates/removes ports, marks ports ready/open, handles resize events, and writes emergency characters through `emerg_wr` when supported.

State and persistence: runtime state includes screen geometry, port list, per-port open/ready flags, names, console designation, and emergency write register content. Config fields are device state; data streams for ports are handled by virtqueues outside this header.

Dependencies and integration: includes Linux types and virtio type/id/config headers. It integrates with guest console/tty/hvc layers, virtio-serial ports, host VMM chardevs, and emergency console paths.

Risks: multiport control events are asynchronous and must be ordered per port. `emerg_wr` is a config register, not a normal data queue. Incorrect port ID handling can route console data to the wrong chardev. Geometry fields are feature-gated by `VIRTIO_CONSOLE_F_SIZE`.

Test signals: boot console tests, multiport add/remove/open/name tests, resize event tests, emergency write tests, and host/guest virtio-serial integration tests.
