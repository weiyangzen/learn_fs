# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/InfoController.m

Purpose: implements the information sheet controller.

Important APIs and control flow: `awakeFromNib` clears `htmlLicence`. `showHtmlResource:` reads file data from `resourcePath`, initializes an `NSAttributedString` with RTF data, and installs it in the text view's storage. `closePanel:` releases the attributed string and ends the sheet.

State and persistence: holds only the current attributed license content in memory.

Dependencies and integration: called by `AFSCommanderPref info:` with the bundle's `license.rtf` path. Depends on Cocoa text storage APIs.

Risks: repeated `showHtmlResource:` calls before `closePanel:` leak the previous `htmlLicence`. Missing or invalid RTF data can produce nil behavior without user feedback. Outlet casts assume `texEditInfo` is an `NSTextView`.

Test signals: valid RTF rendering, missing file behavior, repeated show/close cycles, and close button ending the correct sheet.
