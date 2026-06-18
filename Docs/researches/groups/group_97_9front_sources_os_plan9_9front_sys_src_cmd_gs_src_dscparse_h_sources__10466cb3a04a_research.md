# Group Research: group_97_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_dscparse_h_sources__10466cb3a04a

Scope: `Docs/research_subset_a.md`; source tree `sources/os/plan9/9front`.

This grouped report covers Ghostscript sources vendored under 9front's Plan 9 tree. The files in this batch are not Plan 9 filesystem implementation code; they are Ghostscript DSC parser/interpreter headers, DesqView/X build makefiles, and Win32 display/installer support sources retained in the 9front source import.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dscparse.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dscparse.h

## Role
Public interface for Ghostgum's DSC parser used by Ghostscript/GSview-style consumers. It defines the parser object layout, DSC comment return codes, document/page metadata structures, error reporting enums, and the callable parser API.

## Contents
- Establishes local scalar types (`GSBOOL`, `GSDWORD`, `GSWORD`) and configurable `DSC_OFFSET`/format macros for file offsets.
- Defines parser sizing constants: legal DSC line length, string allocation chunk size, page allocation chunk size, and scan buffer length.
- Enumerates `CDSC_RETURN_CODE` values for recognized DSC comments across header, preview, defaults, prolog, setup, page, trailer, and EOF sections.
- Defines document metadata enums for preview type, page order, orientation, and binary/clean document data.
- Provides data structures for integer and floating bounding boxes, media descriptions, viewing orientation CTM, pages, DOS EPS headers, MacBinary headers, pooled string chunks, DCS 2.0 plate records, and process/custom colors.
- Defines DSC message identifiers, severity, and response codes.
- Declares `struct CDSC_s`, including public parsed document state plus private scanner state, callbacks, memory allocator hooks, string pool state, skip counters, and reference count.
- Declares the public lifecycle, scanning, callback, reference-counting, lookup, and display/debug APIs.

## Important Interfaces
- `dsc_init`, `dsc_init_with_alloc`, `dsc_free`, `dsc_new`, `dsc_ref`, `dsc_unref`.
- `dsc_set_length`, `dsc_scan_data`, `dsc_fixup`.
- `dsc_set_error_function`, `dsc_set_debug_function`, `dsc_debug_print`.
- `dsc_find_platefile`, `dsc_stricmp`, `dsc_add_page`, `dsc_add_media`, `dsc_set_page_bbox`, `dsc_display`.

## Dependencies And Coupling
- Expects `size_t` to be visible from prior includes; this header itself does not include `<stddef.h>`.
- Exposes the full `CDSC` structure rather than an opaque handle, so clients can inspect and possibly depend on layout details.
- References `dsc_known_media` and `dsc_message` tables implemented elsewhere.
- The artificial `char dummy[1024]` at the start of `struct CDSC_s` is unusual and affects ABI/layout compatibility.

## Risks And Notes
- Default `DSC_OFFSET` is `unsigned long`, which may be 32-bit on some targets and insufficient for large PostScript/PDF inputs.
- Uses C strings and manual allocation callbacks; callers must respect parser ownership of stored string/media/page pointers.
- API exposes internal helper functions for GSview PDF handling, so implementation changes may have external compatibility impact.

## Filesystem Relevance
Indirect only. It parses file-stream metadata and tracks byte offsets into documents, but it does not implement filesystem behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dscparse.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dstack.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dstack.h

## Role
Ghostscript interpreter header defining dictionary-stack access macros and documenting dictionary lookup/cache design.

## Contents
- Includes `idstack.h` and `icstate.h`.
- Maps interpreter context fields to short dictionary-stack macros such as `idict_stack`, `d_stack`, `dsbot`, `dsp`, and `dstop`.
- Defines interpreter-specific wrappers around generic dstack APIs for name lookup, permanent dictionary tests, GC cleanup, and top-of-stack cache maintenance.
- Defines `check_dstack(n)` to fail with `e_dictstackoverflow` if the current block lacks room.
- Contains a long design note on dictionary lookup performance, current caching behavior, and a proposed improved cache/restoration-stack design.

## Important Interfaces
- Macros: `dict_find_name_by_index`, `dict_find_name`, `dict_find_name_by_index_inline`, `if_dict_find_name_by_index_top`.
- Stack/cache macros: `dict_set_top`, `dict_is_permanent_on_dstack`, `dicts_gc_cleanup`, `systemdict`.
- Safety macro: `check_dstack`.

## Dependencies And Coupling
- Tightly coupled to interpreter context variable `i_ctx_p`, `dict_stack` shape, Ghostscript ref spaces, and error constants.
- Assumes dictionary stack is a linked list of blocks and warns that full-stack operations must not only inspect the top block.

## Risks And Notes
- Mostly macro API, so misuse can cause hidden control flow (`return_error`) and context-dependent side effects.
- Comments describe an improved design but not all behavior is implemented in this header; treat notes as architecture context rather than active code.

## Filesystem Relevance
None directly. This is language interpreter state management inside the vendored Ghostscript tree.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dstack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dvx-gcc.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dvx-gcc.mak

## Role
Top-level GCC makefile for building Ghostscript on DesqView/X with X11 support.

## Contents
- Sets build directories (`BINDIR`, `GLSRCDIR`, `GLOBJDIR`, `PSSRCDIR`, `PSLIBDIR`, etc.) and installation paths rooted at DOS-style `c:/bin`, `c:/gs`, and `c:/gsfonts`.
- Configures install commands, default Ghostscript library path, initialization file name, generic compile options, executable name, and build-time Ghostscript.
- Selects bundled/shared dependency behavior for JPEG, PNG, zlib, jbig2dec, and icclib.
- Documents IJS as not ported to DesqView/X but still includes `ijs.mak` later.
- Sets compiler/linker variables for `gcc`, optimization flags, extra libraries, standard math library, and X11 include/library names.
- Defines platform values such as `FPU_TYPE=1`, `SYNC=posync`, file I/O mode, stdio implementation, band-list storage/compression, language feature devices, and display/output devices.
- Includes the platform head/tail makefiles and the Ghostscript component makefiles.

## Important Interfaces
- Build variables consumed by `gs.mak`, `lib.mak`, `int.mak`, `devs.mak`, `contrib.mak`, and `unix-end.mak`.
- Device lists `DEVICE_DEVS` through `DEVICE_DEVS20`.
- Feature list `FEATURE_DEVS`.

## Dependencies And Coupling
- Depends on many sibling makefiles in `$(GLSRCDIR)` and `$(PSSRCDIR)`.
- Assumes Quarterdeck DesqView/X/DJGPP-like environment, X11 libraries, DOS-style paths, and `coff2exe` behavior supplied by `dvx-tail.mak`.

## Risks And Notes
- Historical platform build file; many paths and library names are hard-coded and unlikely to work unchanged on modern systems.
- Comments call out security/confusion risks of `SEARCH_HERE_FIRST=1`, but it remains enabled.
- Includes `ijs.mak` even though the comments state IJS is not ported, which may require values to remain harmless/defaulted.

## Filesystem Relevance
Build-system only. It controls installation and runtime search paths but does not implement filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dvx-gcc.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dvx-head.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dvx-head.mak

## Role
Common platform header makefile fragment for DesqView/X Ghostscript builds.

## Contents
- Sets `PLATFORM=dvx_`.
- Defines command/object/executable suffixes and command-line syntax macros for a DOS/DJGPP-like make environment.
- Defines path separators, shell command variables, copy/remove commands, and genconf arguments.
- Maps internal compiler macros (`CC_D`, `CC_INT`) to `$(CC_)`.
- Clears `PCFBASM` to avoid warnings from PC-specific build pieces that are irrelevant to DV/X.

## Important Interfaces
- Variables consumed by Ghostscript's generic build rules: `CMD`, `OBJ`, `XE`, `D`, `CP_`, `RM_`, `CONFILES`, `CONFLDTR`, `CC_D`, `CC_INT`.

## Dependencies And Coupling
- Included after compiler-specific settings and before generic Ghostscript makefiles.
- Intended to pair with `dvx-tail.mak`.

## Risks And Notes
- Assumes make programs with quirks around trailing spaces and `==`; `NULL` is used to work around this.
- Historical platform support fragment.

## Filesystem Relevance
Only via build path and command variables.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dvx-head.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dvx-tail.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dvx-tail.mak

## Role
Common final makefile fragment for DesqView/X Ghostscript builds.

## Contents
- Uses `.NOEXPORT` to avoid oversized inherited environment argument lists.
- Defines the DesqView/X platform device `dvx_.dev` from platform object files and `nosync.dev`.
- Provides rules for compiling `gp_dvx.c` with `-D__DVX__` and `gp_stdin.c`.
- Provides auxiliary program build rules for `echogs`, `genarch`, `genconf`, `gendev`, `genht`, and `geninit`, compiling with GCC, stripping, converting COFF to `.exe`, and deleting intermediate executables.
- Generates `gconfig_.h` with `echogs`, defining `HAVE_SYS_TIME_H` and `HAVE_DIRENT_H`.
- Defines final interpreter link rule for `$(GS_XE)` using `ld.tr`, object/library/device lists, extra libraries, and `coff2exe`.

## Important Interfaces
- Target `$(GLGEN)dvx_.dev`.
- Targets for Ghostscript auxiliary executables.
- Target `$(gconfig__h)`.
- Target `$(GS_XE)`.

## Dependencies And Coupling
- Depends on objects and generated variables from Ghostscript generic makefiles.
- Requires platform tools `strip`, `coff2exe`, and DOS `del`.
- Assumes `/djgpp/include` for `INCLUDE`.

## Risks And Notes
- Legacy DOS/DVX build rules are brittle outside the intended toolchain.
- The platform device includes both DOS/unix-ish filesystem glue objects (`gp_unifs`, `gp_dosfs`) alongside DV/X glue.

## Filesystem Relevance
Build glue references filesystem platform objects but contains no filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dvx-tail.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwdll.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwdll.c

## Role
Win32 dynamic loader for the Ghostscript DLL (`gsdll32.dll`), populating a `GSDLL` function table.

## Contents
- Tries to load the DLL from the executable directory, then from the `GS_DLL` registry/environment value via `gp_getenv`, then via the system search path.
- Reports `LoadLibrary` failures through caller-provided `last_error`.
- Resolves Ghostscript API entry points with `GetProcAddress`.
- Checks `gsapi_revision` and requires the DLL revision to equal the compile-time `gs_revision`.
- On any missing symbol or version mismatch, unloads the DLL and returns failure.
- `unload_dll` clears all function pointers and calls `FreeLibrary`.

## Important Interfaces
- `int load_dll(GSDLL *gsdll, char *last_error, int len)`.
- `void unload_dll(GSDLL *gsdll)`.

## Dependencies And Coupling
- Includes Windows API, `gpgetenv.h`, `gscdefs.h`, and `dwdll.h`.
- Depends on symbols declared by `iapi.h` through `dwdll.h`.
- Hard-codes `gsdll32.dll` and revision equality.

## Risks And Notes
- Uses fixed-size buffers and `strcat`/`sprintf`; safe only if executable paths remain under the 1024-byte buffer size.
- Uses old `HINSTANCE_ERROR` comparison idiom.
- `strncpy(last_error, ..., len-1)` does not explicitly append a NUL after truncation.

## Filesystem Relevance
Loads DLLs from filesystem paths and search paths; no filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwdll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwdll.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwdll.h

## Role
Header defining the Win32 Ghostscript DLL function table and loader API.

## Contents
- Ensures `__PROTOTYPES__` is defined before including `iapi.h`.
- Defines `GSDLL` with an `HINSTANCE` module handle and function pointers for revision, instance lifecycle, stdio, polling, display callback, initialization, string execution, exit, and visual tracer APIs.
- Declares `load_dll` and `unload_dll`.

## Important Interfaces
- `GSDLL` struct.
- `load_dll`/`unload_dll`.

## Dependencies And Coupling
- Requires Windows `HINSTANCE` to be available before use.
- Depends on Ghostscript API pointer typedefs from `iapi.h`.

## Risks And Notes
- Consumers must check loader success before using function pointers.
- Header supports both dynamic (`dwdll.c`) and static (`dwnodll.c`) binding implementations.

## Filesystem Relevance
No direct filesystem behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwdll.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwimg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwimg.c

## Role
Win32 image window implementation for Ghostscript's display device callback. It creates and manages raster display windows, scrolling, clipboard export, separations menus, palettes, and pixel-format conversion.

## Contents
- Maintains global linked list `first_image` of `IMAGE` objects keyed by Ghostscript handle/device.
- Main-thread APIs create/find/delete image records and update bitmap metadata from Ghostscript display callbacks.
- GUI-thread APIs register/create/destroy image windows, redraw/sync pages, manage periodic update timers, and update scrollbars.
- Converts Ghostscript display formats to Windows DIB output: native indexed/16-bit/32-bit, gray, RGB, CMYK, and DeviceN separations.
- Builds palettes and clipboard DIB data, avoiding 16/32-bit clipboard formats for older viewers.
- Provides system menu commands for copying to clipboard, toggling DeviceN gray preview, and toggling individual separations.
- Window procedure handles creation, sizing, scrolling, keyboard forwarding, character forwarding to text/console, timer updates, painting, drag-and-drop, and persistence of image/tracer window geometry in the Ghostscript registry key.

## Important Interfaces
- From `dwimg.h`: `image_find`, `image_new`, `image_delete`, `image_size`, `image_open`, `image_close`, `image_sync`, `image_page`, `image_poll`, `image_updatesize`.
- Extra implemented function used externally: `image_separation`.
- Internal conversion helpers: `image_convert_line`, 16-bit RGB/BGR converters, CMYK/DeviceN converters, `copy_dib`, `create_palette`, `draw`.
- Window procedure `WndImg2Proc`.

## Dependencies And Coupling
- Includes Win32, Ghostscript API/display headers (`iapi.h`, `gdevdsp.h`), `dwmain.h`, `dwimg.h`, and `dwreg.h`.
- Shares `hwndtext` from `dwmain.h` to forward input to the text window.
- Designed to operate in both single-threaded `dwmain.c` and two-threaded `dwmainc.c`; thread safety depends on `IMAGE::hmutex` when used.
- Uses registry helpers to persist `"Image"` and `"Tracer"` window positions.

## Risks And Notes
- Several fixed-size buffers and legacy Win32 APIs are used.
- Background brush selection uses assignment in conditions (`if (lb.lbColor = RGB(...))`), which means the intended "compare and fall back if white" logic is suspect and always assigns the tested color before entering the branch.
- In `image_4CMYK_to_24BGR`, `if (i & 0)` is always false, so packed nibble handling appears broken for odd pixels.
- `image_separation` allows `comp_num == IMAGE_DEVICEN_MAX`, which is out of bounds for the array of size `IMAGE_DEVICEN_MAX`.
- Paint/clipboard paths assume valid bitmap dimensions and image pointer when called; callers must synchronize around resize/close.

## Filesystem Relevance
Only through drag-and-drop filenames and registry persistence. It is mainly GUI/raster display code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwimg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwimg.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwimg.h

## Role
Header for Win32 Ghostscript display image windows.

## Contents
- Defines `IMAGE_DEVICEN`, tracking one color separation/component: usage, visibility, name, CMYK values, and menu state.
- Defines `IMAGE_DEVICEN_MAX` as 8.
- Defines `IMAGE`, the full window/raster state object: Ghostscript handle/device, HWND, brush, raster format/pointer, BITMAPINFOHEADER, palette, DeviceN state, timer state, scroll state, mutex, linked-list pointer, associated text HWND, and saved geometry.
- Declares global `first_image`.
- Declares main-thread and GUI-thread image management APIs.

## Important Interfaces
- Main-thread API: `image_find`, `image_new`, `image_delete`, `image_size`.
- GUI-thread API: `image_open`, `image_close`, `image_sync`, `image_page`, `image_presize`, `image_poll`, `image_updatesize`.

## Dependencies And Coupling
- Requires Win32 types (`HWND`, `HBRUSH`, `BITMAPINFOHEADER`, `HPALETTE`, `HANDLE`).
- Closely paired with `dwimg.c`, `dwmain.c`, `dwmainc.c`, and `dwtrace.c`.

## Risks And Notes
- Header declares `image_presize`, but the implementation in `dwimg.c` does not define it in the read file; callbacks perform presize handling in launcher code.
- The shared `IMAGE` structure is accessed from multiple threads in console mode, so callers must honor the mutex discipline documented in `dwimg.c`.

## Filesystem Relevance
None directly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwimg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwinst.cpp -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwinst.cpp

## Role
C++ implementation of the Ghostscript Win32 installer backend (`CInstall`). It handles file copying/checking, Start Menu shortcut creation, registry updates, uninstall-log generation, and Add/Remove Programs uninstall registration.

## Contents
- Initializes COM in the constructor and uninitializes in the destructor.
- Stores source directory, file-list name, target directory, target Start Menu group, Programs folder, uninstall name, main directory, and temporary log filenames.
- Reads `filelist.txt`/`fontlist.txt`: first line uninstall name, second line main directory, remaining lines files to install.
- Recursively creates target directories for drive and UNC paths.
- Installs files by copying source files to target paths or, in no-copy mode, checking that sources exist.
- Creates temporary logs for newly installed files, old/new registry state, and old/new shell-link state.
- Uses COM `IShellLink`/`IPersistFile` to save Start Menu `.LNK` files and records pre-existing link details for restoration.
- Creates registry keys under `HKEY_LOCAL_MACHINE\SOFTWARE\<product>\<version>`, writes string values, and records old/new `.reg`-style state.
- Copies `uninstgs.exe` and writes `HKLM\...\Uninstall\<m_szUninstallName>` with `DisplayName` and `UninstallString`.
- Consolidates temporary logs into `uninstal.txt` with section separators.
- Looks up current-user or common Programs folder from registry.

## Important Interfaces
- Public `CInstall` methods in `dwinst.h`: initialization, target setters, file install, Start Menu begin/add/end, registry begin/key/value/end, uninstall writing, log creation, cleanup.
- Private helpers: `SetRegistryValue`, `CreateShellLink`, `CopyFileContents`, `ResetReadonly`.
- Free helper `reg_quote`.

## Dependencies And Coupling
- Includes Win32, COM, shell APIs, stdio, direct I/O, and `dwinst.h`.
- Used by `dwsetup.cpp`.
- Uninstall log format is consumed by `dwuninst.cpp`; section names and field names must remain compatible.
- Uses `HKEY_LOCAL_MACHINE`, so installation expects sufficient privileges for registry writes.

## Risks And Notes
- Heavy use of fixed-size `MAXSTR` buffers and `strcpy`/`strcat`/`sprintf`.
- `MakeDir` UNC detection checks `dirname[1] == '\\' && dirname[1] == '\\'`, likely meant to check both first and second characters.
- `MakeTemp` uses `mktemp`, which is race-prone.
- Some error paths close temporary files directly and may leave class members pointing at closed streams until cleanup.
- Start Menu logging field names must match uninstaller expectations; inconsistency would prevent restoration.

## Filesystem Relevance
Installer file operations only: directory creation, file copy/delete logging, temporary files, shortcut files. Not filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwinst.cpp -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwinst.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwinst.h

## Role
Class declaration for the Ghostscript Win32 installer backend.

## Contents
- Defines `MAXSTR` from `MAX_PATH` or 256.
- Declares `CInstall` constructor/destructor and public methods for message callbacks, program/folder lookup, initialization, file installation, directory creation, temp file creation, all-users mode, target setters, Start Menu operations, registry operations, uninstall entry/log generation, cleanup, and appending installed-file records.
- Stores installer state, paths, log filenames, log stream pointers, and message callback.
- Declares private helpers for registry value writing, shell-link creation, file copying, and readonly attribute reset.

## Important Interfaces
- `CInstall` public API is the contract used by `dwsetup.cpp`.

## Dependencies And Coupling
- Requires Win32 types (`BOOL`, `HKEY`, `LPCSTR`) and `FILE`.
- Paired with `dwinst.cpp`.

## Risks And Notes
- Path buffers are fixed-size and public methods accept raw C strings.
- Members `m_bNoCopy`, `m_bQuit`, and some flags are declared but not central in the implementation, suggesting historical leftovers.

## Filesystem Relevance
Installer helper abstraction for filesystem copy/log operations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwinst.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwmain.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwmain.c

## Role
Win32 GUI executable launcher for Ghostscript. It creates a text window for stdio, loads the Ghostscript API, installs display callbacks, and runs the interpreter.

## Contents
- Defines global instance handle, text-window pointer, `GSDLL` table, Ghostscript instance pointer, and `hwndtext`.
- Implements message polling that dispatches Windows messages and aborts Ghostscript if the text window is closing.
- Redirects Ghostscript stdin/stdout/stderr to the custom text window.
- Implements display-device callbacks that create/delete/update/sync/page image windows through `dwimg.c`.
- Defines `display_callback display` for Ghostscript display device integration.
- `new_main` loads the DLL, creates an instance, optionally initializes the visual tracer under `DEBUG`, sets stdio/poll/display callbacks, injects default display format and resolution arguments, runs `gsapi_init_with_args`, runs `systemdict /start get exec`, exits and deletes the instance, unloads the DLL, and maps Ghostscript error codes to process status.
- `WinMain` parses the command line manually, creates and configures the text window, restores/saves text-window position through registry helpers, runs `new_main`, and keeps the error window open on failure.
- `set_font` reads/writes `gswin32.ini` font settings.

## Important Interfaces
- Entry point `WinMain`.
- Internal Ghostscript runner `new_main`.
- Display callback table `display`.
- Stdio callbacks `gsdll_stdin`, `gsdll_stdout`, `gsdll_stderr`; poll callback `gsdll_poll`.

## Dependencies And Coupling
- Includes Ghostscript API/errors/display headers, visual tracer header, and local Win32 helpers `dwdll`, `dwtext`, `dwimg`, `dwtrace`, `dwreg`.
- Shares image/text window behavior with `dwimg.c` and `dwtext.c`.
- Depends on registry helper values `"Text"` for geometry.

## Risks And Notes
- Manual command-line parser handles quotes but not embedded quotes and uses `MAXCMDTOKENS=128`.
- Allocates `nargv` without checking `malloc` result.
- Uses structured exception handling only for MSVC/Borland stack overflow cases.
- Display size/sync callbacks assume `image_find` succeeds before dereferencing in some paths.

## Filesystem Relevance
Interacts with filenames through command line and drag/drop via text/image windows, but primarily process/UI glue.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwmain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwmain.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwmain.h

## Role
Small shared Win32 launcher header.

## Contents
- Defines resource icon IDs `GSTEXT_ICON` and `GSIMAGE_ICON`.
- Declares external `HWND hwndtext`.

## Important Interfaces
- `hwndtext` shared by image code for forwarding key and drag/drop input to the text window.

## Dependencies And Coupling
- Requires `HWND` from Win32 headers before inclusion.
- Used by `dwmain.c`, `dwimg.c`, and related Win32 sources.

## Risks And Notes
- Minimal global-state header.

## Filesystem Relevance
None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwmain.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwmainc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwmainc.c

## Role
Win32 console executable launcher for Ghostscript. It keeps stdio on the console while running display windows on a separate GUI thread.

## Contents
- Provides Ghostscript stdio callbacks backed by `_read`, `fwrite`, and `fflush`.
- Spawns a GUI message thread (`winthread`) because the main thread may block on stdin while Ghostscript runs.
- Uses custom `WM_USER+101` and later messages to ask the GUI thread to open/close/resize/sync/page/poll display windows.
- Implements display callbacks with mutex discipline around image raster access.
- Maintains `first_image` via `image_new`, `image_find`, `image_delete`; posts GUI operations to `thread_id`.
- Initializes DLL/API, optional visual tracer under `DEBUG`, display callback, display format/resolution arguments, and Ghostscript execution.
- Sets console stdin/stdout/stderr modes to binary as appropriate.
- Shuts down the GUI thread by posting `WM_QUIT`.

## Important Interfaces
- Entry point `main`.
- Display callback table `display`.
- GUI thread message handler `winthread`.
- Display callbacks: `display_open`, `display_preclose`, `display_close`, `display_presize`, `display_size`, `display_sync`, `display_page`, `display_update`, `display_separation`.

## Dependencies And Coupling
- Includes Win32, CRT I/O/process headers, Ghostscript API/display/trace headers, and local `dwdll`, `dwimg`, `dwtrace`.
- Paired with `dwimg.c` for image-window implementation.
- Uses `hwndtext = NULL` to signal console mode to image windows.

## Risks And Notes
- `image_new` is dereferenced for mutex creation before checking `img` for null.
- Thread startup wait checks `hthread == INVALID_HANDLE_VALUE`, but `hthread` is a global not initialized to that sentinel in the file.
- Uses `PostThreadMessage`; messages can fail until the thread has created a message queue, hence the explicit retry loop.
- Main and GUI threads rely on correct mutex acquisition/release around image raster pointers.

## Filesystem Relevance
No direct filesystem implementation. Console/drop interactions may pass filenames to Ghostscript.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwmainc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwnodll.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwnodll.c

## Role
Static-link alternative to `dwdll.c` for filling the `GSDLL` table without loading a DLL.

## Contents
- Includes the same Ghostscript/Win32 setup headers as the dynamic loader.
- `load_dll` assigns Ghostscript API function pointers directly to linked symbols.
- `unload_dll` is a no-op.

## Important Interfaces
- `load_dll`.
- `unload_dll`.

## Dependencies And Coupling
- Requires the Ghostscript API symbols (`gsapi_new_instance`, `gsapi_delete_instance`, etc.) to be linked into the executable.
- Uses the same `GSDLL` structure as dynamic loading.

## Risks And Notes
- Does not populate `revision` or `hmodule`; consumers relying on those fields after load must account for static mode.
- No version check is performed because the functions are statically linked.

## Filesystem Relevance
None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwnodll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwreg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwreg.c

## Role
Win32 registry helper for Ghostscript application settings.

## Contents
- Builds a registry key path under `Software\<gs_productfamily>`.
- Reads named string values from `HKEY_CURRENT_USER`.
- Writes named string values under `HKEY_CURRENT_USER`, creating the product key if needed.
- Mimics `gp_getenv`-style return behavior for value lookup: `0` found/copied, `-1` buffer too small, `1` not found.

## Important Interfaces
- `win_registry_key`.
- `win_get_reg_value`.
- `win_set_reg_value`.

## Dependencies And Coupling
- Includes Win32 registry APIs and `gscdefs.h` for `gs_productfamily`.
- Declared by `dwreg.h`; used by `dwmain.c` and `dwimg.c`.

## Risks And Notes
- `win_registry_key` return value is ignored by callers inside this file.
- Uses fixed 256-byte key buffers.
- Registry values are per-user, unlike installer registry entries that are under HKLM.

## Filesystem Relevance
None directly; stores window positions and settings outside the filesystem.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwreg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwreg.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwreg.h

## Role
Header for Win32 Ghostscript application registry helpers.

## Contents
- Declares `win_get_reg_value` and `win_set_reg_value` for named registry values.

## Important Interfaces
- `int win_get_reg_value(const char *name, char *ptr, int *plen)`.
- `int win_set_reg_value(const char *name, const char *value)`.

## Dependencies And Coupling
- Implementation in `dwreg.c`.
- Return semantics align with Ghostscript environment lookup conventions.

## Risks And Notes
- Minimal API; caller supplies buffer length pointer for reads.

## Filesystem Relevance
None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwreg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwsetup.cpp -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwsetup.cpp

## Role
Win32 setup application for AFPL Ghostscript. It provides interactive and batch installation, drives `CInstall`, creates file lists, writes registry/search-path values, creates Start Menu shortcuts, optionally installs fonts/CJK support, and launches uninstall setup.

## Contents
- Documents expected self-extracting archive contents and `filelist.txt`/`fontlist.txt` format.
- Defines global installer state: source directory, target directory, Start Menu group, app name, flags for batch/no-copy/fonts/CJK/all-users, dialog handles, and quit/error flags.
- `WinMain` calls `init`, then runs the message loop for interactive mode.
- Provides a modeless install log dialog with copy-to-clipboard support and rolling text buffer.
- Provides a simple directory/group browse dialog using `DlgDirList`/`DlgDirSelectEx`.
- `init` validates Windows version, parses command line, supports file-list creation mode, batch install mode, and interactive dialog setup.
- `install_all` runs program and optional font installation, handles no-copy mode, displays log, and opens the Start Menu folder on success.
- `install_prog` copies program files, calculates version from main directory name, writes `GS_DLL` and `GS_LIB` under `HKLM\SOFTWARE\AFPL Ghostscript\<version>`, creates Start Menu links to `gswin32.exe` and `Readme.htm`, optionally rewrites `lib\cidfmap`, writes uninstall logs, and registers uninstall.
- `install_fonts` copies font files and writes font uninstall logs unless in no-copy mode.
- `get_font_path` and `write_cidfmap` build Windows fonts path and launch hidden `gswin32c.exe` with `mkcidfm.ps` to generate `cidfmap`.
- `dirwalk` and `make_filelist` create file-list manifests from path specs or `@file` lists.
- `GetProgramFiles` dynamically resolves shell folder APIs or falls back to registry.

## Important Interfaces
- Entry point `WinMain`.
- Dialog procs `TextWinDlgProc`, `DirDlgProc`, `MainDlgProc`.
- Installation routines `install_all`, `install_prog`, `install_fonts`.
- Manifest helpers `dirwalk`, `make_filelist`.
- Utility `GetProgramFiles`.

## Dependencies And Coupling
- Uses `CInstall` from `dwinst.cpp`.
- Uses resource IDs from `dwsetup.h`.
- Produces uninstall logs consumed by `dwuninst.cpp`.
- Requires `filelist.txt`, optionally `fontlist.txt`, and a source tree with Ghostscript binaries/libs.
- Uses Shell/COM/registry APIs and may require privileges for HKLM and common Start Menu writes.

## Risks And Notes
- Manual command-line parser has limited quote handling.
- Extensive fixed-size buffer concatenation.
- `write_cidfmap` starts Ghostscript and returns success without waiting for or checking the child process result.
- Batch mode suppresses UI unless errors occur.
- File-list generation recursively walks directories through Win32 `FindFirstFile`.

## Filesystem Relevance
Installer/file-list generation code: copies files, creates directories, launches files, writes generated config files. Not filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwsetup.cpp -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwsetup.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwsetup.h

## Role
Resource identifier header for the Ghostscript Win32 setup program.

## Contents
- Defines dialog IDs, resource IDs, string IDs, and control IDs used by `dwsetup.cpp` and resources.
- Includes IDs for main dialog controls: target directory/group, browse buttons, readme, install fonts, text log, install button, all-users checkbox, copyright, and CJK fonts.

## Important Interfaces
- IDs such as `IDD_MAIN`, `IDD_TEXTWIN`, `IDC_TARGET_DIR`, `IDC_INSTALL`, `IDC_INSTALL_FONTS`, `IDC_ALLUSERS`, `IDC_CJK_FONTS`.

## Dependencies And Coupling
- Paired with resource scripts and `dwsetup.cpp`.

## Risks And Notes
- Values must stay synchronized with `.rc` resources.

## Filesystem Relevance
None directly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwsetup.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwtext.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwtext.c

## Role
Custom Win32 text-window implementation used as Ghostscript GUI stdio console.

## Contents
- Defines a `TW`-backed text window class with fixed-size screen buffer, keyboard circular buffer, font metrics, scroll state, drag/drop strings, and line-input buffering.
- Implements font selection, screen size setup, window positioning, object allocation/destruction, class registration, and window creation.
- Writes output into the screen buffer with handling for CR, LF, BEL, tab, backspace/delete, wrapping, and scrolling.
- Provides blocking character and line input using the Windows message loop and keyboard buffer.
- Supports file drag/drop by injecting configured pre/post strings and converted path characters into the keyboard stream.
- Supports copy-to-clipboard of the screen buffer and paste-from-clipboard into the keyboard buffer.
- Window procedure handles system menu copy/paste, focus/caret, move/size/scroll, keyboard navigation, character buffering, painting visible screen buffer lines, drop files, close, and destroy.
- Includes a disabled `NOTUSED` test program.

## Important Interfaces
- `text_new`, `text_destroy`, `text_register_class`, `text_create`.
- `text_font`, `text_size`, `text_setpos`, `text_getpos`.
- `text_putch`, `text_write_buf`, `text_puts`, `text_getch`, `text_gets`, `text_read_line`, `text_kbhit`.
- `text_drag`, `text_to_cursor`, `text_get_handle`.
- Window procedure `WndTextProc`.

## Dependencies And Coupling
- Uses Win32, WindowsX, common dialog, shell drag/drop APIs, and `dwtext.h`.
- Used by `dwmain.c` for GUI Ghostscript stdio.

## Risks And Notes
- The opening file comment is malformed-looking in the read source: `/* Microsoft Windows text window for Ghostscript.` is followed by includes without a visible closing `*/` before them. In this repository content, that would comment out following includes until the later `*/` in an inline include comment; this appears to be an upstream text oddity or transcription artifact worth verifying if compiling.
- Fixed-size buffers, manual circular buffer management, and blocking message loops make behavior sensitive to window lifecycle.
- `text_read_line` does not NUL-terminate returned buffers by design.
- Copy/paste and drag/drop use legacy `CF_TEXT` and fixed path buffers.

## Filesystem Relevance
Only drag/drop filename injection and no direct filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwtext.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwtext.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwtext.h

## Role
Header for the custom Win32 text-window class used by Ghostscript GUI launcher.

## Contents
- Defines `TW`, holding title/icon, screen buffer, screen size, drag/drop strings, window handle, keyboard buffer, quit state, line input buffer/state, focus/input state, font settings, caret/cursor metrics, scroll state, and saved geometry.
- Declares text window lifecycle, input, output, scrolling, class registration, window creation, font/size/position, drag/drop, and handle accessor functions.

## Important Interfaces
- `TW` struct.
- `text_new`, `text_destroy`, `text_kbhit`, `text_gets`, `text_read_line`, `text_putch`, `text_write_buf`, `text_puts`, `text_to_cursor`, `text_register_class`, `text_create`, `text_font`, `text_size`, `text_setpos`, `text_getpos`, `text_drag`, `text_get_handle`.

## Dependencies And Coupling
- Requires Win32 types (`HICON`, `BYTE`, `POINT`, `HWND`, `BOOL`, `HFONT`).
- Used by `dwmain.c` and implemented by `dwtext.c`.

## Risks And Notes
- Declares `int getch(void);` rather than `text_getch`, even though implementation defines `text_getch`; this may be a stale declaration.
- `TW` is fully exposed, so callers can couple to internal state.

## Filesystem Relevance
None directly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwtext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwtrace.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwtrace.c

## Role
Win32 graphical trace server for Ghostscript visual debugging, implementing `vd_trace_interface` callbacks with GDI drawing into an image/tracer window.

## Contents
- Defines `vd_trace_host_s` holding initialization state, tracer `IMAGE`, HDC nesting count, window height, line width, current color, selected pen/brush objects, and last move point.
- Lazily creates a tracer window using `image_new(NULL, NULL)` and `image_open`.
- Converts RGB integers to Windows `COLORREF`.
- Provides coordinate conversion with Y-axis inversion based on current window height.
- Manages HDC acquisition/release with nested `get_dc`/`release_dc` counting and pen/brush selection/deletion.
- Implements trace drawing callbacks for erase, begin/end path, move, line, Bezier curve, close path, circle, filled round marker, fill, stroke, set color, set line width, text, and placeholder wait.
- Reads optional scale/shift/origin adjustments from `gs_vdtrace.ini`.
- `visual_tracer_init` installs callbacks into global `visual_tracer`; `visual_tracer_close` deletes/closes the tracer image.

## Important Interfaces
- Global `vd_trace_interface visual_tracer`.
- `visual_tracer_init`.
- `visual_tracer_close`.

## Dependencies And Coupling
- Includes `dwimg.h` before Ghostscript headers to avoid `RGB` macro conflicts.
- Uses `vdtrace.h`, `gsdll.h`, `gscdefs.h`, and local `dwtrace.h`.
- Reuses image-window infrastructure from `dwimg.c`; tracer windows are identified by `device == NULL`.

## Risks And Notes
- Comment states WM_PAINT restoration is not implemented, so trace drawings may not repaint after exposure.
- `dw_gt_erase` passes raw `rgbcolor` to `CreateSolidBrush` rather than using `WindowsColor`, unlike pen/brush creation elsewhere.
- Several callbacks call `get_window` but then assume an HDC is already active; callers must respect the trace interface get/release protocol.
- Uses `private` macro from Ghostscript headers after include ordering.

## Filesystem Relevance
None, except reading trace settings from an INI file.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwtrace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwtrace.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwtrace.h

## Role
Header for the Win32 graphical trace server interface.

## Contents
- Declares external `visual_tracer`.
- Declares initialization and cleanup functions.

## Important Interfaces
- `extern struct vd_trace_interface_s visual_tracer`.
- `visual_tracer_init`.
- `visual_tracer_close`.

## Dependencies And Coupling
- Requires the `vd_trace_interface_s` type to be visible or at least forward-declarable as a struct tag.
- Implemented by `dwtrace.c`; used by `dwmain.c` and `dwmainc.c` under `DEBUG`.

## Risks And Notes
- Minimal debug-only style interface.

## Filesystem Relevance
None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwtrace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwuninst.cpp -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwuninst.cpp

## Role
Win32 uninstaller for Ghostscript. It reads `uninstal.txt` logs generated by `CInstall`, removes installed files and shortcuts, restores old registry values and shell links, and removes Add/Remove Programs entries.

## Contents
- Parses command line to locate uninstall log path.
- Validates log structure and reads the uninstall title.
- Uses section separators (`////////////////////////////////`) and section names to dispatch uninstall actions.
- Deletes files listed in `FileNew`.
- Deletes registry keys/values described in `RegistryNew`, scanning keys first and deleting in reverse order.
- Restores registry values from `RegistryOld` with a `REGEDIT4`-style parser and unquoting helper.
- Removes Start Menu links/folder from `ShellNew`.
- Restores old Start Menu links from `ShellOld` using COM `IShellLink`.
- Deletes the uninstall log at EOF and posts the completion message.
- Displays a modeless removal dialog with progress text and start/exit controls.
- Removes the uninstall registry key under `HKLM\...\Uninstall\<title>` after completion.

## Important Interfaces
- Entry point `WinMain`.
- Dialog proc `RemoveDlgProc`.
- Log parsing helpers `GetLine`, `IsSection`, `NextSection`, `ReadSection`.
- Action handlers `dofiles`, `registry_delete`, `registry_import`, `shell_new`, `shell_old`, `doEOF`.
- Shell helper `CreateShellLink`; directory helper `MakeDir`.

## Dependencies And Coupling
- Consumes exact log format written by `dwinst.cpp`.
- Uses Win32 registry, shell, COM, and file APIs.
- Uses resource IDs from `dwuninst.h`.

## Risks And Notes
- Fixed-size buffers and manual command-line parsing.
- `MakeDir` repeats the same UNC test bug pattern as installer code (`dirname[1]` checked twice).
- `shell_old` looks for `"Program"` entries, while installer logs shortcut path as `"Path"`; this mismatch may prevent restoring previous links.
- Registry deletion parser creates/open keys while deleting values and then deletes keys by saved names; malformed logs could cause partial removal.
- Does not remove directories except the Start Menu group and does not remove itself, by design noted in setup comments.

## Filesystem Relevance
Uninstall file deletion and shortcut restoration only. Not filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwuninst.cpp -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwuninst.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwuninst.h

## Role
Resource identifier header for the Ghostscript Win32 uninstaller.

## Contents
- Defines menu/dialog/control IDs for uninstall resources, including dialog ID, icon, progress text, done/press-ok controls, and text labels.

## Important Interfaces
- IDs such as `ID_UNINSTGS`, `ID_UNINST`, `IDD_UNSET`, `IDC_GSICON`, `IDC_PROG`, `IDC_DONE`, `IDC_PRESSOK`, `IDC_T1`, `IDC_T2`.

## Dependencies And Coupling
- Paired with resource scripts and `dwuninst.cpp`.

## Risks And Notes
- Minimal resource contract; duplicate value aliases are intentional (`IDC_DONE`/`IDC_PRESSOK`).

## Filesystem Relevance
None directly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dwuninst.h -->