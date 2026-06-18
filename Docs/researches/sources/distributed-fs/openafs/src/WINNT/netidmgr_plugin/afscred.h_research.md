# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afscred.h

## Purpose

`afscred.h` is the central private/public include for the OpenAFS NetIDMgr credential provider. It gathers Windows, OpenAFS, Kerberos, NetIDMgr, resource, extension, token-acquisition, configuration, help, notification-icon, and compatibility declarations used by the plugin implementation.

## Important APIs, types, and functions

It defines plugin and credential names (`AFS_PLUGIN_NAME`, `AFS_CREDTYPE_NAME`, `KRB5_CREDTYPE_NAME`, `KRB4_CREDTYPE_NAME`), attribute/type names (`AFS_ATTRNAME_*`, `AFS_TYPENAME_*`), configuration node names, valid cell/realm character sets, and help file name. It declares lifecycle functions `init_afs`, `exit_afs`, `init_module`, `exit_module`, the plugin callback `afs_plugin_cb`, configuration dialog procs, `afs_html_help`, extension lookup/method APIs, `afs_ext_resolve_token`, `afs_ext_klog`, shortcut lookup, notification icon APIs, and global handles/attribute ids.

## Control flow

This header declares the plugin's main control surfaces but contains no executable code. It also conditionally declares dynamic NetIDMgr UI function pointers when `KH_VERSION_API < 7`, mapping older decorated DLL exports into modern-looking macros.

## State and persistence behavior

Extern globals include module/resource instances, credential type ids, attribute ids, message type ids, credential set, configuration space handles, and subscription handles. These are process-lifetime plugin state initialized and released by module/plugin code outside this work item. Persistent configuration is accessed through schema names declared here.

## Dependencies and integration points

The header bridges `netidmgr.h`, OpenAFS auth/cache manager headers, `afspext.h`, `afsfuncs.h`, `afsnewcreds.h`, string safety APIs, language resources, and Windows. It is included by every plugin implementation file in this work item.

## Risks and edge cases

Because it is broad, include-order and macro side effects matter: `_WINSOCKAPI_`, `_USE_32BIT_TIME_T`, `NOSTRSAFE`, and compatibility macros can affect consumers. Most extension APIs are explicitly "not thread safe" and must be called only from the plugin thread. Global handles must be initialized before use by dialogs and token functions.

## Test signals

Build tests should cover 32-bit, 64-bit, `KH_VERSION_API < 7`, and newer API cases. Runtime tests should verify global id registration, extension method enumeration, valid method lookup/name conversion, and compatibility function-pointer loading on older NetIDMgr builds.
