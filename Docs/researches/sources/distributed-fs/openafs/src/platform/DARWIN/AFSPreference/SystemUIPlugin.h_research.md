# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/SystemUIPlugin.h

Purpose: declares private AppKit/SystemUIServer interfaces for menu extras, dock extras, and menu-extra views used by legacy menu bar integration.

Important APIs and types: defines `NSMenuExtra`, `NSMenuExtraPrivate`, `NSDockExtra`, dock/menu item helper categories, `NSApplicationDockExtra`, and `NSMenuExtraView` method surfaces. Methods cover initialization with bundles/data, image/menu/title/action/target properties, popup/unload behavior, accessibility attributes, dock menu commands, and menu item dictionary helpers.

Control flow and persistence: header only. It enables code to compile against private system classes without official SDK headers.

Dependencies and integration: imports AppKit. Related to the background menu extra and comments in `AFSCommanderPref.h` about loading/unloading menu extras.

Risks: these are private APIs and can break across macOS releases or cause App Store/signing rejection. Many methods use untyped `id` and historical parameter names. Accessibility and UI behavior depend on private implementation details.

Test signals: compile against the target SDK, runtime class availability, menu extra load/unload on supported macOS versions, and fallback behavior when private APIs are absent.
