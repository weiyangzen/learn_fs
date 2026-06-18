# sources/distributed-fs/ceph-client/include/media/v4l2-fwnode.h

Purpose: declares firmware-node parsing helpers for V4L2 endpoints, media bus configuration, connector descriptions, endpoint links, and camera device properties such as orientation and rotation.

Important APIs/types: `struct v4l2_fwnode_endpoint` combines a generic `fwnode_endpoint`, `enum v4l2_mbus_type`, bus-specific parallel/CSI-1/CSI-2 config, and optional link-frequency array. `V4L2_FWNODE_PROPERTY_UNSET` marks absent properties. `enum v4l2_fwnode_orientation` and `struct v4l2_fwnode_device_properties` describe camera placement and rotation. `struct v4l2_fwnode_link` holds local/remote endpoint nodes and port/id numbers. Connector types and structures model analog composite/S-video connectors and their links.

Control flow: drivers zero or initialize endpoint structs, call `v4l2_fwnode_endpoint_parse()` for fixed-size properties or `v4l2_fwnode_endpoint_alloc_parse()` when `link-frequencies` are needed, validate returned bus type, then call `v4l2_fwnode_endpoint_free()` for allocated fields. Link parsers take fwnode references and require `v4l2_fwnode_put_link()`. Connector parse/add-link paths allocate labels/link nodes and require `v4l2_fwnode_connector_free()`. Device properties are parsed with `v4l2_fwnode_device_parse()`.

State and persistence: parsed data is caller-owned. Alloc-parse can allocate `link_frequencies`; connector parsing can allocate labels and link entries; link parsing takes references to local and remote nodes. Helpers guarantee endpoint state is not changed on parse failure.

Dependencies and integration: includes Linux fwnode/list/types/errno and `v4l2-mediabus.h`. It feeds async subdevice binding, media graph creation, bus configuration, camera sensor orientation controls through `v4l2_ctrl_new_fwnode_properties()`, and connector-aware analog video pipelines.

Risks: new bindings must not rely on deprecated bus-type guessing; callers must initialize structs before parsing and free allocated resources; mismatched explicit bus type returns `-ENXIO`; NULL fwnode can return `-EPROBE_DEFER`; and missing reference cleanup leaks fwnode handles.

Test signals: parse parallel, BT.656, CSI-1/CCP2, CSI-2 D-PHY and C-PHY endpoints; verify explicit bus mismatch; parse/free link frequencies; parse connector labels and multiple links; check first/last link macros; validate orientation/rotation property ranges; and confirm no state mutation on failures.
