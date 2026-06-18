<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-devattr.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-devattr.h

Purpose: type definitions and constants for pvrusb2 per-device descriptions.

Important APIs/types/functions: defines client IDs, routing/digital/LED/IR scheme IDs, `struct pvr2_device_client_desc`, `struct pvr2_device_client_table`, `struct pvr2_string_table`, and `struct pvr2_device_desc`. Declares `pvr2_device_table[]`.

Control flow: `pvrusb2-devattr.c` populates descriptors with these structures; the hardware layer reads the matched descriptor to choose firmware, clients, capabilities, and control schemes.

State and persistence: descriptors are static metadata. Fields include default std/tuner, firmware lists, client tables, DVB props, and numerous one-bit capability flags.

Dependencies and integration: includes USB mod_devicetable and V4L2 standard definitions; includes DVB declarations when DVB support is compiled.

Risks: bitfield flags are compact and easy to mis-set. `i2c_address_list` is documented as null-terminated bytes, requiring care because address zero is used as terminator. Routing scheme IDs are arbitrary internal integers and must match routing helper tables.

Test signals: compile descriptor users; static validation that each USB table entry points to a complete descriptor; runtime capability exposure for each product family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-devattr.h -->
