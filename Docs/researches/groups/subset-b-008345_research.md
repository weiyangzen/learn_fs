# subset-b-008345 research

Grouped research for the SELinux GUI and libselinux files assigned to `subset-b-008345`. Each section is source-path titled and delimited for deterministic per-file reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/gui/polgengui.py -->
# sources/security-integrity/selinux/gui/polgengui.py

## Purpose
`polgengui.py` implements the GTK 3 wizard for generating SELinux policy modules. It collects a policy type, application or user name, executable/init-script paths, transition/admin roles, network port permissions, file write locations, and custom booleans, then drives `sepolicy.generate.policy` to emit policy files into a selected output directory.

## Important APIs, types, and functions
The main type is `childWindow`, whose page constants map logical wizard steps onto notebook page indexes from `/usr/share/system-config-selinux/polgen.ui`. `get_all_modules()` shells out to `semodule -l` to detect already-loaded module names. `get_type()` maps radio buttons to `sepolicy.generate` constants. `generate_policy()` is the core handoff into `sepolicy.generate.policy`: it adds booleans, sets application helper flags, selected transitions/admin roles, network settings, writable files/directories, and calls `generate(outputdir)`. UI helpers include `forward()`, `back()`, `setupScreen()`, `exec_select()`, `init_script_select()`, `add()`, `add_dir()`, and validation hooks for names and ports.

## Control flow
Module import initializes gettext, appends the system-config-selinux install path, builds a global `Gtk.Builder`, and loads `polgen.ui`. Standalone execution installs the default SIGINT handler, constructs `childWindow`, calls `setupScreen()`, shows the main window, and enters `Gtk.main()`. Within the wizard, `forward()` validates the current page before advancing through the per-policy page list in `self.pages`. The finish page calls `generate_policy()` and changes the cancel button to close. Name validation also pre-populates executable or init-script paths when files matching the entered name exist in standard locations.

## State and persistence behavior
Runtime state is held in GTK widgets, `Gtk.ListStore` instances, `self.pages`, `self.current_page`, selected tree rows, and the cached module/type/role/user lists from `sepolicy.generate`. Persistent effects occur only when `sepolicy.generate.policy.generate()` writes policy artifacts into the chosen output directory. The script reads installed policy data through `sepolicy`, installed modules through `semodule`, and local filesystem paths for candidate executables.

## Dependencies and integration points
This file depends on PyGObject GTK 3, `sepolicy`, `sepolicy.generate`, `sepolicy.interface`, `semodule`, gettext domain `selinux-gui`, and a fixed UI path under `/usr/share/system-config-selinux`. It integrates with the wider GUI through desktop launchers and with SELinux policy generation through the `sepolicy.generate` Python API.

## Risks and edge cases
Several exception handlers use `e.message`, which is not valid on normal Python 3 `Exception` objects. `on_existing_user_page_next()` checks `self.view` rather than `existing_user_treeview`, so existing-user selection validation appears wrong. The wizard relies on fixed installed UI paths and will fail before constructing a window if `polgen.ui` is absent. Name validation allows only alphanumeric values, which may reject valid SELinux naming patterns but prevents spaces. Port validation is delegated to `sepolicy.generate.verify_ports()`. The generated policy behavior depends heavily on `sepolicy.generate` internals, so tests need version-compatible bindings.

## Test signals
Useful tests cover wizard page ordering for every `sepolicy.generate` policy type, invalid and valid names, executable and init-script auto-fill, inbound/outbound port validation, boolean/file/dir list mutation, transition and role selection propagation, duplicate module/type warning paths, and `generate_policy()` interactions with a mocked `sepolicy.generate.policy`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/gui/polgengui.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/gui/portsPage.py -->
# sources/security-integrity/selinux/gui/portsPage.py

## Purpose
`portsPage.py` implements the "Network Port" management page for the SELinux configuration GUI. It displays SELinux port type mappings, supports list and grouped views, filters rows, and adds, modifies, or deletes port mappings through `semanage port`.

## Important APIs, types, and functions
`portsPage` extends `semanagePage`. Column constants define the `Gtk.ListStore` layout: SELinux type, protocol, MLS/MCS level, and port/range. `init_store()` creates the table columns and numeric range sorting. `load()` reads individual records from `seobject.portRecords().get_all(self.local)`. `group_load()` reads grouped records from `get_all_by_type()`. `dialogInit()` and `dialogClear()` synchronize selected rows with the edit dialog. `add()`, `modify()`, and `delete()` run `semanage port -a`, `-m`, and `-d` via `getstatusoutput()`. `on_group_clicked()` toggles between editable list view and read-only grouped view.

## Control flow
Construction wires the group button, filter entry, protocol combo, dialog entries, and action buttons, then initializes the store and loads current records. Filtering calls either `load()` or `group_load()` based on the current mode. Add/modify/delete operations set the busy cursor through the base class, run the external command, restore the cursor, update the in-memory store, and report command output on failure.

## State and persistence behavior
The page keeps display state in `self.store`, `self.filter`, `self.group`, `self.edit`, selected tree rows, and dialog widgets. Persistent system changes are not made through libsemanage bindings directly; they are delegated to the `semanage port` CLI, which updates SELinux local policy configuration. Group view is display-only and disables add/properties/delete buttons while active.

## Dependencies and integration points
The file depends on GTK/GObject, `seobject.portRecords`, the base `semanagePage`, gettext domain `selinux-gui`, and the `semanage` command. It is added by `system-config-selinux.py` when SELinux is enabled and relies on widget IDs from `system-config-selinux.ui`.

## Risks and edge cases
The `semanage` command strings interpolate user-controlled type, MLS, and port values into a shell command; only port characters are lightly checked and the range bounds are not validated. Type and MLS values are not shell-quoted. Empty port input becomes `1`, which may surprise users. Group toggle sensitivity is based on the previous `self.group` value before flipping, so the first transition intentionally disables editing but is easy to misread. Error handling preserves command text but not structured error causes.

## Test signals
Tests should mock `seobject.portRecords` and `getstatusoutput()` to verify list/group loading, filtering across type/protocol/MLS/port fields, numeric sorting of ranges, add/modify/delete command construction, rejection of nonnumeric ranges, button sensitivity in grouped mode, and UI-store refresh after successful operations.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/gui/portsPage.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/gui/selinux-polgengui.desktop -->
# sources/security-integrity/selinux/gui/selinux-polgengui.desktop

## Purpose
This desktop entry exposes the SELinux policy generation GUI in desktop application menus. It labels the tool as "SELinux Policy Generation Tool" and describes it as a way to generate SELinux policy modules.

## Important APIs, types, and functions
The file is freedesktop `.desktop` metadata rather than executable code. Key fields are `Name`, localized `Name[...]` translations, `Comment`, localized `Comment[...]` translations, `StartupNotify=true`, `Icon=system-config-selinux`, `Exec=/usr/bin/selinux-polgengui`, `Type=Application`, `Terminal=false`, and `Categories=System;Security;`.

## Control flow
Desktop shells parse this file, show the localized name/comment where possible, and invoke `/usr/bin/selinux-polgengui` when the user launches the item. There is no internal branching; control transfers to the installed launcher or GUI script.

## State and persistence behavior
The entry stores static launch metadata and translation strings. It does not persist runtime state. Installation into an applications directory determines menu visibility, and the `Exec` path determines which binary or wrapper is launched.

## Dependencies and integration points
It integrates with freedesktop-compliant menu systems, icon themes providing `system-config-selinux`, and the installed `/usr/bin/selinux-polgengui` command. It complements `polgengui.py` and the shell wrapper/package layout that installs the executable.

## Risks and edge cases
If `/usr/bin/selinux-polgengui` or the icon is missing, menu launch fails or displays a generic icon. The entry has no privilege escalation field, so elevation behavior depends on the launched command. Localized strings are static and can become stale relative to the English name/comment.

## Test signals
Validation should run `desktop-file-validate`, confirm the `Exec` target exists after packaging, verify the icon resolves, and smoke-test launch in a graphical session with the expected gettext locale.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/gui/selinux-polgengui.desktop -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/gui/semanagePage.py -->
# sources/security-integrity/selinux/gui/semanagePage.py

## Purpose
`semanagePage.py` defines the common base class for SELinux GUI pages that manage semanage-backed records. It centralizes filter handling, row activation, confirmation dialogs, add/modify dialog loops, delete confirmation, local/customized toggling, search behavior, and busy cursor state.

## Important APIs, types, and functions
`idle_func()` drains pending GTK events so cursor changes become visible during blocking operations. `semanagePage.__init__()` binds common widgets named from a page prefix, such as `<name>View`, `<name>Dialog`, and `<name>FilterEntry`. `wait()` and `ready()` switch the root-window cursor. `filter_changed()`, `search()`, and `match()` implement common filtering. `addDialog()` and `propertiesDialog()` loop until subclass `add()` or `modify()` succeeds or the dialog is canceled. `deleteDialog()` asks for confirmation before calling subclass `delete()`. `on_local_clicked()` toggles between customized and all records.

## Control flow
Subclasses call the base constructor with their widget prefix and description, then provide page-specific `load()`, `dialogClear()`, `dialogInit()`, `add()`, `modify()`, and `delete()` methods. Menu and toolbar actions in the main window dispatch to these common methods on the current page. Row activation opens the properties dialog.

## State and persistence behavior
The base class tracks `self.local`, `self.view`, `self.dialog`, `self.filter_entry`, the root window, cursor objects, and the human-readable page description. It does not directly persist SELinux configuration; persistence is delegated to subclasses. UI state changes include current filter text, selected rows, dialog state, and local/all mode.

## Dependencies and integration points
The base depends on GTK and GDK from PyGObject, gettext, and widget IDs defined in `system-config-selinux.ui`. It is used by pages such as ports and users and is called indirectly by `system-config-selinux.py` menu/toolbar dispatch.

## Risks and edge cases
The class assumes subclasses initialize `self.filter` before filter signals fire. Blocking subclass operations still run in the GTK main thread; cursor changes are cosmetic and the UI can remain unresponsive. `match()` swallows all exceptions, which hides unexpected non-string data issues. Confirmation strings format before translation lookup, limiting translator flexibility. The default `use_menus()` returns true, so non-editable subclasses must override it.

## Test signals
Tests should exercise base dialog loops with subclass stubs, filter signal behavior, case-insensitive search/match, local/all toggle label and reload behavior, delete confirmation routing, and cursor state changes around mocked long-running operations.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/gui/semanagePage.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/gui/sepolgen -->
# sources/security-integrity/selinux/gui/sepolgen

## Purpose
`sepolgen` is a minimal shell wrapper for SELinux policy generation. It forwards all command-line arguments to `sepolicy generate`.

## Important APIs, types, and functions
The file uses `/bin/sh` and a single `exec sepolicy generate "$@"`. `exec` replaces the wrapper process with the `sepolicy` process, preserving signal and exit-status behavior for callers.

## Control flow
When invoked, the shell expands `"$@"` as the original argument vector and transfers control to `sepolicy generate`. There is no validation, branching, or fallback.

## State and persistence behavior
The wrapper has no state. Any generated files or policy side effects are produced by `sepolicy generate`, not this script.

## Dependencies and integration points
It depends on `sepolicy` being available in `PATH` and on the `generate` subcommand. It integrates as a compatibility or convenience command for callers expecting `sepolgen`.

## Risks and edge cases
If `sepolicy` is missing or lacks the `generate` subcommand, launch fails with the shell's command-not-found or command error. The wrapper deliberately performs no privilege handling, environment sanitization, or argument validation.

## Test signals
Tests should verify argument preservation, exit-code propagation, and behavior when `sepolicy` is absent or returns an error. Packaging tests should confirm executable mode and installed path.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/gui/sepolgen -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/gui/sepolicy.desktop -->
# sources/security-integrity/selinux/gui/sepolicy.desktop

## Purpose
This desktop entry exposes the `sepolicy gui` policy management interface in desktop menus under "SELinux Policy Management Tool".

## Important APIs, types, and functions
Important fields are `Name`, `Comment`, `Icon=sepolicy`, `Exec=/usr/bin/sepolicy gui`, `Type=Application`, `Terminal=false`, `Categories=System;Security;`, and `Keywords=policy;security;selinux;avc;permission;mac;`. It contains no localized strings beyond the default English fields.

## Control flow
A desktop shell reads the metadata and launches `/usr/bin/sepolicy gui`. The executable then owns all GUI behavior.

## State and persistence behavior
The file is static application metadata and stores no runtime state. Persistence depends on package installation and desktop database indexing.

## Dependencies and integration points
It depends on the `sepolicy` executable supporting the `gui` argument and on an icon named `sepolicy`. It integrates with freedesktop application menus and search through categories and keywords.

## Risks and edge cases
Launch fails if `sepolicy` is not installed at `/usr/bin/sepolicy`. The desktop entry does not request a terminal or privilege wrapper, so any authorization must be handled by `sepolicy gui` itself. Lack of localized fields may reduce usability in non-English locales.

## Test signals
Run `desktop-file-validate`, confirm the command and icon exist after install, and smoke-test menu launch in a graphical session.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/gui/sepolicy.desktop -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/gui/statusPage.py -->
# sources/security-integrity/selinux/gui/statusPage.py

## Purpose
`statusPage.py` implements the SELinux status page for the GUI. It displays and changes current enforcing mode, configured boot-time SELinux mode, configured policy type, and whether a filesystem relabel should be requested on next reboot.

## Important APIs, types, and functions
`statusPage` uses constants `ENFORCING`, `PERMISSIVE`, `DISABLED`, `modearray`, `SELINUXDIR`, and `RELABELFILE`. `get_current_mode()` reads runtime state using `selinux.is_selinux_enabled()` and `selinux.security_getenforce()`. `set_current_mode()` calls `selinux.security_setenforce()`. `read_selinux_config()` populates configured mode and available policy types. `write_selinux_config()` rewrites `selinux.selinux_path() + "config"` through a `.bck` file and rename. `on_relabel_toggle()` creates or removes `/.autorelabel`.

## Control flow
Construction binds status widgets from the GTK builder, initializes relabel state, populates current-mode choices based on runtime SELinux status, reads `/etc/selinux` policy directories, and connects mode/type signal handlers. Changing policy type prompts because it requires relabeling, toggles relabel when accepted, writes config, and updates history. Changing configured enabled mode prompts for disabling or re-enabling scenarios and writes the new config.

## State and persistence behavior
Runtime state is kept in widget selections plus `initialtype`, `initEnabled`, `enabled`, `types`, and `typeHistory`. Persistent effects include writing the SELinux config file, setting runtime enforce mode through selinuxfs, and creating/removing `/.autorelabel`.

## Dependencies and integration points
The page depends on PyGObject GTK, Python `selinux` bindings, `/etc/selinux`, selinuxfs, and the widget IDs from `system-config-selinux.ui`. It is always added by `system-config-selinux.py`, even when SELinux is disabled, but current-mode controls are disabled if SELinux is not active.

## Risks and edge cases
The file requires sufficient privileges to write `/etc/selinux/config`, call `security_setenforce`, and touch `/.autorelabel`. `write_selinux_config()` does not fsync and only rewrites existing `SELINUX=` and `SELINUXTYPE=` lines. The code assumes `selinux_getpolicytype()` and `selinux_getenforcemode()` Python bindings return tuple-like values. Relabel changes are made immediately when the checkbox toggles, including toggles triggered programmatically after warning dialogs.

## Test signals
Tests should mock `selinux` bindings and filesystem calls to cover enabled/permissive/disabled initialization, config rewrite behavior, policy-type list population, relabel file creation/removal, warning-dialog rejection restoring previous values, and permission-error reporting.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/gui/statusPage.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/gui/system-config-selinux -->
# sources/security-integrity/selinux/gui/system-config-selinux

## Purpose
`system-config-selinux` is the privileged launcher for the graphical SELinux administration tool. It runs the Python GUI through PolicyKit.

## Important APIs, types, and functions
The shell script uses `/bin/sh` and a single `exec /usr/bin/pkexec /usr/share/system-config-selinux/system-config-selinux.py`. `exec` makes `pkexec` replace the shell, so the launcher exits with the GUI command status.

## Control flow
Invocation immediately transfers to `pkexec`, which handles authentication and then launches the installed Python GUI. The wrapper has no fallback path.

## State and persistence behavior
The script stores no state. Persistent SELinux changes are made later by the GUI pages after PolicyKit authorization succeeds.

## Dependencies and integration points
It depends on `/usr/bin/pkexec`, a PolicyKit configuration that permits the GUI action, and the installed Python script under `/usr/share/system-config-selinux`. It is the `Exec` target of `system-config-selinux.desktop`.

## Risks and edge cases
If `pkexec` is missing, graphical authentication is unavailable, or the target script is not installed, the launcher fails. Environment variables are filtered by `pkexec`, so the GTK display/session environment must be allowed or reconstructed correctly by policy.

## Test signals
Packaging tests should confirm executable mode and installed paths. Runtime smoke tests should cover successful authorization, canceled authorization, no-display sessions, and missing target script handling.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/gui/system-config-selinux -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/gui/system-config-selinux.desktop -->
# sources/security-integrity/selinux/gui/system-config-selinux.desktop

## Purpose
This desktop entry exposes the main graphical SELinux administration application in desktop menus under "SELinux Management".

## Important APIs, types, and functions
The `.desktop` fields include localized `Name[...]` and `Comment[...]` values, `StartupNotify=true`, `Icon=system-config-selinux`, `Exec=/usr/bin/system-config-selinux`, `Type=Application`, `Terminal=false`, and `Categories=System;Security;`.

## Control flow
Desktop shells parse the file, display a localized menu item, and invoke `/usr/bin/system-config-selinux`. That wrapper then delegates privilege handling to `pkexec` and starts `system-config-selinux.py`.

## State and persistence behavior
The file is static launch metadata. It does not store application settings or SELinux state; it only determines how the GUI appears and starts.

## Dependencies and integration points
It integrates with freedesktop menu systems, the installed launcher at `/usr/bin/system-config-selinux`, the `system-config-selinux` icon asset, and PolicyKit through the wrapper.

## Risks and edge cases
Missing launcher or icon resources cause failed launches or degraded menu presentation. Localized strings must remain synchronized with the application's role. The entry does not define keywords, which may reduce menu search discoverability compared with `sepolicy.desktop`.

## Test signals
Use `desktop-file-validate`, verify installed `Exec` and icon targets, and perform a menu launch smoke test through a graphical session with PolicyKit.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/gui/system-config-selinux.desktop -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/gui/system-config-selinux.py -->
# sources/security-integrity/selinux/gui/system-config-selinux.py

## Purpose
`system-config-selinux.py` is the main GTK application for graphical SELinux administration. It loads the UI definition, constructs the navigation list and notebook pages, and dispatches menu/toolbar actions to the currently selected page object.

## Important APIs, types, and functions
The main class is `childWindow`. Its constructor connects builder signals, adds `statusPage`, and, when SELinux is enabled, adds booleans, file contexts, logins, users, ports, modules, and domains pages. `add_page()` appends page objects. `setupScreen()` builds the left navigation `Gtk.ListStore` from each page's `get_description()`. `itemSelected()` keeps the hidden notebook page and menu sensitivity synchronized. `add()`, `delete()`, `properties()`, and `on_local_clicked()` delegate to the active tab. `policy()` and `logging()` spawn external tools.

## Control flow
Import-time setup requires GTK 3, handles missing DISPLAY-related runtime errors, appends `/usr/share/system-config-selinux`, imports page modules, initializes gettext, and loads `system-config-selinux.ui`. Standalone execution resets SIGINT, constructs `childWindow`, calls `stand_alone()`, builds screen state, shows the main window, and enters `Gtk.main()`. The left-side tree selection drives which page is visible and whether edit menus are enabled.

## State and persistence behavior
Application state is in `self.tabs`, selected navigation rows, the hidden notebook index, menu sensitivity, and page-local state. The main shell does not directly persist SELinux data; page objects perform those changes through libselinux bindings, `semanage`, or other helpers.

## Dependencies and integration points
The script depends on PyGObject GTK 3, the Python SELinux bindings, peer page modules, the installed UI XML, gettext domain `selinux-gui`, `semanagegui.py`, and `seaudit`. It is launched through the privileged shell wrapper and referenced by the desktop entry.

## Risks and edge cases
The script uses fixed installed paths, so development-tree execution without installed assets fails. Some exception handling uses `e.message`, which is not portable to Python 3. `os.spawnl()` calls do not pass an explicit argv[0], which can be fragile depending on platform behavior. If SELinux is disabled, only the status page is added; menu dispatch must therefore respect `use_menus(False)` on that page.

## Test signals
Tests should mock GTK builder objects and page classes to verify tab construction with SELinux enabled/disabled, selection-to-notebook synchronization, menu sensitivity, action delegation to active tabs, no-DISPLAY error behavior, and external tool spawn calls.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/gui/system-config-selinux.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/gui/system-config-selinux.ui -->
# sources/security-integrity/selinux/gui/system-config-selinux.ui

## Purpose
`system-config-selinux.ui` is the GTK Builder/Glade definition for the main SELinux administration GUI. It declares the application window, menus, navigation tree, hidden notebook pages, toolbars, dialogs, list views, combo models, labels, accelerators, and translatable text consumed by the Python page modules.

## Important APIs, types, and functions
The file is declarative XML requiring GTK 3. Important objects include `mainWindow`, `aboutWindow`, `selectView`, `notebook`, status widgets (`enabledOptionMenu`, `currentOptionMenu`, `selinuxTypeOptionMenu`, `relabelCheckbutton`), page views (`booleansView`, `fcontextView`, `loginsView`, `usersView`, `portsView`, `modulesView`, `domainsView`), filter entries, semanage dialogs (`loginsDialog`, `portsDialog`, `fcontextDialog`, `usersDialog`), and action widgets wired to handlers such as `on_add_clicked`, `on_properties_clicked`, `on_delete_clicked`, `on_local_clicked`, and `on_about_activate`.

## Control flow
`Gtk.Builder.add_from_file()` loads the XML, then `connect_signals()` in `system-config-selinux.py` and page constructors bind handlers. The navigation tree in Python selects hidden notebook pages by index. Toolbars and menus emit shared actions, and the active page object interprets those actions.

## State and persistence behavior
The XML stores static UI structure, default widget properties, list-store seed data such as TCP/UDP and SELinux mode choices, translations, tooltips, and response codes. Runtime state is held by GTK object instances created from this definition; persistent SELinux changes are performed by Python code responding to its signals.

## Dependencies and integration points
It integrates tightly with all GUI Python modules through exact widget IDs. It depends on GTK 3 classes, stock icon identifiers, translation extraction from `translatable="yes"` properties, and image/icon assets such as `system-config-selinux.png`.

## Risks and edge cases
Python modules assume these IDs and notebook ordering remain stable, so UI edits can silently break page binding. Some GTK stock and `GtkImageMenuItem` patterns are legacy in newer GTK 3 environments. The `delete_menu_item` defines an accelerator but no explicit activate signal in the XML, while toolbar delete buttons do connect. Dialog titles and labels must match page semantics; stale labels can confuse operations such as file contexts versus login mappings.

## Test signals
Tests should load the UI through `Gtk.Builder` in a graphical or headless GTK test environment, assert all Python-referenced object IDs exist with expected classes, verify signal names resolve, check notebook page order against `system-config-selinux.py`, and run accessibility/translation checks for visible labels and tooltips.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/gui/system-config-selinux.ui -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/gui/usersPage.py -->
# sources/security-integrity/selinux/gui/usersPage.py

## Purpose
`usersPage.py` implements the "SELinux User" management page for the GUI. It lists SELinux users, MLS/MCS ranges, and roles, and supports add, modify, and delete operations through `semanage user`.

## Important APIs, types, and functions
`usersPage` extends `semanagePage`. Its constructor creates a `Gtk.ListStore`, adds columns for user, range, and roles, loads existing data from `seobject.seluserRecords().get_all()`, and binds dialog entries. `load()` filters and displays translated ranges via `seobject.translate()`. `dialogInit()` and `dialogClear()` move data between selected rows and the dialog. `add()`, `modify()`, and `delete()` shell out to `semanage user`.

## Control flow
The page is constructed by the main application when SELinux is enabled. It loads current records immediately. Menu or toolbar actions call base dialog wrappers, which call page-specific add/modify/delete methods. Successful add appends a row; successful modify reloads the page; successful delete removes the selected row after preventing deletion of required users.

## State and persistence behavior
Display state is in the GTK model, selected rows, filter text, and dialog entries. Persistent state is modified by `semanage user -a`, `-m`, and `-d`, which update SELinux user definitions in local policy. The page does not maintain its own on-disk data.

## Dependencies and integration points
The module depends on GTK/GObject, `seobject`, the `semanage` CLI, gettext, and the common `semanagePage` base. It relies on widget IDs from `system-config-selinux.ui` and is listed in the main navigation by `system-config-selinux.py`.

## Risks and edge cases
User, range, and roles are interpolated into shell commands. Roles are single-quoted, but embedded quotes can still be problematic, and user/range are unquoted. Only `root` and `user_u` are protected from deletion. The `range` variable shadows the built-in, which is harmless locally but reduces readability. Errors from `semanage` are surfaced as text but not parsed.

## Test signals
Tests should mock `seobject.seluserRecords`, `seobject.translate`, and `getstatusoutput()` to cover filtering, add/modify/delete command generation, required-user delete protection, list reload after modify, store append/remove behavior, and handling of command failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/gui/usersPage.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/Makefile -->
# sources/security-integrity/selinux/libselinux/Makefile

## Purpose
This is the top-level recursive makefile for `libselinux`. It configures feature flags, PCRE integration, large-file support, OS/compiler detection, and delegates build/install/clean targets to subdirectories.

## Important APIs, types, and functions
Key variables include `SUBDIRS = include src utils man`, `PKG_CONFIG`, `DISABLE_SETRANS`, `DISABLE_RPM`, `ANDROID_HOST`, `LABEL_BACKEND_ANDROID`, `USE_PCRE2`, `USE_LFS`, `PCRE_MODULE`, `PCRE_CFLAGS`, `PCRE_LDLIBS`, `LFS_CFLAGS`, `OS`, and `COMPILER`. Targets `all`, `install`, `relabel`, `clean`, and `distclean` loop over `SUBDIRS`. Wrapper targets delegate Python/Ruby binding generation and cleanup to `src`.

## Control flow
Make evaluates feature variables, appends preprocessor flags, queries `pkg-config` for PCRE flags, exports settings to sub-makes, detects clang versus gcc from `$(CC) -v`, and runs each subdirectory make target sequentially, aborting on first failure.

## State and persistence behavior
The makefile itself persists no state. Build outputs, installed headers/libraries/man pages, generated wrappers, and cleanup are handled by subdirectory makefiles using the exported variables. Environment overrides allow packaging systems to control optional dependencies.

## Dependencies and integration points
It integrates with `include`, `src`, `utils`, and `man` subtrees, `pkg-config`, PCRE or PCRE2 development packages, compiler tooling, and platform-specific Android feature selection.

## Risks and edge cases
`pkg-config` is evaluated during makefile expansion, so missing PCRE packages can produce empty or bad flags before any target logic runs. `ANDROID_HOST=y` forces some disables, but `DISABLE_BOOL` is otherwise only conditionally referenced and not initialized near the top. Compiler detection by grepping `$(CC) -v` is heuristic. The `test` target is declared but empty.

## Test signals
Build matrix tests should cover PCRE2 and PCRE modes, Android host mode, disabled RPM/setrans/bool/X11 options, large-file support toggling, clang/gcc detection, install staging through `DESTDIR`, and recursive failure propagation from each subdir.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/fuzz/selabel_file_compiled-fuzzer.c -->
# sources/security-integrity/selinux/libselinux/fuzz/selabel_file_compiled-fuzzer.c

## Purpose
This libFuzzer harness exercises the compiled-file-contexts backend parser and lookup logic in libselinux. It feeds one to three compiled file-context data streams plus a lookup key into internal label-file routines and asserts core invariants on successful matches.

## Important APIs, types, and functions
The entry point is `LLVMFuzzerTestOneInput()`. Helpers include `null_log()`, `validate_context()`, `write_full()`, and `convert_data()`. The harness constructs a `struct selabel_handle`, `struct saved_data`, `struct spec_node`, and calls internal functions from `../src/label_file.h`: `load_mmap()`, `sort_specs()`, `cmp()`, `lookup_all()`, `free_lookup_result()`, and `free_spec_node()`. Control bits select partial matching, find-all mode, and whether to use `S_IFSOCK` mode.

## Control flow
The first input byte is a control byte. Remaining bytes are split on `0xde 0xad 0xbe 0xef` into required primary compiled data, optional homedir/local-style compiled data, and a lookup key. Each data segment is copied into memory, written to an anonymous memfd, converted to `FILE *`, and loaded with `load_mmap()` using file indexes 0, 1, and 2. The specs are sorted, self-comparison is asserted equal, `lookup_all()` is run, and each returned result is checked for nonempty regex/context, no translated context, validation, and prefix bounds.

## State and persistence behavior
All state is in process memory and anonymous memfds. The harness installs process-global SELinux callbacks for logging and validation. It manually cleans lookup results, spec tree data, mmap areas, key/data buffers, and FILE handles.

## Dependencies and integration points
It depends on libFuzzer, Linux `memfd_create`, `mmap`/`munmap`, libselinux public `label.h`, and private label-file internals. It is intended to be built in a fuzzing configuration that exposes internal parser functions.

## Risks and edge cases
Assertions are intentional fuzz oracles, so builds must run with assertions enabled for full checking. `memmem()` and `memfd_create()` are GNU/Linux-specific. The callback installation is global and could interfere if combined with other fuzz targets in one process. The harness copies fuzz slices before memfd writing, increasing memory pressure for large inputs.

## Test signals
Seed corpora should include valid compiled file-contexts data, malformed headers, multiple overlay files, empty and nonempty lookup keys, mode-sensitive patterns, partial matches, all-match queries, digest-related data, and separator-edge cases.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/fuzz/selabel_file_compiled-fuzzer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/fuzz/selabel_file_text-fuzzer.c -->
# sources/security-integrity/selinux/libselinux/fuzz/selabel_file_text-fuzzer.c

## Purpose
This libFuzzer harness exercises textual file-context parsing and lookup in libselinux. It converts fuzzer bytes into a text file-context definition and lookup key, then drives internal label-file parsing and matching.

## Important APIs, types, and functions
`LLVMFuzzerTestOneInput()` is the fuzz entry point. Helpers `null_log()`, `validate_context()`, `write_full()`, and `convert_data()` support callback behavior and in-memory file conversion. The harness uses `process_text_file()`, `sort_specs()`, `cmp()`, `lookup_all()`, `free_lookup_result()`, and `free_spec_node()` from `../src/label_file.h`. Control bits select partial lookup, find-all behavior, and optional `S_IFSOCK` mode.

## Control flow
The first byte is a constrained control byte. The remaining input is split at the first `0xde 0xad 0xbe 0xef` separator into file-context text and a NUL-terminated lookup key. The text is written to a memfd-backed `FILE *`, parsed into a mocked `selabel_handle`, sorted, self-compared, and queried. Successful lookup results are validated for nonempty regex/context, no translated context, prior validation, and sane prefix length.

## State and persistence behavior
The harness uses only heap allocations, an anonymous memfd, mmap areas created by parser internals, and global SELinux callbacks. It frees all owned state on cleanup and creates no filesystem artifacts.

## Dependencies and integration points
It depends on libFuzzer, Linux/GNU interfaces, public `selinux/label.h`, private label-file parser internals, and SELinux callback APIs. It complements the compiled-context harness by targeting the text parser path.

## Risks and edge cases
The target is Linux-specific because of `memfd_create()`. Assertions double as correctness checks and require assert-enabled builds. The simplistic separator format means some fuzz bytes are discarded before parser entry if the separator is absent or first. Global callbacks can affect other code in the same process.

## Test signals
Useful seeds include minimal valid file-context lines, regex-heavy paths, invalid contexts, empty contexts, `<<none>>`, malformed line formats, comments/whitespace, mode-qualified entries, very long regexes, partial-match paths, and keys containing embedded unusual bytes before NUL termination.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/fuzz/selabel_file_text-fuzzer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/include/Makefile -->
# sources/security-integrity/selinux/libselinux/include/Makefile

## Purpose
This makefile installs libselinux public headers into the target include directory.

## Important APIs, types, and functions
Key variables are `PREFIX ?= /usr` and `INCDIR = $(PREFIX)/include/selinux`. The `install` target creates `$(DESTDIR)$(INCDIR)` with mode 755 and installs `selinux/*.h` with mode 644. `all` and `relabel` are no-ops. `clean` and `distclean` remove editor backup files under `selinux/`.

## Control flow
Running `make install` first ensures the include directory exists, then copies every header matching the wildcard. Clean targets remove `selinux/*~` and ignore missing files.

## State and persistence behavior
Persistent effects are limited to installed header files under `DESTDIR` and cleanup of local backup files. The makefile does not generate headers.

## Dependencies and integration points
It is called by the top-level libselinux makefile and depends on POSIX `test`, `install`, and `rm`. It publishes headers such as `selinux.h`, `label.h`, `restorecon.h`, and `avc.h` for downstream C consumers.

## Risks and edge cases
If the wildcard expands to an empty list, install behavior is shell-dependent and may fail trying to copy a literal pattern. The install command does not remove stale headers already present in the destination. Directory ownership and SELinux labels are left to the packaging/install environment.

## Test signals
Tests should run `make install DESTDIR=...`, verify all expected headers and modes, check no-op `all` and `relabel`, and confirm `clean` removes only backup files.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/include/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/include/selinux/avc.h -->
# sources/security-integrity/selinux/libselinux/include/selinux/avc.h

## Purpose
`avc.h` declares the userspace Access Vector Cache interface for object managers. It provides SID management, access checks, auditing, cache lifecycle, callbacks, statistics, netlink handling, and SELinux status-page helpers.

## Important APIs, types, and functions
Core types include `security_id_t`, `struct security_id`, `struct avc_entry_ref`, callback structs for memory/log/thread/lock behavior, `struct avc_cache_stats`, and event constants such as `AVC_CALLBACK_GRANT`. Key APIs include `avc_open()`, deprecated `avc_init()`, `avc_destroy()`, `avc_reset()`, `avc_cleanup()`, `avc_context_to_sid()`, `avc_sid_to_context()`, `avc_has_perm_noaudit()`, `avc_has_perm()`, `avc_audit()`, `avc_compute_create()`, `avc_compute_member()`, `avc_add_callback()`, statistics functions, `avc_netlink_*()`, and `selinux_status_*()`.

## Control flow
Callers initialize the cache with callbacks/options, convert security contexts to internal SIDs, check permissions against source/target SID/class/access vectors, optionally audit decisions, and respond to kernel policy-change events through netlink or status-page polling. Cache refs can be initialized with `avc_entry_ref_init()` and reused across repeated checks.

## State and persistence behavior
The AVC maintains in-process SID mappings, cached access vector decisions, callback registrations, statistics, and optional netlink/status mappings. It does not persist state across process lifetime. SID lifetime is reference-counted through deprecated `sidget()`/`sidput()` semantics and invalidated on destroy/reset paths.

## Dependencies and integration points
The header includes `selinux/selinux.h` for access vector types, decisions, options, and callbacks. It integrates with kernel SELinux policy services, userspace object managers, audit/log callbacks, threading/locking abstractions, and policy reload notifications.

## Risks and edge cases
Callers must initialize and destroy global AVC state in the right order, provide thread/lock callbacks when used concurrently, and handle `EACCES` versus other errors. Deprecated APIs remain for compatibility. Netlink FD ownership can be transferred to application event loops, so acquire/release pairing matters. Callback behavior affects logging and audit side effects.

## Test signals
Tests should cover init/open with default and custom callbacks, context/SID conversion, allow and deny permission checks, noaudit plus explicit audit flow, cache reset/statistics, callback registration events, netlink acquire/release/check paths, policy reload handling, and concurrent callers with lock callbacks.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/include/selinux/avc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/include/selinux/context.h -->
# sources/security-integrity/selinux/libselinux/include/selinux/context.h

## Purpose
`context.h` declares a small userspace API for parsing, inspecting, modifying, serializing, and freeing SELinux security contexts.

## Important APIs, types, and functions
`context_s_t` wraps an opaque `void *ptr`, and `context_t` is a pointer to that wrapper. `context_new()` parses a context string. `context_str()` returns an internal string valid until the next serialization/free on the same context. `context_to_str()` returns a caller-owned string. `context_free()` releases storage. Component getters and setters expose `user`, `role`, `type`, and `range` fields.

## Control flow
Typical use creates a context with `context_new()`, reads or updates components with getters/setters, serializes with `context_str()` or `context_to_str()`, and then calls `context_free()`.

## State and persistence behavior
State is heap-backed and process-local. Getter string pointers are borrowed from the context object, while `context_to_str()` returns independent storage that callers free with `free(3)`. The API has no direct persistence behavior.

## Dependencies and integration points
The header is C/C++ compatible and integrates with higher-level libselinux APIs that accept or return context strings. It intentionally hides the parsed representation behind an opaque pointer.

## Risks and edge cases
Borrowed pointers from getters and `context_str()` become invalid after later serialization changes or `context_free()`. Setter failures return nonzero but do not document partial mutation semantics here. Callers must distinguish `free()` for `context_to_str()` from `context_free()` for the context object.

## Test signals
Tests should parse valid and invalid contexts, mutate each component, verify serialization, check MLS range preservation, assert borrowed-pointer lifetime assumptions, and run leak/error tests for setter failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/include/selinux/context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/include/selinux/get_context_list.h -->
# sources/security-integrity/selinux/libselinux/include/selinux/get_context_list.h

## Purpose
`get_context_list.h` declares APIs for determining authorized and preferred SELinux login/session contexts for a Linux user, optionally constrained by role or MLS level.

## Important APIs, types, and functions
The default SELinux user fallback is `SELINUX_DEFAULTUSER`. APIs include `get_ordered_context_list()`, `get_ordered_context_list_with_level()`, `get_default_context()`, `get_default_context_with_level()`, `get_default_context_with_role()`, `get_default_context_with_rolelevel()`, `query_user_context()`, and `manual_user_enter_context()`.

## Control flow
Callers supply a target user and optional source context, level, or role. The library computes policy-authorized contexts, orders them according to customizable preferences, returns a list or default context, or asks the user to select/enter a context. `fromcon == NULL` means the current context is used.

## State and persistence behavior
Returned context arrays are caller-owned and freed with `freeconary()`. Returned single contexts are caller-owned and freed with `freecon()`. The functions consult policy and preference data but do not persist changes themselves.

## Dependencies and integration points
The header includes `selinux/selinux.h` for memory-freeing and context APIs. It integrates with login managers, PAM/session setup, role selection, MLS/MCS level handling, and user preference files.

## Risks and edge cases
The include guard name `_SELINUX_GET_SID_LIST_H_` does not match the file name, which is harmless but confusing. Interactive functions are unsuitable for noninteractive services unless carefully gated. Callers must free using the libselinux-specific free helpers rather than plain `free()` for contexts.

## Test signals
Tests should cover reachable and unreachable users, role-restricted lookup, MLS level override, NULL `fromcon`, ordered preference behavior, no-policy/error paths, interactive selection cancellation, and ownership/freeing contracts.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/include/selinux/get_context_list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/include/selinux/get_default_type.h -->
# sources/security-integrity/selinux/libselinux/include/selinux/get_default_type.h

## Purpose
`get_default_type.h` declares functions for locating and reading the default SELinux type/domain associated with a role.

## Important APIs, types, and functions
`selinux_default_type_path()` returns the path to the default type file. `get_default_type(const char *role, char **type)` finds the default type for a role and returns caller-owned storage that must be freed with `free()`.

## Control flow
Callers typically locate the config path only for diagnostics or custom reading. Normal use passes a role to `get_default_type()`, checks for `0` success or `-1` failure, uses the returned type string, and frees it.

## State and persistence behavior
The API reads SELinux configuration data and allocates memory for results. It does not modify policy or persist state.

## Dependencies and integration points
It is part of libselinux's login/session support and complements role/context selection APIs in `get_context_list.h` and path discovery APIs in `selinux.h`.

## Risks and edge cases
Callers must handle absent role mappings, unreadable configuration, NULL output pointers, and memory ownership. The header documents `free()` rather than `freecon()`, so using the wrong deallocator is a caller bug.

## Test signals
Tests should cover existing and missing roles, unreadable default type files, malformed records, memory allocation failures, returned path stability, and correct caller freeing.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/include/selinux/get_default_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/include/selinux/label.h -->
# sources/security-integrity/selinux/libselinux/include/selinux/label.h

## Purpose
`label.h` declares the libselinux labeling interface used by userspace object managers and tools to load label backends and look up security contexts for files, media, X objects, databases, Android properties, and services.

## Important APIs, types, and functions
The central opaque type is `struct selabel_handle`. Backend constants include `SELABEL_CTX_FILE`, `MEDIA`, `X`, `DB`, `ANDROID_PROP`, and `ANDROID_SERVICE`. Options include validation, base-only loading, alternate path, subset, and digest. APIs include `selabel_open()`, `selabel_close()`, `selabel_lookup()`, `selabel_lookup_raw()`, partial-match and digest/hash helpers, best-match lookups, `selabel_digest()`, `selabel_cmp()`, and `selabel_stats()`. It also defines X and DB type codes and `enum selabel_cmp_result`.

## Control flow
Callers open a backend with optional `struct selinux_opt` values, perform one or more lookups using backend-specific keys and type codes, optionally inspect digests/statistics or compare handles, and close the handle. Raw variants bypass translation where applicable.

## State and persistence behavior
Each handle owns parsed label configuration and any backend-specific caches or digests. The API reads policy context files but does not modify them. Returned contexts are caller-owned and freed with `freecon()`, while digest/specfile pointers follow implementation-defined ownership documented by the man page.

## Dependencies and integration points
The header depends on `selinux/selinux.h`, `stdbool.h`, `stdint.h`, and `sys/types.h`. It integrates with restorecon, matchpathcon replacement paths, file-context validation, Android labeling backends, and tools needing digest comparison against `security.sehash`.

## Risks and edge cases
Backend/type combinations are not universally valid. Callers must not use handles after `selabel_close()`. Digest APIs require `SELABEL_OPT_DIGEST`; otherwise callers can receive failures or missing data. Raw versus translated context use must match the caller's audit/display needs. Partial and best-match behavior can be subtle for aliases and file modes.

## Test signals
Tests should cover each backend where available, option parsing, file lookup by path/mode, raw and translated lookups, aliases in best-match calls, digest generation and specfile lists, handle comparison outcomes, partial-match queries, invalid backend/options, and close-after-use safety.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/include/selinux/label.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/include/selinux/restorecon.h -->
# sources/security-integrity/selinux/libselinux/include/selinux/restorecon.h

## Purpose
`restorecon.h` declares high-level relabeling APIs for restoring filesystem contexts according to SELinux file-context specifications, including recursive and parallel relabeling, digest/xattr management, exclude lists, alternate roots, and counters.

## Important APIs, types, and functions
Primary APIs are `selinux_restorecon()`, `selinux_restorecon_parallel()`, `selinux_restorecon_set_sehandle()`, `selinux_restorecon_default_handle()`, `selinux_restorecon_set_exclude_list()`, `selinux_restorecon_set_alt_rootpath()`, `selinux_restorecon_xattr()`, `selinux_restorecon_get_skipped_errors()`, and `selinux_restorecon_get_relabeled_files()`. Flags control no-change mode, recursion, progress, realpath, xdev, syslog, match logging, digest behavior, conflict handling, user/role changes, error counting, relabel counting, and multilink skipping. `struct dir_xattr` reports digest xattr scan/delete results.

## Control flow
Callers optionally set a custom selabel handle, exclude list, or alternate root, then call restorecon on a path with flags. The library lazily creates a default file-label handle when needed. Xattr-specific calls scan or delete `security.sehash` digests and return a linked result list.

## State and persistence behavior
The restorecon subsystem uses process-global configuration for the default handle, exclude list, alternate root, and counters. Persistent effects can include changing file security labels, writing/removing digest xattrs, logging changes, and reading mount information.

## Dependencies and integration points
The header depends on `selinux/label.h` and system types. It integrates with file-context backends, filesystem traversal, xattrs, syslog, mount filtering, and command-line tools such as `restorecon` and `setfiles`.

## Risks and edge cases
Global restorecon settings and counters are sensitive to threading and call ordering. Flag combinations can change semantics significantly, especially no-change/counting/progress/digest modes. Recursive relabeling can cross large trees unless `XDEV` or excludes are set. Digest read/write may require `CAP_SYS_ADMIN`. Alternate root handling must avoid accidentally relabeling the host tree.

## Test signals
Tests should cover dry-run and real relabeling, recursive traversal, xdev and exclude behavior, custom handles, alternate roots, digest skip/ignore/delete paths, conflict-error handling, error counting, relabeled-file counters, parallel execution, and hard-link multilink skipping.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/include/selinux/restorecon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/include/selinux/selinux.h -->
# sources/security-integrity/selinux/libselinux/include/selinux/selinux.h

## Purpose
`selinux.h` is the central public libselinux header. It declares status queries, context get/set wrappers, xattr helpers, socket peer context access, policy decision APIs, boolean management, class/permission mapping, file-context matching compatibility APIs, SELinux path discovery, access checking, translation, login mapping, and configuration reset functions.

## Important APIs, types, and functions
Major types include deprecated `security_context_t`, `access_vector_t`, `security_class_t`, `struct av_decision`, `struct selinux_opt`, `union selinux_callback`, `SELboolean`, and `struct security_class_mapping`. Important functions include `is_selinux_enabled()`, `getcon()`/`setcon()` families, exec/fs/key/socket create context APIs, file xattr context APIs, `security_compute_*()`, `security_load_policy()`, `selinux_mkload_policy()`, `selinux_init_load_policy()`, boolean APIs, context validation/canonicalization, enforcing and unknown-permission queries, class/permission string mapping, `matchpathcon*()` compatibility APIs, policy path getters, `selinux_check_access()`, `set_selinuxmnt()`, `selinuxfs_exists()`, translation/color APIs, `getseuser*()`, file-context verification/defaulting, and `selinux_reset_config()`.

## Control flow
Callers use status/path APIs to discover SELinux availability and policy layout, context APIs to read or set process/file/socket labels, policy APIs to compute or load decisions, boolean APIs to stage and commit changes, and access-check APIs to audit permission decisions. Callback APIs allow logging, audit formatting, context validation, and policy event handling to be customized globally.

## State and persistence behavior
Many functions operate on kernel SELinux state through `/proc`, xattrs, selinuxfs, policy files, booleans, and process attributes. Some set process-local state for future exec/file/key/socket creation. Callback registration and cached configuration are process-global. Persistent effects include file label changes, boolean commits, policy loading, and config/path-root changes.

## Dependencies and integration points
The header depends on Linux system types and `<asm/bitsperlong.h>`. It is consumed by almost every libselinux user, including AVC, labeling, restorecon, login/session setup, package managers, init systems, and object managers.

## Risks and edge cases
The API mixes raw and translated context variants; callers must choose correctly. Many returned strings require `freecon()`, `freeconary()`, or `free()` depending on function. Deprecated APIs remain for compatibility and may always fail or be unsupported, such as runtime disable on newer kernels and local boolean loading. `selinux_reset_config()` is explicitly not thread-safe. Process context changes can invalidate access to already-open descriptors unless policy permits use.

## Test signals
Coverage should include enabled/disabled kernels, raw versus translated context round trips, file/xattr operations on symlinks and fds, process attribute get/set, compute decision APIs, boolean staging/commit, class/permission mapping, matchpathcon compatibility, path getters under alternate roots, access checks with callbacks, policy load failures, and thread-safety boundaries around global reset/configuration.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/include/selinux/selinux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/man/Makefile -->
# sources/security-integrity/selinux/libselinux/man/Makefile

## Purpose
This makefile installs libselinux manual pages for sections 3, 5, and 8, including optional localized man pages.

## Important APIs, types, and functions
Variables include `LINGUAS`, `PREFIX`, `MANDIR`, `MAN3SUBDIR`, `MAN5SUBDIR`, `MAN8SUBDIR`, and derived install directories. `install` creates section directories, installs `man3/*.3`, `man5/*.5`, and `man8/*.8`, then loops through each language in `LINGUAS` and installs localized section files if the language section directory exists. `all`, `relabel`, `format`, `distclean`, and `clean` are present but empty.

## Control flow
Running `make install` performs base English installation first, then iterates languages and conditionally creates/copies localized man pages per section.

## State and persistence behavior
Persistent effects are installed man-page files under `$(DESTDIR)$(MANDIR)` and localized subdirectories. No source files are generated or cleaned by this makefile.

## Dependencies and integration points
It is invoked from the top-level libselinux makefile and depends on shell conditionals, `mkdir`, and `install`. It integrates with packaging variables for prefix, man section subdirectory names, and selected localization list.

## Risks and edge cases
Empty globs such as `man3/*.3` can cause install failures if a section has no files. Localized installation only checks directory existence, not whether matching files exist. Empty clean/format targets may surprise maintainers expecting generated man artifacts to be removed or formatted.

## Test signals
Tests should install to a staging `DESTDIR`, verify base and localized section paths, run with empty and nonempty `LINGUAS`, check custom man subdir variables, and validate behavior when a localized section directory exists but has no matching pages.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/man/Makefile -->
