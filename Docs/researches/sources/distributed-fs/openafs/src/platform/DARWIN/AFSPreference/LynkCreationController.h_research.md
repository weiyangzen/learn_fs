# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/LynkCreationController.h

Purpose: declares the symlink/link configuration sheet controller used by the preference pane link tab.

Important APIs and state: stores `lynkCreationSheet`, destination path and link-name text fields, and `choiceResult`. Exposes `getView`, `save:`, `cancell:`, and `selectLinkDest:`.

Control flow and persistence: the implementation writes link-name to destination-path mappings into the preference domain under `PREFERENCE_LINK_CONFIGURATION`.

Dependencies and integration: imports Cocoa and depends on constants from `global.h` in the implementation. `AFSCommanderPref` opens the sheet and reloads link configuration on close.

Risks: spelling of class/file uses `Lynk`, and `cancell:` is misspelled. Header does not document expected path semantics or duplicate-name behavior.

Test signals: nib outlet wiring, empty fields, duplicate link names, directory picker selection/cancel, and CFPreferences round trip.
