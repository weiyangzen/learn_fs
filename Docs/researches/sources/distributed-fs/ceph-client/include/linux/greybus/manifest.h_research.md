<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/manifest.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/manifest.h

Purpose: This header declares Greybus manifest parsing entry points.

Important APIs/types/functions: `gb_manifest_parse()` parses a raw manifest buffer of known size for a given interface, and `gb_manifest_free()` releases parsed manifest descriptor state from the interface.

Control flow, state, and persistence: Control retrieves raw bytes, `gb_manifest_parse()` validates/deserializes them into interface descriptors, bundle devices, and CPort descriptors, and `gb_manifest_free()` tears down descriptor lists on interface cleanup or parse failure.

Dependencies/integration: It consumes packed definitions from `greybus_manifest.h` and mutates `struct gb_interface` state from `interface.h`.

Risks and test signals: Parser correctness depends on size validation, descriptor ordering rules, string handling, and cleanup after partial parse. Tests should cover malformed sizes, duplicate descriptors, unknown descriptor types, missing interface descriptor, invalid bundle/CPort references, and repeated parse/free cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/manifest.h -->
