<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_admsvr.h -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/al_admsvr.h

Purpose: declares AfsAppLib's exported admin-server client wrappers and, for normal consumers, remaps `asc_*` symbols to those wrappers so direct admin-client calls use AfsAppLib's initialized client-library instance.

Important APIs/types/functions: prototypes cover `AfsAppLib_asc_*` list management, admin-server open/close, credentials, local cell, error translation, actions, cells, object search/properties/listen/refresh, random key, fast object access, critical-section access, user operations, and group operations. The `#ifndef EXPORT_AFSAPPLIB` block defines `asc_*` macros to `AfsAppLib_asc_*`.

Control flow: when included by an application, calls written as `asc_ObjectFind()` compile to AfsAppLib wrapper calls. When building AfsAppLib itself, `EXPORT_AFSAPPLIB` suppresses remapping so the implementation can call the real client library.

State and persistence: no state in the header; wrapper implementation stores active admin-server client id.

Dependencies/integration: requires AfsAppLib export macros and admin-client public types. It is conditionally included by `afsapplib.h` when the admin-client header has already been included.

Risks and test signals: macro remapping is include-order-sensitive and can surprise code that expects the original `asc_*` symbol addresses. Tests should compile representative consumers with direct client-library linking, AfsAppLib DLL linking, and `EXPORT_AFSAPPLIB` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_admsvr.h -->
