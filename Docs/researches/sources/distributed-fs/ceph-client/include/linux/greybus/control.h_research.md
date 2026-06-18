<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/control.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/control.h

Purpose: This header declares the Greybus control-protocol object for an interface. Control handles version negotiation, manifest retrieval, CPort connected/disconnected notifications, mode switching, bundle PM, and interface PM preparation.

Important APIs/types/functions: `struct gb_control` embeds a device, points to its interface and control connection, stores protocol version, capability booleans for bundle activation/version, and vendor/product strings. Lifecycle APIs are create, enable/disable, suspend/resume, add/del, get/put. Operation helpers cover bundle version discovery, connected/disconnected/disconnecting notifications, mode switch, manifest size/data retrieval, bundle suspend/resume/deactivate/activate, and interface suspend/deactivate/hibernate-abort preparations.

Control flow, state, and persistence: Interface activation creates/enables control, negotiates versions, fetches manifest data, and later uses control operations to notify CPort and power-management changes. Vendor/product strings persist as parsed interface metadata.

Dependencies/integration: It sits between `gb_interface`, `gb_connection`, Greybus control wire structs in `greybus_protocols.h`, runtime PM, and manifest parsing.

Risks and test signals: Version/capability checks must gate newer operations such as bundle activate/version. Manifest size must be trusted only after bounds checks. Tests should cover older peer capabilities, manifest size/data failures, connected/disconnected sequencing, suspend/resume status handling, mode switch, and reference cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/control.h -->
