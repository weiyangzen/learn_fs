# sources/distributed-fs/ceph-client/include/uapi/linux/usb/g_printer.h

Purpose: Defines ioctl ABI for the USB printer gadget function.

Important APIs/types/functions: Printer gadget ioctls return device ID, get/set bidirectional mode, and soft-reset printer state. They use printer gadget-specific ioctl numbers and character-device interaction.

Control flow: Userspace opens the printer gadget device, queries identity, toggles bidirectional behavior, exchanges print data through reads/writes, and can request a soft reset.

State and persistence behavior: Bidirectional mode and soft-reset effects are runtime gadget state. Device ID is configured gadget identity.

Dependencies and integration points: Integrates with the USB gadget printer function, host USB printer class drivers, and userspace print emulators.

Risks: Host class drivers expect IEEE-1284-compatible IDs and reset behavior. Mode changes during active transfers need synchronization.

Test signals: Enumerate as printer gadget, query device ID, toggle bidirectional mode, exchange bulk data with host printer class driver, and test soft reset during idle and active transfers.
