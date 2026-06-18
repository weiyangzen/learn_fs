<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtraView.m -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtraView.m

## Purpose
Implements the custom drawing and menu interaction for the OpenAFS backgrounder status item.

## Important APIs, Types, And Functions
Methods include `initWithFrame:backgrounder:menu:`, `drawRect:`, `makeKerberosIndicator:`, `mouseDown:`, `menuWillOpen:`, `menuDidClose:`, and `menuNeedsUpdate:`. It uses `drawStatusBarBackgroundInRect:withHighlight:`, `imageToRender`, `compositeToPoint:operation:`, `NSAttributedString`, `NSFont`, and `popUpStatusItemMenu:`.

## Control Flow
`drawRect:` paints the status bar background, draws the current token-state image, and overlays a small `K` indicator when the delegate reports aklog mode. `mouseDown:` sets itself as menu delegate and opens the menu. Menu callbacks toggle highlight state and forward `menuNeedsUpdate:` to the backgrounder delegate so titles/enabled states are fresh before display.

## State And Persistence
The implementation stores only transient highlight/menu references and has no persistent side effects.

## Dependencies And Integration Points
It is instantiated by `AFSBackgrounderDelegate setStatusItem:` and bridges user clicks into the delegate's `NSMenu`. It depends on image assets and `global.h` constants such as menu-bar height.

## Risks And Test Signals
Risks include deprecated `NSCompositeSourceOver`/`compositeToPoint` APIs, fixed drawing origin/indicator placement, and delegate lifetime assumptions. Test signals include visual state updates after token changes, menu highlight behavior, click-to-open, and no drawing errors when images are nil.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtraView.m -->
