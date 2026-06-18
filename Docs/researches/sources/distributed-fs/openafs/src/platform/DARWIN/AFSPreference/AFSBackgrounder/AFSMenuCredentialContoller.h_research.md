<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuCredentialContoller.h -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuCredentialContoller.h

## Purpose
Declares a controller object for the backgrounder credential popover/window. It owns the view rectangle, credential view/window/controller outlets, and an `AFSPropertyManager` used to obtain tokens after the user submits credentials.

## Important APIs, Types, And Functions
The interface imports Cocoa, `CredentialWindowController`, and `AFSPropertyManager`. Public methods are `initWhitRec:afsPropManager:`, `showWindow`, and `closeWindow`.

## Control Flow
Callers initialize it with the menu/status-item rectangle and property manager, call `showWindow` to load and display the credential UI, and call `closeWindow` in response to the credential-window notification so it can either obtain tokens or dismiss.

## State And Persistence
It retains an `AFSPropertyManager`, references the credential window/view/controller, and stores the source rectangle. Persistent token changes occur only through the implementation's call to `getTokens`.

## Dependencies And Integration Points
It is used by `AFSBackgrounderDelegate` and the older `AFSMenuExtra` path when aklog mode is disabled. It depends on `CredentialWindow.nib` outlet wiring and `CredentialWindowController`.

## Risks And Test Signals
Risks include manual memory management, the misspelled initializer name being part of the call contract, and weakly typed `id` outlets. Test signals are nib loading, window placement, submit/cancel notification handling, and token acquisition with provided credentials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuCredentialContoller.h -->
