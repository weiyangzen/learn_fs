<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSCommanderPref.h -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSCommanderPref.h

## Purpose
Declares the main OpenAFS macOS preference pane controller. It manages UI for AFS service state, cache parameters, CellServDB entries, tokens, aklog/login preferences, Kerberos renewal, menu/backgrounder activation, startup behavior, and desktop link configuration.

## Important APIs, Types, And Functions
The class subclasses `NSPreferencePane` and implements table data source/delegate protocols. It imports PreferencePanes, SecurityInterface authorization UI, `AFSPropertyManager`, global constants, and link-creation support. It declares private CoreMenuExtra functions for adding/removing menu extras. Ivars include many IBOutlet controls, sheets/controllers, `AFSPropertyManager`, filtered CellServDB data, token list, timer, locks, and link configuration. Methods cover pane lifecycle, authorization, timers, refresh/save actions, AFS start/stop, token/unlog, menu activation, aklog/startup/Kerberos preference changes, CellServDB filtering/editing, token refresh notifications, volume-change notifications, table delegates, and table value providers.

## Control Flow
The implementation (outside this header) uses these actions and outlets to load preferences into the UI, allow authorized edits, persist preference values, notify the backgrounder/menu extra, start/stop AFS via `AFSPropertyManager`, manage token lists, edit CellServDB/link data, and respond to tab/table/timer events.

## State And Persistence
The controller's runtime state includes UI controls, current token/cell/link lists, timers, locks, and sheet controllers. Persistent state flows through CFPreferences, OpenAFS config files under `/var/db/openafs`, launchd/menu-extra settings, and CellServDB/cache configuration managed by `AFSPropertyManager`.

## Dependencies And Integration Points
It is the user-facing preference pane counterpart to the backgrounder. It integrates with privileged authorization, CoreMenuExtra APIs, `AFSPropertyManager`, distributed notifications, launch agents/daemons, and the OpenAFS macOS package resources.

## Risks And Test Signals
Risks include very broad controller responsibility, private CoreMenuExtra API compatibility, many untyped `id` outlets, manual memory/timer management, and preference/backgrounder synchronization drift. Test signals include pane load/unload, authorization lock/unlock, saving cache and preference values, start/stop service actions, CellServDB table edits, token refresh, menu/backgrounder toggle, Kerberos renewal settings, and link configuration persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSCommanderPref.h -->
