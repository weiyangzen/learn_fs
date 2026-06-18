# Group Research: group_1535_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_dscparse_h_sources__65064e9bc51d

Scope checked against `Docs/research_subset_a.md`. All listed files are within `sources/os/plan9/plan9`, but this group is Ghostscript support code carried in the Plan 9 source tree, mostly Windows/DesqView/X display, setup, uninstall, registry, and build support plus one DSC parser interface and one interpreter dictionary-stack header.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dscparse.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dscparse.h

Purpose: Public interface and data model for Ghostscript/Ghostgum DSC parsing. It defines the parser state, DSC comment return codes, page/media/bounding-box metadata, preview metadata, DCS 2.0 plate-file metadata, color separation metadata, and callback hooks.

Key structures and APIs:
- `CDSC`: central parser object containing public document metadata and private scan state.
- `CDSCPAGE`, `CDSCMEDIA`, `CDSCBBOX`, `CDSCFBBOX`, `CDSCCTM`: parsed page/media/geometry records.
- `CDSCDOSEPS`, `CDSCMACBIN`: binary EPS/MacBinary offsets.
- `CDSCSTRING`: chunk allocator list for parser-owned strings.
- `CDCS2`, `CDSCCOLOUR`: DCS 2.0 and process/custom color records.
- Public lifecycle and parsing calls: `dsc_init`, `dsc_init_with_alloc`, `dsc_free`, `dsc_new`, `dsc_ref`, `dsc_unref`, `dsc_set_length`, `dsc_scan_data`, `dsc_fixup`.
- Callback configuration: `dsc_set_error_function`, `dsc_set_debug_function`.
- Utility/exported helpers: `dsc_find_platefile`, `dsc_stricmp`, `dsc_add_page`, `dsc_add_media`, `dsc_set_page_bbox`, `dsc_display`.

Implementation notes:
- Offsets use configurable `DSC_OFFSET`, defaulting to `unsigned long`; large-file support requires overriding this typedef/macro pair.
- Line handling is bounded around DSC’s 255-character legal line length, with a larger 8192-byte scan buffer.
- Return codes group comments by DSC section, with ranges for header, preview, defaults, prolog, setup, page, trailer, and EOF.
- `struct CDSC_s` contains `char dummy[1024]` before real fields, likely ABI padding or legacy compatibility.
- The header mixes public and private fields in one exposed struct, so consumers can couple to internal scan state.

Filesystem relevance: Indirect. It models document offsets and file lengths for PostScript/EPS parsing but has no OS/VFS behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dscparse.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dstack.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dstack.h

Purpose: Interpreter dictionary-stack definitions and performance design notes for Ghostscript’s PostScript interpreter.

Key definitions:
- Maps interpreter context fields to shorthand stack macros: `idict_stack`, `d_stack`, `dsbot`, `dsp`, `dstop`.
- Defines stack capacity check macro `check_dstack(n)`.
- Exposes dictionary-stack lookup wrappers such as `dict_find_name_by_index`, `dict_find_name`, and inline/top lookup variants.
- Defines shorthand for dictionary stack state: `min_dstack_size`, `dstack_userdict_index`, `dsspace`, `dtop_*`, `systemdict`.

Design notes:
- The file includes a long architecture note on dictionary lookup performance.
- It describes existing lookup caching around name values, top-dictionary key/value caches, and def-region caches.
- It proposes an improved per-context name lookup cache `C`, restoration stack `R`, per-stack-entry restoration-depth metadata, and dictionary occurrence counts.
- It covers required invalidation/repair behavior for `def`, `put`, `undef`, `restore`, dictionary grow, `begin`, `end`, context switch, access changes, and GC relocation.

Filesystem relevance: None directly. It is core Ghostscript interpreter state machinery, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dstack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dvx-gcc.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dvx-gcc.mak

Purpose: Top-level makefile for building Ghostscript on DesqView/X with GCC and X11.

Key build configuration:
- Directory defaults: `BINDIR=bin`, `GLSRCDIR=src`, generated/object dirs under `obj`, `PSLIBDIR=lib`.
- Install defaults: `prefix=c:/bin`, `gsdatadir=c:/gs`, `gsfontdir=c:/gsfonts`.
- Runtime library path: `GS_LIB_DEFAULT="$(gsdatadir)/lib;$(gsdatadir)/Resource;$(gsfontdir)"`.
- Compiler/linker: `CC=gcc`, `CFLAGS=-O $(XCFLAGS)`, `EXTRALIBS=-lsys -lc`, `STDLIBS=-lm`.
- X11 settings: default `XLIBS=Xt Xext X11`.
- Feature devices include PostScript Level 3, PDF, DPS, TrueType, EPSF, pipe, and FAPI.
- Default output device is `x11.dev`, with many printer/image/pdfwrite devices enabled across `DEVICE_DEVS*`.

Included makefiles:
- `dvx-head.mak`, `gs.mak`, `lib.mak`, `int.mak`, `cfonts.mak`, JPEG/zlib/libpng/jbig2/icclib/ijs makefiles, `devs.mak`, `contrib.mak`, `dvx-tail.mak`, `unix-end.mak`, `unixinst.mak`.

Filesystem relevance: Build/install paths and runtime search paths only. No OS filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dvx-gcc.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dvx-head.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dvx-head.mak

Purpose: Shared DesqView/X makefile header included before the generic Ghostscript makefiles.

Key definitions:
- Sets `PLATFORM=dvx_`.
- Defines command/object/executable suffix conventions: `.bat`, `.o`, `.exe`.
- Defines make syntax helpers for `-D`, `-I`, output switches, quoting, and no-op commands.
- Defines DOS/DesqView/X command flavor: `CAT=type`, path separator `D=\\`, empty shell variables.
- Sets generic file commands `CP_=cp`, `RM_=rm -f`.
- Sets `genconf` arguments: `CONFILES=-p -pl &-l%%s`, `CONFLDTR=-ol`.
- Makes `CC_D` and `CC_INT` aliases to `CC_`.
- Clears `PCFBASM` to avoid irrelevant PC framebuffer assembler warnings.

Filesystem relevance: Only build-path and shell-command conventions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dvx-head.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dvx-tail.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dvx-tail.mak

Purpose: Shared DesqView/X makefile tail, included after device and feature makefiles.

Key targets:
- Defines `dvx_.dev` from platform objects `gp_getnv`, `gp_dvx`, `gp_unifs`, `gp_dosfs`, `gp_stdin`, and `nosync.dev`.
- Builds `gp_dvx.o` with `-D__DVX__`.
- Provides DesqView/X auxiliary program build rules for `echogs`, `genarch`, `genconf`, `gendev`, `genht`, and `geninit`, using `strip`, `coff2exe`, and `del`.
- Generates `gconfig_.h` with `HAVE_SYS_TIME_H` and `HAVE_DIRENT_H`.
- Links the main Ghostscript executable by copying `ld.tr`, appending extra/standard libs, invoking `gcc`, stripping, converting COFF to `.exe`, and deleting the intermediate.

Notable behavior:
- Uses `.NOEXPORT` to prevent huge environment propagation into command lines.
- Hardcodes `INCLUDE=/djgpp/include` for config generation.

Filesystem relevance: Build artifact creation and generated config only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dvx-tail.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwdll.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwdll.c

Purpose: Runtime loader for `gsdll32.dll` on Windows.

Key behavior:
- `load_dll` tries to load `gsdll32.dll` from:
  1. The executable directory.
  2. `GS_DLL` environment/registry value via `gp_getenv`.
  3. The system DLL search path.
- After loading, it resolves Ghostscript API entry points with `GetProcAddress`.
- Validates DLL revision using `gsapi_revision` against compiled `gs_revision`.
- Required functions include instance creation/deletion, stdio, poll, display callback, initialization, run-string, exit, and visual tracer setup.
- `unload_dll` nulls all function pointers and frees the module.

Risks/legacy notes:
- Uses fixed 1024-byte path buffer and `strcat`/`sprintf`.
- Uses old `HINSTANCE_ERROR` comparison style.
- Does not consistently force NUL termination after `strncpy`.

Filesystem relevance: DLL discovery path behavior only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwdll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwdll.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwdll.h

Purpose: Declares the Windows Ghostscript DLL dispatch structure and loader API.

Key definitions:
- `GSDLL` stores `HINSTANCE hmodule` plus function pointers for the Ghostscript C API.
- Function pointers cover revision, instance lifecycle, stdio, poll, display callback, argument initialization, string execution, exit, and visual tracing.
- Declares `load_dll(GSDLL *, char *last_error, int len)` and `unload_dll(GSDLL *)`.

Dependencies:
- Requires Windows types and Ghostscript `iapi.h`.
- Forces `__PROTOTYPES__` if absent.

Filesystem relevance: None beyond DLL loading interface.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwdll.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwimg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwimg.c

Purpose: Win32 image display window implementation for Ghostscript’s display device and graphical trace window.

Major responsibilities:
- Maintains a process-global linked list of `IMAGE` objects keyed by Ghostscript handle/device.
- Creates and destroys image windows.
- Converts Ghostscript display formats to Windows DIB-compatible formats.
- Manages palettes, clipboard export, scroll bars, repainting, drag/drop forwarding, and DeviceN/separation menu controls.
- Supports single-thread and multi-thread modes through per-image mutexes.

Key functions:
- Main-thread image management: `image_find`, `image_new`, `image_delete`, `image_size`, `image_separation`.
- GUI-thread lifecycle: `image_open`, `image_close`, `image_sync`, `image_page`, `image_poll`, `image_updatesize`.
- Color conversion: 16-bit RGB/BGR 555/565 converters, CMYK 4-bit/32-bit conversion, DeviceN conversion, `image_convert_line`.
- Clipboard: `copy_dib`.
- Rendering: `WndImg2Proc`, `draw`.

Notable behavior:
- Supports native, gray, RGB, CMYK, and separation display formats from `gdevdsp.h`.
- For CMYK/DeviceN, adds system-menu entries for visible separations and optional gray display when one component is visible.
- Saves/restores window positions via `win_get_reg_value`/`win_set_reg_value`.
- Uses `SetDIBitsToDevice`, splitting transfers because old Windows limits large DIB transfers.

Risks/bugs observed:
- In `create_window`, comparisons like `if (lb.lbColor = RGB(...))` are assignments, so the intended color checks are not actually comparisons.
- In `image_4CMYK_to_24BGR`, `if (i & 0)` is always false, so odd-pixel nibble selection appears broken.
- Uses old `SetWindowLong`/`GetWindowLong` casts to `LONG`, not pointer-width safe.
- Fixed-size path/title buffers and many unchecked string operations.
- Clipboard path leaks the global allocation if `GlobalLock` fails after `GlobalAlloc`.

Filesystem relevance: None directly. It is Win32 UI/rendering code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwimg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwimg.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwimg.h

Purpose: Declares the `IMAGE` and `IMAGE_DEVICEN` structures plus image-window APIs.

Key structures:
- `IMAGE_DEVICEN`: used/visible flags, component name, CMYK equivalent values, and menu state.
- `IMAGE`: Ghostscript handle/device, Win32 window/brush/palette state, raster format, image pointer, `BITMAPINFOHEADER`, DeviceN state, update timer state, scroll state, mutex, linked-list pointer, text-window handle, and saved window rectangle.

Public API:
- Main-thread only: `image_find`, `image_new`, `image_delete`, `image_size`.
- GUI-thread only: `image_open`, `image_close`, `image_sync`, `image_page`, `image_presize`, `image_poll`, `image_updatesize`.

Notes:
- Header declares `image_presize`, but the read implementation in `dwimg.c` does not define it.
- The shared `first_image` list is exported.

Filesystem relevance: None.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwimg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwinst.cpp -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwinst.cpp

Purpose: C++ helper class implementing Windows Ghostscript installation operations.

Class: `CInstall`.

Main responsibilities:
- Initializes install source/list metadata.
- Copies listed files or validates them in no-copy mode.
- Creates directories recursively.
- Creates Start Menu folders and shell links via COM `IShellLink`/`IPersistFile`.
- Writes and records registry updates.
- Copies uninstaller and writes Add/Remove Programs uninstall keys.
- Builds consolidated uninstall logs from temporary file/registry/shell logs.
- Provides Start Menu folder lookup.

Key methods:
- Lifecycle/message: constructor/destructor, `CleanUp`, `SetMessageFunction`, `AddMessage`.
- Paths/init: `SetTargetDir`, `SetTargetGroup`, `Init`, `GetMainDir`, `GetUninstallName`, `GetPrograms`, `SetAllUsers`.
- File copy: `InstallFiles`, `InstallFile`, `AppendFileNew`, `MakeDir`, `ResetReadonly`.
- Shell: `StartMenuBegin`, `StartMenuAdd`, `StartMenuEnd`, `CreateShellLink`.
- Registry: `UpdateRegistryBegin`, `UpdateRegistryKey`, `UpdateRegistryValue`, `SetRegistryValue`, `UpdateRegistryEnd`.
- Uninstall/logging: `WriteUninstall`, `MakeTemp`, `MakeLog`, `CopyFileContents`.

Important details:
- Installer file lists use the first line as uninstall name, second line as main directory, subsequent lines as files.
- Registry update logs are written in `REGEDIT4`-style form for later uninstall restore/delete.
- `MakeTemp` uses `mktemp`, making it race-prone by modern standards.
- `MakeDir` has a UNC-path typo: `dirname[1]=='\\' && dirname[1]=='\\'` should likely test indexes 0 and 1.
- String handling is mostly fixed-buffer `strcpy`/`strcat`/`sprintf`.

Filesystem relevance: File installation/uninstallation and directory creation behavior, but only for Windows Ghostscript packaging.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwinst.cpp -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwinst.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwinst.h

Purpose: Declares the `CInstall` class for the Windows Ghostscript installer.

Public capabilities:
- Configure message callback, target directory/group, and all-users mode.
- Initialize from source directory and file list.
- Install files, individual files, and make directories.
- Manage Start Menu entries.
- Begin/update/end registry modifications.
- Write uninstall metadata and consolidated uninstall logs.
- Clean up temporary files.
- Append extra generated files to the uninstall file list.

Private state:
- Source/list/target/group/programs paths.
- Uninstall name and main/log directories.
- Temporary log filenames for files, registry, and shell.
- Open log file handles.
- Internal helpers for shell links, registry values, file copying, and readonly-bit reset.

Filesystem relevance: Installer path/file bookkeeping declarations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwinst.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwmain.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwmain.c

Purpose: Win32 GUI launcher for Ghostscript using `gsdll32.dll`.

Major responsibilities:
- Creates a text window for redirected Ghostscript stdio.
- Loads the Ghostscript DLL and creates a Ghostscript instance.
- Registers stdio, polling, and display callbacks.
- Creates image display windows via `dwimg.c`.
- Determines default display format/resolution from the desktop device context.
- Runs Ghostscript initialization and `systemdict /start get exec`.
- Saves/restores text window size through registry helper functions.

Key parts:
- `poll`: pumps Win32 messages and aborts if the text window is closing.
- `gsdll_stdin/stdout/stderr`: bridge Ghostscript stdio to `TW`.
- Display callback functions: `display_open`, `display_close`, `display_size`, `display_sync`, `display_page`, `display_update`, `display_separation`.
- `new_main`: DLL load, instance lifecycle, display-format argument injection, Ghostscript execution, exit-code mapping.
- `set_font`: reads/writes `gswin32.ini` font settings.
- `WinMain`: command-line parsing, text-window creation, error wait loop, cleanup.

Notes:
- Command-line parser handles quoted spaces but not embedded quotes.
- Uses structured exception handling for stack overflow when compiled with MSVC/Borland.
- Uses old pointer-to-`%x` debug formatting and legacy Win32 APIs.

Filesystem relevance: Runtime file-path handling through command-line and ini/registry settings only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwmain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwmain.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwmain.h

Purpose: Small shared header for Win32 Ghostscript main/display resources.

Contents:
- Icon resource IDs: `GSTEXT_ICON=50`, `GSIMAGE_ICON=51`.
- Extern declaration for global `HWND hwndtext`.

Filesystem relevance: None.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwmain.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwmainc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwmainc.c

Purpose: Win32 console launcher for Ghostscript using the DLL/static loader and a separate GUI thread for display windows.

Major responsibilities:
- Bridges Ghostscript stdio to real console stdin/stdout/stderr.
- Starts a secondary Win32 message-loop thread for image windows because the main thread runs Ghostscript and may block on stdin.
- Posts custom display messages to the GUI thread for open/close/size/sync/page/update.
- Uses mutexes to protect image bitmap access across Ghostscript and GUI threads.
- Loads Ghostscript, creates an instance, registers callbacks, injects display defaults, runs Ghostscript, and shuts down the GUI thread.

Key details:
- Custom messages start at `WM_USER+101` to avoid a known Japanese Windows `WM_USER+1` collision.
- Uses `_beginthread` and waits briefly until the GUI thread can receive posted messages.
- Sets stdin to binary when not a TTY and stdout/stderr to binary.
- Display callback structure mirrors `dwmain.c`, but message-passes image work to `winthread`.
- Optional debug memory allocation callbacks are present under `DISPLAY_DEBUG_USE_ALLOC`.

Risks/legacy notes:
- `hthread` is not visibly initialized before the startup wait comparison with `INVALID_HANDLE_VALUE`.
- Uses fixed buffers and older thread/message APIs.
- Pointer debug output uses old integer formatting.

Filesystem relevance: None beyond command-line and console stream behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwmainc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwnodll.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwnodll.c

Purpose: Static-link alternative to `dwdll.c`.

Behavior:
- `load_dll` does not load a DLL. It assigns `GSDLL` function pointers directly to linked `gsapi_*` symbols.
- `unload_dll` is a no-op.

Use case:
- Allows the same Windows main programs to call through the `GSDLL` dispatch table whether Ghostscript is loaded dynamically or statically linked.

Filesystem relevance: None.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwnodll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwreg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwreg.c

Purpose: Win32 registry helper for Ghostscript application settings.

Key functions:
- `win_registry_key`: builds `Software\<gs_productfamily>`.
- `win_get_reg_value`: reads a named `REG_SZ` value from `HKEY_CURRENT_USER`.
- `win_set_reg_value`: opens or creates the Ghostscript key under `HKEY_CURRENT_USER` and writes a named `REG_SZ`.

Usage:
- Used by text/image windows to persist positions and likely other user settings.
- Comments note the product family comes from `gscdefs.h`.

Risks:
- Ignores return from `win_registry_key` in callers.
- Uses fixed 256-byte key buffer.
- In `win_get_reg_value`, `bptr == (char *)NULL` compares a `BYTE *` against a `char *` cast, harmless but untidy.

Filesystem relevance: None directly; registry persistence only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwreg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwreg.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwreg.h

Purpose: Declares registry get/set helpers for Ghostscript application values.

API:
- `win_get_reg_value(const char *name, char *ptr, int *plen)`
- `win_set_reg_value(const char *name, const char *value)`

Filesystem relevance: None.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwreg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwsetup.cpp -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwsetup.cpp

Purpose: Win32 setup program for AFPL Ghostscript.

Major responsibilities:
- Interactive or batch installation of Ghostscript program files and optional fonts.
- Creates file lists from directory specs when invoked with `-title`, `-dir`, and `-list`.
- Provides installer dialog, folder browsing, log window, and Readme launcher.
- Uses `CInstall` to copy files, write registry entries, create Start Menu shortcuts, and build uninstall logs.
- Optionally creates `cidfmap` for CJK fonts by running installed `gswin32c.exe`.

Key flows:
- `WinMain` calls `init`, then either enters dialog message loop or completes batch install.
- `init` determines Windows version, source directory, command-line mode, default Program Files target, and initializes main dialog.
- `install_all` coordinates program install, optional font install, and Start Menu folder opening.
- `install_prog` copies files, writes `GS_DLL` and `GS_LIB`, creates Start Menu shortcuts, optionally backs up/writes `lib/cidfmap`, and writes uninstall metadata.
- `install_fonts` installs from `fontlist.txt` and writes font uninstall metadata unless no-copy mode.
- `make_filelist` recursively walks files and writes list files for packaging.

File/list behavior:
- `filelist.txt` and `fontlist.txt` first line: uninstall name.
- Second line: main directory for uninstall logs.
- Remaining lines: files to install.
- If target equals source, no-copy mode validates file existence without copying.

Risks/legacy notes:
- Uses many fixed-size buffers and unchecked `strcpy`/`strcat`.
- Uses custom command-line parser.
- `write_cidfmap` launches a hidden process and does not wait for success.
- `dirwalk` uses Win32 `FindFirstFile` recursion and does not deeply guard path length.
- Batch install defaults to all-users on NT.

Filesystem relevance: Significant as packaging/install file traversal, copy, and uninstall-log generation, but not filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwsetup.cpp -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwsetup.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwsetup.h

Purpose: Resource ID definitions for the Win32 Ghostscript setup program.

Contents:
- Dialog IDs: text window, directory dialog, main dialog.
- Control IDs: target directory/group, browse buttons, Readme button, product name, install fonts, log edit control, copy/install buttons, file/folder/target controls, all-users checkbox, copyright, CJK fonts.
- String resource IDs for app name, target directory, and target group.

Filesystem relevance: None except UI controls for install paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwsetup.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwtext.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwtext.c

Purpose: Win32 text-window/terminal abstraction used by the Ghostscript GUI launcher.

Major responsibilities:
- Creates a fixed-size character grid window backed by `ScreenBuffer`.
- Renders text with a selectable monospaced font.
- Maintains scroll bars and cursor visibility.
- Provides keyboard input buffering, line input, and basic editing.
- Supports clipboard copy/paste and drag/drop file injection.
- Handles caret/focus and window message processing.

Key API implementations:
- Lifecycle: `text_new`, `text_destroy`, `text_register_class`, `text_create`.
- Configuration: `text_size`, `text_font`, `text_drag`, `text_setpos`, `text_getpos`, `text_get_handle`.
- Output: `text_putch`, `text_write_buf`, `text_puts`.
- Input: `text_kbhit`, `text_getch`, `text_read_line`, `text_gets`.
- UI internals: `WndTextProc`, `text_copy_to_clipboard`, `text_paste_from_clipboard`, `text_drag_drop`.

Notable behavior:
- `text_read_line` returns non-NUL-terminated chunks for Ghostscript stdio compatibility.
- Drag/drop injects configured prefix, normalized filename with `/`, and suffix into the keyboard buffer.
- Clipboard copy exports trimmed screen-buffer lines.
- `WM_CLOSE` marks `quitnow` and changes title to “closing” but defers actual destruction until Ghostscript exits.

Risks/legacy notes:
- Uses `SetWindowLong`/`GetWindowLong` pointer casts, not 64-bit safe.
- `text_write_buf` uses bitwise `&` in a loop condition where `&&` was likely intended.
- Fixed-size input line buffer is 256 bytes.
- The opening comment appears malformed: the descriptive block starts `/* Microsoft Windows text window for Ghostscript.` and source continues with includes; compilers may tolerate only if the actual file text is historically intended, but as read it looks like an unterminated comment before includes.

Filesystem relevance: None directly. Drag/drop only converts dropped file paths into Ghostscript commands.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwtext.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwtext.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwtext.h

Purpose: Declares the Win32 text-window data structure and API.

Key structure:
- `TW` stores title/icon, screen buffer and dimensions, drag strings, window handle, keyboard circular buffer, line buffer, focus/caret state, font settings, character metrics, cursor/client/scroll positions, and saved window rectangle.

Public API:
- Create/destroy: `text_new`, `text_destroy`.
- Input: `text_kbhit`, `text_gets`, `text_read_line`.
- Output: `text_putch`, `text_write_buf`, `text_puts`.
- Window/cursor: `text_to_cursor`, `text_register_class`, `text_create`, `text_get_handle`.
- Configuration: `text_font`, `text_size`, `text_setpos`, `text_getpos`, `text_drag`.

Notes:
- Declares `int getch(void);` even though the implementation provides `text_getch(TW *)`; this may be legacy or stale.
- Requires Win32 types.

Filesystem relevance: None.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwtext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwtrace.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwtrace.c

Purpose: Win32 graphical trace server for Ghostscript’s visual tracing interface.

Major responsibilities:
- Lazily creates a trace `IMAGE` window.
- Provides `vd_trace_interface` callbacks that draw with Win32 GDI.
- Maps Ghostscript trace coordinates to window coordinates.
- Manages an HDC, selected pen/brush, color, line width, and nested `get_dc`/`release_dc` calls.
- Reads optional trace scale/shift/origin settings from `gs_vdtrace.ini`.

Key callbacks:
- Window/device context: `get_size_x`, `get_size_y`, `get_dc`, `release_dc`, `erase`.
- Path construction/drawing: `beg_path`, `end_path`, `moveto`, `lineto`, `curveto`, `closepath`, `fill`, `stroke`.
- Markers/text: `circle`, `round`, `text`.
- Style/settings: `setcolor`, `setlinewidth`, `set_scale`, `set_shift`, `set_origin`.
- `wait` is intentionally not implemented.
- `visual_tracer_init` installs callbacks; `visual_tracer_close` destroys the trace image.

Notes:
- Comments say WM_PAINT image restoration is not implemented.
- Non-Win32 callback macro sets callbacks to zero.
- `dw_gt_erase` passes `rgbcolor` directly to `CreateSolidBrush` instead of converting through `WindowsColor`, unlike pen/brush color setup.

Filesystem relevance: None.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwtrace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwtrace.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwtrace.h

Purpose: Declares the Win32 graphical trace interface.

API:
- Extern `visual_tracer` of type `struct vd_trace_interface_s`.
- `visual_tracer_init(void)`.
- `visual_tracer_close(void)`.

Filesystem relevance: None.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwtrace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwuninst.cpp -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwuninst.cpp

Purpose: Win32 uninstaller for Ghostscript, driven by uninstall logs generated by `CInstall::MakeLog`.

Main responsibilities:
- Parses uninstall log path from command line.
- Validates log section structure and reads uninstall title.
- Presents a modeless uninstall dialog.
- Processes log sections for installed files, new registry keys/values, old registry values, new shell links, and old shell links.
- Deletes installed files and the uninstall log.
- Removes Add/Remove Programs uninstall registry entry on completion.

Log sections handled:
- `UninstallName`: product title.
- `FileNew`: delete installed files.
- `RegistryNew`: delete registry values/keys created by install.
- `RegistryOld`: restore previous registry values from `REGEDIT4`-style data.
- `ShellNew`: delete Start Menu links/folder created by install.
- `ShellOld`: recreate previously existing Start Menu links.
- Empty section terminates uninstall.

Key functions:
- Parsing/control: `GetLine`, `IsSection`, `NextSection`, `ReadSection`, `doEOF`, `do_message`, `init`.
- File removal: `dofiles`.
- Registry: `registry_delete`, `registry_delete_key`, `registry_import`, `registry_unquote`.
- Shell: `shell_new`, `shell_old`, `CreateShellLink`, `MakeDir`.
- UI: `RemoveDlgProc`, `WinMain`.

Risks/legacy notes:
- Registry key deletion uses reverse-order scanning via a linked list of file offsets.
- `registry_import` debug output prints literal `"skey"` instead of the variable in one path.
- `shell_old` looks for `Program`, while installer logs the target as `Path`; this may prevent restoration of old shortcut paths.
- Uses fixed 256-byte buffers and many `strncpy`/`strtok` paths.
- Directory removal is shallow; installer comments already state directories and the uninstaller itself are not fully removed.

Filesystem relevance: Significant for Windows package cleanup: deletes installed files and removes generated uninstall log, but not OS filesystem internals.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwuninst.cpp -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwuninst.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwuninst.h

Purpose: Resource ID definitions for the Win32 Ghostscript uninstaller.

Contents:
- Program/dialog IDs: `ID_UNINSTGS`, `ID_UNINST`, `IDD_UNSET`.
- Control IDs for icon, program label, done/press-OK button, and status text fields.

Filesystem relevance: None except UI controls for uninstall progress.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwuninst.h -->