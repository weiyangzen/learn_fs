# subset-b-007747 research

Grouped research for OpenAFS Windows pthread tests, TaLocale support code, large-file/network tests, and WinTorture helpers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/pthread/test/ptest.c -->
# sources/distributed-fs/openafs/src/WINNT/pthread/test/ptest.c

## Purpose

`ptest.c` is a no-output-on-success regression test for the OpenAFS Windows pthread compatibility layer. It exercises thread creation/join, thread identity, one-time initialization, mutex locking and trylocking, condition wait/signal/broadcast, timed condition waits, object destruction, and explicit invalid-argument paths. It is intended to fail through `assert()` if the NT pthread implementation diverges from the expected API contract.

## Important APIs, Types, and Functions

- Uses OpenAFS platform headers `afs/param.h` and `afs/stds.h`, the Win32 `Sleep()` call, and pthread types/functions from `pthread.h`.
- Global synchronization state includes `pthread_once_t once_c`, counters `should_be_one`, `should_be_NTH`, `should_be_NTH_minus_1`, mutexes `g_mutex`, `try_mutex`, `cond_mutex`, and condition variable `g_cond`.
- `once_me()` is the `pthread_once` initializer. It increments `should_be_one` and initializes the mutex and condition objects that later tests rely on.
- `threadFunc()` verifies `pthread_equal(*me, pthread_self())`, runs `pthread_once`, increments a shared count under `g_mutex`, then tests `pthread_mutex_trylock()` contention by letting one thread hold `try_mutex` during `Sleep(SLEEP_TIME)`.
- `condWaitFunc()`, `condSignalFunc()`, `condBroadcastFunc()`, and `condTimeWaitFunc()` exercise condition-variable wakeup and timeout behavior.
- `main()` is the test orchestrator and contains the final invalid-argument assertions.

## Control Flow

The first phase creates `NTH` threads, each receiving a pointer to its `pthread_t` slot. All threads call `pthread_once`; only one should run `once_me()`. Every thread increments `should_be_NTH` under `g_mutex`; one thread should acquire `try_mutex` and sleep, while the other nine increment `should_be_NTH_minus_1`. The main thread joins all workers, destroys `g_mutex`, and validates the counters.

The second phase verifies condition variables. One waiter blocks until a signaler sleeps and sets `cond_flag`, then signals. A broadcast run resets `cond_flag`, starts `NTH - 1` waiters and one broadcaster, and joins all threads. A timed-wait run resets `cond_flag`, starts one waiter using an absolute timeout of `time(NULL) + COND_WAIT_TIME`, expects `ETIME`, and checks elapsed wall-clock time.

The final phase destroys the remaining synchronization objects and calls pthread APIs with null pointers or invalid attribute pointers, asserting that each returns a nonzero error instead of succeeding.

## State and Persistence

All state is process-local. The test depends on zero-initialized static globals and modifies only counters, mutexes, condition variables, and the `cond_flag`. It does not persist files, registry keys, or logs. Timing state comes from `time()` and Win32 `Sleep()`.

## Dependencies and Integration Points

The file integrates with the OpenAFS Windows pthread library and intentionally includes OpenAFS standard headers before libc/pthread headers. It assumes the pthread implementation maps timed condition wait failure to `ETIME` and supports Win32-style sleeping. It is a test binary rather than a library module.

## Risks and Edge Cases

- The trylock test is timing-sensitive: it assumes all non-owning threads reach `pthread_mutex_trylock()` while one thread still holds `try_mutex` for two seconds.
- `condSignalFunc()` and `condBroadcastFunc()` write `cond_flag` without holding `cond_mutex`, which can hide or introduce condition-variable ordering races in stricter implementations.
- Timed wait uses wall-clock seconds and allows a one-second tolerance, so clock changes or slow scheduling can affect the elapsed check.
- The invalid attribute tests pass literal pointer value `4`; that is useful for validation but is intentionally unsafe outside a test process.

## Test Signals

Successful execution emits no diagnostic text and exits zero. Any pthread behavior mismatch terminates through `assert()`. The strongest signals are the final counter checks, successful condition joins, `ETIME` from timed wait, and nonzero error returns for null/invalid arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/pthread/test/ptest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/pthread/test/tsd.c -->
# sources/distributed-fs/openafs/src/WINNT/pthread/test/tsd.c

## Purpose

`tsd.c` is a focused regression test for pthread thread-specific data in the OpenAFS Windows pthread layer. It verifies that each thread can store and retrieve a different value under the same key without cross-thread leakage.

## Important APIs, Types, and Functions

- Uses `pthread_key_t key`, `pthread_key_create()`, `pthread_setspecific()`, `pthread_getspecific()`, `pthread_create()`, and `pthread_join()`.
- `destruct(void *val)` is an empty destructor supplied to `pthread_key_create()`.
- `threadFunc(void *arg)` stores its argument in the global key and asserts the same pointer is returned by `pthread_getspecific()`.
- `main()` creates the key, starts `NTH` threads with distinct small integer values cast to `void *`, and joins every thread.

## Control Flow

The test creates one global key with `destruct`, starts ten worker threads, and passes each thread its loop index as the thread argument. Each worker sets that argument as key-specific data and immediately reads it back. The main thread joins all workers and returns zero if every API call succeeded and every assertion held.

## State and Persistence

State is entirely in-process: one pthread key and per-thread key values. The destructor does not mutate state and there is no persistent output.

## Dependencies and Integration Points

This file is a unit-style consumer of the OpenAFS Windows pthread compatibility API. It includes OpenAFS platform headers but does not call OpenAFS filesystem APIs.

## Risks and Edge Cases

- The loop index is cast directly to `void *`; this is common in small C tests but can trigger portability warnings and does not exercise pointer lifetime.
- The test does not call `pthread_key_delete()` and does not verify destructor invocation at thread exit.
- Because each thread sets and gets immediately, it validates key isolation but not long-lived TSD behavior across deeper call stacks.

## Test Signals

Passing behavior is silent exit zero. Assertion failures identify key creation, thread creation/join, or TSD isolation regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/pthread/test/tsd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/talocale/tal_alloc.cpp -->
# sources/distributed-fs/openafs/src/WINNT/talocale/tal_alloc.cpp

## Purpose

`tal_alloc.cpp` implements the debug memory instrumentation backend declared in `tal_alloc.h`. In debug builds it tracks allocations made through `Allocate`/`Free` and `New`/`Delete`, records file/line/expression metadata, detects invalid frees, double frees, and overwritten trailing signatures, maintains aggregate allocation statistics, and optionally presents a Win32 list-view memory-manager window.

## Important APIs, Types, and Functions

- It forces `DEBUG` on and `NO_DEBUG_ALLOC` off for this implementation so the instrumentation itself is built.
- `MEMCHUNK` records one allocation: data pointer, size, expression, source file, line, allocation tick, optional trailing signature, C++/dynamic kind, hash links, freed/list/tared flags.
- `BUCKET` and `HASH()` implement a pointer-keyed hash table over `MEMCHUNK` entries.
- `ALLOCEXPANDARRAY` is a private segmented array that stores `MEMCHUNK` records in `GlobalAlloc()` heaps of 1024 elements each.
- `STATISTICS` tracks live C++ allocations, dynamic allocations, totals, and tared counts/bytes.
- `MemMgr_Initialize()` initializes the process-global critical section, chunk array, and default hash buckets.
- `MemMgr_TrackAllocation()` writes an optional end signature, creates or reuses a `MEMCHUNK`, links it into the hash table, updates stats, and posts UI refresh messages.
- `MemMgr_TrackDestruction()` finds the chunk, validates the pointer and trailing signature, warns on invalid/double free, marks the chunk freed, removes it from the UI list, and decrements stats.
- Public exports are `ShowMemoryManager()`, `WhileMemoryManagerShowing()`, `IsMemoryManagerMessage()`, `MemMgr_AllocateMemory()`, `MemMgr_FreeMemory()`, `MemMgr_TrackNew()`, and `MemMgr_TrackDelete()`.
- UI helpers include `MemMgr_DlgProc()`, `MemMgr_OnInit()`, `MemMgr_OnRefresh()`, `MemMgr_OnTare()`, `MemMgr_OnReset()`, `MemMgr_OnSort()`, and list insertion/removal helpers.

## Control Flow

Instrumentation starts lazily. A public allocate/new wrapper calls `MemMgr_TrackAllocation()`, which calls `MemMgr_Initialize()` if needed, enters the global critical section, grows/rebuilds hash buckets when the chunk count crosses the bucket threshold, writes the trailing `'Okay'` signature for `Allocate()`, fills a `MEMCHUNK`, links or reuses a record, updates live byte/count statistics, and schedules a manager-window refresh if the UI is open.

Free/delete calls flow through `MemMgr_TrackDestruction()`. The function locates the chunk by pointer hash, warns if the pointer is unknown, warns if the dynamic-allocation trailer was overwritten, warns if a chunk is already marked freed, then marks it freed and updates UI/statistics. With `TRACK_FREED` enabled, freed records remain in the metadata heap so future reuse of the same address can be detected and replaced.

The UI path begins with `ShowMemoryManager()`, which restores window/list settings from the registry and creates a top-level window by creating a `Static` window and replacing its window procedure with `MemMgr_DlgProc()`. `IDC_INITIALIZE` creates child controls, populates the list from non-tared live chunks, installs a timer, and refreshes statistics. Tare hides current live allocations from the list and moves counts into tared buckets; reset reverses that tare state. Column clicks resort by rebuilding the list in sorted insertion order.

## State and Persistence

The main state is the static `l` structure: critical section pointer, manager window handle, timer ID, expandable chunk heap, chunk count, bucket table, and live statistics. The static `lr` structure stores UI window bounds, column widths, sort column, and sort direction. `MemMgr_RestoreSettings()` and `MemMgr_StoreSettings()` persist `lr` under `HKLM\Software\Random\MemMgr\Settings`. Allocation metadata and stats are process-local and are not persisted.

## Dependencies and Integration Points

This file depends heavily on Win32 and common controls: `GlobalAlloc`, `GlobalFree`, critical sections, registry APIs, `CreateWindowEx`, list-view messages, timers, message boxes, and stock GUI fonts. It integrates with `tal_alloc.h` macros used by the TaLocale library and any other debug Windows code that includes the header. It also provides `FormatBytes`/`FormatTime` helpers local to the memory-manager UI, separate from similarly named TaLocale string exports.

## Risks and Edge Cases

- Pointer hashing uses `PtrToUlong()`/`DWORD`, which truncates pointer identity on 64-bit builds.
- The code stores numeric sort keys by casting integers and pointers to `LPTSTR`, and compares them by pointer subtraction; this is legacy Win32 C++ and risky on modern compilers.
- `MemMgr_TrackDestruction()` returns `TRUE` even after unknown or double frees, so `MemMgr_FreeMemory()` still calls `GlobalFree()` on the supplied pointer.
- Registry persistence uses `HKEY_LOCAL_MACHINE`, which may fail under normal user privileges.
- The manager window is implemented by subclassing a `Static` control rather than registering a dedicated class; behavior depends on Win32 message handling quirks.
- The UI and allocation tracking share state through posted messages and copied chunks; correctness depends on the global critical section and window lifetime checks.

## Test Signals

The code is testable through debug builds that use `Allocate`/`Free`/`New`/`Delete`, open the memory manager with `ShowMemoryManager()` or F8 through `IsMemoryManagerMessage()`, and intentionally exercise double free, bad pointer free, and trailer overwrite cases. The visible signals are MessageBox warnings, live list rows, aggregate stats, and stable process behavior during concurrent allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/talocale/tal_alloc.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/talocale/tal_alloc.h -->
# sources/distributed-fs/openafs/src/WINNT/talocale/tal_alloc.h

## Purpose

`tal_alloc.h` exposes TaLocale's optional debug allocation instrumentation. It lets callers replace raw `GlobalAlloc`/`GlobalFree` and C++ `new`/`delete` usage with macros that record expression, file, and line metadata in debug builds, while compiling to normal allocation operations when instrumentation is disabled.

## Important APIs, Types, and Functions

- `NO_DEBUG_ALLOC` is automatically defined when `DEBUG` is not defined, disabling instrumentation.
- `MEMMGR_CALLCONV` defaults to `_cdecl`; `EXPORTED` defaults to `__declspec(dllexport)`.
- In non-instrumented mode, `Allocate`, `Free`, `New`, `New2`, and `Delete` directly wrap `GlobalAlloc`, `GlobalFree`, `new`, and `delete`.
- In instrumented mode, those macros call `MemMgr_AllocateMemory`, `MemMgr_FreeMemory`, `MemMgr_TrackNew`, and `MemMgr_TrackDelete` with source metadata.
- Debug UI exports are `ShowMemoryManager()`, `WhileMemoryManagerShowing()`, and `IsMemoryManagerMessage(MSG *pMsg)`.

## Control Flow

Including the header selects either the fast path or the instrumentation path at compile time. Non-debug code allocates directly. Debug instrumented code routes every macro call to the backend before or after the actual C++ operation, allowing `tal_alloc.cpp` to track metadata and validate frees. `New2` exists for constructors requiring a parenthesized argument list.

## State and Persistence

The header itself has no state. It controls whether client code contributes state to the backend memory manager. In debug builds, UI/window settings and allocation metadata are handled in `tal_alloc.cpp`.

## Dependencies and Integration Points

Consumers must include Windows types and link against the backend implementation when `DEBUG` and instrumentation are enabled. The comments note that DLL users must export/import the memory-manager functions consistently so all modules share the same manager instance.

## Risks and Edge Cases

- The `Delete` macro is single-object `delete`; it does not use `delete[]`, even though the examples show `New(TCHAR[256])`, which is a mismatch in modern C++ terms.
- Instrumentation is compile-time and macro-based, so mixed modules with inconsistent `DEBUG`, `NO_DEBUG_ALLOC`, or import/export settings can track only part of the process.
- Passing macro arguments with side effects is risky because the macros embed them into allocation expressions and metadata strings.

## Test Signals

Compile-time signal is whether macros expand to direct allocation or `MemMgr_*` calls. Runtime signal comes from the backend memory-manager UI and validation warnings when instrumented allocation/free paths are exercised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/talocale/tal_alloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/talocale/tal_dialog.cpp -->
# sources/distributed-fs/openafs/src/WINNT/talocale/tal_dialog.cpp

## Purpose

`tal_dialog.cpp` provides localized dialog and message-box helpers for TaLocale. It loads dialog templates through the TaLocale resource search chain and wraps `MessageBox()` so callers can supply literal strings or resource IDs with TaLocale formatting.

## Important APIs, Types, and Functions

- `ModelessDialog()` and `ModelessDialogParam()` load a dialog template with `TaLocale_GetDialogResource()` and create it with `CreateDialogIndirectParam()`.
- `ModalDialog()` and `ModalDialogParam()` do the same for modal dialogs through `DialogBoxIndirectParam()`.
- Overloaded `Message()` and `vMessage()` variants accept title/text as `LPCTSTR` or integer resource IDs.
- `MESSAGE_PARAMS` stores message-box type, formatted title, and formatted text for synchronous or background display.
- `Message_ThreadProc()` calls `MessageBox()`, frees formatted strings, deletes the parameter block, and returns the selected button.

## Control Flow

Dialog creation first resolves a localized `DLGTEMPLATE` and module handle. If no resource exists, creation returns `NULL`; otherwise the resolved module handle is used for indirect dialog creation. Message formatting funnels all overloads into `vMessage(UINT, LONG, LONG, LPCTSTR, va_list)`. It allocates a `MESSAGE_PARAMS`, formats the title with `FormatString()` and text with `vFormatString()`, adds a default icon if the low message-box bits imply a question/info style but no icon bits are present, and either creates a background thread for `MB_MODELESS` or calls `Message_ThreadProc()` synchronously.

## State and Persistence

There is no persistent module-local state. Each message allocates temporary formatted strings and a parameter block that are freed in `Message_ThreadProc()`. Modeless messages outlive the caller on a Win32 thread.

## Dependencies and Integration Points

The file depends on `WINNT/talocale.h`, which brings in TaLocale resource lookup, string formatting, and allocation macros. It integrates with the localized resource system in `tal_main.cpp` and the formatting/string allocation functions in `tal_string.cpp`. Win32 dependencies include indirect dialog creation, `CreateThread`, `SetThreadPriority`, and `MessageBox`.

## Risks and Edge Cases

- The overload set encodes either pointers or integer resource IDs into `LONG`, which is unsafe on 64-bit builds and relies on `PtrToLong`.
- The same `va_list` is passed to both `FormatString()` and `vFormatString()` without a `va_copy`; on ABIs where consuming a `va_list` mutates it, text formatting may see an exhausted list.
- For modeless messages, failure to create the thread leaks `pmp` and its strings because the code still returns `-1`.
- Background message threads are not closed with `CloseHandle()`, so thread handles leak after successful `CreateThread()`.

## Test Signals

Useful tests include loading modal and modeless dialogs from localized DLLs, formatting message titles/text from both literals and resource IDs, verifying default icon selection, and checking cleanup under synchronous and modeless message paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/talocale/tal_dialog.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/talocale/tal_dialog.h -->
# sources/distributed-fs/openafs/src/WINNT/talocale/tal_dialog.h

## Purpose

`tal_dialog.h` declares TaLocale's dialog creation and generic message-box helpers. It is the public interface used by Windows UI code that wants localized dialog templates and formatted localized messages.

## Important APIs, Types, and Functions

- Defines `MB_MODELESS` as a high-bit flag consumed by TaLocale's `Message()` wrapper, not by Win32 `MessageBox()` directly.
- Declares `ModelessDialog`, `ModelessDialogParam`, `ModalDialog`, and `ModalDialogParam`.
- Declares overloaded `Message()` and `vMessage()` forms for literal/resource-ID title and text combinations.
- Uses `EXPORTED` for DLL export by default.

## Control Flow

The header has no runtime flow. It exposes overloads that implementation code funnels into the `LONG`-based formatter and message-box executor in `tal_dialog.cpp`.

## State and Persistence

No state is defined here. State is transient in implementation-allocated message parameter blocks and resource handles.

## Dependencies and Integration Points

Consumers need Win32 dialog types (`HWND`, `DLGPROC`, `LPARAM`, `INT_PTR`, `UINT`, `LPCTSTR`) and C varargs support. It is normally included through `talocale.h` after Windows headers.

## Risks and Edge Cases

- The custom `MB_MODELESS` value occupies the high bit of a `UINT` message type and must be stripped before calling `MessageBox()`.
- C++ overloads make call-site type selection important; integer constants can bind to resource-ID overloads instead of pointer overloads.
- `cdecl` varargs declarations require callers and the implementation to agree on calling convention.

## Test Signals

Compile/link tests should verify all overloads are exported and callable from UI modules. Runtime tests should validate `MB_MODELESS`, literal strings, resource IDs, and `va_list` variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/talocale/tal_dialog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/talocale/tal_main.cpp -->
# sources/distributed-fs/openafs/src/WINNT/talocale/tal_main.cpp

## Purpose

`tal_main.cpp` implements TaLocale's core resource-location service. It maintains a priority-ordered module list, initializes default language selection, loads locale-specific resource DLLs, supports a registry language override, and wraps Win32 resource loading for dialogs, string tables, menus, images, icons, and accelerators.

## Important APIs, Types, and Functions

- `MODULE` stores a search priority and `HINSTANCE`.
- Static state includes `l_lang`, `l_csModules`, `l_aModules`, and `l_cModules`.
- `TaLocale_Initialize()` initializes common controls, the module-list critical section, default executable module, user default language, and optional registry override.
- `TaLocaleReallocFunction()` backs the public `REALLOC` macro using TaLocale allocation functions.
- `TaLocale_GuessBestLangID()` maps broad locales to likely shipped sublanguages such as US English, Simplified Chinese, German, Spanish, and Brazilian Portuguese.
- `TaLocale_SpecifyModule()` adds, reorders, or removes modules in priority order.
- `FindAfsCommonPathByComponent()` and `FindAfsCommonPath()` locate an AFS `Common` directory using Transarc/OpenAFS registry component paths.
- `TaLocale_LoadCorrespondingModule()` and `TaLocale_LoadCorrespondingModuleByName()` search for locale-suffixed DLLs such as `module_1033.dll`, wildcard language DLLs, AFS Common DLLs, and US-English fallback DLLs.
- `TaLocale_EnumModule()` enumerates the current module search chain.
- `TaLocale_GetLanguage()`, `TaLocale_SetLanguage()`, `TaLocale_GetLanguageOverride()`, `TaLocale_SetLanguageOverride()`, and `TaLocale_RemoveLanguageOverride()` manage volatile and registry language selection.
- `TaLocale_GetResource()`, `TaLocale_GetStringResource()`, `TaLocale_GetDialogResource()`, `TaLocale_LoadMenu()`, `TaLocale_LoadImage()`, `TaLocale_LoadIcon()`, and `TaLocale_LoadAccelerators()` are the resource-loading API.

## Control Flow

Most public entry points call `TaLocale_Initialize()` either directly or indirectly. Initialization uses a per-process-name mutex to avoid concurrent first-time initialization, initializes common controls and the module critical section, registers the executable module, sets `l_lang` from `GetUserDefaultLCID()`, then applies a persistent override if present.

Module registration removes any existing matching handle, then inserts the handle before lower-priority modules, growing the module array with `REALLOC`. Locale-DLL loading derives a filename from the supplied module or filename, replaces the extension with a language suffix, tries exact language, guessed language, wildcard language, AFS Common wildcard, and US-English fallback, then registers the loaded DLL at the requested priority.

Resource lookup iterates `TaLocale_EnumModule()` in priority order. General resources try `FindResourceEx()` for the selected language, US English, then any resource. String lookup computes the 16-string resource table and index, loads the table, walks length-prefixed entries, validates the selected string, and returns a pointer to the in-memory resource.

## State and Persistence

The module list and selected language are process-local static state protected by `l_csModules` for module operations. The language override is persisted under `HKLM\Software\Microsoft\Windows\CurrentVersion\Nls`, value `Default Language`. Loaded resource DLLs remain loaded for process lifetime unless managed elsewhere.

## Dependencies and Integration Points

The module depends on Win32 resource APIs, common controls, registry APIs, locale APIs, file search/loading APIs, and TaLocale string helpers (`FindBaseFileName`, `FindExtension`) plus allocation macros. It is the backend for `tal_string.cpp` and `tal_dialog.cpp`.

## Risks and Edge Cases

- `TaLocale_Initialize()` uses a non-interlocked static boolean plus a named mutex; recursive calls during initialization can be subtle because `TaLocale_SpecifyModule()` calls back into initialization.
- The module-array insertion loop casts `size_t` to `LONG` for reverse iteration, which is fragile for very large arrays.
- `TaLocale_GetResourceEx()` accepts `fSearchDefaultLanguageToo` but does not use it.
- `FindFirstFile()` is checked against `NULL`; Win32 returns `INVALID_HANDLE_VALUE`, so wildcard failure handling may be incorrect.
- String table walking uses exception handling around raw resource memory, which masks malformed resources but is not portable.
- Registry writes under HKLM require elevated privilege.

## Test Signals

Strong tests cover exact-language DLL loading, guessed-language fallback, wildcard/Common-directory fallback, module priority ordering, language override persistence/removal, string table lookup across missing entries, dialog/menu/image/accelerator lookup, and behavior when resource DLLs are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/talocale/tal_main.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/talocale/tal_string.cpp -->
# sources/distributed-fs/openafs/src/WINNT/talocale/tal_string.cpp

## Purpose

`tal_string.cpp` implements TaLocale's localized string, formatting, encoding, path, and utility-string functions. Its central feature is a resource-aware formatter that converts printf-style arguments into strings and substitutes them into message templates using `%1`, `%2`, and similar positional markers.

## Important APIs, Types, and Functions

- `GetString()` loads one or more consecutive string resources, continuing when a resource ends in `+`.
- `GetStringLength()` computes the required buffer length for possibly continued string resources.
- `SearchMultiString()`, `FormatMultiString()`, and `vFormatMultiString()` manage Windows multistring buffers.
- `FormatString()` and `vFormatString()` support literal or resource-ID templates and parse a caller-supplied printf-like argument format.
- The private `vartype` enum classifies arguments as words, dwords, floats/doubles, ANSI/Unicode strings, nested messages, byte counts, system/elapsed time, errors, socket addresses, or `LARGE_INTEGER`.
- Specialized formatters include `FormatSockAddr()`, `FormatElapsed()`, `FormatTime()`, `FormatError()`, `FormatBytes()`, `FormatLargeInt()`, and `FormatDouble()`.
- `SetErrorTranslationFunction()` installs a caller-supplied error-message translator.
- Path helpers are `FindExtension()`, `FindBaseFileName()`, `ChangeExtension()`, `CopyBaseFileName()`, and `lsplitpath()`.
- Encoding/allocation helpers convert and clone ANSI, Unicode, `TCHAR`, and multistring data and free strings allocated through TaLocale allocation macros.
- Additional `lstr*` helpers provide uppercasing, character search, case-insensitive prefix compare, bounded copy, and nul-terminated copy.

## Control Flow

Literal or resource formatting enters `vFormatString(LONG, LPCTSTR, va_list)`. A high-word check decides whether the source is a string pointer or a resource ID. Resource IDs are loaded through `GetStringLength()` and `GetString()`. The function counts `%` entries in the caller's `pszFmt`, parses each format descriptor to determine a `vartype`, consumes the corresponding vararg, formats it into a temporary allocated string, then scans the template to compute output length and substitute positional `%N` references. Temporary argument strings and resource templates are freed before returning the final allocated string.

Multistring formatting calls `vFormatString()` for one entry, substitutes `cszMultiStringNULL` for empty entries, calculates the old multistring byte count including the double terminator, and allocates a new multistring with the new entry at the head or tail.

Error formatting first calls an optional callback, then `FormatMessage()` from the system, then `FormatMessage()` from `NTDLL.DLL`, and appends the hexadecimal status when translated. Encoding helpers allocate appropriately sized buffers and use Win32 conversion APIs or `wsprintfW`/copy helpers depending on `UNICODE`.

## State and Persistence

State is mostly transient allocated strings. Persistent process-local state includes `pfnTranslateError`, plus static conversion buffers in `CopyUnicodeToAnsi()` and `CopyAnsiToUnicode()`. No files or registry keys are written by this file.

## Dependencies and Integration Points

The file depends on `WINNT/talocale.h`, Win32 locale/time/message APIs, Winsock `inet_ntoa`, TaLocale resource lookup from `tal_main.cpp`, and allocation macros from `tal_alloc.h`. It is used by TaLocale dialogs and resource consumers that need localized messages and path/encoding utilities.

## Risks and Edge Cases

- `vFormatString()` consumes `float` with `va_arg(arg, float)`, but C varargs promote `float` to `double`; this is undefined behavior for `%f` inputs classified as `vtFLOAT`.
- Pointer/resource discrimination through `HIWORD(pszSource)` and pointer-to-`LONG` casts is unsafe on 64-bit builds.
- Static conversion buffers make `CopyUnicodeToAnsi()` and `CopyAnsiToUnicode()` non-thread-safe.
- Several helpers assume non-null inputs despite public signatures accepting pointer types.
- `FormatBytes()` always formats megabytes rather than selecting byte/kilobyte/megabyte units dynamically.
- `FormatDouble()` is hand-written and does not round like standard printf.

## Test Signals

Tests should cover resource continuation with `+`, positional template substitution, nested `%m` messages, `%e` error formatting, `%b`/`%B` bytes, `%t` and `%et` time formats, ANSI/Unicode conversions under both Unicode and non-Unicode builds, multistring append/prepend/search, and path helper behavior with drive, extension, and UNC-like paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/talocale/tal_string.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/talocale/tal_string.h -->
# sources/distributed-fs/openafs/src/WINNT/talocale/tal_string.h

## Purpose

`tal_string.h` declares TaLocale's public string and formatting helpers. It gives Windows UI and utility code a common API for localized string loading, message formatting, multistring handling, byte/time/error/socket formatting, path manipulation, encoding conversion, and string allocation/freeing.

## Important APIs, Types, and Functions

- Constants include `cchRESOURCE`, `cchLENGTH()`, and `cszMultiStringNULL`.
- Resource string APIs are `GetString()` and `GetStringLength()`.
- Formatting APIs include `FormatString`, `vFormatString`, `FormatMultiString`, `vFormatMultiString`, `FormatBytes`, `FormatDouble`, `FormatTime`, `FormatElapsed`, `FormatError`, `FormatSockAddr`, and `FormatLargeInt`.
- `LPERRORPROC` and `SetErrorTranslationFunction()` allow custom error translation.
- Path APIs include `FindExtension`, `FindBaseFileName`, `ChangeExtension`, `CopyBaseFileName`, and `lsplitpath`.
- Conversion APIs include copy, allocate/convert, clone, and `FreeString` helpers for ANSI, Unicode, `TCHAR`, and multistrings.
- Compatibility helpers include `lstrupr`, `lstrchr`, `lstrrchr`, `lstrncmpi`, `lstrncpy`, and `lstrzcpy`.

## Control Flow

The header defines allocation-size macros `AllocateAnsi`, `AllocateUnicode`, and `AllocateString`, which route through `Allocate()` from `tal_alloc.h`. Implementations allocate returned strings; callers are expected to use `FreeString()` for buffers returned from conversion/clone/format functions.

## State and Persistence

No state is stored here. The declared implementation uses transient allocated buffers and a process-local error translation callback.

## Dependencies and Integration Points

The header includes `winsock2.h` for `SOCKADDR_IN` and expects Windows/TCHAR types to be available through `talocale.h`. It is included by `talocale.h` before dialog and allocation headers, making these helpers broadly available to TaLocale consumers.

## Risks and Edge Cases

- Many APIs return allocated memory without encoding ownership in the type; callers must consistently call `FreeString()`.
- Format functions use C varargs and custom specifiers, so format/argument mismatches are runtime hazards.
- `CloneMultiString()` is declared as taking `LPCSTR` while the implementation takes `LPCTSTR`, indicating type drift between header and implementation.
- `Allocate*` macros guarantee at least `cchRESOURCE + 1` characters, which can mask caller sizing mistakes but may overallocate small strings.

## Test Signals

Compile tests should cover Unicode and non-Unicode consumers, Winsock include ordering, and all exported declarations. Runtime coverage belongs in `tal_string.cpp` tests around allocation ownership, format specifiers, and conversion correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/talocale/tal_string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/talocale/talocale.h -->
# sources/distributed-fs/openafs/src/WINNT/talocale/talocale.h

## Purpose

`talocale.h` is the umbrella public header for the TaLocale Windows localization helper library. It normalizes Unicode macros, includes Windows/common-control/TCHAR support, defines the string-resource table shape, includes the string/dialog/allocation sub-APIs, and declares the core module/language/resource-loading API.

## Important APIs, Types, and Functions

- Synchronizes `UNICODE` and `_UNICODE` definitions.
- Defines `STRINGTEMPLATE`, the length-prefixed string-table entry format used by Win32 `RT_STRING` resources.
- Includes `tal_string.h`, `tal_dialog.h`, and `tal_alloc.h`.
- Defines the `REALLOC` macro over `TaLocaleReallocFunction()`.
- Module priorities include highest, boosted, normal, lowest, and remove.
- Declares module management (`TaLocale_SpecifyModule`, `TaLocale_EnumModule`), locale DLL loading, language get/set/override APIs, generic resource lookup, string/dialog resource lookup, and menu/image/icon/accelerator loading wrappers.

## Control Flow

The header provides the API shape; implementations lazily initialize TaLocale state, build a module search chain, select a language, then retrieve resources in priority and language-fallback order. The `REALLOC` macro is used internally and by consumers that need growable arrays allocated through TaLocale allocation policy.

## State and Persistence

The header itself has no state. Declared APIs manage process-local module/language state and a registry-backed language override in `tal_main.cpp`.

## Dependencies and Integration Points

This is the main integration point for Win32 UI modules using localized resources. It depends on `windows.h`, `commctrl.h`, and `tchar.h`, and exports functions suitable for DLL boundaries through `EXPORTED`.

## Risks and Edge Cases

- The umbrella include order pulls in `winsock2.h` indirectly through `tal_string.h`; consumers that already included `windows.h` with older Winsock headers may see include-order conflicts in some environments.
- `REALLOC(_a,_c,_r,_i)` evaluates `_a` and `_c` by address and expects `_c` to be a `size_t`-like variable matching the target element count.
- Default arguments in exported C++ declarations require consumers to compile with compatible C++ settings.

## Test Signals

Header-level tests should compile representative Unicode/non-Unicode modules, DLL import/export configurations, and callers of each resource wrapper. Runtime signals come from `tal_main.cpp`, `tal_string.cpp`, and `tal_dialog.cpp` tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/talocale/talocale.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/largefiles/lftest.c -->
# sources/distributed-fs/openafs/src/WINNT/tests/largefiles/lftest.c

## Purpose

`lftest.c` is a Windows large-file smoke test for AFS-mounted paths. It writes a fixed test string at several offsets spaced just under 1 GiB apart, flushes the AFS volume through `fs.exe flushvolume`, reopens the file, and verifies the strings can be read back from the same 64-bit offsets.

## Important APIs, Types, and Functions

- Uses Win32 file APIs: `CreateFile`, `SetCurrentDirectory`, `SetFilePointerEx`, `WriteFile`, `ReadFile`, `LockFile`, `UnlockFile`, and `CloseHandle`.
- `teststr` is the expected string payload.
- `test_write(HANDLE, LARGE_INTEGER)` locks 4096 bytes at an offset, seeks, writes `teststr` plus terminator, unlocks, and reports failures.
- `test_read(HANDLE, LARGE_INTEGER)` locks/seeks/reads at the same offset, prints the read data, compares to `teststr`, and unlocks.
- `main()` opens `largefile.test`, writes seven offsets, runs `fs.exe flushvolume <path>`, reopens, and reads the offsets.

## Control Flow

The program requires one path argument, changes into that directory, opens or creates `largefile.test` with read/write sharing, random access, and write-through attributes, then iterates `i = 0..6` with `offset = i * (0x40000000 - 4)`. After writes, it closes the handle, shells out to flush the AFS volume for the provided path, reopens the file, and repeats the same offset sequence for reads and comparison.

## State and Persistence

The test creates or modifies `largefile.test` in the target directory and leaves it in place. It also changes the process current directory. No cleanup removes the test file.

## Dependencies and Integration Points

The program is Windows-only and expects `fs.exe` from OpenAFS to be on `PATH`. It is meant to run against an AFS path or another filesystem being checked for sparse/large-file offset correctness and locking behavior.

## Risks and Edge Cases

- Return values from `test_write()` and `test_read()` are ignored in `main()`, so the process can still exit zero after individual failures.
- `sprintf(cmdline, "fs.exe flushvolume %s", argv[1])` does not quote the path and can fail or be unsafe with spaces/metacharacters.
- The file is opened with `OPEN_ALWAYS`, so stale content can remain outside tested offsets.
- Lock length is only 4096 bytes while payload is short; this is adequate for the test string but not a full region integrity check.

## Test Signals

Console output reports each successful write/read and prints detailed Win32 `GetLastError()` diagnostics on lock, seek, read, write, or unlock failures. A string comparison failure is the core correctness signal after flush/reopen.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/largefiles/lftest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/netrpc/enumrpc.c -->
# sources/distributed-fs/openafs/src/WINNT/tests/netrpc/enumrpc.c

## Purpose

`enumrpc.c` is a Unicode Windows NetAPI diagnostic that queries workstation, server, and share information for a specified `\\ServerName`. It enumerates shares and then retrieves detailed information for each share, useful for checking SMB/RPC visibility of AFS-related servers or Windows hosts.

## Important APIs, Types, and Functions

- Forces `UNICODE` and includes `windows.h` and `lm.h`.
- `CallNetWkstaGetInfo()` calls `NetWkstaGetInfo()` level 102 and prints platform, computer name, version, domain, LAN root, and logged-on users.
- `CallNetServerGetInfo()` calls `NetServerGetInfo()` level 101 and classifies the target as server or workstation from `sv101_type`.
- `CallNetShareEnum()` calls `NetShareEnum()` level 2 in a resume loop, prints share rows, and calls `CallNetShareGetInfo()` for each share.
- `CallNetShareGetInfo()` calls `NetShareGetInfo()` level 2 and prints net name, local path, and remark.
- `wmain()` validates the single server argument and invokes all reports.

## Control Flow

After argument validation, the program performs workstation info, server info, and share enumeration in sequence. Share enumeration handles `ERROR_MORE_DATA` by looping with the resume handle. Each successful enumeration buffer is traversed twice: once to print summary rows and again to call per-share detail queries. NetAPI-allocated buffers are freed with `NetApiBufferFree()`.

## State and Persistence

There is no persistent state. All data is returned by NetAPI calls and printed to stdout/stderr.

## Dependencies and Integration Points

The program depends on Windows LAN Manager NetAPI and links against the appropriate NetAPI library. It is a standalone test/diagnostic, not an OpenAFS library consumer, but can be used against OpenAFS SMB gateway/server scenarios.

## Risks and Edge Cases

- `BufPtr` is not initialized before `NetShareEnum()` and is freed only on success/more-data paths.
- The comments mention level 502 for `NetShareGetInfo()` but the code uses level 2.
- Mixed `printf`, `wprintf`, `%S`, and `%s` formatting relies on Microsoft CRT semantics under `UNICODE`.
- The program requires server-name syntax and permissions sufficient for NetAPI queries.

## Test Signals

Successful output includes workstation metadata, server/workstation classification, share summary rows, and per-share details. Failures print NetAPI status codes for the relevant call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/netrpc/enumrpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/nmtest/nmtest.c -->
# sources/distributed-fs/openafs/src/WINNT/tests/nmtest/nmtest.c

## Purpose

`nmtest.c` generates and verifies deterministic block-oriented test files for Windows filesystem stress. It writes a file containing a metadata bitmap followed by 1024-byte pseudo-random data blocks derived from each block offset, optionally overwrites random blocks with a second deterministic variant, and later verifies every block against the bitmap.

## Important APIs, Types, and Functions

- Uses Win32 CryptoAPI (`CryptAcquireContext`, `CryptCreateHash`, `CryptHashData`, `CryptDeriveKey`, `CryptEncrypt`, `CryptGenRandom`) to generate deterministic block bytes.
- Uses Win32 file APIs with byte-range locking: `CreateFile`, `SetFilePointerEx`, `ReadFile`, `WriteFile`, `LockFileEx`, `UnlockFileEx`, `FlushFileBuffers`, and `GetFileSizeEx`.
- `hash_data` combines `offset` and `param` as the deterministic seed.
- `bitmap` stores magic `BMAGIC`, data length, data offset, and per-data-block overwrite bits.
- `allocbits()`, `setbit()`, and `getbit()` manage bitmap state.
- `write_bitmap()` and `read_bitmap()` serialize/deserialize the bitmap in block-sized chunks at the start of the file.
- `do_write_test()` implements `-w N M filename`; `do_verify_test()` implements `-r filename`.
- `parse_cmdline()` selects write or verify mode.

## Control Flow

Write mode rounds `N` and `M` up to `BLOCKSIZE`, creates/truncates the output file, allocates a bitmap whose data offset is block-aligned after the bitmap, initializes CryptoAPI, writes the bitmap header area, and sequentially writes deterministic `param=0` blocks for the full data range. It flushes and reopens the file for random access, then performs `M / BLOCKSIZE` random overwrite attempts: choose a random block in the data range, generate deterministic `param=1` data for that offset, lock/seek/write/unlock the block, and mark the bitmap bit. Finally it rewrites the bitmap so verification knows which blocks were overwritten.

Verify mode opens the file read-only, reads and validates the bitmap, checks file size and data offset, initializes CryptoAPI, then sequentially locks/reads each data block. For each offset it chooses expected `param=1` if the bitmap bit is set, otherwise `param=0`, regenerates the block, and compares all 1024 bytes.

## State and Persistence

The persistent state is the generated file: a bitmap header at offset zero, padded to a block boundary, followed by data blocks. Global process state includes `h_prov`, `N`, `M`, `filename`, and mode flags. Crypto provider state is acquired per test and released at exit.

## Dependencies and Integration Points

This standalone test depends on Windows CryptoAPI and filesystem byte-range locking. It is suitable for AFS cache/server validation because it detects stale reads, lost writes, random overwrite failures, file-size errors, and locking/seek problems.

## Risks and Edge Cases

- `parse_cmdline()` uses `atol()`, so sizes larger than `long` or nonnumeric suffixes are not handled robustly despite `offset_t` being 64-bit.
- `show_offsets` is never set from the command line in this file.
- `write_bitmap()` and data writes use synchronous `WriteFile()` with an `OVERLAPPED` only for lock offsets; correctness depends on explicit file-pointer positioning where used.
- Some error paths after a failed read/write can leave locks held because unlock is not always in a guaranteed cleanup block.
- `CryptEncrypt()` is called with a zeroed buffer and `cb_data = BLOCKSIZE`; this deterministic stream depends on provider behavior for RC4 derivation.

## Test Signals

Write mode prints phase progress and exits zero on success. Verify mode prints file size, verification progress, and `Verify succeeded!` on success. Failure signals include corrupt magic, invalid file size/data offset, lock/read/write errors, and exact verification offset for mismatched blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/nmtest/nmtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/DumpAfsLog/DumpAfsLog.c -->
# sources/distributed-fs/openafs/src/WINNT/tests/torture/DumpAfsLog/DumpAfsLog.c

## Purpose

`DumpAfsLog.c` is a Windows console utility that repeatedly dumps OpenAFS client trace logs, optionally captures minidumps, and archives the generated files into a timestamp-like sequence under `DumpAfsLogDir`. It is intended for long-running diagnostic capture during stress or deadlock reproduction.

## Important APIs, Types, and Functions

- Uses OpenAFS/roken headers plus Win32 console, environment, sleep, and process APIs.
- `main()` parses options, enables and resets `fs trace`, creates a logging directory, loops until runtime expires or the user presses Q, and disables tracing at exit.
- Options include `-d <drive>`, `-e` for `fs minidump`, `-h <host>` parsed but not used in the shown flow, `-m <minutes>`, `-s <seconds>`, and help.
- `usage()` prints supported options.
- `GetConsoleInput()` peeks/reads console input and exits immediately on `q` or `Q`.

## Control Flow

Startup defaults to 15 seconds between dumps and 30 minutes total runtime. The program runs `fs trace -on` and `fs trace -reset`, builds a working directory on the requested logging drive, removes and recreates `DumpAfsLogDir`, then enters a loop. Each iteration optionally runs `fs minidump`, copies `%windir%\TEMP\afsd.dmp` into the log directory, renames it to `afsd_#####.dmp`, runs `fs trace -dump`, copies `%windir%\TEMP\afsd.log`, and renames it to `afsd_#####.log`. Between iterations it polls console input every 500 ms until the delay expires. On normal timeout it runs `fs trace -off`.

## State and Persistence

Persistent output is the `DumpAfsLogDir` directory in the current/logging-drive-adjusted working directory, containing numbered `afsd_*.log` and optionally `afsd_*.dmp` files. The utility mutates OpenAFS client tracing state by turning trace on, resetting it, dumping it, and turning it off.

## Dependencies and Integration Points

The utility depends on `fs.exe` commands (`trace -on`, `trace -reset`, `trace -dump`, `trace -off`, `minidump`), `%windir%\TEMP\afsd.log`, `%windir%\TEMP\afsd.dmp`, and Windows shell commands `rmdir`, `mkdir`, `copy`, and `rename`. It uses roken `strlcpy`/`strlcat` for safer string construction.

## Risks and Edge Cases

- Many operations are shell-command based and depend on paths without full quoting, so spaces in directories can break commands.
- `HostName`, `NewSessionDeadlock`, and related variables are parsed or declared but unused in the active flow.
- `GetConsoleInput()` exits the process directly on Q, bypassing the final `fs trace -off`.
- `system()` return codes are assigned but largely ignored.
- The directory is removed recursively at startup, so an incorrect working directory or logging drive can destroy prior capture data.

## Test Signals

Signals are visible console commands, numbered copied logs/dumps, and successful trace-off on timeout. During testing, verify that `%windir%\TEMP` artifacts are copied and renamed each cycle, Q stops the loop, and `fs trace -dump` produces fresh logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/DumpAfsLog/DumpAfsLog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/Source/ResolveLocker.c -->
# sources/distributed-fs/openafs/src/WINNT/tests/torture/Source/ResolveLocker.c

## Purpose

`ResolveLocker.c` is a Hesiod-backed locker resolver used by the WinTorture tooling when `HAVE_HESOID` is enabled. It converts a logical locker name into an AFS UNC submount or NFS UNC path and updates a `USER_OPTIONS` attach structure for downstream attach/resource-mount code.

## Important APIs, Types, and Functions

- Compiled only under `HAVE_HESOID`; it defines `_WIN32_WINNT 0x0500` and includes `hesiod.h` and `locker.h`.
- `ResolveLocker(USER_OPTIONS *attachOption)` validates `type == "locker"`, gets locker info, parses filesystem type, and fills `SubMount`, `type`, or `FileType`.
- `GetLockerInfo(char *Locker, char *Path)` calls Hesiod and selects an AFS or NFS filsys entry, preferring the lowest AFS weight if present.
- `ResolveHesName(char *locker)` calls `hes_resolve(locker, "filsys")`.

## Control Flow

`ResolveLocker()` only handles input type `locker`. It retrieves a filsys path string; an `AFS` entry becomes `\\afs\<locker>` with forward slashes normalized to backslashes, changes the type to `AFS`, and returns true. An `NFS` entry is accepted only if no submount is already set; it expects five parsed fields, builds `\\<HostName><path>`, normalizes slashes, sets `FileType` to `NFS`, and returns true. Unknown types, missing info, parse failures, or unsupported initial type return false.

`GetLockerInfo()` iterates Hesiod results. For AFS entries it reads a weight field if present and keeps the lowest-weight entry; if no weight is parsed, it copies that AFS entry. For NFS entries it copies the entry directly. `ResolveHesName()` is a thin wrapper around `hes_resolve`.

## State and Persistence

No persistent state is written. The function mutates the caller-provided `USER_OPTIONS` fields. Hesiod result memory ownership is not handled in this file.

## Dependencies and Integration Points

The module depends on MIT Hesiod and locker structures. It is referenced by `WinTorture.c` to resolve and attach lockers when `-l` is used and by `WinThreads.c` through optional locker attach operations.

## Risks and Edge Cases

- Uses `sprintf`, `strcpy`, and fixed-size buffers without bounds checks.
- Hesiod result memory is not freed, which may leak depending on resolver ownership rules.
- AFS resolution ignores the actual AFS path in the Hesiod entry and constructs `\\afs\<locker>`, which may not match weighted path details.
- The NFS `sprintf("\\\\%s%s", HostName, temp)` assumes `temp` already starts with a slash/backslash-like path.
- The file returns `TRUE` after an unreachable comment even though all active branches already returned.

## Test Signals

Tests need Hesiod fixtures for AFS weighted entries, unweighted AFS entries, NFS entries, unknown filesystem entries, and missing lockers. The observable signal is the mutated `USER_OPTIONS` structure and boolean return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/Source/ResolveLocker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/Source/WinThreads.c -->
# sources/distributed-fs/openafs/src/WINNT/tests/torture/Source/WinThreads.c

## Purpose

`WinThreads.c` implements the per-thread execution engine for WinTorture. Each thread reads a dbench/netbench-style script file, substitutes client/locker variables, dispatches operations to `nb_*` filesystem functions, records per-command timing/error statistics, reacts to global pause/continue/shutdown events, and checks whether an AFS path is online after certain network-name failures.

## Important APIs, Types, and Functions

- Includes optional OpenAFS headers for `pioctl` and `VIOC_PATH_AVAILABILITY`; in `NO_AFS_SOURCE` mode it declares enough local types to dynamically call `pioctl`.
- Global named handles include `MutexHandle`, `FileMutexHandle`, `ShutDownEventHandle`, `PauseEventHandle`, `ContinueEventHandle`, and `OSMutexHandle`.
- Many thread-local (`__declspec(thread)`) values hold current command state: process number, log ID, buffer, locker paths, hostname, command stats, file table, event handle, exit status, and last error.
- `StressTestThread()` initializes thread-local state from `PARAMETERLIST`, opens its completion event, allocates the I/O buffer, creates/open named events and mutexes, repeatedly runs `run_netbench()`, and handles `ERROR_NETNAME_DELETED` recovery by polling `IsOnline()`.
- `run_netbench()` reads the script file, parses commands, performs substitutions, handles control events, dispatches operations such as `NTCreateX`, `Mkdir`, `Attach`, `CreateFile`, `WriteX`, `ReadX`, `LockingX`, and cleans up open handles.
- `IsOnline()` dynamically loads `afsauthent.dll`, gets `pioctl`, and calls `VIOC_PATH_AVAILABILITY` on the path.

## Control Flow

`StressTestThread()` receives a `PARAMETERLIST`, copies shared settings into thread-local variables, opens a uniquely named completion event created by `WinTorture.c`, allocates and fills `IoBuffer`, creates named control events/mutexes, and enters a retry loop. Before each run it resets shared and thread-local command counters. It calls `run_netbench()`. If `LastKnownError` is not `ERROR_NETNAME_DELETED`, the loop ends. Otherwise it logs recovery, clears exit status, marks the thread active, and calls `IsOnline()` up to four times with ten-second sleeps. Persistent offline or missing AFS DLL/pioctl marks the thread failed.

`run_netbench()` opens the client script, reads up to 128 bytes at a time, manually advances the file pointer by the consumed line length, strips CR/LF, handles pause and shutdown named events, skips blank/comment lines, substitutes `client1`, `clients`, `\\afs\\locker`, and optional second directory placeholders, tokenizes on spaces into `params`, updates benchmark state commands, and dispatches each recognized operation to its matching `nb_*` function. Any operation returning `-1` breaks execution. At exit it ends timing, closes all open file-table handles, deletes the local critical section, and returns.

`IsOnline()` serializes dynamic AFS DLL loading with `OSMutexHandle`, loads `afsauthent.dll`, resolves `pioctl`, invokes `VIOC_PATH_AVAILABILITY`, and maps specific `errno` values to offline versus online status. Missing DLL/function are distinct return statuses.

## State and Persistence

Per-thread state is held in TLS and in log files written through external `LogMessage()`/`LogStats()`. Threads create or open named Win32 events and mutexes shared across the process or processes. File operation state is in the TLS `ftable`. Persistent artifacts are thread logs and stats under the WinTorture log directory.

## Dependencies and Integration Points

This file is tightly coupled to `WinTorture.c` for thread creation and `PARAMETERLIST`, to `nbio.c` for operation implementations, to `output.c` for logging/statistics, and optionally to OpenAFS `afsauthent.dll`/`pioctl` for online checks. The script grammar is the dbench/netbench command stream plus OpenAFS-specific commands like `SetLocker`, `Attach`, `Detach`, and `Xrmdir`.

## Risks and Edge Cases

- Expressions such as `if (rc = WaitForSingleObject(...) == WAIT_OBJECT_0)` assign the boolean comparison result, not the raw wait status.
- Script reading in fixed 128-byte chunks can mishandle lines longer than the chunk size.
- Tokenization is space-only and does not handle quoted paths.
- Several string copies and `sprintf` calls use fixed buffers without bounds checks.
- `run_netbench()` initializes a local critical section per thread; it only protects that thread's verbose `printf`, not global console output.
- `IsOnline()` calls `pioctl` and then checks `errno` only when `code` is zero, which may reflect legacy OpenAFS semantics but is counterintuitive.
- Named control objects use fixed global names, so separate WinTorture runs can interfere.

## Test Signals

Signals include per-thread logs, command timing/error stats, exit status reasons, recovery logs after `ERROR_NETNAME_DELETED`, and online/offline statuses from `IsOnline()`. Script coverage should exercise every dispatched command, pause/continue/shutdown events, long paths, failure paths, and AFS DLL absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/Source/WinThreads.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/Source/WinTorture.c -->
# sources/distributed-fs/openafs/src/WINNT/tests/torture/Source/WinTorture.c

## Purpose

`WinTorture.c` is the top-level Windows stress-test coordinator for OpenAFS. It parses command-line options, prepares log directories and named synchronization objects, starts worker threads implemented in `WinThreads.c`, aggregates per-thread statistics, loops by iteration count or runtime, and finalizes master logs when the last process in a job finishes.

## Important APIs, Types, and Functions

- Uses `includes.h`, `common.h`, PSAPI, optional Hesiod locker resolution, and external logging/stat functions from `output.c`.
- Globals hold option state (`ClientText`, `PathToSecondDir`, `verbose`, `BufferSize`, `UseLocker`, `EndOnError`, `AfsTrace`, `ChronLog`, `PrintStats`), thread status, named mutex/event handles, and `ExitStatus`.
- `create_procs()` allocates per-thread command-stat blocks and `PARAMETERLIST` structures, creates per-thread events, starts suspended worker threads, resumes them, optionally resolves/attaches lockers, waits for all thread events, logs completion reasons, and calls `show_results()`.
- `show_results()` aggregates `cmd_struct` counters across threads, writes process stats, and updates master logs.
- `main()` parses options, derives target/locker paths, creates mutexes/events/job object/directories, runs the main iteration/time loop, builds master logs, updates process/iteration counts, and performs final job-level cleanup/renaming.
- `FindProcessCount()` uses `QueryInformationJobObject()` to determine assigned process count.
- A local `getopt()` implementation supports Unix-like option parsing on Windows.

## Control Flow

`main()` initializes defaults, parses options such as script file, target hostname/log name, iteration count, runtime, thread count, locker/UNC target, second directory, stats, tracing, end-on-error, and verbose mode. It validates required target and locker inputs, reconstructs a command-line summary, normalizes slash direction, and optionally derives an AFS locker target from Hesiod data. It creates global named mutexes/events and a job object, creates log/test directories, removes the current host log directory, and then loops.

Each loop checks time/iteration/shutdown limits, increments the loop counter, logs start time, calls `create_procs()`, logs end/lapse time, updates a shared `IterationCount` file under a mutex, handles end-on-error and recovery sleep, then repeats. After the loop it builds a `Master.log` by concatenating thread logs, builds process/master stat logs, increments `ProcessCount`, and if this is the only process in the job, moves raw count/stat files, builds the final master stat log, renames `log#####` to a timestamped directory, resets and closes global events, and releases the exit mutex.

`create_procs()` starts up to `NumberOfThreads` worker threads. It skips inactive threads when `EndOnError` is set, creates named events keyed by process ID/host/thread, passes each thread a slice of the command stats array, resumes the thread, waits for all event handles, logs per-thread completion or failure reason, aggregates results, and frees per-thread allocations.

## State and Persistence

Persistent artifacts include `log#####` directories, host subdirectories, thread logs, process stats, master logs, raw/final stat logs, `IterationCount`, and `ProcessCount`. Runtime state is coordinated through named events/mutexes (`AfsShutdownEvent`, `AfsPauseEvent`, `AfsContinueEvent`, `WinTorture*Mutex`) and a Windows job object named from `LogID`.

## Dependencies and Integration Points

The file depends on `WinThreads.c` for `StressTestThread()`, `output.c` for stats/log aggregation, `nbio.c` indirectly through worker execution, and optional Hesiod/locker attach functions. It uses Windows process, job-object, event, mutex, directory, file, time, and PSAPI APIs. It is the central executable entry point for the WinTorture test suite.

## Risks and Edge Cases

- `MAX_THREADS` is 100 but arrays such as `ThreadStatus` are sized by `MAX_HANDLES` from shared headers; option validation for `-n` is not visible here.
- Several `sprintf`, `strcpy`, and shell `system("rmdir ...")` uses are unquoted and fixed-buffer.
- `CloseHandle(hEventHandle[i])` is called after handles were already closed and nulled in an earlier loop, which can produce invalid-handle calls.
- `grand_total += FinalCmdInfo[j].total_sec` in `show_results()` indexes by thread `j` instead of command `i`, suggesting a stats aggregation bug.
- `FindProcessCount()` returns immediately after `QueryInformationJobObject()`, leaving the PSAPI fallback dead code.
- Named global events/mutexes can collide across simultaneous test runs with different working directories.
- If the process exits early, log directory renaming and event cleanup may not run.

## Test Signals

Useful signals are iteration start/end console output, thread completion logs, per-thread and process stats, master stat logs, job-level final log directory rename, correct handling of `-i` versus `-m`, and recovery behavior when `ThreadStatus` marks errors. Integration testing requires a representative command script and AFS target path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/Source/WinTorture.c -->
