## sources/distributed-fs/ceph-client/include/uapi/linux/dvb/version.h

Purpose: This small header declares the DVB API version exposed by the kernel UAPI.

Important APIs and types: It defines `DVB_API_VERSION` as 5 and `DVB_API_VERSION_MINOR` as 12. There are no structs, functions, or ioctls.

Control flow and state: There is no runtime control flow. Userspace can compile-time or runtime-gated logic against these constants when checking DVB API availability.

Persistence and dependencies: No state or dependencies beyond the header guard.

Integration points: DVB applications and libraries use this with the rest of `linux/dvb/*` to reason about feature availability, especially DVBv5 properties.

Risks and test signals: Risks are mostly version skew and userspace assuming that a numeric version guarantees every driver supports every optional feature. Tests should verify that build environments expose the expected constants and that feature probing still uses actual ioctls such as `FE_GET_PROPERTY` and `DTV_ENUM_DELSYS` rather than version checks alone.
