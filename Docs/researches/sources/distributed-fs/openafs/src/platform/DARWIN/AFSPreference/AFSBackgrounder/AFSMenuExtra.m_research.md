<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtra.m -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtra.m

## Purpose
Implements the older OpenAFS SystemUIServer menu extra. It creates a custom menu/view, polls AFS/token state, reacts to preference and mount notifications, gets/releases tokens, and informs the preference pane when token operations occur.

## Important APIs, Types, And Functions
Key methods are `initWithBundle:`, `willUnload`, `startTimer`, `stopTimer`, `dealloc`, `menu`, `readPreferenceFile:`, `getToken:`, `releaseToken:`, `afsVolumeMountChange:`, `updateAfsStatus:`, `klogUserEven:`, `getImageFromBundle:fileExt:`, `imageToRender`, `updateMenu`, and `useAklogPrefValue`. It uses `NSMenuExtra`, `NSMenu`, `AFSMenuExtraView`, `AFSPropertyManager`, `AFSMenuCredentialContoller`, distributed notifications, workspace mount notifications, and token-state images.

## Control Flow
Initialization creates locks and a custom view, loads images, constructs menu items for start/stop/login/unlog, registers for preference/state/mount notifications, reads preferences, and starts a periodic token-status timer. `getToken:` either calls `getTokens` directly when aklog is enabled or opens the credential window and waits for its close notification. `updateAfsStatus:` lock-guards AFS status and token-list reads, updates menu titles/enabled state, and redraws the view. Unload/ dealloc invalidates timers and removes observers.

## State And Persistence
Runtime state includes menu objects, timer, lock, images, token/AFS booleans, and credential controller. Persistent effects are token creation/destruction through `AFSPropertyManager`; preferences are read through CFPreferences/NSUserDefaults.

## Dependencies And Integration Points
This code is tied to the old `SystemUIPlugin`/MenuExtra path and shares constants/notifications with the preference pane. It relies on `AFSPropertyManager` for actual OpenAFS operations and on `CredentialWindow.nib` for password-based login.

## Risks And Test Signals
Risks include private API breakage, inconsistent constant names (`afsCommanderID` vs `kAfsCommanderID`), assigning a BOOL result into an `NSNumber *` before replacing it, releasing an `AFSPropertyManager` while a credential controller may retain/use it, and manual observer cleanup. Test signals include menu extra load/unload, preference changes, mount notification refresh, aklog and manual credential flows, and no crashes when toggling the menu repeatedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtra.m -->
