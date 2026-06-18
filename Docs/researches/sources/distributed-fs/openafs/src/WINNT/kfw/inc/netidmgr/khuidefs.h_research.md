# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khuidefs.h

## Purpose

`khuidefs.h` is the umbrella public UI header for NetIDMgr. It includes Windows, KMQ, credential database, error, action, resource, hyperlink, new-credential, property-sheet, alert, configuration, tracker, and remote-dialog contracts, then exposes version-query APIs for plugin compatibility and common controls.

## Important APIs, Types, and Functions

- Includes `windows.h`, `kmq.h`, `kcreddb.h`, `kherror.h`, `kherr.h`, `khmsgtypes.h`, `khaction.h`, `khactiondef.h`, `khrescache.h`, `khhtlink.h`, `khnewcred.h`, `khprops.h`, `khalerts.h`, `khconfigui.h`, `khtracker.h`, and `khremote.h`.
- Internal `khm_version_init()` initializes library version state.
- `khm_get_lib_version(khm_version * libver, khm_ui_4 * apiver)` returns NetIDMgr library and API versions.
- `khm_get_commctl_version(khm_version * pdvi)` returns a packed Windows Common Controls version and optionally fills a version record.

## Control Flow

Plugins include this one header to gain access to the full UI surface. During plugin loading, the module manager can compare plugin version metadata with `khm_get_lib_version()` results. UI code may call `khm_get_commctl_version()` before using controls that require a minimum Common Controls version.

## State and Persistence Behavior

Version state is initialized in-process and read by callers. It reflects the loaded NetIDMgr library and API level rather than persisted configuration. Common Controls version reflects the currently loaded Windows library in the process.

## Dependencies and Integration Points

This header deliberately creates a broad dependency fan-in. It is the integration point between KMQ, KCDB, KMM/plugin-facing UI helpers, alerts, actions, and remote compatibility. Its use simplifies plugin source at the cost of increased rebuild and namespace coupling.

## Risks and Edge Cases

- Including this header pulls in many Windows and NetIDMgr symbols, increasing compile-time coupling and collision risk.
- The Common Controls version function returns `MAKELONG(minor, major)` packing; callers must unpack correctly.
- `khm_get_lib_version()` accepts optional API version but requires a valid library-version pointer by contract.
- Version checks must consider both library version and API version, not only one.

## Test Signals

- Compile representative plugins with only `khuidefs.h` and verify all included contracts are visible.
- Assert library/API version values match build metadata from `netidmgr_version.h`.
- Test Common Controls version retrieval on supported Windows versions and fallback behavior if optional output is null.
