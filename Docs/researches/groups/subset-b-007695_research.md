# subset-b-007695 Research

Grouped research for the requested OpenAFS Windows application-library and afsclass sources. Each section is source-tree-aligned and wrapped for reconciliation into the matching per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/hashlist.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/hashlist.cpp

## Purpose
Implements the `EXPANDARRAY`, `HASHLIST`, `HASHLISTKEY`, and `ENUMERATION` classes declared in `hashlist.h`, plus general string hash helpers. The module is a Windows-only in-memory indexed object list: callers store raw object pointers while one or more hash keys provide fast lookup and keyed enumeration.

## Important APIs and Control Flow
`EXPANDARRAY` lazily allocates fixed-size heaps of element slots using `GlobalAlloc`; `GetAt` returns an existing element pointer and `SetAt` allocates the containing heap before optionally copying element bytes. `HASHLIST::Add` inserts a non-NULL object into a sparse array slot, links it into the global doubly linked list, adds an internal pointer-index key entry, and indexes the object through all user keys. `Remove` uses the internal key to find a slot in near constant time, unlinks global and per-key entries, and clears the object pointer without compacting the array. `Update` refreshes every user key for an existing object without changing list order.

`CreateKey` allocates a `HASHLISTKEY`, stores it in the growable key table, and indexes existing live objects. `HASHLISTKEY::Add`, `Remove`, and `Resize` maintain bucket chains backed by an `EXPANDARRAY` parallel to the owning list's object slots. `FindFirst`, `FindLast`, and `GetFirstObject` hash caller data, walk one bucket, and call the supplied compare callback. `ENUMERATION` snapshots next/previous slot links in `PrepareWalk`, holds the list critical section for its lifetime, and self-deletes when traversal reaches the end.

## State, Dependencies, and Integration
The persistent state is process memory only: object slot arrays, key arrays, bucket arrays, linked-list indices, and a `CRITICAL_SECTION`. The class does not own user objects. It depends on Win32 allocation and synchronization APIs, `TaLocale.h` allocation macros such as `New2`/`Delete`, and caller-provided callback functions. `HashString`, `HashAnsiString`, and `HashUnicodeString` are utility hashers used by clients that key on text.

## Risks and Test Signals
Enumeration leaks are severe because an unfinished `ENUMERATION` keeps the critical section locked. Several paths rely on recursive critical sections because key operations enter the owning list while callers already hold it. `KeyIndex_HashData` casts pointers through `DWORD`, which is risky for 64-bit builds despite `HASHVALUE` being `UINT_PTR`. String hashing reads unaligned `DWORD` values from character buffers. `FreeDebugInfo` frees only the bucket array and not the `HASHLISTKEYDEBUGINFO` object itself, so callers may leak unless they also delete it. Good tests would cover duplicate pointer add/remove, keyed duplicate suppression, key creation after population, update during enumeration, resize thresholds, enumeration deletion behavior, and 64-bit pointer hashing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/hashlist.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/hashlist.h -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/hashlist.h

## Purpose
Declares a generic, thread-safe object list with optional hash indexes. The header is also the primary usage documentation: it explains ownership, enumeration lifetime, key callbacks, duplicate handling, update requirements, and safe object deletion patterns.

## Important APIs and Types
Core exported types are `EXPANDARRAY`, `HASHLIST`, `HASHLISTKEY`, and `ENUMERATION`/`ENUM`. `HASHLISTENTRY` stores a generic object pointer, its hash value, and slot links. `HASHLISTKEYDEBUGINFO` reports bucket counts and distribution effectiveness. Callback typedefs define the key contract: compare object to data, hash object, and hash raw lookup data.

`HASHLIST` exposes `Add`, `Remove`, `Update`, `AddUnique`, `fIsInList`, `CreateKey`, `FindKey`, `RemoveKey`, list enumeration, object accessors, count retrieval, and explicit `Enter`/`Leave` locking. `HASHLISTKEY` exposes hash callback wrappers, keyed enumeration/object lookup, keyed membership, and debug distribution helpers. `ENUMERATION` exposes `GetObject`, `FindNext`, and `FindPrevious`, with destructor-based lock release.

## State, Dependencies, and Integration
The declarations assume Win32 types (`PVOID`, `LPCTSTR`, `CRITICAL_SECTION`, `BOOL`) and OpenAFS's `EXPORTED` convention. The owning list stores raw pointers and never deletes caller objects, so integration code must manage object lifetimes and call `Update` after mutating indexed fields. `SetCriticalSection` lets a caller supply a shared lock to coordinate hashlist access with broader object state.

## Risks and Test Signals
The public contract makes enumeration lifetime part of synchronization; callers that break early must delete the enumeration. `AddUnique` semantics differ depending on whether a key is provided: no key means pointer uniqueness, key means compare-callback uniqueness. Callback correctness is critical: hash-object/hash-data must agree with compare or lookup silently misses entries. Header examples are the main test signal; additional tests should assert the documented auto-delete behavior at traversal end, explicit delete behavior mid-traversal, key lookup with colliding values, and update requirements after changing key fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/hashlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/regexp.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/regexp.cpp

## Purpose
Implements a compact custom regular-expression matcher for TCHAR strings. It supports a small historical expression language: anchors, single-character wildcards, star repetition, character sets and negated sets, escaped capture groups, and numeric backreferences.

## Important APIs and Control Flow
`SetExpression` calls `Compile`, which translates source text into `m_achCompiled`. Marker bytes encode token type, repetition, parenthesis boundaries, references, end-of-line, and end-of-pattern. A leading `^` sets `m_fMatchFromStart`; a terminal `$` becomes `markENDLINE`; `.` and `?` become any-character tokens; `[...]` expands ranges into explicit character lists; `\(`, `\)`, and `\1` through `\9` become capture and reference tokens.

`Matches` initializes capture start/end arrays. Anchored expressions call `MatchSubset` once, character-led unanchored expressions scan for the first literal before trying subsets, and other unanchored expressions try every position. `MatchSubset` is a recursive backtracking interpreter. Starred tokens consume greedily, then backtrack by recursively testing the remainder. Capture tokens record string positions; references compare current text with the captured substring through `CompareParen`. `fIsRegExp` inspects compiled tokens and treats anything except a pure literal sequence as a regexp.

## State, Dependencies, and Integration
The object stores only the compiled buffer and anchor flag. Static helpers create temporary `REGEXP` instances. It depends on Win32 error codes (`ERROR_INVALID_PARAMETER`, `ERROR_BAD_FORMAT`, `ERROR_META_EXPANSION_TOO_LONG`) and TCHAR APIs. No external regex library is used, so callers get deterministic but limited syntax.

## Risks and Test Signals
The compiled buffer is fixed at 512 TCHARs and range expansion can overflow if size checks are off by one. Character-set length is stored in a character slot and iterated with byte casts, so non-ASCII or Unicode ranges are suspect. `CompareParen` assumes valid captured bounds and simple character equality. Recursive backtracking can be expensive on adversarial expressions. Tests should cover invalid empty expressions, unmatched parentheses and brackets, literal `*` handling, anchors, terminal `$`, positive and negative sets, expanded ranges, repeated backreferences, Unicode builds, and maximum-length compiled expressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/regexp.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/regexp.h -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/regexp.h

## Purpose
Declares the `REGEXP` class and documents its simplified pattern language. The API is intentionally small: compile an expression into an object, match strings repeatedly, or use static one-shot helpers.

## Important APIs and Types
`cchCOMPILED_BUFFER_MAX` fixes the internal compiled pattern size at 512 TCHARs. `nCOMPILED_PARENS_MAX` limits backreference-capable capture groups to nine. Public methods are the default and expression constructors, destructor, `SetExpression`, instance/static `Matches`, and instance/static `fIsRegExp`.

Private helpers expose the implementation shape: `Compile` produces the internal marker stream, `MatchSubset` interprets it against a candidate string, `CompareParen` implements backreferences, and `fIsInCharSet` handles inclusive and exclusive sets. State is `m_fMatchFromStart` plus `m_achCompiled`.

## State, Dependencies, and Integration
The class is exported through the same `EXPORTED` convention as the rest of afsapplib and depends on Win32/TCHAR types. It is not a POSIX or PCRE-compatible interface; consumers must use the documented subset (`^`, `$`, `.`, `?`, `*`, `[]`, `[^]`, escaped groups and numeric references). Objects are reusable via `SetExpression`.

## Risks and Test Signals
Because the header exposes no error retrieval, callers must inspect the Boolean return from `SetExpression` and use `GetLastError` if they need details. The static `Matches` helper does not surface compile failure separately from no-match. Test signals should include API-level tests for expression reuse, no-expression defaults, static helper behavior, and `fIsRegExp` distinguishing literal strings from true patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/regexp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/resize.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/resize.cpp

## Purpose
Implements generic Win32 dialog resizing and splitter support. A caller supplies `rwWindowData` rules for each child control, then `ResizeWindow` applies movement and sizing deltas when the parent changes size or its client area changes.

## Important APIs and Control Flow
`ResizeWindow` records the previous parent rectangle in a global `WindowList`, optionally moves the parent for `rwaMoveToHere`, computes deltas for normal resize or `rwaNewClientArea`, and uses `BeginDeferWindowPos`/`DeferWindowPos` to update child windows according to `raMove*`, `raSize*`, and center-half flags. It handles repaint and resize notification flags after all positions are deferred.

`rwFindOrAddWnd` registers a tracked window and installs `Resize_DialogProc` through the subclass helper. `Resize_DialogProc` handles `WM_GETMINMAXINFO` by calling `FindResizeLimits` and removes tracking on `WM_DESTROY`. `CreateSplitter` determines a splitter rectangle between two controls, registers horizontal and vertical splitter window classes, allocates `SplitterData`, and creates a child splitter. `SplitterWndProc` tracks mouse capture and calls `ResizeSplitter`, which clamps movement with `FindSplitterMinMax` and applies child deltas. `GetRectInParent` converts screen coordinates to parent client coordinates.

## State, Dependencies, and Integration
State is global and in-process: tracked windows in `awl`, per-window saved rectangles and half-pixel remainder accumulators, static splitter class registration, and per-splitter `SplitterData`. Dependencies include Win32 windowing APIs, `al_resource.h` cursor IDs, afsapplib allocation helpers, `subclass.h`, and `TaLocale.h`.

## Risks and Test Signals
The global tracking list and splitter registration are unsynchronized. `rwFindAndRemoveWnd` calls `Subclass_RemoveHook(awl[ii].hWnd, hWnd)` even though the hook installed was `Resize_DialogProc`, which looks like a removal bug. In `SplitterWndProc`, `WM_DESTROY` frees `SplitterData` only inside `if (psd->fDragging)`, so non-dragging splitters may leak. The code uses `SetWindowLong`/`GetWindowLong` and a `GWL_USER` fallback, which is fragile for pointer-sized data. Tests should exercise resize deltas, odd-pixel center accumulation, min/max tracking, destroy cleanup, splitter drag clamping, hook removal, and both horizontal and vertical layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/resize.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/resize.h -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/resize.h

## Purpose
Declares the public dialog-resizing contract for afsapplib. The comments provide the expected integration pattern: call `ResizeWindow` during dialog initialization, on `WM_SIZE`, and after adding UI elements that alter the client area.

## Important APIs and Types
`rwAction` selects the operation: move parent then resize guts, fix child controls against a new parent size, resync without moving children, or account for a changed client area. `ra*` flags describe each child rule: leave alone, move or size in positive or negative X/Y, move or size by half the delta, repaint, and notify. `rwWindowData` binds a child control ID to flags and optional packed minimum/maximum sizes. `idDEFAULT` supplies default behavior and `idENDLIST` terminates rule arrays.

Exports are `CreateSplitter`, `DeleteSplitter`, `ResizeWindow`, and `GetRectInParent`.

## State, Dependencies, and Integration
The header includes `windows.h` and uses HWND, RECT, LONG, and DWORD. Rule arrays are caller-owned and must remain valid while the window is tracked because the implementation caches the last `rwWindowData *`. Splitter creation also needs a caller-owned delta variable and rule table.

## Risks and Test Signals
The API encodes min/max dimensions in low/high words of DWORD fields, which limits range and requires callers to pack values correctly. The behavior of `rwaNewClientArea` depends on `RECT` being interpreted as a delta, not a literal rectangle. Test signals should validate documented sample layouts, default-rule fallback, min/max packing, repaint/notify flags, and splitter cleanup through `DeleteSplitter`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/resize.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/settings.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/settings.cpp

## Purpose
Implements registry convenience functions for versioned binary settings, generic binary values, multi-string values, and recursive key deletion.

## Important APIs and Control Flow
`StoreSettings` allocates a buffer, prefixes the caller's structure with a `WORD` version, and stores it as `REG_BINARY`. `RestoreSettings` obtains the stored size, reads the full value, validates version compatibility by equal major byte and stored minor byte greater than or equal to expected minor, and copies only the expected structure size into the caller's buffer. `EraseSettings` deletes a named value.

`GetRegValueSize`, `GetBinaryRegValue`, and `SetBinaryRegValue` are generic wrappers around `RegOpenKey`/`RegCreateKey`, `RegQueryValueEx`, and `RegSetValueEx`. `GetMultiStringRegValue` loads `REG_MULTI_SZ` data into an allocated string buffer; `SetMultiStringRegValue` computes the double-NUL-terminated byte length and writes it. `RegDeltreeKey` recursively enumerates and deletes subkeys before deleting the requested key.

## State, Dependencies, and Integration
Persistence is the Windows registry under the parent key and base path selected by the caller. The file depends on Win32 registry APIs, `winerror.h`, `TaLocale.h` allocation helpers, and the version macros in `settings.h`. Callers own defaulting behavior when restore fails.

## Risks and Test Signals
Several functions close `hk` instead of `hkFinal` after opening or creating a subkey, which can leak the opened handle and accidentally close the caller-provided parent handle. `GetBinaryRegValue` does not validate that the registry type is `REG_BINARY`. `RestoreSettings` rejects stored data shorter than `sizeof(WORD)+cbStructure`, which conflicts with the header's claim that older/larger minor-version compatibility can ignore trailing fields. String copies and sizes assume trusted registry data. Tests should cover handle lifetime, major/minor restore rules, shorter and longer stored structures, registry type mismatches, multi-string round trips, and recursive deletion on nested trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/settings.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/settings.h -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/settings.h

## Purpose
Declares registry settings utilities and documents the versioning scheme for persistent binary application state. It is intended for simple global settings structs saved at shutdown and restored on startup.

## Important APIs and Types
The header defines convenience aliases for root registry hives (`HKCR`, `HKCU`, `HKLM`) and byte/version macros (`HIBYTE`, `LOBYTE`, `MAKEVERSION`) when absent. Public functions are `EraseSettings`, `RestoreSettings`, `StoreSettings`, `GetRegValueSize`, `GetBinaryRegValue`, `SetBinaryRegValue`, `GetMultiStringRegValue`, `SetMultiStringRegValue`, and `RegDeltreeKey`.

## State, Dependencies, and Integration
Callers provide a registry parent key, subkey path, value name, structure pointer, size, and version. The documented policy is major-version equality and stored minor-version compatibility for appended fields. Multi-string helpers allocate output buffers that callers must free through the afsapplib string allocator.

## Risks and Test Signals
The header contract strongly depends on append-only structure evolution, but the implementation's size check should be verified against that promise. API users must not store pointers or process-local handles inside persisted structs. Tests should assert version macro encoding, restore failure defaults, registry deletion behavior, and allocation/free ownership for multi-string values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/settings.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/subclass.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/subclass.cpp

## Purpose
Implements a small global manager for stacking multiple window-procedure hooks on the same HWND without requiring strict reverse-order uninstallation by independent callers.

## Important APIs and Control Flow
`Subclass_AddHook` finds or creates a `SubclassWindow` entry for the target, finds or creates a hook slot for the requested procedure, increments the request count, and installs `Subclass_WndProc` as the real Win32 window procedure when the first active hook is added. `Subclass_RemoveHook` decrements the hook's request count, clears the slot at zero, decrements active-hook count, and restores the original window procedure when no hooks remain. `Subclass_FindNextHook` returns the next registered hook after the caller's procedure, or the original proc if the caller is last. `Subclass_WndProc` dispatches each message to the first active hook; hook code is expected to call `Subclass_FindNextHook` and forward manually.

## State, Dependencies, and Integration
State is a process-global dynamic `aTargets` array, each target containing original procedure, hook array, capacity, and active count. Allocation uses `GlobalAlloc` through a local `REALLOC`. It depends on Win32 `GetWindowLongPtr`, `SetWindowLongPtr`, and `CallWindowProc`, plus afsapplib's public `subclass.h` contract.

## Risks and Test Signals
There is no synchronization around global arrays, so cross-thread subclass changes can race. Underflow is possible if `Subclass_RemoveHook` is called for an unregistered hook because `nHooksActive` is decremented once a target is found regardless of whether a hook was removed. `SetWindowLongPtr` receives `PtrToLong(Subclass_WndProc)`, which can truncate on 64-bit builds. Hook ordering is slot order, not necessarily reverse install order, and duplicate add calls only increment `nReq`, so the procedure appears once in dispatch. Tests should cover duplicate add/remove counts, removing unknown hooks, multiple hooks on one window, multiple windows, forwarding chain correctness, and 64-bit pointer safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/subclass.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/subclass.h -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/subclass.h

## Purpose
Declares the afsapplib subclass-chain helper. The header explains why direct `SetWindowLong(GWL_WNDPROC)` chaining is brittle when multiple components subclass the same child window and provides a cooperative alternative.

## Important APIs and Types
`Subclass_AddHook(HWND, PVOID)` registers a window procedure hook. `Subclass_RemoveHook(HWND, PVOID)` unregisters one request for that hook. `Subclass_FindNextHook(HWND, PVOID)` lets a hook discover the next hook or original procedure to forward to. The header intentionally exposes procedures as `PVOID`, leaving casts to caller code.

## State, Dependencies, and Integration
Consumers are expected to call add on creation, find-next and `CallWindowProc` inside the hook, and remove on destruction. Repeated add calls with the same target/proc require the same number of remove calls. This integrates with `resize.cpp`, which installs `Resize_DialogProc` on tracked dialogs.

## Risks and Test Signals
The API is cooperative: if a hook does not forward, later hooks and the original window proc do not see the message. Because the header uses `PVOID`, type safety is weak, especially across ANSI/Unicode and pointer-size builds. Tests should verify forwarding examples, duplicate-count behavior, and removal that is not reverse install order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/subclass.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/test/resource.h -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/test/resource.h

## Purpose
Defines resource IDs for the afsapplib wizard test program. It maps string resources, dialog templates, bitmap resources, button/control IDs, and App Studio next-value metadata used by `wiztest.cpp` and its resource script.

## Important APIs and Types
The file has no functions. Important constants include wizard button text and message strings (`IDS_NEXT`, `IDS_FINISH`, help/cancel IDs), dialog templates (`IDD_WIZARD`, `IDD_STEP1`, `IDD_STEP2`, `IDD_STEP3`), bitmap resources (`IDB_GRAPHIC_16`, `IDB_GRAPHIC_256`), navigation buttons (`IDNEXT`, `IDBACK`), radio controls (`IDC_GOTO_TWO`, `IDC_GOTO_THREE`), and pane controls (`IDC_WIZARD_LEFTPANE`, `IDC_WIZARD_RIGHTPANE`).

## State, Dependencies, and Integration
This is compile-time resource state shared with Windows `.rc` files and the wizard test source. Several IDs intentionally overlap across different resource classes, which is normal in Win32 resource tables but requires context-sensitive use.

## Risks and Test Signals
Changing IDs can break dialog procedure message handling and wizard template binding. The overlap between `IDD_STEP2` and `IDB_GRAPHIC_256`, and between `IDC_GOTO_THREE` and `IDC_WIZARD_LEFTPANE`, is acceptable only because they are used in different namespaces or templates. Test signals are successful resource compilation and manual wizard navigation through all three pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/test/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/test/wiztest.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/test/wiztest.cpp

## Purpose
Provides a Win32 sample/test application for the afsapplib `WIZARD` class. It demonstrates wizard state setup, page transitions, button text/default control changes, optional state disabling, help/cancel handling, bitmap graphics, and a custom animated overlay callback.

## Important APIs and Control Flow
`WinMain` seeds randomness, starts a timer for animation, constructs a `WIZARD`, binds the outer template and pane/button IDs, sets 16/256-color graphics, registers `Wiz_DrawOverlay`, supplies three `WIZARD_STATE` entries, starts at step one, and shows the wizard modally. `WizStep_Common_DlgProc` handles help and cancel commands. Step procedures configure buttons during `WM_INITDIALOG` and change wizard state on `IDBACK`/`IDNEXT`. Step two handles `wcIS_STATE_DISABLED` so the first page can skip it.

The drawing section computes animated line endpoints inside the left graphic pane. `Wiz_ForceGraphicRedraw` invalidates and updates the left pane on each timer tick. `Wiz_DrawOverlay` chooses a color based on display depth, draws a bounding rectangle and rotating cross, moves the center point with bouncing velocity, and cleans up GDI pen objects.

## State, Dependencies, and Integration
Global state includes `g_pWiz`, `g_fSkipStep2`, wizard states, and static animation variables inside the drawing callback. Dependencies include `afsapplib.h`, Win32 dialogs/GDI/timers, math functions, and `resource.h`. It is a test/demo executable rather than production library code.

## Risks and Test Signals
The timer is created with a NULL HWND and never explicitly killed; the process exit normally cleans it up, but repeated embedding would need lifecycle care. `g_pWiz` is assumed valid during timer callbacks. The sample returns `FALSE` after common handling even when it handled a command, which may be intentional for this wizard framework but is worth checking. Tests are mostly interactive: resource loading, page navigation, skip-step behavior, cancel confirmation, help display, bitmap rendering, and overlay animation without GDI leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/test/wiztest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/afsclass.h -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/afsclass.h

## Purpose
Public umbrella header for the Windows `afsclass` object model. It establishes common constants and forward declarations, includes the class-specific headers, and declares library-level initialization, locking, refresh-domain, time, allocation, and address helpers.

## Important APIs and Types
Constants include `cchNAME`, ghost-status bit masks, and refresh-domain flags (`AFSCLASS_WANT_VOLUMES`, `AFSCLASS_WANT_USERS`). `ACCOUNTACCESS` abstracts PTS permission visibility. The header aliases `HENUM` to `LPENUMERATION` from the hashlist library and declares `VOLUMEID`, notification, cell, server, service, aggregate, fileset, user, group, ident, and ident-list classes.

It includes `c_debug.h`, `c_notify.h`, `c_ident.h`, `c_identlist.h`, `c_cell.h`, `c_svr.h`, `c_svc.h`, `c_agg.h`, `c_set.h`, `c_usr.h`, `c_grp.h`, and `afsclassfn.h`. Declared utility functions are `AfsClass_Initialize`, `AfsClass_SpecifyRefreshDomain`, `AfsClass_Enter`, `AfsClass_Leave`, `AfsClass_GetEnterCount`, `AfsClass_RequestLongServerNames`, Unix/system time conversion, `AfsClass_ReallocFunction`, `AfsClass_SkipRefresh`, and address conversions.

## State, Dependencies, and Integration
This header is the main entry point for applications using the AFS admin class library. It depends on `WINNT/afsapplib.h` and the full afsclass object hierarchy. The explicit enter/leave API exposes a global class lock used heavily by action wrappers in `afsclassfn.cpp`.

## Risks and Test Signals
The umbrella inclusion pattern can hide heavy dependencies and compile-time coupling. `cchNAME` fixed buffers are common across implementations, so truncation/overflow behavior is a key integration risk. Tests should validate initialization, lock recursion/count reporting, refresh-domain flags, time conversion round trips, address conversion, and inclusion order with both C and C++ Windows build settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/afsclass.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/afsclassfn.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/afsclassfn.cpp

## Purpose
Implements high-level administrative operations for the Windows AFS class library. These functions translate `LPIDENT` objects into BOS, VOS, KAS, and PTS worker tasks, send notifications, release the global class lock while performing remote operations, and refresh cached class objects after mutations.

## Important APIs and Control Flow
The file covers server/service actions (`GetServerLogFile`, auth toggle, start/stop/restart service, create/delete service, install/uninstall/prune files, restart times, execute command), fileset/VLDB/VOS actions (create/delete/move/rename fileset, quota, sync VLDB, lock/unlock, create/delete/move replica, clone, dump/restore, release, salvage), BOS admin/key/host list editing, PTS property access, user lifecycle/property/password/unlock operations, and group lifecycle/property/rename/membership operations.

Most functions follow a common pattern: `AfsClass_Enter`, send an `evt...Begin` notification, open the necessary cell/server/service/fileset/aggregate/user/group object, obtain low-level handles such as hBOS, hVOS, hKAS, or hCell, fill a `WORKERPACKET`, call `AfsClass_Leave` before `Worker_DoTask`, re-enter, invalidate or refresh affected caches, close opened objects and server handles, send an `evt...End` notification, then write `pStatus` only on failure.

Fileset operations pay attention to ghost status bits to decide whether to delete VLDB entries, zap server volumes, or do both. Replica move has compensating cleanup depending on whether source and target are on the same server. User creation can create KAS and/or PTS entries and rolls back KAS creation if PTS creation fails. User and group deletion/rename collect owner/member multi-strings so related cached accounts can be refreshed after the worker task.

## State, Dependencies, and Integration
Persistent state lives outside this file in AFS servers and in afsclass caches. Local state is mostly stack `WORKERPACKET`s, allocated list structures (`ADMINLIST`, `KEYLIST`, `HOSTLIST`), and temporary log or multi-string buffers. Dependencies include Winsock headers, `afsconfig.h`, `roken.h`, `afsclass.h`, `internal.h`, notification events, object `Open*/Close` methods, cache invalidation/refresh methods, and worker task enums/packet fields.

## Risks and Test Signals
The file is correctness-critical because it coordinates remote side effects and local cache coherence. Several end notifications appear mismatched or incomplete, such as `AfsClass_SetUserProperties` and `AfsClass_SetGroupProperties` sending `evtChange...Begin` at the end rather than an end event, and `AfsClass_UnlockAllFilesets` ending without status. Many functions use fixed `cchNAME` buffers and `lstrcpy`/`wsprintf`. `AfsClass_CreateService` concatenates command and params into `MAX_PATH + MAX_PATH` without bounds checking. Some worker calls occur while still holding the global class lock in list/key helpers, unlike the broader pattern of leaving around remote work. `status` is sometimes left dependent on earlier calls when success paths skip assignment. Tests should mock `Worker_DoTask` and object open/refresh methods to verify notification pairing, lock release/reacquire behavior, handle close calls, rollback paths, ghost-status branching, cache invalidation coverage, and `pStatus` propagation across failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/afsclassfn.cpp -->
