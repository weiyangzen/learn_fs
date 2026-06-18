<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/CredentialWindow/CredentialWindowController.h -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/CredentialWindow/CredentialWindowController.h

## Purpose
Declares the controller for the credential-entry nib used by the backgrounder. It captures username/password fields and posts a notification when the user submits or cancels.

## Important APIs, Types, And Functions
The interface declares outlets/ids for the credential view, parent menu controller, username and password text fields, state flag `taken`, and stored `uName`/`uPwd`. Public methods are `getToken:`, `closePanel:`, `takenToken`, `uName`, and `uPwd`.

## Control Flow
The controller is driven by nib actions. Submit records field values, sets `taken`, and notifies the menu controller; cancel clears `taken` and notifies as well.

## State And Persistence
It stores entered credentials in memory as Objective-C strings. Token creation is performed by `AFSMenuCredentialContoller` after reading this state.

## Dependencies And Integration Points
It integrates `CredentialWindow.nib` with `AFSMenuCredentialContoller` and distributed notification constant `kLogWindowClosed`.

## Risks And Test Signals
Risks include untyped outlets, password string retention without wiping, and returning internal string references. Test signals are nib action wiring, submit/cancel notification delivery, and correct values returned to the wrapper controller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/CredentialWindow/CredentialWindowController.h -->
