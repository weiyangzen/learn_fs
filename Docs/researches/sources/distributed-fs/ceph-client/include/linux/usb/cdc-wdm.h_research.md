<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/cdc-wdm.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/cdc-wdm.h

Purpose: declares the registration hook for the USB CDC WDM subdriver used by modem/WWAN management interfaces.

Important APIs and types: `usb_cdc_wdm_register()` binds a CDC WDM subdriver to a USB interface and endpoint descriptor, with buffer size, WWAN port type, and optional power-management callback.

Control flow: parent composite drivers call this helper after parsing a suitable management endpoint; the WDM layer creates the character/WWAN management port and uses `manage_power()` to coordinate interface power state.

State and persistence: runtime state is owned by the CDC WDM driver and returned `struct usb_driver`; this header owns none.

Dependencies and integration points: depends on WWAN port types, CDC WDM UAPI, USB interface and endpoint descriptors. It integrates MBIM/QMI-like modem drivers with the shared CDC WDM character device implementation.

Risks and test signals: risks include endpoint mismatch, buffer too small for management messages, power callback races, and teardown ordering with parent drivers. Test modem probe/remove, suspend/resume, management reads/writes, and parent-driver unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/cdc-wdm.h -->
