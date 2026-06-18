<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuCredentialContoller.m -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuCredentialContoller.m

## Purpose
Implements the backgrounder credential window wrapper. It loads the credential nib, displays an `NSWindow` near the status item, and on close obtains tokens with the username/password captured by `CredentialWindowController`.

## Important APIs, Types, And Functions
Methods are `initWhitRec:afsPropManager:`, `dealloc`, `showWindow`, and `closeWindow`. It uses `NSBundle loadNibNamed`, `NSWindow initWithContentRect`, `setFrameTopLeftPoint`, `makeKeyAndOrderFront`, and `AFSPropertyManager getTokens:true usr:pwd:`.

## Control Flow
Initialization stores the display rectangle and retains the property manager. `showWindow` computes a top-left point near the menu bar, loads `CredentialWindow.nib`, creates a titled window with the loaded credential view, and shows it. `closeWindow` checks whether the credential controller reports `takenToken`; if so it calls `getTokens` with the captured username/password, releases the property manager, then closes and clears the window.

## State And Persistence
Runtime state includes the credential window and retained property manager. The persistent/externally visible side effect is token creation through OpenAFS tools if the user submitted credentials.

## Dependencies And Integration Points
It integrates the credential nib/controller with both backgrounder menu implementations and with `AFSPropertyManager` token acquisition.

## Risks And Test Signals
Risks include not releasing `afsPropMngr` on cancel, using deprecated `loadNibNamed`, window/view ownership ambiguity, storing password strings without copying/wiping, and hard-coded positioning. Test signals include submit/cancel flows, no leaked observers/controllers after close, token acquisition with valid credentials, and behavior when the nib fails to load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuCredentialContoller.m -->
