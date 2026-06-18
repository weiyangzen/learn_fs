# sources/distributed-fs/ceph-client/include/linux/comedi/comedi_usb.h

Purpose: This header provides Comedi helper APIs for USB-backed Comedi drivers.

Important APIs/types/functions: It declares `comedi_to_usb_interface`, `comedi_to_usb_dev`, `comedi_usb_auto_config`, `comedi_usb_auto_unconfig`, `comedi_usb_driver_register`, `comedi_usb_driver_unregister`, and macro `module_comedi_usb_driver`.

Control flow: USB probe calls auto-config with the interface, Comedi driver, and context. Disconnect calls auto-unconfig. Register/unregister helpers bind Comedi driver lifecycle to the USB driver lifecycle.

State and persistence behavior: State lives in USB interface/device references and the attached Comedi device. Auto-unconfig detaches Comedi state during disconnect.

Dependencies and integration points: It includes `<linux/usb.h>` and `comedidev.h`, integrating USB core probe/disconnect with Comedi low-level drivers.

Risks: USB disconnect can race with open Comedi users and async commands. Drivers must stop URBs and detach cleanly. Device/interface conversion helpers depend on correct `hw_dev` association.

Test signals: USB plug/unplug, active acquisition disconnect, module unload, URB cleanup, Comedi minor removal, and runtime PM tests are relevant.
