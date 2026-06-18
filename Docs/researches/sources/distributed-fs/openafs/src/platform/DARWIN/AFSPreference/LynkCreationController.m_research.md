# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/LynkCreationController.m

Purpose: implements adding a named link mapping to preference storage.

Important APIs and control flow: `save:` rejects blank trimmed destination or name, loads existing `PREFERENCE_LINK_CONFIGURATION` plist data from CFPreferences, creates a mutable dictionary if absent, stores destination path under link name, serializes XML plist data, writes it back to the current user's preference domain, synchronizes, and ends the sheet. `cancell:` ends the sheet. `selectLinkDest:` opens a directory-only `NSOpenPanel` and copies the selected path into the destination field.

State and persistence: persistent link configuration is a dictionary serialized as XML plist data in CFPreferences for `it.infn.lnf.network.openafs`.

Dependencies and integration: used by `AFSCommanderPref addLink:` and `didEndSymlinkSheet:`. Link enablement and table display are handled in the main controller.

Risks: no validation for link name characters, existing destination existence after selection, duplicates beyond overwriting, or stale preference data. `propertyListFromData` return is assigned to `NSMutableDictionary *` but may be immutable depending on API behavior.

Test signals: first link creation, appending to existing plist, duplicate overwrite, invalid/blank fields, directory selection cancel, and reloading in the parent link table.
