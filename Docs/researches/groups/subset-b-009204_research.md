# subset-b-009204 research

Grouped research report for the exact subset B work item. Every section preserves the source path in the title and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/Bridge.m -->
# sources/sync-backup/unison/src/uimac/Bridge.m

Source read: complete file, 418 lines, 15625 bytes, sha256 `81368b8837a9a742`.

Purpose: Objective-C/C bridge between the Cocoa UI and Unison's OCaml core. It starts the OCaml runtime off the AppKit main thread, exposes `ocamlCall()`, and marshals C/Objective-C calls through an OCaml-owned callback thread so value allocation and field access happen while the OCaml runtime lock is held.

Important APIs/types/functions: `Bridge +startup:`, `-_ocamlStartup:`, `bridgeThreadWait`, `ocamlCall`, `_passCall`, `getField`, and `OCamlValue` are the key surfaces. The type signature alphabet is `x`, `i`, `s`, `S`, `N`, and `@`, with a hard limit of three converted arguments. It also installs an `NSExceptionHandler` delegate and registers OCaml global roots for wrapped values.

Implementation inventory: discovered Objective-C/C callback methods include `_ocamlStartup, startup, exceptionHandler, bridgeThreadWait, count, getField, value, dealloc`.

Control flow: Startup saves argv, detaches `_ocamlStartup:`, waits on `init_cond`, runs `caml_startup`, then calls the OCaml `callbackThreadCreate` entry. Cocoa callers populate a stack `CallState`; `_passCall` publishes it under `global_call_lock`, waits for `_RetState`, and rethrows OCaml exceptions as `NSException`. `bridgeThreadWait` loops forever, enters a blocking section while idle, converts arguments, invokes the named OCaml callback or field access, converts the result, and signals the waiting caller.

State and persistence behavior: The bridge owns global mutex/condition pairs, `_CallState`, `_RetState`, `doneInit`, `the_argv`, and OCaml global roots held by `OCamlValue`. Results that become Objective-C objects are autoreleased on the caller side. There is no durable persistence, but thread state is process-wide and singleton-style.

Dependencies and integration points: Depends on Cocoa, ExceptionHandling, pthreads, the OCaml C runtime headers, OCaml named values `callbackThreadCreate` and `unisonExnInfo`, and every UI file that uses `ocamlCall` or `OCamlValue`.

Risks: The single global call slot serializes all OCaml calls and would deadlock if a caller re-enters incorrectly. Varargs signatures are unchecked at compile time, only three arguments are supported, exception strings are leaked with `strdup`, and unsafe legacy callback code remains compiled out. Incorrect use of `OCamlValue value` outside the bridge thread can race the OCaml GC.

Test signals: Exercise GUI startup, non-GUI startup, password callbacks, table updates, diff/status callbacks, and exception paths. Static checks should verify all `ocamlCall` signatures against OCaml registrations and that every `OCamlValue` field access goes through `getField`.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/Bridge.m -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ColorGradientView.h -->
# sources/sync-backup/unison/src/uimac/ColorGradientView.h

Source read: complete file, 22 lines, 456 bytes, sha256 `487fcd00abedb20f`.

Purpose: Declares a small `NSView` subclass used by the Unison Mac UI to paint gradient backgrounds behind connection/status/detail regions.

Important APIs/types/functions: Exports retained `startingColor` and `endingColor` properties plus an assign `angle` property. The public contract is intentionally just configurable colors and gradient direction.

Control flow: The implementation initializes defaults and draws the gradient during AppKit `drawRect:` callbacks. Interface Builder can bind outlets to this class and set properties through Objective-C accessors.

State and persistence behavior: State is per-view retained color objects and an integer angle. There is no persistence beyond nib/runtime view state.

Dependencies and integration points: Depends on Cocoa/AppKit and `NSGradient` behavior in the implementation. It is referenced by `MyController` outlets for the connection and details views.

Risks: Manual retain semantics mean missing release/dealloc would leak in long-lived nib reloads. Nil `startingColor` would make the fill path unsafe if set externally.

Test signals: Instantiate from the nib and programmatically, set equal and different colors, and snapshot the connection/details panels for solid-fill and gradient cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ColorGradientView.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ColorGradientView.m -->
# sources/sync-backup/unison/src/uimac/ColorGradientView.m

Source read: complete file, 46 lines, 1220 bytes, sha256 `b52d55aa12c63e99`.

Purpose: Implements `ColorGradientView`, drawing either a solid background or an `NSGradient` over the view bounds.

Important APIs/types/functions: Uses synthesized `startingColor`, `endingColor`, and `angle`. `initWithFrame:` sets grid/control-shadow defaults and `drawRect:` performs the render.

Implementation inventory: discovered Objective-C/C callback methods include `initWithFrame, drawRect`.

Control flow: When AppKit asks the view to draw, equal or nil ending colors trigger a plain `NSRectFill`; otherwise the method allocates an `NSGradient`, draws it over `[self bounds]` at `angle`, and releases it.

State and persistence behavior: Only the three properties affect rendering. Drawing is stateless aside from retained colors, and no backing cache is kept.

Dependencies and integration points: Depends on AppKit color and gradient classes and on nib/controller code that embeds the view.

Risks: The class lacks an explicit `dealloc` for retained synthesized properties in manual reference counting. `drawRect:` ignores the dirty `rect` and redraws full bounds, which is simple but less efficient.

Test signals: Verify no crash with default initialization, equal colors, and changed colors. Run under leaks/static analyzer to catch retained property cleanup.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ColorGradientView.m -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ImageAndTextCell.h -->
# sources/sync-backup/unison/src/uimac/ImageAndTextCell.h

Source read: complete file, 20 lines, 349 bytes, sha256 `8152461ef119cb2c`.

Purpose: Declares an Apple sample-derived `NSTextFieldCell` subclass that displays an icon and text in the same outline/table cell.

Important APIs/types/functions: `setImage:`, `image`, `drawWithFrame:inView:`, and `cellSize` are the main surface used by the reconcile table's path/change columns.

Implementation inventory: discovered Objective-C/C callback methods include `setImage, image, drawWithFrame, cellSize`.

Control flow: Controllers set an image on the cell before display; the implementation divides the cell frame into image and text regions for drawing, editing, and selection.

State and persistence behavior: The cell stores one retained `NSImage`. Copied cells retain the same image reference.

Dependencies and integration points: Depends on Cocoa `NSTextFieldCell` and is used from `MyController` while displaying `ReconItem` objects.

Risks: Manual memory management and inherited cell copying must keep image ownership correct. Image width affects editing/selection frame math.

Test signals: Render rows with and without images, copy cells through table reuse, and edit/select text to ensure the editor starts after the icon.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ImageAndTextCell.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ImageAndTextCell.m -->
# sources/sync-backup/unison/src/uimac/ImageAndTextCell.m

Source read: complete file, 130 lines, 5359 bytes, sha256 `ef0be26e27272c67`.

Purpose: Implements combined icon/text cell rendering for older AppKit table views.

Important APIs/types/functions: Overrides `copyWithZone:`, `dealloc`, `editWithFrame:...`, `selectWithFrame:...`, `drawWithFrame:inView:`, and `cellSize`; adds private `imageFrameForCellFrame:`.

Implementation inventory: discovered Objective-C/C callback methods include `dealloc, setImage, image, imageFrameForCellFrame, editWithFrame, selectWithFrame, drawWithFrame, cellSize`.

Control flow: Drawing reserves `3 + image.width` points at the leading edge, fills image background if needed, vertically centers the image with flipped-view handling, composites it, then delegates text drawing to `NSTextFieldCell`. Editing and selection use the same split so the text editor does not overlap the image.

State and persistence behavior: Owns a retained image pointer. No persistent state or caches are maintained.

Dependencies and integration points: Depends on AppKit image compositing APIs including older `NSCompositeSourceOver`; integrates with table display code in `MyController`.

Risks: The file contains old Apple license text with a mojibake copyright character. Deprecated compositing APIs may warn or fail on modern SDKs. `setStatus`-style retain/release is correct here, but frame math assumes non-nil image in edit/select paths.

Test signals: Table visual smoke tests with folder/file icons, selected rows, flipped views, and empty images. Compile on the target macOS SDK to catch deprecated API errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ImageAndTextCell.m -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/Makefile -->
# sources/sync-backup/unison/src/uimac/Makefile

Source read: complete file, 26 lines, 1312 bytes, sha256 `2cbb521768b7019c`.

Purpose: Delegating build entry for the Mac UI; the parent Unison makefile calls it to build, sign, and clean the Xcode-based application bundle.

Important APIs/types/functions: Targets are `default`, `macexecutable`, and `clean`. `macexecutable` writes `ExternalSettings.xcconfig`, runs `xcodebuild`, compiles `cltool.c`, and performs ad-hoc code signing.

Control flow: `default` recurses to `../Makefile macui`. `macexecutable` detects OCaml 5.1+ native library suffixes, writes Xcode build settings, invokes Xcode, adds the command-line helper to the bundle, removes stale signatures, signs helper and app with entitlements, and verifies the bundle. `clean` asks Xcode to clean and removes generated build/settings artifacts.

State and persistence behavior: Creates transient `ExternalSettings.xcconfig` and `build/`. It mutates bundle signatures but no source state.

Dependencies and integration points: Depends on `make`, `ocaml`, Xcode/xcodebuild, C compiler, Carbon framework for `cltool`, `codesign`, entitlements generated by Xcode, and parent make variables such as `VERSION`, `OCAMLLIBDIR`, `XCODEFLAGS`, `CC`, and `CFLAGS`.

Risks: OCaml release parsing assumes `ocaml -e` is available. Code signing order is brittle because `cltool` is added after initial Xcode signing. Build products live under an old `Default` configuration path.

Test signals: Run parent `make macui`, verify the app passes `codesign --verify --deep --strict`, and execute bundled `cltool` against the built app.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/MyController.h -->
# sources/sync-backup/unison/src/uimac/MyController.h

Source read: complete file, 146 lines, 3941 bytes, sha256 `27b5ecbd3dd0504f`.

Purpose: Declares the central Cocoa controller for the Unison Mac UI: profile selection, profile creation, connection, reconciliation table, sync execution, progress, diff display, preferences, notifications, and validation.

Important APIs/types/functions: Exports many IB actions and delegate methods, including `chooseProfiles`, `createButton:`, `openButton:`, `connect:`, `syncButton:`, `updateReconItems:`, `displayDetails:`, `validateItem:`, and font/profile/preference actions. It also exposes `reconItems` for `ReconTableView`.

Implementation inventory: discovered Objective-C/C callback methods include `init, awakeFromNib, chooseProfiles, createButton, saveProfileButton, cancelProfileButton, profile, profileSelected, showPreferences, restartButton, rescan, openButton, connect, raisePasswordWindow, controlTextDidEndEditing, endPasswordWindow, afterOpen, syncButton, tableModeChanged, initTableMode, reconItems, updateForChangedItems, updateReconItems, updateForIgnore, statusTextSet, diffViewTextSet, displayDetails, clearDetails` and more.

Control flow: The controller is loaded from the main nib, wires multiple view panels into one main window, and switches toolbar/window state as the workflow moves from profile choice to preferences, connecting, update review, and synchronization.

State and persistence behavior: Holds outlets, selected profile name, `reconItems`, `rootItem`, OCaml preconnection state, sync flags, password wait flag, timers, table mode, font target, and batch/quit state.

Dependencies and integration points: Depends on every local UI class (`ProfileController`, `PreferencesController`, `NotificationController`, `ReconItem`, `ReconTableView`, `UnisonToolbar`, cells/views) plus `Bridge.h` for OCaml values.

Risks: The large controller surface couples UI state, OCaml callbacks, and table model state tightly. Many outlets are implicitly required by the nib; missing connections can fail at runtime rather than compile time.

Test signals: Nib loading, profile selection/creation, toolbar validation, OCaml callback smoke tests, password dialog, sync completion, batch timeout, and table-mode persistence should all exercise this header's contract.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/MyController.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/MyController.m -->
# sources/sync-backup/unison/src/uimac/MyController.m

Source read: complete file, 1263 lines, 43955 bytes, sha256 `8de43fce1ad71672`.

Purpose: Implements the main Unison Mac GUI controller and OCaml callback entry points. It coordinates profile selection/creation, connection to the OCaml engine, reconciliation item model construction, action validation, sync execution, progress/diff/status rendering, notifications, and shutdown behavior.

Important APIs/types/functions: Important Objective-C methods include `awakeFromNib`, `chooseProfiles`, profile save/cancel/open actions, `connect:`, `raisePasswordWindow:`, `afterOpen`, `syncButton:`, `doSync`, `afterUpdate:`, `afterSync:`, `updateReconItems:`, table data source/delegate methods, validation methods, font/preference handlers, and helper view-resize methods. C entry points exported to OCaml include `unisonInit1Complete`, `unisonInit2Complete`, `syncComplete`, `reloadTable`, `displayStatus`, `displayGlobalProgress`, `displayDiff`, `displayDiffErr`, `fatalError`, and `warnPanel`.

Implementation inventory: discovered Objective-C/C callback methods include `trim, applicationShouldTerminateAfterLastWindowClosed, init, applicationWillTerminate, awakeFromNib, checkOpenProfileChanged, chooseFont, changeFont, updateFontDisplay, chooseProfiles, createButton, saveProfileButton, cancelProfileButton, profile, profileSelected, showPreferences, restartButton, rescan, openButton, updateToolbar, updateTableViewWithReset, updateProgressBar, updateTableViewSelection, outlineViewSelectionDidChange, connect, unisonInit1Complete, unisonInit1Complete, raisePasswordWindow` and more.

Control flow: `awakeFromNib` configures toolbar, views, cells, fonts, profile box, and initial profile selection. Opening a profile calls OCaml `unisonInit1`, waits for callback completion, possibly raises a password sheet, then calls `afterOpen` to initialize scanning. OCaml update callbacks deliver reconciliation data; `updateReconItems:` builds `LeafReconItem` and `ParentReconItem` structures, updates the outline, expands rows, and refreshes detail/progress state. User toolbar/table actions call into `ReconItem` to update OCaml directions/ignore rules. `syncButton:` either starts `doSync` or handles post-sync/batch quit logic, and OCaml `syncComplete` returns the UI to an after-sync state.

State and persistence behavior: Maintains current view, profile, syncability flags, batch mode, table nesting preference, font preferences, preconnection handle, root and flattened reconciliation items, progress bar values, timeout alert/timer, and password wait state. It persists user preferences through `NSUserDefaults` for opening profiles and fonts; synchronization state itself lives in OCaml and is reflected into UI objects.

Dependencies and integration points: Depends on AppKit, `Bridge`/OCaml named callbacks (`unisonInit1`, `unisonInit2`, `unisonSynchronize`, profile/path/diff/status functions), local table/cell/toolbar classes, notification delivery, user defaults, and bundled icon assets.

Risks: High coupling and manual memory management create leak/dangling risks. UI updates must happen on the main thread after OCaml callbacks; callback signatures are vararg/stringly typed. Batch timeout and `shouldExitAfterWarning` paths can exit unexpectedly if warning state is mishandled. Sorting/selection relies on model object identity and cached sort keys.

Test signals: End-to-end GUI tests should cover profile open/create, remote/local preference validation, password prompt, scan completion, conflicts and direction changes, ignore rules, diff display, sync completion notification, batch timeout, font changes, toolbar/menu validation, and fatal/warn OCaml callbacks.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/MyController.m -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/NotificationController.h -->
# sources/sync-backup/unison/src/uimac/NotificationController.h

Source read: complete file, 18 lines, 394 bytes, sha256 `268b2193bf3512d7`.

Purpose: Declares a small notification delegate/controller for scan and sync completion notifications.

Important APIs/types/functions: Exports `updateFinishedFor:` and `syncFinishedFor:` and conforms to `NSApplicationDelegate` and `NSUserNotificationCenterDelegate`.

Implementation inventory: discovered Objective-C/C callback methods include `updateFinishedFor, syncFinishedFor`.

Control flow: The implementation installs itself as the user notification center delegate at nib wakeup and sends notifications when `MyController` reports completion events.

State and persistence behavior: No explicit instance state; notification center delegate registration is global process state.

Dependencies and integration points: Depends on Cocoa `NSUserNotificationCenter`, which is deprecated on modern macOS in favor of UserNotifications.

Risks: Deprecated API can affect future builds; no authorization/error handling is present. Delegate lifetime depends on nib ownership.

Test signals: Trigger scan and sync completion with the app foreground/background and verify notifications present with the expected profile text.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/NotificationController.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/NotificationController.m -->
# sources/sync-backup/unison/src/uimac/NotificationController.m

Source read: complete file, 50 lines, 1480 bytes, sha256 `2ef3c5fcf72ae890`.

Purpose: Implements simple macOS user notifications for finished scan and synchronization events.

Important APIs/types/functions: `awakeFromNib`, `updateFinishedFor:`, `syncFinishedFor:`, delegate `shouldPresentNotification:`, and file-local `simpleNotify` are the relevant functions.

Implementation inventory: discovered Objective-C/C callback methods include `awakeFromNib, updateFinishedFor, syncFinishedFor, userNotificationCenter`.

Control flow: Completion methods call `simpleNotify` with a title and profile-aware format. `simpleNotify` allocates `NSUserNotification`, fills title/body/sound, and delivers it through the default center. The delegate always returns YES so notifications appear even while the app is active.

State and persistence behavior: Only transient notification objects are created. The function leaks the allocated notification under manual reference counting because it is never released.

Dependencies and integration points: Depends on AppKit/Foundation notification APIs and `MyController` calls after update/sync completion.

Risks: Deprecated notification API, missing release, no user authorization handling, and no localization of notification strings.

Test signals: Manual or UI automation should verify foreground presentation, notification text for profile names with spaces, and behavior on macOS versions where `NSUserNotification` is deprecated.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/NotificationController.m -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/PreferencesController.h -->
# sources/sync-backup/unison/src/uimac/PreferencesController.h

Source read: complete file, 20 lines, 548 bytes, sha256 `9d70b8a4c35881a2`.

Purpose: Declares the controller for creating/editing profile preferences in the Mac UI.

Important APIs/types/functions: Outlets represent profile name, first root, local/remote toggles, and remote user/host/path fields. Methods are `reset`, `validatePrefs`, `anyEnter:`, `localClick:`, and `remoteClick:`.

Implementation inventory: discovered Objective-C/C callback methods include `anyEnter, localClick, remoteClick, validatePrefs, reset`.

Control flow: The main controller presents this panel during profile creation; validation constructs a Unison root pair and asks OCaml to initialize the profile.

State and persistence behavior: State lives in text fields and radio button cells. There is no independent model object.

Dependencies and integration points: Depends on Cocoa controls and `PreferencesController.m`'s OCaml bridge use.

Risks: Validation policy is in UI code and only checks emptiness, not duplicate profile names or path syntax.

Test signals: Exercise local/remote toggle enablement, empty-field validation, and successful profile creation with local and SSH roots.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/PreferencesController.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/PreferencesController.m -->
# sources/sync-backup/unison/src/uimac/PreferencesController.m

Source read: complete file, 89 lines, 2876 bytes, sha256 `5fa728f4cdd2afc2`.

Purpose: Implements the profile creation preferences panel and emits profile initialization requests to the OCaml core.

Important APIs/types/functions: `reset`, `validatePrefs`, `anyEnter:`, `localClick:`, and `remoteClick:`. The OCaml integration point is `ocamlCall("xSSS", "unisonProfileInit", profileName, firstRoot, secondRoot)`.

Implementation inventory: discovered Objective-C/C callback methods include `reset, validatePrefs, anyEnter, localClick, remoteClick`.

Control flow: `reset` clears controls and defaults to remote mode. `validatePrefs` checks profile and root fields, builds either `ssh://user@host/path` or a local second root, shows modal alerts for missing data, and calls OCaml on success. Toggle handlers enable or disable remote user/host fields.

State and persistence behavior: Form widgets are the sole mutable state. No preferences are persisted here; OCaml writes profile files through `unisonProfileInit`.

Dependencies and integration points: Depends on Cocoa, modal alert panels, and the bridge. It is owned and presented by `MyController`.

Risks: Uses bitwise `|` instead of logical `||` in nil/empty checks; this works for BOOL-ish values but does not short-circuit. SSH URL construction does not escape user/host/path characters. `anyEnter:` is noted as broken because it fires for tab/mouse focus changes.

Test signals: Test empty field rejection, local path profile creation, remote profile creation with special characters, and reloading the new profile list after save.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/PreferencesController.m -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProfileController.h -->
# sources/sync-backup/unison/src/uimac/ProfileController.h

Source read: complete file, 20 lines, 658 bytes, sha256 `d435c51ad1c7b9a1`.

Purpose: Declares the profile-list controller backing the initial profile selection table.

Important APIs/types/functions: Exports `initProfiles`, table data source methods, `selected`, `tableView`, and `getProfiles`.

Implementation inventory: discovered Objective-C/C callback methods include `initProfiles, numberOfRowsInTableView, tableView, selected, tableView, getProfiles`.

Control flow: At nib wakeup the implementation asks OCaml for the Unison directory, scans `.prf` files, sorts them, and selects `default` when available.

State and persistence behavior: Stores a mutable profile-name array and the index of the default profile.

Dependencies and integration points: Depends on Cocoa `NSTableView` and the bridge function that supplies the Unison directory.

Risks: `defaultIndex` uses an unsigned type with `-1` sentinel, which relies on wraparound semantics. The selected index is computed before sorting and can become stale.

Test signals: Populate a temporary Unison directory with several `.prf` files, including `default.prf`, and verify table rows, sorting, and selected profile.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProfileController.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProfileController.m -->
# sources/sync-backup/unison/src/uimac/ProfileController.m

Source read: complete file, 90 lines, 2580 bytes, sha256 `e005e27a706c2d16`.

Purpose: Implements profile discovery and table data-source behavior for the Mac UI profile chooser.

Important APIs/types/functions: Global `unisonDirectory()` calls OCaml, `initProfiles` scans files, `awakeFromNib` initializes and selects defaults, and table methods return row count/name values.

Implementation inventory: discovered Objective-C/C callback methods include `initProfiles, awakeFromNib, numberOfRowsInTableView, tableView, selected, tableView, getProfiles`.

Control flow: The controller reads directory contents, filters names ending in `.prf`, strips extensions, records `default`, sorts names, selects the first row and then default if available, and reloads the table.

State and persistence behavior: Owns the retained `profiles` array. `defaultIndex` is reset on each scan. It does not persist data itself.

Dependencies and integration points: Depends on `NSFileManager`, `NSTableView`, and OCaml `unisonDirectory`. It integrates with `MyController` for open/create flows.

Risks: The `defaultIndex` is captured before sorting, so selecting it after sort can select the wrong row. There is no `dealloc` releasing `profiles`. Directory read failures silently produce an empty list.

Test signals: Run profile-list tests with unsorted filenames where `default` would move after sort, missing directories, and profile creation refresh.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProfileController.m -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProfileTableView.h -->
# sources/sync-backup/unison/src/uimac/ProfileTableView.h

Source read: complete file, 11 lines, 163 bytes, sha256 `9f99e0686d50d9bc`.

Purpose: Declares a profile chooser table subclass that forwards Return key activation to `MyController`.

Important APIs/types/functions: Contains one outlet to `MyController`; behavior is implemented by overriding `keyDown:` and highlight color in the `.m` file.

Control flow: When the profile table is first responder, Return opens the selected profile instead of merely editing/selecting.

State and persistence behavior: No persistent state; only the outlet matters.

Dependencies and integration points: Depends on `NSTableView` and `MyController`.

Risks: Missing outlet wiring makes Return key activation a no-op or crash depending on nil messaging expectations.

Test signals: Select a profile and press Return, plus verify normal key events still pass to `NSTableView`.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProfileTableView.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProfileTableView.m -->
# sources/sync-backup/unison/src/uimac/ProfileTableView.m

Source read: complete file, 36 lines, 894 bytes, sha256 `49fd84af95629fcf`.

Purpose: Adds keyboard activation and custom highlight color to the profile table.

Important APIs/types/functions: Overrides `keyDown:` and private `_highlightColorForCell:`.

Implementation inventory: discovered Objective-C/C callback methods include `keyDown, _highlightColorForCell`.

Control flow: Empty character events pass through. Return calls `[myController openButton:self]`; other keys delegate to the superclass. Highlight color changes depending on first responder/key-window state to match the reconciliation table style.

State and persistence behavior: Uses only table/window focus state and the controller outlet.

Dependencies and integration points: Depends on `MyController` and AppKit private highlight override behavior.

Risks: `_highlightColorForCell:` is a private/undocumented override and may break on newer AppKit. Return key behavior depends on characters rather than key codes.

Test signals: Keyboard smoke tests for Return, arrow navigation, empty-character function keys, and selected-row colors in active/inactive windows.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProfileTableView.m -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProgressCell.h -->
# sources/sync-backup/unison/src/uimac/ProgressCell.h

Source read: complete file, 15 lines, 411 bytes, sha256 `cab15ab31bba726d`.

Purpose: Declares a custom cell for displaying per-item synchronization progress, status text, and optional icons in the reconciliation outline.

Important APIs/types/functions: Exports setters for status string, icon, and active state. Internal fields track min/max, active/full/error flags, icon, and status text.

Implementation inventory: discovered Objective-C/C callback methods include `setStatusString, setIcon, setIsActive`.

Control flow: The table delegate configures the cell per row from `ReconItem` progress values before AppKit calls drawing.

State and persistence behavior: State is retained icon/status text and draw flags per cell copy.

Dependencies and integration points: Depends on AppKit `NSCell` and image assets loaded by the implementation.

Risks: The header exposes only setters, so object value and hidden flags must be coordinated by table code and implementation defaults.

Test signals: Render inactive, active, complete, empty, text-only, and icon states in selected and unselected rows.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProgressCell.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProgressCell.m -->
# sources/sync-backup/unison/src/uimac/ProgressCell.m

Source read: complete file, 199 lines, 7263 bytes, sha256 `0f5fb3812aaf592f`.

Purpose: Implements a custom progress/status cell using bundled Transmission-derived progress bar image slices.

Important APIs/types/functions: `+initialize` loads static images, `drawBarImage:width:point:`, `drawBar:point:`, `drawWithFrame:inView:`, setter methods, `copyWithZone:`, and `dealloc` are the key methods.

Implementation inventory: discovered Objective-C/C callback methods include `initialize, init, dealloc, setStatusString, setIcon, setIsActive, drawBarImage, drawBar, drawWithFrame, copyWithZone`.

Control flow: Class initialization loads progress and error assets. Drawing computes progress from `[self objectValue]` over `_minVal.._maxVal`, composites left cap, filled bar, remaining bar, and right cap, then draws optional icon and centered status text with highlight-aware color.

State and persistence behavior: Static image cache is process-wide. Each cell instance tracks active state, icon, and status string. The object value supplies numeric progress.

Dependencies and integration points: Depends on progress image assets under `progressicons`, `Error.tiff`, AppKit image compositing, and `MyController` table display code.

Risks: `setStatusString:` and `setIcon:` retain new values without releasing old values, leaking on repeated updates. `_isError` and `_useFullView` exist but are not publicly configured in this file. Deprecated compositing APIs may require modernization.

Test signals: Use the table during a real sync and inspect progress rendering; run leak checks while progress updates repeatedly; verify all named image assets are present in the bundle.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProgressCell.m -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ReconItem.h -->
# sources/sync-backup/unison/src/uimac/ReconItem.h

Source read: complete file, 80 lines, 1934 bytes, sha256 `91694cf98bce0176`.

Purpose: Declares the model hierarchy for reconciliation rows displayed by the Mac UI: base `ReconItem`, OCaml-backed `LeafReconItem`, and aggregating `ParentReconItem`.

Important APIs/types/functions: Base methods expose path/full path, replica change summaries, direction, icons, file counts/sizes, progress, details, conflict/default state, action/ignore commands, diff behavior, sort keys, and tree navigation. `LeafReconItem` initializes from an OCaml recon item and list index. `ParentReconItem` adds children, sorting, and conflict aggregation.

Implementation inventory: discovered Objective-C/C callback methods include `selected, setSelected, path, fullPath, left, right, direction, fileIcon, fileCount, fileSize, fileSizeString, bytesTransferred, bytesTransferredString, setDirection, doAction, doIgnore, progress, progressString, resetProgress, details, updateDetails, isConflict, changedFromDefault, revertDirection, canDiff, showDiffs, leftSortKey, rightSortKey` and more.

Control flow: `MyController` builds leaves from OCaml data and inserts them into parent nodes for flat or nested table modes. Table delegates ask these objects for display values, sorting keys, and action handlers.

State and persistence behavior: Base state stores parent/path/fullPath, selection flag, cached direction image/sort key, cached size/progress values, and resolved flag. Leaves keep OCaml recon item handles and index; parents keep children and aggregate counts.

Dependencies and integration points: Depends on Cocoa and `OCamlValue` from the bridge; integrates tightly with `MyController` and `ReconTableView`.

Risks: The model mixes UI caches with OCaml-backed mutable synchronization state. Incorrect cache invalidation can show stale direction/progress/file size.

Test signals: Build nested and flat recon trees, sort by every column, execute every action/ignore command, and verify table values after OCaml progress updates.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ReconItem.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ReconItem.m -->
# sources/sync-backup/unison/src/uimac/ReconItem.m

Source read: complete file, 861 lines, 21654 bytes, sha256 `d485e4284dbadaac`.

Purpose: Implements reconciliation row models, display formatting, icon lookup, OCaml-backed leaf operations, and parent aggregation for the Mac UI outline table.

Important APIs/types/functions: Base `ReconItem` implements path/fullPath caching, change icons, file/direction/progress formatting, sort keys, action/ignore stubs, conflict/default checks, and diff hooks. `LeafReconItem` extracts fields from an OCaml recon item, calls OCaml functions for direction/actions/ignore/diff/details/progress, and caches details/progress. `ParentReconItem` manages children, nesting by path components, aggregate file counts/sizes/progress, conflict detection, action fanout, and single-child collapse.

Implementation inventory: discovered Objective-C/C callback methods include `dealloc, parent, setParent, willChange, children, selected, setSelected, path, setPath, fullPath, setFullPath, left, right, changeIconFor, leftIcon, rightIcon, computeFileSize, bytesTransferred, fileCount, fileSize, formatFileSize, fileSizeString, bytesTransferredString, percentTransferred, iconForExtension, fileIcon, dirString, direction` and more.

Control flow: Leaves are created with an OCaml value and index, then inserted under a root parent. The table asks rows for icons/text/progress and sort keys. User actions call `doAction:`/`doIgnore:`, which either call OCaml for a leaf or propagate through children for a parent. Progress and details are fetched lazily from OCaml and reset when needed; parent rows aggregate child states.

State and persistence behavior: Uses static dictionaries for change icons and file-extension icons. Instance caches include full path, direction image/sort string, file size, bytes transferred, details, and progress. Leaf state is backed by retained `OCamlValue` and list index; parent state is retained child arrays and aggregate file count.

Dependencies and integration points: Depends on AppKit image/workspace APIs, Carbon folder icon constants, the bridge, OCaml named functions for recon item field access/actions/diff, and table icon assets.

Risks: Manual memory management is complex. Static image caches can store nil if assets are missing. Bitwise `|` is used in a boolean check. Parent aggregate direction/conflict logic must stay consistent with OCaml action semantics. Lazy caches can become stale without `resetProgress` or direction invalidation.

Test signals: Unit-style construction of leaf/parent trees, action propagation, ignore removal, conflict selection, sorting, collapse behavior, diff enablement, file-size formatting, and progress aggregation. GUI tests should verify icons and direction changes after user commands.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ReconItem.m -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ReconTableView.h -->
# sources/sync-backup/unison/src/uimac/ReconTableView.h

Source read: complete file, 43 lines, 1180 bytes, sha256 `6f701753a49001fd`.

Purpose: Declares the reconciliation outline view subclass and an `NSOutlineView` category for selected-object and auto-expansion helpers.

Important APIs/types/functions: Public actions cover ignore by path/ext/name, copy left-right/right-left, skip, force older/newer, select conflicts, revert, merge, show diff, validation, and editability. The category adds `selectedObjects`, `setSelectedObjects:`, `selectedObjectEnumerator`, and `expandChildrenIfSpace`.

Implementation inventory: discovered Objective-C/C callback methods include `editable, setEditable, validateItem, validateMenuItem, validateToolbarItem, ignorePath, ignoreExt, ignoreName, copyLR, copyRL, leaveAlone, forceOlder, forceNewer, selectConflicts, revert, merge, showDiff, canDiffSelection, selectedObjects, selectedObjectEnumerator, setSelectedObjects, expandChildrenIfSpace`.

Control flow: `MyController` uses this as the outline view for recon items; toolbar/menu/key events call actions here, which in turn delegate to selected `ReconItem` objects.

State and persistence behavior: Only an `editable` flag is stored in the table view. Selection state remains AppKit-owned.

Dependencies and integration points: Depends on AppKit `NSOutlineView`, `ReconItem`, and `MyController` in implementation.

Risks: Action availability depends on `editable`; callers must update it when sync state changes. Category methods assume data source implements outline child APIs.

Test signals: Validate menu/toolbar enablement before scan, after scan, during sync, and after sync; exercise multiple selection and auto-expansion.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ReconTableView.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ReconTableView.m -->
# sources/sync-backup/unison/src/uimac/ReconTableView.m

Source read: complete file, 298 lines, 7716 bytes, sha256 `3385741ea016899c`.

Purpose: Implements selection helpers, keyboard shortcuts, command validation, row auto-expansion, and action dispatch for the reconciliation outline table.

Important APIs/types/functions: Category methods convert selected rows to objects and back, estimate row capacity, and expand children if space permits. `ReconTableView` implements validation, `doAction:`, `doIgnore:`, all IB action methods, `keyDown:`, `canDiffSelection`, and highlight color override.

Implementation inventory: discovered Objective-C/C callback methods include `selectedObjects, setSelectedObjects, selectedObjectEnumerator, rowCapacityWithoutScrolling, _canAcceptRowCountWithoutScrolling, _expandChildrenIfSpace, expandChildrenIfSpace, editable, setEditable, validateItem, validateMenuItem, validateToolbarItem, doIgnore, ignorePath, ignoreExt, ignoreName, doAction, copyLR, copyRL, leaveAlone, forceOlder, forceNewer, selectConflicts, revert, merge, showDiff, keyDown, canDiffSelection` and more.

Control flow: Commands are enabled only when the table is editable, with diff/merge further requiring diff-capable selection. Ignore commands call selected items, ask `MyController updateForIgnore:` for the replacement selection, and reload. Direction commands call selected items, advance to the next row for single selections, and reload. Keyboard shortcuts map `>`, right arrow, `<`, left arrow, `?`, and `/` to common actions.

State and persistence behavior: Stores editability; selection and expansion are owned by the outline view. It relies on model mutations inside `ReconItem`.

Dependencies and integration points: Depends on `ReconItem`, `MyController`, AppKit toolbar/menu validation protocols, and private `_highlightColorForCell:` behavior.

Risks: Several `while (item = [e nextObject])` loops rely on intentional assignment. Selection after ignore assumes the replacement item remains visible. Private highlight override may be fragile. `canDiffSelection` returns YES for empty selection, though callers usually check row count for show diff.

Test signals: Keyboard/action tests for single and multi-selection, ignore flows, conflict selection, diff enablement, row advancement, and selection preservation after table reload/sort.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ReconTableView.m -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/UnisonToolbar.h -->
# sources/sync-backup/unison/src/uimac/UnisonToolbar.h

Source read: complete file, 33 lines, 1045 bytes, sha256 `c8d73bf5120708f0`.

Purpose: Declares the Mac UI toolbar controller subclass that swaps toolbar items according to the current main view.

Important APIs/types/functions: Initializer takes a controller and reconciliation table. Delegate methods create items and expose default/allowed identifiers. `setView:` changes item layout, and `takeTableModeView:` installs the segmented table-mode control.

Implementation inventory: discovered Objective-C/C callback methods include `toolbar, itemIdentifiersForView, toolbarDefaultItemIdentifiers, toolbarAllowedItemIdentifiers, setView, takeTableModeView`.

Control flow: `MyController` creates the toolbar and calls `setView:` whenever the UI transitions between profile, preferences, connecting, and updates states.

State and persistence behavior: Tracks target table/controller, current view name, and retained table-mode view.

Dependencies and integration points: Depends on AppKit `NSToolbar`, `ReconTableView`, and `MyController` actions.

Risks: Toolbar identifiers are string literals in the implementation, so view names/actions must stay synchronized with nib/controller methods.

Test signals: Switch every main view and verify toolbar items, icons, targets, and validation state.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/UnisonToolbar.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/UnisonToolbar.m -->
# sources/sync-backup/unison/src/uimac/UnisonToolbar.m

Source read: complete file, 216 lines, 9309 bytes, sha256 `a8526d92e1134c86`.

Purpose: Implements the Unison toolbar item factory and per-view toolbar layouts.

Important APIs/types/functions: Defines identifiers for Quit/Open/New/Go/Cancel/Save/Restart/Rescan/direction/Merge/Skip/Diff/TableMode. Implements toolbar delegate item creation, default/allowed identifiers, `itemIdentifiersForView:`, `setView:`, and `takeTableModeView:`.

Implementation inventory: discovered Objective-C/C callback methods include `takeTableModeView, toolbar, itemIdentifiersForView, toolbarDefaultItemIdentifiers, toolbarAllowedItemIdentifiers, setView`.

Control flow: Item creation maps identifiers to labels, bundled `.tif` images, targets, and actions on either `NSApp`, `MyController`, or `ReconTableView`. `setView:` diffs desired identifiers against current toolbar items, replacing/inserting/removing as needed. The updates view adds sync/reconcile commands and the table-mode segmented view.

State and persistence behavior: Stores retained table-mode view and current view string. Toolbar autosave/customization is disabled.

Dependencies and integration points: Depends on toolbar image assets, `MyController` action names, `ReconTableView` actions, and AppKit toolbar validation.

Risks: No `dealloc` releases `tableModeView`. `currentView` is assigned, not copied/retained, though callers use stable string literals. Missing images silently produce blank toolbar items.

Test signals: View transition tests should verify item order and targets. Bundle validation should check every `toolbar/*.tif` asset exists and validation disables table actions while not editable.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/UnisonToolbar.m -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/cltool.c -->
# sources/sync-backup/unison/src/uimac/cltool.c

Source read: complete file, 67 lines, 2115 bytes, sha256 `eec058c365f05e43`.

Purpose: Command-line launcher installed inside the Mac app bundle; it finds the GUI app through Launch Services and execs the real bundled `Unison` binary with the original arguments.

Important APIs/types/functions: Single `main` uses `LSFindApplicationForInfo`, `FSRefMakePath`, buffer concatenation with `/Contents/MacOS/Unison`, and `execv`.

Control flow: The tool resolves bundle id `edu.upenn.cis.Unison`, converts the app `FSRef` to a path, appends the executable suffix, replaces `argv[0]` with the absolute executable path, and calls `execv`. On lookup/path/exec failure it writes a user-facing stderr error and exits nonzero.

State and persistence behavior: No persistent state; it uses a fixed 1024-byte stack buffer for the app path.

Dependencies and integration points: Depends on CoreServices/ApplicationServices Launch Services and the app's Info.plist bundle identifier. It is compiled by the Mac UI Makefile with the Carbon framework.

Risks: Uses deprecated FSRef/Launch Services C APIs and a fixed path buffer. If the Launch Services database is stale, users must launch the app once from Finder. Bundle id changes break lookup.

Test signals: After installing/copying the app, run `cltool -version`, server mode, and a normal profile invocation; test renamed app bundles and overlong paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/cltool.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/main.m -->
# sources/sync-backup/unison/src/uimac/main.m

Source read: complete file, 53 lines, 1756 bytes, sha256 `ed2009bdfd179533`.

Purpose: Mac UI process entry point. It strips Finder process-serial-number arguments, starts the OCaml bridge/runtime, handles command-line modes that should run without the GUI, and otherwise enters `NSApplicationMain`.

Important APIs/types/functions: `main` calls `[Bridge startup:argv]`, tests arguments such as `-doc`, `-help`, `-version`, `-server`, `-socket`, and `-ui`, and invokes OCaml `unisonNonGuiStartup` through `ocamlCall`.

Control flow: An autorelease pool is created, a Finder `-psn_` argument is removed when present, OCaml starts before AppKit main loop, and each command-line flag that may be non-GUI triggers OCaml startup. If OCaml exits, the process ends; if it returns because GUI mode is needed, AppKit starts normally.

State and persistence behavior: Mutates local `argc/argv` for Finder launches. No persistent state is stored here.

Dependencies and integration points: Depends on Cocoa, `Bridge`, OCaml command-line startup logic, and `NSApplicationMain` loading the main nib.

Risks: Starting OCaml before AppKit main loop means bridge initialization failures abort the app early. The flag loop can call non-GUI startup multiple times if multiple flags are present unless OCaml exits first. `argv` is `const char **` but later cast in the bridge.

Test signals: Launch from Finder, `open`, direct binary execution, `cltool -version`, server/socket modes, and `-ui graphic` fallback to GUI.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/main.m -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbar.h -->
# sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbar.h

Source read: complete file, 27 lines, 886 bytes, sha256 `639fce8865cee3dc`.

Purpose: Declares a reusable selectable toolbar that swaps a window's content view when selectable toolbar items are chosen.

Important APIs/types/functions: Properties are retained `window` outlet and assign `defaultItemIndex`. Methods include `itemWithIdentifier:`, `selectItemWithIndex:`, and `selectableItemIndexToMainIndex:`.

Implementation inventory: discovered Objective-C/C callback methods include `itemWithIdentifier, selectItemWithIndex, selectableItemIndexToMainIndex`.

Control flow: The implementation waits for the window to become key, selects a default item, and then changes the window content and size on toolbar selection.

State and persistence behavior: Tracks the target window, a blank placeholder view, and default selectable item index.

Dependencies and integration points: Depends on AppKit `NSToolbar` and custom `SSSelectableToolbarItem` linked views.

Risks: A missing `window` outlet prevents content switching. Index methods count only selectable toolbar items, which differs from raw toolbar item indexes.

Test signals: Nib-load with multiple selectable items, default selection, and index mapping around spacers/nonselectable items.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbar.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbar.m -->
# sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbar.m

Source read: complete file, 157 lines, 5155 bytes, sha256 `b5ed19caa6931c0d`.

Purpose: Implements toolbar-driven content switching for preference-style windows.

Important APIs/types/functions: `initWithIdentifier:`, `awakeFromNib`, `selectDefaultItem:`, `setSelectedItemIdentifier:`, `selectItemWithIndex:`, `selectableItemIndexToMainIndex:`, and `itemWithIdentifier:` are the main methods.

Implementation inventory: discovered Objective-C/C callback methods include `initWithIdentifier, dealloc, toolbarItemClicked, selectDefaultItem, awakeFromNib, itemWithIdentifier, setSelectedItemIdentifier, selectItemWithIndex, selectableItemIndexToMainIndex`.

Control flow: Initialization creates a blank view. At nib wakeup, selectable toolbar items get a dummy target/action so they are clickable, and the toolbar registers for the window becoming key. Selecting an item finds its linked view, computes a new window frame preserving toolbar height, temporarily sets the blank content view, animates resizing, installs the linked view, updates the title, and focuses the linked view's `nextKeyView` if present.

State and persistence behavior: Owns `blankView` and retained `window`; selection state is held by `NSToolbar`. Default selection is a numeric index over selectable items.

Dependencies and integration points: Depends on `SSSelectableToolbarItem`, AppKit window/content sizing, and notification center.

Risks: The notification observer is removed only after default selection; if the toolbar deallocs before notification, there is observer risk on older runtimes. `setSelectedItemIdentifier:` assumes linked views have meaningful frames. Window release in `dealloc` must match property ownership from nib binding.

Test signals: Open the preferences window as a normal window and sheet, switch every toolbar item, verify animated resize/title/focus, and close before/after the key-window notification.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbar.m -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbarItem.h -->
# sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbarItem.h

Source read: complete file, 19 lines, 345 bytes, sha256 `7b642afa5b415295`.

Purpose: Declares an `NSToolbarItem` subclass that associates a toolbar item with an `NSView` to display when selected.

Important APIs/types/functions: The single retained IBOutlet property is `linkedView`.

Control flow: `SSSelectableToolbar` reads `linkedView` from selected items and installs it as the window content view.

State and persistence behavior: Owns the linked view reference.

Dependencies and integration points: Depends on Cocoa and Interface Builder wiring.

Risks: Missing linked view wiring makes selection change only the toolbar state without swapping content.

Test signals: Inspect nib connections and switch every toolbar item to verify each has a non-nil linked view.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbarItem.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbarItem.m -->
# sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbarItem.m

Source read: complete file, 22 lines, 355 bytes, sha256 `63f46bdd6b7f49ca`.

Purpose: Implements property synthesis and cleanup for selectable toolbar items.

Important APIs/types/functions: Synthesizes `linkedView` and releases it in `dealloc`.

Implementation inventory: discovered Objective-C/C callback methods include `dealloc`.

Control flow: There is no runtime behavior beyond storage; the owning toolbar performs selection/content switching.

State and persistence behavior: One retained view pointer per toolbar item.

Dependencies and integration points: Depends on `SSSelectableToolbarItem.h` and AppKit `NSToolbarItem` lifecycle.

Risks: Manual reference counting requires the release in `dealloc`; ownership must align with nib loading semantics.

Test signals: Run leak/static analyzer checks and verify toolbar items retain linked views through window switches.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbarItem.m -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/bcache/001 -->
# sources/test-tools/blktests/tests/bcache/001

Source read: complete file, 44 lines, 1113 bytes, sha256 `97e65a177fe13151`.

Purpose: blktests `bcache/001` case, `test bcache setup and teardown`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `test_device_array`; requirement/condition hooks `none beyond sourced group requirements`; sourced libraries `tests/bcache/rc`. It calls helpers/commands `_create_bcache, _remove_bcache, _setup_bcache, bcache`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device_array`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `test bcache setup and teardown` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `bcache`, common libraries, root privileges, udev, and kernel facilities exercised by `test bcache setup and teardown`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `bcache/001`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/bcache/001.out` exists with 3 lines; first signals: `Running bcache/001; number of bcaches: 1; number of bcaches: 2`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/bcache/001 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/bcache/rc -->
# sources/test-tools/blktests/tests/bcache/rc

Source read: complete file, 381 lines, 8400 bytes, sha256 `9d366f7cd4fa0eb2`.

Purpose: Shared bcache test library for creating, registering, removing, wiping, and cleaning bcache devices used by the bcache test group.

Important APIs/types/functions: shell functions `group_requires, _bcache_wipe_devs, _bcache_register, _create_bcache, _remove_bcache, _cleanup_bcache, _setup_bcache`. Key helpers/commands referenced include `_cleanup_bcache, _create_bcache, _have_crypto_algorithm, _have_kernel_options, _have_program, _register_test_cleanup, _remove_bcache, _setup_bcache, dd, blockdev, umount, udevadm, make-bcache, bcache, timeout, cat`.

Control flow: It parses `make-bcache` output for cache-set UUIDs, writes devices to `/sys/fs/bcache/register`, waits for `/dev/bcache/by-uuid` links, stops `/sys/block/bcache*/bcache` devices, unregisters cache sets, and wipes superblock regions before/after tests. Numbered tests source this file before running their `requires`, `device_requires`, `test`, or `test_device` hooks.

State and persistence behavior: The file mutates kernel test devices, sysfs/configfs/debugfs state, temporary files, and test cleanup registrations only while a blktests run is active. Persistent state should be restored by registered cleanup paths and explicit device teardown.

Dependencies and integration points: Integrates with the top-level blktests harness, common shell libraries, root privileges, kernel modules/drivers, udev settlement, and external storage-management tools.

Risks: Cleanup bugs can leave mapped devices, loop/md/dm/bcache state, mounted filesystems, or altered kernel settings behind. Helper assumptions are kernel-version-sensitive and often require destructive test devices.

Test signals: Run the corresponding group with disposable devices and verify skips, cleanup, expected `.out` comparisons, and absence of dmesg warnings or leaked kernel objects after interruption.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/bcache/rc -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/blktrace/001 -->
# sources/test-tools/blktests/tests/blktrace/001

Source read: complete file, 90 lines, 2127 bytes, sha256 `4e4ebb3fa7708547`.

Purpose: blktests `blktrace/001` case, `blktrace zone management command tracing`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/blktrace/rc, common/null_blk`. It calls helpers/commands `_configure_null_blk, _dmesg_since_test_start, _exit_null_blk, _have_module_param, _have_null_blk, _have_program, blkzone, blktrace, grep, cat`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `blktrace zone management command tracing` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `blktrace`, common libraries, root privileges, udev, and kernel facilities exercised by `blktrace zone management command tracing`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `blktrace/001`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/blktrace/001.out` exists with 2 lines; first signals: `Running blktrace/001; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/blktrace/001 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/blktrace/002 -->
# sources/test-tools/blktests/tests/blktrace/002

Source read: complete file, 97 lines, 2452 bytes, sha256 `bcf1382e929319ef`.

Purpose: blktests `blktrace/002` case, `blktrace ftrace corruption with sysfs trace`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/blktrace/rc, common/null_blk`. It calls helpers/commands `_configure_null_blk, _exit_null_blk, _have_null_blk, _have_tracefs, dd, blktrace, grep`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `blktrace ftrace corruption with sysfs trace` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `blktrace`, common libraries, root privileges, udev, and kernel facilities exercised by `blktrace ftrace corruption with sysfs trace`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `blktrace/002`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/blktrace/002.out` exists with 3 lines; first signals: `Running blktrace/002; Trace output looks correct; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/blktrace/002 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/blktrace/rc -->
# sources/test-tools/blktests/tests/blktrace/rc

Source read: complete file, 13 lines, 240 bytes, sha256 `25803a0f0e38fad1`.

Purpose: Small group prerequisite file for blktrace tests.

Important APIs/types/functions: shell functions `group_requires`. Key helpers/commands referenced include `_have_blktrace, _have_program, _have_root, blktrace`.

Control flow: It requires the blktrace tooling stack through `_have_blktrace` and `_have_program blkparse`; individual tests provide their own device setup and tracing logic. Numbered tests source this file before running their `requires`, `device_requires`, `test`, or `test_device` hooks.

State and persistence behavior: The file mutates kernel test devices, sysfs/configfs/debugfs state, temporary files, and test cleanup registrations only while a blktests run is active. Persistent state should be restored by registered cleanup paths and explicit device teardown.

Dependencies and integration points: Integrates with the top-level blktests harness, common shell libraries, root privileges, kernel modules/drivers, udev settlement, and external storage-management tools.

Risks: Cleanup bugs can leave mapped devices, loop/md/dm/bcache state, mounted filesystems, or altered kernel settings behind. Helper assumptions are kernel-version-sensitive and often require destructive test devices.

Test signals: Run the corresponding group with disposable devices and verify skips, cleanup, expected `.out` comparisons, and absence of dmesg warnings or leaked kernel objects after interruption.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/blktrace/rc -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/001 -->
# sources/test-tools/blktests/tests/block/001

Source read: complete file, 62 lines, 1255 bytes, sha256 `d52a580f38dec0db`.

Purpose: blktests `block/001` case, `stress device hotplugging`. It is a harness-executed destructive/block-layer regression or behavior test (TIMED=1).

Important APIs/types/functions: shell hooks `requires, stress_scsi_debug, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/scsi_debug`. It calls helpers/commands `_configure_scsi_debug, _exit_scsi_debug, _have_driver, _have_kernel_option, _have_scsi_debug`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `stress device hotplugging` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `stress device hotplugging`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/001`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/001.out` exists with 4 lines; first signals: `Running block/001; Stressing sd; Stressing sr`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/001 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/002 -->
# sources/test-tools/blktests/tests/block/002

Source read: complete file, 37 lines, 756 bytes, sha256 `48582aac61b66676`.

Purpose: blktests `block/002` case, `remove a device while running blktrace`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/scsi_debug`. It calls helpers/commands `_configure_scsi_debug, _exit_scsi_debug, _have_blktrace, _have_scsi_debug, blktrace`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `remove a device while running blktrace` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `remove a device while running blktrace`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/002`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/002.out` exists with 2 lines; first signals: `Running block/002; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/002 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/003 -->
# sources/test-tools/blktests/tests/block/003

Source read: complete file, 32 lines, 582 bytes, sha256 `0559d2e6a534fdde`.

Purpose: blktests `block/003` case, `run various discard sizes`. It is a harness-executed destructive/block-layer regression or behavior test (TIMED=1).

Important APIs/types/functions: shell hooks `requires, device_requires, test_device`; requirement/condition hooks `requires, device_requires`; sourced libraries `tests/block/rc`. It calls helpers/commands `_fio_perf, _have_fio, _require_test_dev_can_discard`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `run various discard sizes` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `run various discard sizes`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/003`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/003.out` exists with 2 lines; first signals: `Running block/003; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/003 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/004 -->
# sources/test-tools/blktests/tests/block/004

Source read: complete file, 42 lines, 794 bytes, sha256 `46128146d2b2482e`.

Purpose: blktests `block/004` case, `run lots of flushes`. It is a harness-executed destructive/block-layer regression or behavior test (TIMED=1).

Important APIs/types/functions: shell hooks `requires, device_requires, test_device`; requirement/condition hooks `requires, device_requires`; sourced libraries `tests/block/rc`. It calls helpers/commands `_fio_perf, _have_fio, _have_fio_zbd_zonemode, _have_program, _test_dev_is_zoned, _test_dev_max_open_active_zones, _test_dev_set_scheduler, blkzone`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `run lots of flushes` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `run lots of flushes`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/004`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/004.out` exists with 2 lines; first signals: `Running block/004; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/004 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/005 -->
# sources/test-tools/blktests/tests/block/005

Source read: complete file, 57 lines, 1224 bytes, sha256 `a560105cc08ae750`.

Purpose: blktests `block/005` case, `switch schedulers while doing IO`. It is a harness-executed destructive/block-layer regression or behavior test (TIMED=1).

Important APIs/types/functions: shell hooks `requires, device_requires, test_device`; requirement/condition hooks `requires, device_requires`; sourced libraries `tests/block/rc`. It calls helpers/commands `_fio_perf_report, _have_fio, _io_schedulers, _require_test_dev_sysfs, _run_fio_rand_io, _test_dev_is_rotational, _test_dev_queue_set, fio, timeout`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `switch schedulers while doing IO` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `switch schedulers while doing IO`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/005`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/005.out` exists with 2 lines; first signals: `Running block/005; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/005 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/006 -->
# sources/test-tools/blktests/tests/block/006

Source read: complete file, 44 lines, 988 bytes, sha256 `e107a27a592db37b`.

Purpose: blktests `block/006` case, `run null-blk in blocking mode`. It is a harness-executed destructive/block-layer regression or behavior test (TIMED=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/null_blk`. It calls helpers/commands `_configure_null_blk, _exit_null_blk, _fio_perf, _have_fio, _have_module_param, _have_null_blk`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `run null-blk in blocking mode` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `run null-blk in blocking mode`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/006`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/006.out` exists with 2 lines; first signals: `Running block/006; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/006 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/007 -->
# sources/test-tools/blktests/tests/block/007

Source read: complete file, 78 lines, 1559 bytes, sha256 `acaa3f960a33d6d2`.

Purpose: blktests `block/007` case, `test classic and hybrid IO polling`. It is a harness-executed destructive/block-layer regression or behavior test (TIMED=1).

Important APIs/types/functions: shell hooks `requires, device_requires, fallback_device, cleanup_fallback_device, run_fio_job, test_device`; requirement/condition hooks `requires, device_requires`; sourced libraries `tests/block/rc, common/iopoll, common/null_blk`. It calls helpers/commands `_configure_null_blk, _exit_null_blk, _fio_perf, _have_fio_with_poll, _require_test_dev_supports_io_poll_delay, _test_dev_is_rotational, _test_dev_queue_get, _test_dev_queue_set`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `test classic and hybrid IO polling` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `test classic and hybrid IO polling`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/007`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/007.out` exists with 2 lines; first signals: `Running block/007; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/007 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/008 -->
# sources/test-tools/blktests/tests/block/008

Source read: complete file, 100 lines, 2577 bytes, sha256 `d01ecde5935c6dc1`.

Purpose: blktests `block/008` case, `do IO while hotplugging CPUs`. It is a harness-executed destructive/block-layer regression or behavior test (TIMED=1).

Important APIs/types/functions: shell hooks `requires, test_device`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/cpuhotplug`. It calls helpers/commands `_fio_perf_report, _have_cpu_hotplug, _have_fio, _run_fio_rand_io, _test_dev_is_rotational, fio, timeout, cat`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `do IO while hotplugging CPUs` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `do IO while hotplugging CPUs`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/008`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/008.out` exists with 2 lines; first signals: `Running block/008; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/008 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/009 -->
# sources/test-tools/blktests/tests/block/009

Source read: complete file, 44 lines, 1125 bytes, sha256 `f8e6cfcbd8c189c0`.

Purpose: blktests `block/009` case, `check page-cache coherency after BLKDISCARD`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/scsi_debug`. It calls helpers/commands `_exit_scsi_debug, _have_loadable_scsi_debug, _have_program, _init_scsi_debug, dd, blkdiscard, xfs_io`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `check page-cache coherency after BLKDISCARD` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `check page-cache coherency after BLKDISCARD`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/009`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/009.out` exists with 8 lines; first signals: `Running block/009; 0000000 0000 0000 0000 0000 0000 0000 0000 0000; *`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/009 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/010 -->
# sources/test-tools/blktests/tests/block/010

Source read: complete file, 72 lines, 2348 bytes, sha256 `0b41c706f3d395ce`.

Purpose: blktests `block/010` case, `run I/O on null_blk with shared and non-shared tags`. It is a harness-executed destructive/block-layer regression or behavior test (TIMED=1).

Important APIs/types/functions: shell hooks `requires, run_fio_job, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/null_blk`. It calls helpers/commands `_exit_null_blk, _fio_perf, _have_fio, _have_module_param, _have_null_blk, _init_null_blk`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `run I/O on null_blk with shared and non-shared tags` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `run I/O on null_blk with shared and non-shared tags`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/010`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/010.out` exists with 2 lines; first signals: `Running block/010; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/010 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/011 -->
# sources/test-tools/blktests/tests/block/011

Source read: complete file, 98 lines, 2290 bytes, sha256 `6216aa8777206a49`.

Purpose: blktests `block/011` case, `disable PCI device while doing I/O`. It is a harness-executed destructive/block-layer regression or behavior test (TIMED=1).

Important APIs/types/functions: shell hooks `pci_dev_mounted, requires, device_requires, test_device`; requirement/condition hooks `requires, device_requires`; sourced libraries `tests/block/rc`. It calls helpers/commands `_have_fio, _have_program, _require_test_dev_is_pci, _run_fio_rand_io, _test_dev_is_rotational, fio, grep, cat`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `disable PCI device while doing I/O` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `disable PCI device while doing I/O`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/011`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/011.out` exists with 2 lines; first signals: `Running block/011; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/011 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/012 -->
# sources/test-tools/blktests/tests/block/012

Source read: complete file, 36 lines, 1039 bytes, sha256 `46be2363234b2b30`.

Purpose: blktests `block/012` case, `check that a read-only block device fails writes`. It is a harness-executed destructive/block-layer regression or behavior test (TIMED=1).

Important APIs/types/functions: shell hooks `requires, test_device`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc`. It calls helpers/commands `_have_program, dd, blockdev, xfs_io`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `check that a read-only block device fails writes` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `check that a read-only block device fails writes`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/012`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/012.out` exists with 15 lines; first signals: `Running block/012; 0; 0000000 aaaa aaaa aaaa aaaa aaaa aaaa aaaa aaaa`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/012 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/014 -->
# sources/test-tools/blktests/tests/block/014

Source read: complete file, 57 lines, 1477 bytes, sha256 `362832bba6d5c7c5`.

Purpose: blktests `block/014` case, `run null-blk with blk-mq and timeout injection configured`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/null_blk`. It calls helpers/commands `_configure_null_blk, _exit_null_blk, _have_module_param, _have_null_blk, _init_null_blk, _io_schedulers, _module_file_exists, dd, timeout`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `run null-blk with blk-mq and timeout injection configured` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `run null-blk with blk-mq and timeout injection configured`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/014`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/014.out` exists with 2 lines; first signals: `Running block/014; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/014 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/015 -->
# sources/test-tools/blktests/tests/block/015

Source read: complete file, 53 lines, 1409 bytes, sha256 `33aa3ad8be7247cd`.

Purpose: blktests `block/015` case, `run null-blk on different schedulers with requeue injection configured`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/null_blk`. It calls helpers/commands `_configure_null_blk, _exit_null_blk, _have_module_param, _have_null_blk, _init_null_blk, _io_schedulers, _module_file_exists, dd`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `run null-blk on different schedulers with requeue injection configured` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `run null-blk on different schedulers with requeue injection configured`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/015`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/015.out` exists with 2 lines; first signals: `Running block/015; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/015 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/016 -->
# sources/test-tools/blktests/tests/block/016

Source read: complete file, 49 lines, 1175 bytes, sha256 `cf560e02361d8cde`.

Purpose: blktests `block/016` case, `send a signal to a process waiting on a frozen queue`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/null_blk`. It calls helpers/commands `_configure_null_blk, _exit_null_blk, _have_null_blk, dd`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `send a signal to a process waiting on a frozen queue` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `send a signal to a process waiting on a frozen queue`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/016`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/016.out` exists with 2 lines; first signals: `Running block/016; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/016 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/017 -->
# sources/test-tools/blktests/tests/block/017

Source read: complete file, 76 lines, 1916 bytes, sha256 `3113cacf18efffdd`.

Purpose: blktests `block/017` case, `do I/O and check the inflight counter`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, show_inflight, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/null_blk`. It calls helpers/commands `_configure_null_blk, _exit_null_blk, _have_null_blk, dd`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `do I/O and check the inflight counter` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `do I/O and check the inflight counter`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/017`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/017.out` exists with 14 lines; first signals: `Running block/017; sysfs inflight reads 1; sysfs inflight writes 0`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/017 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/018 -->
# sources/test-tools/blktests/tests/block/018

Source read: complete file, 61 lines, 1437 bytes, sha256 `ff046009584b09a2`.

Purpose: blktests `block/018` case, `do I/O and check iostats times`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, init_times, show_times, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/null_blk`. It calls helpers/commands `_configure_null_blk, _exit_null_blk, _have_null_blk, dd`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `do I/O and check iostats times` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `do I/O and check iostats times`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/018`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/018.out` exists with 10 lines; first signals: `Running block/018; read 0 s; write 0 s`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/018 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/019 -->
# sources/test-tools/blktests/tests/block/019

Source read: complete file, 45 lines, 854 bytes, sha256 `aacff94cfe6bc943`.

Purpose: blktests `block/019` case, `break PCI link device while doing I/O`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, device_requires, test_device`; requirement/condition hooks `requires, device_requires`; sourced libraries `tests/block/rc`. It calls helpers/commands `_have_fio, _have_program, _require_test_dev_in_hotplug_slot, _require_test_dev_is_pci, _run_fio_rand_io, fio`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `break PCI link device while doing I/O` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `break PCI link device while doing I/O`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/019`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/019.out` exists with 2 lines; first signals: `Running block/019; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/019 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/020 -->
# sources/test-tools/blktests/tests/block/020

Source read: complete file, 46 lines, 1153 bytes, sha256 `08e8a770d23c848c`.

Purpose: blktests `block/020` case, `run null-blk on different schedulers with only one hardware tag`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/null_blk`. It calls helpers/commands `_configure_null_blk, _exit_null_blk, _fio_perf, _have_fio, _have_null_blk, _io_schedulers, cat`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `run null-blk on different schedulers with only one hardware tag` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `run null-blk on different schedulers with only one hardware tag`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/020`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/020.out` exists with 2 lines; first signals: `Running block/020; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/020 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/021 -->
# sources/test-tools/blktests/tests/block/021

Source read: complete file, 42 lines, 899 bytes, sha256 `a8b1d6aa86379ba9`.

Purpose: blktests `block/021` case, `read/write nr_requests on null-blk with different schedulers`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/null_blk`. It calls helpers/commands `_configure_null_blk, _exit_null_blk, _have_null_blk, _io_schedulers, cat`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `read/write nr_requests on null-blk with different schedulers` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `read/write nr_requests on null-blk with different schedulers`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/021`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/021.out` exists with 2 lines; first signals: `Running block/021; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/021 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/022 -->
# sources/test-tools/blktests/tests/block/022

Source read: complete file, 56 lines, 1066 bytes, sha256 `cba97f0ab819c25d`.

Purpose: blktests `block/022` case, `Test hang caused by freeze/unfreeze sequence`. It is a harness-executed destructive/block-layer regression or behavior test (TIMED=1).

Important APIs/types/functions: shell hooks `requires, hotplug_test, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/null_blk`. It calls helpers/commands `_exit_null_blk, _have_module_param, _have_null_blk, _init_null_blk, _require_min_cpus`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `Test hang caused by freeze/unfreeze sequence` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `Test hang caused by freeze/unfreeze sequence`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/022`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/022.out` exists with 2 lines; first signals: `Running block/022; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/022 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/023 -->
# sources/test-tools/blktests/tests/block/023

Source read: complete file, 34 lines, 742 bytes, sha256 `5be1d33b79584b56`.

Purpose: blktests `block/023` case, `do I/O on all null_blk queue modes`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/null_blk`. It calls helpers/commands `_configure_null_blk, _exit_null_blk, _have_null_blk, dd`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `do I/O on all null_blk queue modes` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `do I/O on all null_blk queue modes`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/023`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/023.out` exists with 4 lines; first signals: `Running block/023; Queue mode 0; Queue mode 2`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/023 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/024 -->
# sources/test-tools/blktests/tests/block/024

Source read: complete file, 68 lines, 1845 bytes, sha256 `4f04b6be54ff2c1e`.

Purpose: blktests `block/024` case, `do I/O faster than a jiffy and check iostats times`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, init_times, show_times, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/null_blk`. It calls helpers/commands `_configure_null_blk, _exit_null_blk, _have_null_blk, dd`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `do I/O faster than a jiffy and check iostats times` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `do I/O faster than a jiffy and check iostats times`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/024`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/024.out` exists with 10 lines; first signals: `Running block/024; read 0 s; write 0 s`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/024 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/025 -->
# sources/test-tools/blktests/tests/block/025

Source read: complete file, 34 lines, 791 bytes, sha256 `b5191d3957a84eff`.

Purpose: blktests `block/025` case, `do a huge discard with 4k sector size`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/scsi_debug`. It calls helpers/commands `_exit_scsi_debug, _have_loadable_scsi_debug, _init_scsi_debug, blkdiscard`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `do a huge discard with 4k sector size` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `do a huge discard with 4k sector size`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/025`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/025.out` exists with 2 lines; first signals: `Running block/025; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/025 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/027 -->
# sources/test-tools/blktests/tests/block/027

Source read: complete file, 90 lines, 2221 bytes, sha256 `0929463ff031a398`.

Purpose: blktests `block/027` case, `stress device hotplugging with running fio jobs and different schedulers`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, scsi_debug_stress_remove, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/scsi_debug, common/cgroup`. It calls helpers/commands `_configure_scsi_debug, _exit_cgroup2, _exit_scsi_debug, _have_cgroup2_controller, _have_fio, _have_scsi_debug, _init_cgroup2, fio, sed`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `stress device hotplugging with running fio jobs and different schedulers` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `stress device hotplugging with running fio jobs and different schedulers`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/027`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/027.out` exists with 2 lines; first signals: `Running block/027; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/027 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/028 -->
# sources/test-tools/blktests/tests/block/028

Source read: complete file, 45 lines, 1033 bytes, sha256 `52a16a2a83b18898`.

Purpose: blktests `block/028` case, `do I/O on scsi_debug with DIF/DIX enabled`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `requires, test_pi, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/scsi_debug`. It calls helpers/commands `_exit_scsi_debug, _have_loadable_scsi_debug, _init_scsi_debug, dd, blockdev`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `do I/O on scsi_debug with DIF/DIX enabled` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `do I/O on scsi_debug with DIF/DIX enabled`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/028`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/028.out` exists with 9 lines; first signals: `Running block/028; Test(dix:0 dif:0) complete; Test(dix:0 dif:1) complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/028 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/029 -->
# sources/test-tools/blktests/tests/block/029

Source read: complete file, 51 lines, 1210 bytes, sha256 `d037539623f17c69`.

Purpose: blktests `block/029` case, `trigger blk_mq_update_nr_hw_queues()`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, modify_nr_hw_queues, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/null_blk`. It calls helpers/commands `_configure_null_blk, _exit_null_blk, _have_fio, _have_null_blk, fio`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `trigger blk_mq_update_nr_hw_queues()` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `trigger blk_mq_update_nr_hw_queues()`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/029`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/029.out` exists with 1 lines; first signals: `Passed`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/029 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/030 -->
# sources/test-tools/blktests/tests/block/030

Source read: complete file, 73 lines, 2401 bytes, sha256 `29cbfb8262390267`.

Purpose: blktests `block/030` case, `trigger the blk_mq_realloc_hw_ctxs() error path`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/null_blk`. It calls helpers/commands `_configure_null_blk, _exit_null_blk, _have_module_param, _have_null_blk, _init_null_blk, _module_file_exists`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `trigger the blk_mq_realloc_hw_ctxs() error path` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `trigger the blk_mq_realloc_hw_ctxs() error path`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/030`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/030.out` exists with 1 lines; first signals: `Passed`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/030 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/031 -->
# sources/test-tools/blktests/tests/block/031

Source read: complete file, 56 lines, 1604 bytes, sha256 `3ad86521131e3009`.

Purpose: blktests `block/031` case, `do IO on null-blk with a host tag set`. It is a harness-executed destructive/block-layer regression or behavior test (TIMED=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/null_blk`. It calls helpers/commands `_configure_null_blk, _exit_null_blk, _have_fio, _have_module_param, _have_null_blk, _have_null_blk_feature, _init_null_blk, fio`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `do IO on null-blk with a host tag set` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `do IO on null-blk with a host tag set`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/031`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/031.out` exists with 1 lines; first signals: `Passed`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/031 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/032 -->
# sources/test-tools/blktests/tests/block/032

Source read: complete file, 43 lines, 792 bytes, sha256 `df50a3cd154f62df`.

Purpose: blktests `block/032` case, `remove one mounted device`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/xfs, common/scsi_debug`. It calls helpers/commands `_exit_scsi_debug, _have_loadable_scsi_debug, _have_xfs, _init_scsi_debug, umount, udevadm`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `remove one mounted device` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `remove one mounted device`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/032`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/032.out` exists with 2 lines; first signals: `Running block/032; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/032 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/033 -->
# sources/test-tools/blktests/tests/block/033

Source read: complete file, 39 lines, 776 bytes, sha256 `307244f8d5d338ea`.

Purpose: blktests `block/033` case, `add & delete ublk device and test if gendisk is leaked`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/ublk`. It calls helpers/commands `_exit_ublk, _have_ublk, _init_ublk, dd, udevadm`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `add & delete ublk device and test if gendisk is leaked` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `add & delete ublk device and test if gendisk is leaked`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/033`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/033.out` exists with 2 lines; first signals: `Running block/033; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/033 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/034 -->
# sources/test-tools/blktests/tests/block/034

Source read: complete file, 60 lines, 1369 bytes, sha256 `7b3607eaf9a5f9d7`.

Purpose: blktests `block/034` case, `load/unload null_blk memory_backed=1 to check memleak`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1). It samples `/proc/meminfo` around repeated `null_blk memory_backed=1` load/write/unload cycles and flags a leak only if memory remains consumed in most iterations.

Important APIs/types/functions: shell hooks `requires, run_nullblk_dd, free_memory, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/null_blk`. It calls helpers/commands `_exit_null_blk, _have_module, _have_module_param, _have_program, _init_null_blk, dd, sed`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `load/unload null_blk memory_backed=1 to check memleak` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `load/unload null_blk memory_backed=1 to check memleak`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/034`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/034.out` exists with 2 lines; first signals: `Running block/034; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/034 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/035 -->
# sources/test-tools/blktests/tests/block/035

Source read: complete file, 92 lines, 2137 bytes, sha256 `1a3d002773b9c517`.

Purpose: blktests `block/035` case, `shared tag set fairness`. It is a harness-executed destructive/block-layer regression or behavior test (TIMED=1). It creates two memory-backed null_blk devices sharing a tag set with very different completion latencies, runs io_uring fio against both, records IOPS in `TEST_RUN`, and fails if the fast queue underperforms the slow one.

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/null_blk`. It calls helpers/commands `_configure_null_blk, _exit_null_blk, _have_fio, _have_module, _have_module_param, _init_null_blk, _io_uring_enable, _io_uring_restore, fio, sed`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `shared tag set fairness` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `shared tag set fairness`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/035`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/035.out` exists with 2 lines; first signals: `Running block/035; Passed`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/035 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/036 -->
# sources/test-tools/blktests/tests/block/036

Source read: complete file, 87 lines, 2017 bytes, sha256 `40b65ab2f6cdcf7f`.

Purpose: blktests `block/036` case, `test return EIO from BLKRRPART for whole-dev`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1). It saves global debugfs `fail_make_request` settings and per-device `make-it-fail`, forces I/O failure, runs `blockdev --rereadpt`, and expects an Input/output error before restoring all fault-injection settings.

Important APIs/types/functions: shell hooks `_have_debugfs, requires, test_device`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc`. It calls helpers/commands `_have_debugfs, blockdev, grep, cat`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `test return EIO from BLKRRPART for whole-dev` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `test return EIO from BLKRRPART for whole-dev`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/036`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/036.out` exists with 3 lines; first signals: `Running block/036; Return EIO for BLKRRPART on bad disk; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/036 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/037 -->
# sources/test-tools/blktests/tests/block/037

Source read: complete file, 54 lines, 1237 bytes, sha256 `e204053c3be599d4`.

Purpose: blktests `block/037` case, `test cgroup vs. scsi_debug rebind`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, scsi_debug_rebind, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/scsi_debug, common/cgroup`. It calls helpers/commands `_configure_scsi_debug, _exit_cgroup2, _exit_scsi_debug, _have_cgroup2_controller, _have_scsi_debug, _init_cgroup2`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `test cgroup vs. scsi_debug rebind` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `test cgroup vs. scsi_debug rebind`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/037`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/037.out` exists with 2 lines; first signals: `Running block/037; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/037 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/038 -->
# sources/test-tools/blktests/tests/block/038

Source read: complete file, 54 lines, 1247 bytes, sha256 `59a46be88f1a4511`.

Purpose: blktests `block/038` case, `Test null-blk concurrent power/submit_queues operations`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, null_blk_power_loop, null_blk_submit_queues_loop, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/null_blk`. It calls helpers/commands `_configure_null_blk, _exit_null_blk, _have_null_blk, _have_null_blk_feature`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `Test null-blk concurrent power/submit_queues operations` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `Test null-blk concurrent power/submit_queues operations`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/038`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/038.out` exists with 2 lines; first signals: `Running block/038; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/038 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/039 -->
# sources/test-tools/blktests/tests/block/039

Source read: complete file, 54 lines, 1109 bytes, sha256 `4988e8cad57ec616`.

Purpose: blktests `block/039` case, `test race between set_blocksize and read paths`. It is a harness-executed destructive/block-layer regression or behavior test (TIMED=1).

Important APIs/types/functions: shell hooks `requires, change_blocksize, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/null_blk`. It calls helpers/commands `_configure_null_blk, _exit_null_blk, _have_fio, _run_fio, blockdev`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `test race between set_blocksize and read paths` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `test race between set_blocksize and read paths`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/039`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/039.out` exists with 2 lines; first signals: `Running block/039; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/039 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/040 -->
# sources/test-tools/blktests/tests/block/040

Source read: complete file, 73 lines, 1770 bytes, sha256 `0b07e2fdf54f9191`.

Purpose: blktests `block/040` case, `test blk_mq_update_nr_hw_queues() vs switch elevator`. It is a harness-executed destructive/block-layer regression or behavior test (TIMED=1).

Important APIs/types/functions: shell hooks `requires, modify_io_sched, modify_nr_hw_queues, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/null_blk`. It calls helpers/commands `_configure_null_blk, _exit_null_blk, _have_fio, _have_null_blk, _io_schedulers, fio`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `test blk_mq_update_nr_hw_queues() vs switch elevator` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `test blk_mq_update_nr_hw_queues() vs switch elevator`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/040`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/040.out` exists with 1 lines; first signals: `Passed`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/040 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/041 -->
# sources/test-tools/blktests/tests/block/041

Source read: complete file, 78 lines, 1702 bytes, sha256 `5010294ef6e9f8c5`.

Purpose: blktests `block/041` case, `io_uring read with PI metadata buffer on block device`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `device_requires, requires, test_device`; requirement/condition hooks `device_requires, requires`; sourced libraries `tests/block/rc, common/nvme`. It calls helpers/commands `_have_fio, _have_fio_ver, _have_kernel_option, _io_uring_enable, _io_uring_restore, _require_test_dev_is_nvme, _run_fio, _test_dev_disables_extended_lba, _test_dev_has_metadata`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `io_uring read with PI metadata buffer on block device` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `io_uring read with PI metadata buffer on block device`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/041`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/041.out` exists with 2 lines; first signals: `Running block/041; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/041 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/042 -->
# sources/test-tools/blktests/tests/block/042

Source read: complete file, 35 lines, 1090 bytes, sha256 `80cd63481ba90805`.

Purpose: blktests `block/042` case, `Test unusual direct-io offsets`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `device_requires, test_device`; requirement/condition hooks `device_requires`; sourced libraries `tests/block/rc`. It calls helpers/commands `_require_test_dev_sysfs, cat, src/dio-offsets`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `Test unusual direct-io offsets` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `Test unusual direct-io offsets`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/042`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/042.out` exists with 2 lines; first signals: `Running block/042; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/042 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/043 -->
# sources/test-tools/blktests/tests/block/043

Source read: complete file, 33 lines, 643 bytes, sha256 `e8dede1b13ebf8d1`.

Purpose: blktests `block/043` case, `Test userspace metadata offsets`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `device_requires, requires, test_device`; requirement/condition hooks `device_requires, requires`; sourced libraries `tests/block/rc, common/nvme`. It calls helpers/commands `_have_kernel_option, _test_dev_disables_extended_lba, _test_dev_has_metadata, src/metadata`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `Test userspace metadata offsets` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `Test userspace metadata offsets`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/043`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/043.out` exists with 2 lines; first signals: `Running block/043; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/043 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/rc -->
# sources/test-tools/blktests/tests/block/rc

Source read: complete file, 11 lines, 161 bytes, sha256 `9937d6056b98b86a`.

Purpose: Block test group prerequisite shim.

Important APIs/types/functions: shell functions `group_requires`. Key helpers/commands referenced include `_have_root`.

Control flow: The group-level `rc` only declares `group_requires` and relies on each numbered test plus common libraries (`null_blk`, `scsi_debug`, `nvme`, `ublk`) to state concrete prerequisites. Numbered tests source this file before running their `requires`, `device_requires`, `test`, or `test_device` hooks.

State and persistence behavior: The file mutates kernel test devices, sysfs/configfs/debugfs state, temporary files, and test cleanup registrations only while a blktests run is active. Persistent state should be restored by registered cleanup paths and explicit device teardown.

Dependencies and integration points: Integrates with the top-level blktests harness, common shell libraries, root privileges, kernel modules/drivers, udev settlement, and external storage-management tools.

Risks: Cleanup bugs can leave mapped devices, loop/md/dm/bcache state, mounted filesystems, or altered kernel settings behind. Helper assumptions are kernel-version-sensitive and often require destructive test devices.

Test signals: Run the corresponding group with disposable devices and verify skips, cleanup, expected `.out` comparisons, and absence of dmesg warnings or leaked kernel objects after interruption.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/rc -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/dm/001 -->
# sources/test-tools/blktests/tests/dm/001

Source read: complete file, 29 lines, 597 bytes, sha256 `6024093c28793e03`.

Purpose: blktests `dm/001` case, `reload a dm with maps to itself`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test_device`; requirement/condition hooks `requires`; sourced libraries `tests/dm/rc`. It calls helpers/commands `_have_kver, dmsetup`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `reload a dm with maps to itself` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `dm`, common libraries, root privileges, udev, and kernel facilities exercised by `reload a dm with maps to itself`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `dm/001`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/dm/001.out` exists with 2 lines; first signals: `Running dm/001; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/dm/001 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/dm/002 -->
# sources/test-tools/blktests/tests/dm/002

Source read: complete file, 43 lines, 1118 bytes, sha256 `13211093f5c63b4e`.

Purpose: blktests `dm/002` case, `dm-dust general functionality test`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test_device`; requirement/condition hooks `requires`; sourced libraries `tests/dm/rc`. It calls helpers/commands `_have_driver, dd, blockdev, dmsetup, grep`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `dm-dust general functionality test` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `dm`, common libraries, root privileges, udev, and kernel facilities exercised by `dm-dust general functionality test`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `dm/002`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/dm/002.out` exists with 10 lines; first signals: `Running dm/002; countbadblocks: 3 badblock(s) found; 60`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/dm/002 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/dm/003 -->
# sources/test-tools/blktests/tests/dm/003

Source read: complete file, 84 lines, 2140 bytes, sha256 `dc8f70aecc159e30`.

Purpose: blktests `dm/003` case, `test unmap write zeroes sysfs interface with dm devices`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, setup_test_device, cleanup_test_device, test`; requirement/condition hooks `requires`; sourced libraries `tests/dm/rc, common/scsi_debug`. It calls helpers/commands `_configure_scsi_debug, _exit_scsi_debug, _have_scsi_debug, _real_dev, blockdev, dmsetup, cat`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `test unmap write zeroes sysfs interface with dm devices` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `dm`, common libraries, root privileges, udev, and kernel facilities exercised by `test unmap write zeroes sysfs interface with dm devices`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `dm/003`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/dm/003.out` exists with 2 lines; first signals: `Running dm/003; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/dm/003 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/dm/rc -->
# sources/test-tools/blktests/tests/dm/rc

Source read: complete file, 13 lines, 196 bytes, sha256 `568e03e98a665b23`.

Purpose: Device-mapper test group prerequisites.

Important APIs/types/functions: shell functions `group_requires`. Key helpers/commands referenced include `_have_driver, _have_program, _have_root`.

Control flow: It requires `dmsetup` and the `dm-mod` driver so numbered tests can create linear, dust, and discard/zeroes mapping scenarios. Numbered tests source this file before running their `requires`, `device_requires`, `test`, or `test_device` hooks.

State and persistence behavior: The file mutates kernel test devices, sysfs/configfs/debugfs state, temporary files, and test cleanup registrations only while a blktests run is active. Persistent state should be restored by registered cleanup paths and explicit device teardown.

Dependencies and integration points: Integrates with the top-level blktests harness, common shell libraries, root privileges, kernel modules/drivers, udev settlement, and external storage-management tools.

Risks: Cleanup bugs can leave mapped devices, loop/md/dm/bcache state, mounted filesystems, or altered kernel settings behind. Helper assumptions are kernel-version-sensitive and often require destructive test devices.

Test signals: Run the corresponding group with disposable devices and verify skips, cleanup, expected `.out` comparisons, and absence of dmesg warnings or leaked kernel objects after interruption.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/dm/rc -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/001 -->
# sources/test-tools/blktests/tests/loop/001

Source read: complete file, 57 lines, 1321 bytes, sha256 `6de5e21e6b61304f`.

Purpose: blktests `loop/001` case, `scan loop device partitions`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, find_loop_partition_devices, find_loop_partition_sysfs, test`; requirement/condition hooks `requires`; sourced libraries `tests/loop/rc`. It calls helpers/commands `_have_program, losetup, parted, udevadm, sed`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `scan loop device partitions` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `loop`, common libraries, root privileges, udev, and kernel facilities exercised by `scan loop device partitions`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `loop/001`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/loop/001.out` exists with 10 lines; first signals: `Running loop/001; Partition devices; 1`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/001 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/002 -->
# sources/test-tools/blktests/tests/loop/002

Source read: complete file, 50 lines, 1310 bytes, sha256 `2427b6fc7fff8395`.

Purpose: blktests `loop/002` case, `try various loop device block sizes`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/loop/rc`. It calls helpers/commands `_have_loop_set_block_size, _have_program, _have_src_program, dd, xfs_io, losetup, cat`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `try various loop device block sizes` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `loop`, common libraries, root privileges, udev, and kernel facilities exercised by `try various loop device block sizes`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `loop/002`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/loop/002.out` exists with 19 lines; first signals: `Running loop/002; Checking default block size; 512`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/002 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/003 -->
# sources/test-tools/blktests/tests/loop/003

Source read: complete file, 27 lines, 511 bytes, sha256 `07c600f4241b13c8`.

Purpose: blktests `loop/003` case, `time opening and closing an unbound loop device`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/loop/rc`. It calls helpers/commands `_have_src_program, losetup`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `time opening and closing an unbound loop device` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `loop`, common libraries, root privileges, udev, and kernel facilities exercised by `time opening and closing an unbound loop device`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `loop/003`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/loop/003.out` exists with 3 lines; first signals: `Running loop/003; Test took 0 seconds; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/003 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/004 -->
# sources/test-tools/blktests/tests/loop/004

Source read: complete file, 46 lines, 951 bytes, sha256 `7dc1e1c8722052cf`.

Purpose: blktests `loop/004` case, `combine loop direct I/O mode and a custom block size`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/loop/rc, common/scsi_debug`. It calls helpers/commands `_exit_scsi_debug, _have_loadable_scsi_debug, _have_loop_set_block_size, _have_program, _have_src_program, _init_scsi_debug, dd, xfs_io, losetup, udevadm, cat`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `combine loop direct I/O mode and a custom block size` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `loop`, common libraries, root privileges, udev, and kernel facilities exercised by `combine loop direct I/O mode and a custom block size`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `loop/004`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/loop/004.out` exists with 4 lines; first signals: `Running loop/004; 1; 769bd186841c10e5b1106b55986206c0e87fc05a7f565fdee01b5abcaff6ae78  -`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/004 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/005 -->
# sources/test-tools/blktests/tests/loop/005

Source read: complete file, 34 lines, 695 bytes, sha256 `be91b779aae1f0d6`.

Purpose: blktests `loop/005` case, `call LOOP_GET_STATUS{,64} with a NULL arg`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/loop/rc`. It calls helpers/commands `_have_src_program, losetup`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `call LOOP_GET_STATUS{,64} with a NULL arg` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `loop`, common libraries, root privileges, udev, and kernel facilities exercised by `call LOOP_GET_STATUS{,64} with a NULL arg`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `loop/005`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/loop/005.out` exists with 4 lines; first signals: `Running loop/005; Got EINVAL; Got EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/005 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/006 -->
# sources/test-tools/blktests/tests/loop/006

Source read: complete file, 73 lines, 1530 bytes, sha256 `53676562e4b4ea11`.

Purpose: blktests `loop/006` case, `change loop backing file while creating/removing another loop device`. It is a harness-executed destructive/block-layer regression or behavior test (TIMED=1).

Important APIs/types/functions: shell hooks `requires, run_setter, run_switcher, test`; requirement/condition hooks `requires`; sourced libraries `tests/loop/rc`. It calls helpers/commands `_have_src_program, losetup, sed`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `change loop backing file while creating/removing another loop device` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `loop`, common libraries, root privileges, udev, and kernel facilities exercised by `change loop backing file while creating/removing another loop device`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `loop/006`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/loop/006.out` exists with 2 lines; first signals: `Running loop/006; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/006 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/007 -->
# sources/test-tools/blktests/tests/loop/007

Source read: complete file, 39 lines, 878 bytes, sha256 `61c98439eae4bd93`.

Purpose: blktests `loop/007` case, `update loop device capacity with filesystem`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/loop/rc`. It calls helpers/commands `_have_program, losetup, mkfs.ext4, mount, umount`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `update loop device capacity with filesystem` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `loop`, common libraries, root privileges, udev, and kernel facilities exercised by `update loop device capacity with filesystem`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `loop/007`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/loop/007.out` exists with 2 lines; first signals: `Running loop/007; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/007 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/008 -->
# sources/test-tools/blktests/tests/loop/008

Source read: complete file, 46 lines, 1162 bytes, sha256 `6ecaecd70f585233`.

Purpose: blktests `loop/008` case, `setup GPT and ESP on a raw disk image`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/loop/rc`. It calls helpers/commands `_have_program, losetup, parted, mkfs.vfat`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `setup GPT and ESP on a raw disk image` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `loop`, common libraries, root privileges, udev, and kernel facilities exercised by `setup GPT and ESP on a raw disk image`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `loop/008`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/loop/008.out` exists with 2 lines; first signals: `Running loop/008; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/008 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/009 -->
# sources/test-tools/blktests/tests/loop/009

Source read: complete file, 69 lines, 1873 bytes, sha256 `f943659f130485a8`.

Purpose: blktests `loop/009` case, `check that LOOP_CONFIGURE sends uevents for partitions`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/loop/rc`. It calls helpers/commands `losetup, sfdisk, udevadm, timeout, grep, sed`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `check that LOOP_CONFIGURE sends uevents for partitions` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `loop`, common libraries, root privileges, udev, and kernel facilities exercised by `check that LOOP_CONFIGURE sends uevents for partitions`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `loop/009`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/loop/009.out` exists with 3 lines; first signals: `Running loop/009; KERNEL add      /devices/virtual/block/loop_/loop_p1 (block); Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/009 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/010 -->
# sources/test-tools/blktests/tests/loop/010

Source read: complete file, 94 lines, 2012 bytes, sha256 `accbfbc6a0c094b1`.

Purpose: blktests `loop/010` case, `check stale loop partition`. It is a harness-executed destructive/block-layer regression or behavior test (TIMED=1).

Important APIs/types/functions: shell hooks `requires, create_loop, detach_loop, test`; requirement/condition hooks `requires`; sourced libraries `tests/loop/rc`. It calls helpers/commands `_dmesg_since_test_start, _have_kver, _have_program, losetup, parted, mkfs.xfs, udevadm, blkid, grep`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `check stale loop partition` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `loop`, common libraries, root privileges, udev, and kernel facilities exercised by `check stale loop partition`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `loop/010`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/loop/010.out` exists with 2 lines; first signals: `Running loop/010; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/010 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/011 -->
# sources/test-tools/blktests/tests/loop/011

Source read: complete file, 41 lines, 1172 bytes, sha256 `93754ebf055b7f35`.

Purpose: blktests `loop/011` case, `Make sure unsupported backing file fallocate does not fill dmesg with errors`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/loop/rc`. It calls helpers/commands `_dmesg_since_test_start, _have_kver, _have_program, dd, losetup, mkfs.ext2, mount, umount, grep`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `Make sure unsupported backing file fallocate does not fill dmesg with errors` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `loop`, common libraries, root privileges, udev, and kernel facilities exercised by `Make sure unsupported backing file fallocate does not fill dmesg with errors`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `loop/011`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/loop/011.out` exists with 3 lines; first signals: `Running loop/011; Found 1 error(s) in dmesg; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/011 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/012 -->
# sources/test-tools/blktests/tests/loop/012

Source read: complete file, 77 lines, 2219 bytes, sha256 `eab020d39f13105c`.

Purpose: blktests `loop/012` case, `check for spurious partition removal when partscan is enabled`. It is a harness-executed destructive/block-layer regression or behavior test (TIMED=1). It creates a GPT image, monitors kernel partition uevents, repeatedly attaches/detaches a partscan loop device for `TIMEOUT`, and fails if extra add/remove events indicate the stale partition race.

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/loop/rc`. It calls helpers/commands `_have_program, _have_systemd_ver, losetup, sfdisk, udevadm, grep`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `check for spurious partition removal when partscan is enabled` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `loop`, common libraries, root privileges, udev, and kernel facilities exercised by `check for spurious partition removal when partscan is enabled`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `loop/012`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/loop/012.out` exists with 2 lines; first signals: `Running loop/012; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/012 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/rc -->
# sources/test-tools/blktests/tests/loop/rc

Source read: complete file, 20 lines, 361 bytes, sha256 `30c1aee777df11c5`.

Purpose: Loop-device group prerequisite and feature helper file.

Important APIs/types/functions: shell functions `group_requires, _have_loop_set_block_size`. Key helpers/commands referenced include `_have_loop, _have_loop_set_block_size, _have_root, losetup`.

Control flow: It requires root and loop support, and defines `_have_loop_set_block_size` by invoking the local `loblksize` helper on a free loop device. Numbered tests source this file before running their `requires`, `device_requires`, `test`, or `test_device` hooks.

State and persistence behavior: The file mutates kernel test devices, sysfs/configfs/debugfs state, temporary files, and test cleanup registrations only while a blktests run is active. Persistent state should be restored by registered cleanup paths and explicit device teardown.

Dependencies and integration points: Integrates with the top-level blktests harness, common shell libraries, root privileges, kernel modules/drivers, udev settlement, and external storage-management tools.

Risks: Cleanup bugs can leave mapped devices, loop/md/dm/bcache state, mounted filesystems, or altered kernel settings behind. Helper assumptions are kernel-version-sensitive and often require destructive test devices.

Test signals: Run the corresponding group with disposable devices and verify skips, cleanup, expected `.out` comparisons, and absence of dmesg warnings or leaked kernel objects after interruption.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/rc -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/md/001 -->
# sources/test-tools/blktests/tests/md/001

Source read: complete file, 88 lines, 1933 bytes, sha256 `cf7a8b0be439a52f`.

Purpose: blktests `md/001` case, `Raid with bitmap on tcp nvmet with opt-io-size over bitmap size`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, setup_underlying_device, cleanup_underlying_device, setup_nvme_over_tcp, cleanup_nvme_over_tcp, test`; requirement/condition hooks `requires`; sourced libraries `tests/md/rc, common/brd, common/nvme`. It calls helpers/commands `_cleanup_brd, _create_nvmet_host, _create_nvmet_port, _create_nvmet_subsystem, _find_nvme_ns, _have_brd, _have_driver, _have_nvme_cli_with_json_support, _have_program, _init_brd, _nvme_connect_subsys, _nvme_disconnect_subsys, _nvmet_target_cleanup, _require_nvme_trtype, _setup_nvmet, blockdev, dmsetup, mdadm`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `Raid with bitmap on tcp nvmet with opt-io-size over bitmap size` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `md`, common libraries, root privileges, udev, and kernel facilities exercised by `Raid with bitmap on tcp nvmet with opt-io-size over bitmap size`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `md/001`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/md/001.out` exists with 3 lines; first signals: `Running md/001; disconnected 1 controller(s); Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/md/001 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/md/002 -->
# sources/test-tools/blktests/tests/md/002

Source read: complete file, 41 lines, 713 bytes, sha256 `1fad4990acbfd8a6`.

Purpose: blktests `md/002` case, `test md atomic writes`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/scsi/rc, common/scsi_debug, common/xfs`. It calls helpers/commands `_configure_scsi_debug, _exit_scsi_debug, _have_scsi_debug, _md_atomics_test`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `test md atomic writes` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `md`, common libraries, root privileges, udev, and kernel facilities exercised by `test md atomic writes`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `md/002`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/md/002.out` exists with 197 lines; first signals: `Running md_atomics_test; TEST 1 raid0 step 1 - Verify md sysfs atomic attributes matches - pass; TEST 2 raid0 step 1 - Verify sysfs atomic attributes - pass`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/md/002 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/md/003 -->
# sources/test-tools/blktests/tests/md/003

Source read: complete file, 36 lines, 712 bytes, sha256 `b20cb1fa7fb3c1e8`.

Purpose: blktests `md/003` case, `test md atomic writes for NVMe drives`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, device_requires, test_device_array`; requirement/condition hooks `requires, device_requires`; sourced libraries `tests/md/rc, common/nvme, common/xfs`. It calls helpers/commands `_md_atomics_test, _nvme_requires, _require_test_dev_is_nvme, _require_test_dev_size`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device_array`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `test md atomic writes for NVMe drives` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `md`, common libraries, root privileges, udev, and kernel facilities exercised by `test md atomic writes for NVMe drives`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `md/003`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/md/003.out` exists with 197 lines; first signals: `Running md_atomics_test; TEST 1 raid0 step 1 - Verify md sysfs atomic attributes matches - pass; TEST 2 raid0 step 1 - Verify sysfs atomic attributes - pass`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/md/003 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/md/004 -->
# sources/test-tools/blktests/tests/md/004

Source read: complete file, 98 lines, 2676 bytes, sha256 `951febb747dde09b`.

Purpose: blktests `md/004` case, `test unmap write zeroes sysfs interface with MD devices`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, setup_test_device, cleanup_test_device, test`; requirement/condition hooks `requires`; sourced libraries `tests/md/rc, common/scsi_debug`. It calls helpers/commands `_configure_scsi_debug, _exit_scsi_debug, _have_driver, _have_scsi_debug, _real_dev, mdadm, cat`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `test unmap write zeroes sysfs interface with MD devices` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `md`, common libraries, root privileges, udev, and kernel facilities exercised by `test unmap write zeroes sysfs interface with MD devices`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `md/004`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/md/004.out` exists with 2 lines; first signals: `Running md/004; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/md/004 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/md/rc -->
# sources/test-tools/blktests/tests/md/rc

Source read: complete file, 459 lines, 15978 bytes, sha256 `c877496caee859bc`.

Purpose: MD/stacked-device shared helper library, especially for atomic-write validation across mdraid, dm, and LVM personalities.

Important APIs/types/functions: shell functions `group_requires, _stacked_atomic_test_requires, _max_pow_of_two_factor, _md_atomics_boundaries_max, _get_vgsize, _md_atomics_test`. Key helpers/commands referenced include `_have_driver, _have_kver, _have_program, _have_root, _have_xfs_io_atomic_write, _md_atomics_boundaries_max, _md_atomics_test, mdadm, vgcreate, lvcreate, lvremove, vgremove, grep, sed`.

Control flow: It requires `mdadm`, probes stacked atomic-write prerequisites, creates md arrays or dm/LVM devices for raid0/raid1/raid10/linear/stripe/mirror, checks sysfs/statx atomic limits, runs atomic `xfs_io` writes, and tears down arrays, superblocks, LVs, and VGs. Numbered tests source this file before running their `requires`, `device_requires`, `test`, or `test_device` hooks.

State and persistence behavior: The file mutates kernel test devices, sysfs/configfs/debugfs state, temporary files, and test cleanup registrations only while a blktests run is active. Persistent state should be restored by registered cleanup paths and explicit device teardown.

Dependencies and integration points: Integrates with the top-level blktests harness, common shell libraries, root privileges, kernel modules/drivers, udev settlement, and external storage-management tools.

Risks: Cleanup bugs can leave mapped devices, loop/md/dm/bcache state, mounted filesystems, or altered kernel settings behind. Helper assumptions are kernel-version-sensitive and often require destructive test devices.

Test signals: Run the corresponding group with disposable devices and verify skips, cleanup, expected `.out` comparisons, and absence of dmesg warnings or leaked kernel objects after interruption.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/md/rc -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/001 -->
# sources/test-tools/blktests/tests/meta/001

Source read: complete file, 14 lines, 214 bytes, sha256 `57ba82770135c655`.

Purpose: blktests `meta/001` case, `do nothing`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `test`; requirement/condition hooks `none beyond sourced group requirements`; sourced libraries `tests/meta/rc`. It calls helpers/commands `basic shell builtins`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `do nothing` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `meta`, common libraries, root privileges, udev, and kernel facilities exercised by `do nothing`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `meta/001`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/meta/001.out` exists with 2 lines; first signals: `Running meta/001; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/001 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/002 -->
# sources/test-tools/blktests/tests/meta/002

Source read: complete file, 14 lines, 228 bytes, sha256 `2bc2aed5b93e5c0e`.

Purpose: blktests `meta/002` case, `do nothing`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `test_device`; requirement/condition hooks `none beyond sourced group requirements`; sourced libraries `tests/meta/rc`. It calls helpers/commands `basic shell builtins`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `do nothing` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `meta`, common libraries, root privileges, udev, and kernel facilities exercised by `do nothing`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `meta/002`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/meta/002.out` exists with 2 lines; first signals: `Running meta/002; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/002 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/003 -->
# sources/test-tools/blktests/tests/meta/003

Source read: complete file, 15 lines, 270 bytes, sha256 `9449a1ff2fae81ff`.

Purpose: blktests `meta/003` case, `exit with non-zero status`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `test`; requirement/condition hooks `none beyond sourced group requirements`; sourced libraries `tests/meta/rc`. It calls helpers/commands `basic shell builtins`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `exit with non-zero status` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `meta`, common libraries, root privileges, udev, and kernel facilities exercised by `exit with non-zero status`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `meta/003`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/meta/003.out` exists with 2 lines; first signals: `Running meta/003; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/003 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/004 -->
# sources/test-tools/blktests/tests/meta/004

Source read: complete file, 15 lines, 284 bytes, sha256 `c00652dd0d9f2ff6`.

Purpose: blktests `meta/004` case, `exit with non-zero status`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `test_device`; requirement/condition hooks `none beyond sourced group requirements`; sourced libraries `tests/meta/rc`. It calls helpers/commands `basic shell builtins`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `exit with non-zero status` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `meta`, common libraries, root privileges, udev, and kernel facilities exercised by `exit with non-zero status`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `meta/004`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/meta/004.out` exists with 2 lines; first signals: `Running meta/004; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/004 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/005 -->
# sources/test-tools/blktests/tests/meta/005

Source read: complete file, 13 lines, 212 bytes, sha256 `f795b7908e9b65c1`.

Purpose: blktests `meta/005` case, `produce bad output`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `test`; requirement/condition hooks `none beyond sourced group requirements`; sourced libraries `tests/meta/rc`. It calls helpers/commands `basic shell builtins`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `produce bad output` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `meta`, common libraries, root privileges, udev, and kernel facilities exercised by `produce bad output`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `meta/005`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/meta/005.out` exists with 2 lines; first signals: `Running meta/005; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/005 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/006 -->
# sources/test-tools/blktests/tests/meta/006

Source read: complete file, 15 lines, 293 bytes, sha256 `176200ab8093b3fd`.

Purpose: blktests `meta/006` case, `produce lots of bad output`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `test`; requirement/condition hooks `none beyond sourced group requirements`; sourced libraries `tests/meta/rc`. It calls helpers/commands `basic shell builtins`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `produce lots of bad output` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `meta`, common libraries, root privileges, udev, and kernel facilities exercised by `produce lots of bad output`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `meta/006`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/meta/006.out` exists with 2 lines; first signals: `Running meta/006; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/006 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/007 -->
# sources/test-tools/blktests/tests/meta/007

Source read: complete file, 17 lines, 253 bytes, sha256 `abbb20f8cad389b1`.

Purpose: blktests `meta/007` case, `skip in requires()`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/meta/rc`. It calls helpers/commands `basic shell builtins`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `skip in requires()` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `meta`, common libraries, root privileges, udev, and kernel facilities exercised by `skip in requires()`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `meta/007`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/meta/007.out` exists with 2 lines; first signals: `Running meta/007; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/007 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/008 -->
# sources/test-tools/blktests/tests/meta/008

Source read: complete file, 17 lines, 291 bytes, sha256 `a47b9ab065bd6a19`.

Purpose: blktests `meta/008` case, `skip in device_requires()`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `device_requires, test_device`; requirement/condition hooks `device_requires`; sourced libraries `tests/meta/rc`. It calls helpers/commands `basic shell builtins`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `skip in device_requires()` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `meta`, common libraries, root privileges, udev, and kernel facilities exercised by `skip in device_requires()`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `meta/008`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/meta/008.out` exists with 2 lines; first signals: `Running meta/008; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/008 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/009 -->
# sources/test-tools/blktests/tests/meta/009

Source read: complete file, 19 lines, 266 bytes, sha256 `9b26313e2cdd1c92`.

Purpose: blktests `meta/009` case, `check dmesg`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/meta/rc`. It calls helpers/commands `_have_writeable_kmsg`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `check dmesg` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `meta`, common libraries, root privileges, udev, and kernel facilities exercised by `check dmesg`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `meta/009`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/meta/009.out` exists with 2 lines; first signals: `Running meta/009; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/009 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/010 -->
# sources/test-tools/blktests/tests/meta/010

Source read: complete file, 20 lines, 297 bytes, sha256 `09e60638d34c5749`.

Purpose: blktests `meta/010` case, `disable check dmesg`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/meta/rc`. It calls helpers/commands `_have_writeable_kmsg`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `disable check dmesg` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `meta`, common libraries, root privileges, udev, and kernel facilities exercised by `disable check dmesg`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `meta/010`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/meta/010.out` exists with 2 lines; first signals: `Running meta/010; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/010 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/011 -->
# sources/test-tools/blktests/tests/meta/011

Source read: complete file, 20 lines, 295 bytes, sha256 `9326c14b1c9c4150`.

Purpose: blktests `meta/011` case, `filter dmesg`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/meta/rc`. It calls helpers/commands `_have_writeable_kmsg`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `filter dmesg` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `meta`, common libraries, root privileges, udev, and kernel facilities exercised by `filter dmesg`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `meta/011`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/meta/011.out` exists with 2 lines; first signals: `Running meta/011; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/011 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/012 -->
# sources/test-tools/blktests/tests/meta/012

Source read: complete file, 18 lines, 387 bytes, sha256 `54ebf6a47b1967c7`.

Purpose: blktests `meta/012` case, `record pid and random junk`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `test`; requirement/condition hooks `none beyond sourced group requirements`; sourced libraries `tests/meta/rc`. It calls helpers/commands `basic shell builtins`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `record pid and random junk` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `meta`, common libraries, root privileges, udev, and kernel facilities exercised by `record pid and random junk`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `meta/012`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/meta/012.out` exists with 2 lines; first signals: `Running meta/012; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/012 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/013 -->
# sources/test-tools/blktests/tests/meta/013

Source read: complete file, 17 lines, 293 bytes, sha256 `3eef505d6df94352`.

Purpose: blktests `meta/013` case, `skip test_device() in requires()`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `requires, test_device`; requirement/condition hooks `requires`; sourced libraries `tests/meta/rc`. It calls helpers/commands `basic shell builtins`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `skip test_device() in requires()` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `meta`, common libraries, root privileges, udev, and kernel facilities exercised by `skip test_device() in requires()`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `meta/013`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/meta/013.out` exists with 2 lines; first signals: `Running meta/013; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/013 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/014 -->
# sources/test-tools/blktests/tests/meta/014

Source read: complete file, 13 lines, 221 bytes, sha256 `58a62b2e334291ef`.

Purpose: blktests `meta/014` case, `skip in test()`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `test`; requirement/condition hooks `none beyond sourced group requirements`; sourced libraries `tests/meta/rc`. It calls helpers/commands `basic shell builtins`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `skip in test()` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `meta`, common libraries, root privileges, udev, and kernel facilities exercised by `skip in test()`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `meta/014`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/meta/014.out` exists with 2 lines; first signals: `Running meta/014; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/014 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/015 -->
# sources/test-tools/blktests/tests/meta/015

Source read: complete file, 13 lines, 242 bytes, sha256 `3f57dda80370b73a`.

Purpose: blktests `meta/015` case, `skip in test_device()`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `test_device`; requirement/condition hooks `none beyond sourced group requirements`; sourced libraries `tests/meta/rc`. It calls helpers/commands `basic shell builtins`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `skip in test_device()` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `meta`, common libraries, root privileges, udev, and kernel facilities exercised by `skip in test_device()`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `meta/015`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/meta/015.out` exists with 2 lines; first signals: `Running meta/015; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/015 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/016 -->
# sources/test-tools/blktests/tests/meta/016

Source read: complete file, 29 lines, 494 bytes, sha256 `33d65426f7a59ef1`.

Purpose: blktests `meta/016` case, `repeat test()`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `set_conditions, test`; requirement/condition hooks `set_conditions`; sourced libraries `tests/meta/rc`. It calls helpers/commands `basic shell builtins`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `repeat test()` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `meta`, common libraries, root privileges, udev, and kernel facilities exercised by `repeat test()`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `meta/016`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/meta/016.out` exists with 2 lines; first signals: `Running meta/016; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/016 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/017 -->
# sources/test-tools/blktests/tests/meta/017

Source read: complete file, 29 lines, 515 bytes, sha256 `daa04b83d42f7c67`.

Purpose: blktests `meta/017` case, `repeat test_device()`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `set_conditions, test_device`; requirement/condition hooks `set_conditions`; sourced libraries `tests/meta/rc`. It calls helpers/commands `basic shell builtins`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `repeat test_device()` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `meta`, common libraries, root privileges, udev, and kernel facilities exercised by `repeat test_device()`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `meta/017`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/meta/017.out` exists with 2 lines; first signals: `Running meta/017; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/017 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/018 -->
# sources/test-tools/blktests/tests/meta/018

Source read: complete file, 43 lines, 685 bytes, sha256 `8b7de9f8bb56b753`.

Purpose: blktests `meta/018` case, `combine two set_conditions() hooks`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag). It combines two condition generators with `_set_combined_conditions`, expecting the runner to enumerate the Cartesian product and propagate condition descriptions.

Important APIs/types/functions: shell hooks `conditions_x, conditions_y, set_conditions, test`; requirement/condition hooks `set_conditions`; sourced libraries `tests/meta/rc`. It calls helpers/commands `basic shell builtins`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `combine two set_conditions() hooks` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `meta`, common libraries, root privileges, udev, and kernel facilities exercised by `combine two set_conditions() hooks`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `meta/018`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/meta/018.out` exists with 2 lines; first signals: `Running meta/018; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/018 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/019 -->
# sources/test-tools/blktests/tests/meta/019

Source read: complete file, 55 lines, 847 bytes, sha256 `522a15d20dbdd0a7`.

Purpose: blktests `meta/019` case, `combine three set_conditions() hooks`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag). It extends the condition-combination coverage to three generators, validating larger Cartesian-product enumeration and per-condition state propagation.

Important APIs/types/functions: shell hooks `conditions_x, conditions_y, conditions_z, set_conditions, test`; requirement/condition hooks `set_conditions`; sourced libraries `tests/meta/rc`. It calls helpers/commands `basic shell builtins`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `combine three set_conditions() hooks` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `meta`, common libraries, root privileges, udev, and kernel facilities exercised by `combine three set_conditions() hooks`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `meta/019`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/meta/019.out` exists with 2 lines; first signals: `Running meta/019; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/019 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/020 -->
# sources/test-tools/blktests/tests/meta/020

Source read: complete file, 14 lines, 287 bytes, sha256 `7e13f217e3d05549`.

Purpose: blktests `meta/020` case, `do nothing in test_device_array()`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `test_device_array`; requirement/condition hooks `none beyond sourced group requirements`; sourced libraries `tests/meta/rc`. It calls helpers/commands `basic shell builtins`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device_array`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `do nothing in test_device_array()` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `meta`, common libraries, root privileges, udev, and kernel facilities exercised by `do nothing in test_device_array()`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `meta/020`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/meta/020.out` exists with 2 lines; first signals: `Running meta/020; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/020 -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/rc -->
# sources/test-tools/blktests/tests/meta/rc

Source read: complete file, 64 lines, 2230 bytes, sha256 `e080e5e7ee04d6d7`.

Purpose: Self-test helper file for the blktests runner's metadata, skip, dmesg, and condition-combination behavior.

Important APIs/types/functions: shell functions `group_requires, group_device_requires, fake_bug_on`. Key helpers/commands referenced include `cat`.

Control flow: It defines group and device requirements, writes synthetic dmesg content, and supplies hooks used by numbered meta tests to validate runner filtering, `TEST_RUN` metadata capture, and `_set_combined_conditions` expansion. Numbered tests source this file before running their `requires`, `device_requires`, `test`, or `test_device` hooks.

State and persistence behavior: The file mutates kernel test devices, sysfs/configfs/debugfs state, temporary files, and test cleanup registrations only while a blktests run is active. Persistent state should be restored by registered cleanup paths and explicit device teardown.

Dependencies and integration points: Integrates with the top-level blktests harness, common shell libraries, root privileges, kernel modules/drivers, udev settlement, and external storage-management tools.

Risks: Cleanup bugs can leave mapped devices, loop/md/dm/bcache state, mounted filesystems, or altered kernel settings behind. Helper assumptions are kernel-version-sensitive and often require destructive test devices.

Test signals: Run the corresponding group with disposable devices and verify skips, cleanup, expected `.out` comparisons, and absence of dmesg warnings or leaked kernel objects after interruption.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/rc -->
