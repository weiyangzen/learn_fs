<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/main.m -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/main.m

## Purpose
Entry point for the macOS `AFSBackgrounder` Cocoa application.

## Important APIs, Types, And Functions
The file imports Cocoa and defines `main(int argc, char *argv[])`, returning `NSApplicationMain(argc, (const char **)argv)`.

## Control Flow
Process startup immediately hands control to Cocoa's application runtime, which loads the app bundle/nib and invokes `AFSBackgrounderDelegate` through normal application delegate wiring.

## State And Persistence
No state is stored in this file. Runtime application state is owned by Cocoa and the delegate.

## Dependencies And Integration Points
It links the backgrounder executable into the macOS app bundle packaged by the OpenAFS preference pane.

## Risks And Test Signals
Risks are minimal and limited to application bundle/nib configuration. Test signals are successful app launch, delegate initialization, and clean exit code propagation from `NSApplicationMain`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/main.m -->
