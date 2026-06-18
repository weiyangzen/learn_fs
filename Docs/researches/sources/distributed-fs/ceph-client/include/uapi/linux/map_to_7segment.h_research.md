# sources/distributed-fs/ceph-client/include/uapi/linux/map_to_7segment.h

Purpose: provides helpers and predefined ASCII conversion tables for 7-segment display drivers.

Important APIs and types: `BIT_SEG7_*` defines segment bit positions, `struct seg7_conversion_map` stores 128 byte entries, and `map_to_seg7()` maps an ASCII index to a segment mask or returns `-EINVAL` for out-of-range input. Macros include `SEG7_CONVERSION_MAP`, `SEG7_DEFAULT_MAP`, `MAP_TO_SEG7_SYSFS_FILE`, `_SEG7`, `MAP_ASCII7SEG_ALPHANUM`, and `MAP_ASCII7SEG_ALPHANUM_LC`.

Control flow: drivers instantiate a default or custom map, expose `map_seg7` when custom mapping is needed, and convert each character before programming display hardware.

State and persistence: conversion maps are in-memory driver state. Sysfs replacement changes runtime behavior only.

Dependencies and integration points: depends on `linux/errno.h`; integrates simple display drivers, front-panel devices, and sysfs-based map customization.

Risks and test signals: risks include off-by-one ASCII bounds, table initializer length drift, ambiguous upper/lower-case mapping, and sysfs writes with wrong size. Test bounds, digit/hex display, lowercase-map selection, sysfs round trip, and rendered segment masks.
