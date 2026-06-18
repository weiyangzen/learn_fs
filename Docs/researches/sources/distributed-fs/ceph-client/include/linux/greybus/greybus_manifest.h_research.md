<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/greybus_manifest.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/greybus_manifest.h

Purpose: This header defines the packed Greybus manifest wire format. A manifest describes strings, interfaces, bundles, and CPorts exposed by a module/interface.

Important APIs/types/functions: Enums define descriptor types, protocol IDs, class IDs, and interface feature bits. Packed structs include string descriptors with flexible strings, interface descriptor, bundle descriptor, CPort descriptor, descriptor header/union, manifest header, and manifest with flexible descriptor array. Protocol IDs cover control, GPIO, I2C, UART, HID, USB, SDIO, power supply, PWM, SPI, display, camera, sensor, lights, vibrator, loopback, audio, SVC, bootrom, firmware download/management, authentication, log, raw, and vendor.

Control flow, state, and persistence: Control protocol fetches the manifest bytes, then parser code walks descriptor headers, validates sizes/types, creates interface metadata, bundles, and CPort descriptors. The manifest itself is transient input; parsed objects persist in Greybus devices/lists.

Dependencies/integration: It is consumed by `manifest.h` parser APIs and the Greybus control/interface/bundle creation path. All numeric wire fields use explicit fixed-width endian types.

Risks and test signals: Descriptor sizes and flexible arrays must be bounds-checked to avoid malformed manifest reads. String descriptors are not NUL-terminated and are padded to 4 bytes. Tests should include truncated descriptors, unknown types/protocols, duplicate bundle IDs, invalid CPort bundle references, string padding, and feature bit parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/greybus_manifest.h -->
