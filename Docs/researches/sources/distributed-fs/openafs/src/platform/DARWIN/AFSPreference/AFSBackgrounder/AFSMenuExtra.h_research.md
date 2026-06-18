<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtra.h -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtra.h

## Purpose
Declares the older SystemUIServer `NSMenuExtra` plugin implementation for OpenAFS. It predates or coexists with the standalone backgrounder app and provides a menu extra with AFS state, token state, login/unlog controls, and a custom view.

## Important APIs, Types, And Functions
The interface subclasses `NSMenuExtra` from `SystemUIPlugin.h`, imports global constants and the credential controller, and declares timer, preference, token, menu, image, and mount-change methods. Ivars track `afsState`, `gotToken`, `afsSysPath`, `useAklogPrefValue`, menu/menu-items, `AFSMenuExtraView`, token-state images, credential controller, timer, and lock.

## Control Flow
The implementation initializes the menu extra from a bundle, reads preferences, polls status, displays menu items, responds to token operations, and redraws its custom view through methods declared here.

## State And Persistence
The class stores in-memory menu/view/timer/lock state and reads user preferences for aklog behavior. It causes token side effects through `AFSPropertyManager`.

## Dependencies And Integration Points
It depends on the private/deprecated MenuExtra plugin API, custom `AFSMenuExtraView`, distributed notifications with the preference pane, and workspace mount notifications.

## Risks And Test Signals
Risks include private API compatibility, manual memory management, and overlap with the newer `AFSBackgrounderDelegate`. Test signals are plugin loading/unloading in supported macOS versions, menu item enablement, icon updates, and token operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtra.h -->
