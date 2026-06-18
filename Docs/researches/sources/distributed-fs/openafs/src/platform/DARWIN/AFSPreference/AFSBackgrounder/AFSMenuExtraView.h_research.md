<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtraView.h -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtraView.h

## Purpose
Declares the custom status-item view used by the backgrounder menu. It draws the OpenAFS token-state icon, optional Kerberos indicator, and handles mouse/menu delegate events for a status item menu.

## Important APIs, Types, And Functions
The class subclasses `NSView` and conforms to `NSMenuDelegate`. It stores an `AFSBackgrounderDelegate`, `NSStatusItem`, `NSMenu`, and menu visibility flag. Methods include `initWithFrame:backgrounder:menu:`, `makeKerberosIndicator:`, `mouseDown:`, `menuWillOpen:`, `menuDidClose:`, and `menuNeedsUpdate:`.

## Control Flow
The view is initialized by `AFSBackgrounderDelegate` when a status item is shown. Mouse down opens the status item menu; menu delegate callbacks update highlighting and forward menu-update requests back to the delegate.

## State And Persistence
Only transient UI state is stored: status item/menu references and whether the menu is open. There is no persistent storage.

## Dependencies And Integration Points
It depends on `AFSBackgrounderDelegate` for token image selection and aklog preference, and on Cocoa status-item drawing APIs.

## Risks And Test Signals
Risks include deprecated drawing APIs and assuming `[backgrounderDelegator statusItem]` is valid during initialization. Test signals are correct drawing in normal/highlighted states, menu opening/closing redraws, and Kerberos indicator rendering when aklog is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtraView.h -->
