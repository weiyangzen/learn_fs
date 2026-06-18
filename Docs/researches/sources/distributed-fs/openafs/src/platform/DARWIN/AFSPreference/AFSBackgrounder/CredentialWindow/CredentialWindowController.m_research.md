<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/CredentialWindow/CredentialWindowController.m -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/CredentialWindow/CredentialWindowController.m

## Purpose
Implements the credential-entry nib controller. It records submitted username/password values, marks whether token acquisition was requested, and posts a close notification for the surrounding credential window controller.

## Important APIs, Types, And Functions
Methods are `awakeFromNib`, `getToken:`, `closePanel:`, `takenToken`, `uName`, and `uPwd`. It uses `NSTextField stringValue` and `NSDistributedNotificationCenter postNotificationName:kAFSMenuExtraID object:kLogWindowClosed`.

## Control Flow
`getToken:` reads username and password fields, returns early if either is empty according to pointer comparison with `@""`, sets `taken=YES`, and posts the close notification. `closePanel:` sets `taken=NO` and posts the same notification. Accessors return the captured state.

## State And Persistence
State is in-memory only: `taken`, `uName`, and `uPwd`. The actual AFS token side effect happens later in `AFSMenuCredentialContoller`.

## Dependencies And Integration Points
It is loaded from `CredentialWindow.nib` and coordinates with `AFSMenuCredentialContoller` through distributed notifications.

## Risks And Test Signals
Risks include using pointer equality for empty string checks, not copying/retaining field values explicitly, password lifetime/wiping concerns, and no validation feedback. Test signals include submit with empty fields, submit with valid credentials, cancel flow, and notification observer cleanup in the caller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/CredentialWindow/CredentialWindowController.m -->
