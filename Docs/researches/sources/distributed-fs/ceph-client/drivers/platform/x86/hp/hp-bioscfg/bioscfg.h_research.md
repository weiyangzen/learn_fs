# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/bioscfg.h

Purpose: shared contract for the hp-bioscfg module, defining constants, WMI GUIDs, data structures, macro-generated sysfs accessors, and cross-file prototypes.

Important APIs/types/functions: declares `struct common_data` plus typed state structs for string, integer, enumeration, ordered list, password, and secure platform data. `struct bioscfg_priv` is the module-wide state container. Enums define HP WMI commands, SPM/Sure Start command types, firmware error values, data types, and element positions. Macros such as `GET_INSTANCE_ID`, `ATTRIBUTE_PROPERTY_STORE`, `ATTRIBUTE_VALUES_PROPERTY_SHOW`, and property-show helpers generate repeated sysfs code.

Control flow: the header has no direct runtime flow, but `ATTRIBUTE_PROPERTY_STORE` defines the common write sequence for mutable BIOS settings: duplicate input, enforce one-line sysfs input, find instance, validate type-specific value, call `hp_set_attribute()`, update cached value, signal reboot if required, clear credentials, and return either error or byte count.

State and persistence: the declared `bioscfg_drv` external is the single shared state object. Fixed-size arrays bound values, encodings, prerequisites, and element lists; credentials and SPM tokens have dedicated fields.

Dependencies and integration: includes WMI, kernel device/module primitives, strings, types, and NLS. It binds all hp-bioscfg C files together.

Risks: macro-generated stores rely on locally defined functions with exact names, so refactors can silently break build linkage. Fixed limits require careful firmware clamping. Because credentials are stored in process memory before WMI submission, tests should verify clearing paths. Compile tests and sparse/static analysis are important signals for macro expansion and type correctness.
