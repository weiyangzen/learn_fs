# Research: sources/distributed-fs/openafs/src/platform/DARWIN/growlagent/GrowlDefines.h

Purpose: bundled Growl public constants header defining registration, notification, and distributed-notification keys used by Growl clients or the local Growl agent.

Important APIs and state: `XSTR`/`STRING_TYPE` bridge Objective-C and CoreFoundation builds. Defines keys such as `GROWL_APP_NAME`, `GROWL_APP_ID`, app icon, default/all notifications, human-readable names, notification title/description/icon/priority/sticky/click context/display plugin/identifier/progress, and distributed notification names for registration, notification, shutdown, ping/pong, readiness, clicked, and timed out events.

Control flow and persistence: header-only constants. UserInfo dictionaries built with these keys flow through distributed notifications or Growl framework compatibility paths.

Dependencies and integration: used by `growlagent` code and any OpenAFS component that posts Growl notifications. Compatible with ObjC and C/CF consumers.

Risks: Growl direct distributed notifications are documented in this header as deprecated in favor of Growl.framework delegate APIs. String constants are legacy and must match the installed Growl version. No runtime validation of dictionary value types.

Test signals: registration dictionary acceptance by Growl, notification delivery with required keys, optional icon/progress/sticky handling, click callback context, and ObjC vs C macro expansion.
