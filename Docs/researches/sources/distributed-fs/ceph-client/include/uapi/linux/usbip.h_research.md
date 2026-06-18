# sources/distributed-fs/ceph-client/include/uapi/linux/usbip.h

Purpose: Defines USB/IP userspace-visible device status and URB transfer flag constants.

Important APIs/types/functions: `enum usbip_device_status` identifies available, used, shared, and error/unknown statuses. URB flags include short-not-ok, isochronous ASAP, DMA mapping modes, zero packet, no interrupt, free buffer, direction mask, setup mapping, combined SG, aligned temporary buffer, and local mapping flags.

Control flow: USB/IP tooling and kernel code use status values to report exported/imported device state and transfer flags to serialize or reconstruct URB behavior across the network.

State and persistence behavior: Status is runtime export/import state. URB flags are per-transfer metadata.

Dependencies and integration points: Integrates with usbip host/vhci drivers, USB core URB semantics, and usbip userspace utilities.

Risks: Direction and DMA/local mapping flags must be translated safely across machines where DMA addresses are not meaningful. Status races occur when devices are attached/detached remotely.

Test signals: Export/import devices with usbip, verify status transitions, transfer bulk/control/iso URBs, disconnect during transfer, and compare flag preservation across host/vhci boundary.
