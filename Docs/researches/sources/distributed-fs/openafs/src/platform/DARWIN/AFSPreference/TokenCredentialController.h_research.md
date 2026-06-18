# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/TokenCredentialController.h

Purpose: declares the modal credential sheet controller used when the user obtains AFS tokens with klog instead of aklog.

Important APIs and state: stores `credentialPanel`, parent/controller references, username and password text fields, `taken`, `uName`, and `uPwd`. Exposes `getToken:`, `closePanel:`, `takenToken`, `uName`, and `uPwd`.

Control flow and persistence: credentials are in-memory only. `AFSCommanderPref didEndCredentialSheet:` reads them and calls `AFSPropertyManager getTokens:true usr:pwd:`.

Dependencies and integration: imports Cocoa. It is loaded from `CredentialPanel` nib by the main preference pane.

Risks: password is retained in an NSString and not cleared. Empty string detection in implementation uses pointer equality. Outlets are untyped `id`.

Test signals: empty fields, successful submit, cancel, password lifetime after sheet close, and parent token-acquisition call.
