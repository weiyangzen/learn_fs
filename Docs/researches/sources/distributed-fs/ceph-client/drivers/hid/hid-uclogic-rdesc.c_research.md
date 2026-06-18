# sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-rdesc.c

Purpose: stores static fixed HID report descriptors and parameterized descriptor templates for UC-Logic-family tablets, and implements the template substitution engine used by parameter discovery.

Important APIs, types, and functions: exports many `uclogic_rdesc_*_arr` and matching `*_size` symbols for WP4030U/WP5540U/WP8060U/WP1062/PF1209/TWHL850/TWHA60 fixed descriptors, v1/v2 pen templates, v1/v2 frame button/touch/dial descriptors, UGEE v2 probe data and pen/frame/battery templates, Ugee EX07/G5 frame descriptors, XP-PEN Deco01 and Artist 22R/24 Pro descriptors, and `uclogic_rdesc_template_apply()`. The template function copies a template and replaces pen placeholder heads (`0xFE,0xED,0x1D,index`) with little-endian 32-bit parameter values, or frame button placeholder heads (`0xFE,0xED,index`) with a HID Usage Maximum item.

Control flow: most of the file is declarative byte arrays. Runtime work happens only in `uclogic_rdesc_template_apply()`, which scans linearly through the copied descriptor, checks placeholder heads and index bounds, writes substituted values, and returns the kmalloc copy.

State and persistence: static descriptor arrays are immutable. Template application allocates a new descriptor owned by the caller. No persistent state.

Dependencies and integration: consumed by `hid-uclogic-params.c` and declared in `hid-uclogic-rdesc.h`. Uses allocation, unaligned writes, endian helpers, and KUnit visibility export.

Risks: descriptor bytes are dense and hardware-specific; mistakes can break HID parsing or userspace axis/button semantics. Template substitution preserves template size, so placeholders must be designed to occupy exactly the final item width. Array/size symbol consistency is critical.

Test signals: includes `hid-uclogic-rdesc-test.c` under HID KUnit. Hardware validation should cover descriptor parsing and input reports for each static/template descriptor family.
