<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSBackgrounderDelegate.h -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSBackgrounderDelegate.h

## Purpose
Declares the application delegate for the modern macOS OpenAFS backgrounder menu-bar app. The delegate owns the status menu, token/AFS state, preferences, timers, credential window, link creation state, and action methods for starting/stopping AFS and obtaining/releasing tokens.

## Important APIs, Types, And Functions
The interface imports Cocoa and `AFSMenuCredentialContoller`. It exposes `applicationDidFinishLaunching`/termination-related behavior through the implementation, timer controls, preference reading, token operations, status updates, Kerberos renewal, notification handlers, link-mode updates, status-item accessors, and menu action methods. Important ivars include `backgrounderMenu`, `startStopMenuItem`, `getReleaseTokenMenuItem`, `NSStatusItem *statusItem`, `AFSPropertyManager *afsMngr`, preference `NSNumber`s, `NSTimer`s, `NSLock`s, token state booleans, images, credential controller, and link configuration.

## Control Flow
The header defines the object surface used by the app nib and `AFSMenuExtraView`. The implementation initializes the delegate, reads preferences, starts timers, receives distributed/workspace notifications, updates status, and delegates menu drawing/actions through these declarations.

## State And Persistence
The delegate maintains in-memory menu/timer/lock/status state and reads persistent CFPreferences for OpenAFS preference keys. It also tracks user-configured desktop symlink mappings.

## Dependencies And Integration Points
It connects the `AFSBackgrounder` app nib to `AFSPropertyManager`, `Krb5Util`, distributed notifications shared with the preference pane, and the custom status-item view.

## Risks And Test Signals
Risks include manual memory management ownership, duplicated `imageToRender` declaration, timer/lock lifecycle mistakes, and preference values assumed non-null. Test signals are successful nib outlet/action binding, status item visibility changes, token refresh timer behavior, and clean app termination without leaked observers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSBackgrounderDelegate.h -->
