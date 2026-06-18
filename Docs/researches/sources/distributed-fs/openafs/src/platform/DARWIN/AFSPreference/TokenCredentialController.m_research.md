# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/TokenCredentialController.m

Purpose: implements the username/password sheet for klog token acquisition.

Important APIs and control flow: `getToken:` reads the username and password text fields into `uName` and `uPwd`, returns early if either is pointer-equal to `@""`, sets `taken = YES`, and ends the sheet. `closePanel:` sets `taken = NO` and ends the sheet. Accessors return the taken flag and credential strings.

State and persistence: credential strings are kept only in controller ivars, then passed to `AFSPropertyManager`. They are not written to preferences.

Dependencies and integration: loaded by `AFSCommanderPref getNewToken:` when aklog is disabled. Imports `TaskUtil` but does not use it directly.

Risks: string pointer comparison is incorrect for empty validation. Password remains as an immutable Objective-C string until overwritten/released. `taken` is not reset in `awakeFromNib`, so reused controller state could matter.

Test signals: empty field validation with distinct empty NSString instances, cancel after previous successful submit, secure text field behavior, and downstream klog invocation arguments.
