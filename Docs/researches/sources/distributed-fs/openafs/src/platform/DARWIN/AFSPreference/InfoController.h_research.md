# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/InfoController.h

Purpose: declares the controller for the preference pane's information/license sheet.

Important APIs and state: stores `infoPanel`, `texEditInfo`, and `htmlLicence`. Exposes `closePanel:` and `showHtmlResource:`. The implementation loads RTF data into a text view.

Control flow and persistence: no persistent state; the controller is created from a nib and used by `AFSCommanderPref info:` to display the bundled license resource as a modal sheet.

Dependencies and integration: imports Cocoa and is driven by the `Info` sheet outlets in `AFSCommanderPref`.

Risks: outlet names are untyped `id`, so nib wiring errors are compile-time invisible. The retained attributed string must be released on close to avoid leaks.

Test signals: nib outlet binding, loading missing/valid RTF resources, repeated open/close cycles, and modal sheet closure.
