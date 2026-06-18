# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/global.h

Purpose: central macro header for preference-pane localized strings, preference keys, bundle identifiers, menu/backgrounder paths, notification names, and timing constants.

Important APIs and state: defines `TOKENS_REFRESH_TIME_IN_SEC`, localized string macros for UI labels/errors, `PREFERENCE_*` keys for CFPreferences, default Kerberos renewal values, static AFS config base `/var/db/openafs`, menu extra resource URLs, backgrounder and preference bundle IDs, and distributed notification object/name constants.

Control flow and persistence: not executable, but its keys define persistent CFPreferences storage and interprocess notification contracts between `AFSCommanderPref` and `AFSBackgrounder`.

Dependencies and integration: consumed throughout the preference pane, link creation, PListManager flows, and backgrounder-related code.

Risks: macros reference `self` and `[self bundle]`, so they are only safe in Objective-C instance-method contexts. Notification constants include duplicate values (`kMExtraClosedNotification` and `kPrefChangeNotification`) that can blur event semantics. The static config path must match the privileged helper prefix.

Test signals: preference key round trips, localization table coverage, distributed notification delivery, backgrounder resource lookup, and consistency between config path macros and helper paths.
