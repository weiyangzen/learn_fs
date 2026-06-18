# subset-b-007779 research

Grouped research report for the subset-b-007779 source files. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/dumbwindows.c -->
# sources/distributed-fs/openafs/src/gtx/dumbwindows.c

Purpose: implements the GTX "dumb terminal" backend advertised by `gtxdumbwin.h`, but it is mostly a placeholder implementation. It exports `dumb_gwinops` and `gator_dumb_gwinbops` so the generic window layer can select this backend through `gw_init`.

Important APIs and functions: `gator_dumbgwin_init` records `dumb_debug`; `gator_dumbgwin_create` currently returns `NULL`; cleanup, box, clear, destroy, display, draw-char, and draw-string return success without drawing; draw-line, draw-rectangle, invert, getchar, getdimensions, and wait log that they are no-ops and the input/dimension routines return `-1`.

Control flow and state: calls enter only through the generic `WOP_*` dispatch table. The only persistent module state is the global debug flag. No window instances are allocated, so no backend-private state exists.

Dependencies and integration: depends on `gtxdumbwin.h` and the generic `gwin` structures. `windows.c` can select it for `GATOR_WIN_DUMB`, but tests that try to create a dumb window will fail because creation returns `NULL`.

Risks: many operations report success despite doing nothing, which can hide unsupported backend selection. `gator_dumbgwin_destroy` debug output lacks a newline. Test signals should cover backend selection, `WOP_CREATE` failure behavior, and callers that assume successful no-op drawing means a usable terminal surface exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/dumbwindows.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/frame.c -->
# sources/distributed-fs/openafs/src/gtx/frame.c

Purpose: implements GTX frames, which bind a `gwin` to a keymap, display list, menus, prompt/default input state, and a bottom message line. Frames are the interactive controller between the window backend, key processing, and object rendering.

Important APIs and functions: `gtxframe_Create/Delete`, `gtxframe_SetFrame/GetFrame`, menu operations, display-list operations, `gtxframe_Display`, `gtxframe_DisplayString`, `gtxframe_ClearMessageLine`, `gtxframe_AskForString`, and `gtxframe_ExitCmd`. Internal command handlers implement recursive input editing for backspace, Ctrl-U, self-insert, accept, and abort.

Control flow and state: `gtxframe_AskForString` saves the caller keymap, installs a singleton `recursiveMap`, fills `promptLine` and `defaultLine`, then calls `gtx_InputServer` until accept/abort flags are set. `gtxframe_Display` draws menu text, dispatches each listed `onode` through `OOP_DISPLAY`, then draws prompt/message text on the last line.

Dependencies and integration: uses `gtxkeymap`, `gtxinput`, `gtxobjects`, generic `WOP_*` drawing, and curses cleanup in `gtxframe_ExitCmd`.

Risks: fixed 1024-byte buffers are used for menu and prompt composition with unbounded `strcat`/`strcpy`; `gtxframe_ExitCmd` directly calls curses cleanup even when another backend was selected; `gtxframe_Delete` does not clear menus/display-list entries or prompt/default strings. Test signals should exercise recursive input, long menu labels, frame switching, duplicate display-list insertion, abort paths, and non-curses backend exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/frame.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxX11win.h -->
# sources/distributed-fs/openafs/src/gtx/gtxX11win.h

Purpose: declares the GTX X11 backend contract. It gives the generic window layer a backend type value, creation parameters, a base operation table, and the full set of `gwinops`-compatible functions.

Important APIs and types: `GATOR_WIN_X11`, `struct gator_X11gwin_params`, `gator_X11_gwinbops`, `gator_X11gwin_init/create/cleanup`, and drawing/input routines for box, clear, destroy, display, drawline, drawrectangle, drawchar, drawstring, invert, getchar, getdimensions, and wait.

Control flow and state: this header itself stores no state. Runtime state is owned by the X11 backend implementation and generic `struct gwin`. The `gwin_params` embedded in creation parameters carries common type, geometry, and parent-window inputs; `box_vertchar` and `box_horizchar` customize box rendering.

Dependencies and integration: includes `gtxwindows.h`; `windows.c` selects this backend for `GATOR_WIN_X11`. Object and frame code use it only through generic `WOP_*` macros after initialization.

Risks: the interface mirrors curses/dumb, so callers may assume behavioral parity across backends. Test signals should compile the header with the implementation, verify the `gwinops` table signatures stay aligned, and run backend-specific draw/input tests when X11 support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxX11win.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxcurseswin.h -->
# sources/distributed-fs/openafs/src/gtx/gtxcurseswin.h

Purpose: declares the GTX curses backend. It adapts platform curses headers, provides portability glue for `getmaxyx`, defines curses-private window data, and exports the `gwinops` functions used by the generic GTX window interface.

Important APIs and types: `GATOR_WIN_CURSES`, `struct gator_cursesgwin` with `WINDOW *wp`, character dimensions, and box characters; `struct gator_cursesgwin_params`; `gator_curses_gwinbops`; and init/create/cleanup/draw/input functions.

Control flow and state: the header defines shape only. Curses state is held in backend-private `WINDOW` objects and attached to `gwin.w_data`. Creation parameters include common geometry through `gwin_createparams` and curses-specific character metrics.

Dependencies and integration: includes `gtxwindows.h` and conditionally includes `ncurses.h`, `ncurses/ncurses.h`, or `curses.h`. `windows.c`, `gtx_Init`, `screen_test.c`, and `object_test.c` rely on this backend as the practical interactive implementation.

Risks: portability macros use private curses fields `_maxy`/`_maxx` as a fallback. Code outside the header, including tests, uses global `LINES` and `COLS`, so curses initialization order matters. Test signals should include configure variants with different curses header availability and runtime creation/dimension/readiness checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxcurseswin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxdumbwin.h -->
# sources/distributed-fs/openafs/src/gtx/gtxdumbwin.h

Purpose: declares the "dumb terminal" GTX backend interface. It exposes the same generic operation surface as curses and X11 while assigning the backend type `GATOR_WIN_DUMB`.

Important APIs and types: `struct gator_dumbgwin_params` embeds common `gwin_createparams` and box characters. Exported functions include package initialization, window creation/cleanup, all drawing operations, input polling, dimension lookup, and wait.

Control flow and state: no state is declared in the header. Runtime users call `gw_init` with `GATOR_WIN_DUMB`, then interact through `WOP_*` macros backed by `gator_dumb_gwinbops` and the dumb backend `gwinops` table.

Dependencies and integration: includes `gtxwindows.h`; used by `windows.c`, `screen_test.c`, `object_test.c`, and `textobject.c` as one of the selectable backends. The implementation currently does not create usable windows.

Risks: the header advertises full backend capability but `dumbwindows.c` is largely nonfunctional. Callers selecting this backend need explicit handling for failed creation and unsupported input/dimension operations. Test signals should validate advertised signatures and confirm callers degrade cleanly when `gator_dumbgwin_create` returns `NULL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxdumbwin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxframe.h -->
# sources/distributed-fs/openafs/src/gtx/gtxframe.h

Purpose: defines the public frame structure and frame manipulation API for GTX interactive views. A frame holds a keymap, display object list, menu list, message/prompt strings, an owning window pointer, and state flags.

Important APIs and types: `struct gtxframe_dlist`, `struct gtxframe_menu`, `struct gtx_frame`, flags `GTXFRAME_NEWDISPLAY`, `GTXFRAME_RECURSIVEEND`, and `GTXFRAME_RECURSIVEERR`, plus APIs for frame/window association, menus, prompting, message display, object list operations, display, deletion, and the exit command.

Control flow and state: the header exposes state directly instead of hiding it behind accessors. Input code mutates `flags` and keymap state, frame display traverses `menus` and `display`, and prompt handling uses `promptLine`/`defaultLine`.

Dependencies and integration: relies on forward-visible `struct gwin`, `struct onode`, and keymap types from companion headers. It is included by `frame.c`, input handling, tests, and curses backend code.

Risks: direct struct access makes ABI and invariants fragile. `display` stores `char *data` but actually holds `struct onode *`, which is type-unsafe. Test signals should cover header consumers, frame lifecycle cleanup, and mutation of flags during nested input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxframe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxinput.h -->
# sources/distributed-fs/openafs/src/gtx/gtxinput.h

Purpose: declares the GTX input server entry point.

Important API: `void *gtx_InputServer(void *)` accepts a generic parameter that is expected to be a `struct gwin *` at runtime. It returns a `void *` so it can be used as a pthread start routine as well as called synchronously.

Control flow and state: this header contains no state, but the implementation reads and mutates the window's attached `gtx_frame`, dispatches keys through the frame keymap, and exits recursive loops via frame flags.

Dependencies and integration: used by `frame.c` for recursive prompts, by `gtxtest.c` for the main event loop, and by `input.c` for pthread startup integration.

Risks: because the parameter is untyped, misuse is only caught at runtime. The current `gtx_Init` implementation can create an input thread with a `NULL` argument, which would be unsafe if that path is used. Test signals should include synchronous calls with a valid window and avoid or fix threaded startup before testing it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxinput.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxkeymap.h -->
# sources/distributed-fs/openafs/src/gtx/gtxkeymap.h

Purpose: defines a small trie-like keymap system for GTX keyboard command dispatch.

Important APIs and types: `KEYMAP_NENTRIES` is 256; entries are `KEYMAP_EMPTY`, `KEYMAP_PROC`, or `KEYMAP_SUBMAP`. `struct keymap_entry` stores a command name, function pointer or submap, and rock. `struct keymap_map` contains a refcount field and 256 entries. `struct keymap_state` tracks the initial and current map. Public functions create, bind, delete, initialize, process, reset, and duplicate strings.

Control flow and state: multi-character bindings are represented by nested `keymap_map` submaps. `keymap_state.currentMap` advances into submaps until a final procedure executes or a missing entry resets state.

Dependencies and integration: frames own one keymap and one state; input server feeds keycodes into `keymap_ProcessKey`; tests bind printable keys and escape-prefixed sequences.

Risks: the exposed refcount is unused by the implementation, and deleting recursively assumes exclusive ownership of submaps. Key values outside 0..255 are rejected. Test signals should cover duplicate binding replacement, deletion by binding a `NULL` proc, submap teardown, and invalid key input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxkeymap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxlightobj.h -->
# sources/distributed-fs/openafs/src/gtx/gtxlightobj.h

Purpose: declares the GTX light object, a small labeled indicator object rendered through a generic window.

Important APIs and types: `GATOR_OBJ_LIGHT`, appearance masks for outline, inverse video, flash, and flash-cycle state, `GATOR_LABEL_CHARS`, `struct gator_lightobj`, `struct gator_light_crparams`, `gator_light_create/destroy/display/release/set`, and exported `gator_light_ops`.

Control flow and state: a light object stores on/off `setting`, `appearance`, flash metadata, label text, and an `llrock` pointer used by the implementation to hold lower-level drawing parameters. `gator_light_set` changes both logical setting and draw highlight.

Dependencies and integration: includes `gtxobjects.h`; instantiated through `gator_objects_create` after `objects.c` maps object type 1 to `gator_light_create` and `gator_light_ops`. Display dispatch uses `OOP_DISPLAY`.

Risks: appearance flags for outline/flash are declared but not fully implemented in `lightobject.c`. Label copying requires callers to respect fixed buffer size. Test signals should cover create/display/set and verify appearance flags either work or are documented unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxlightobj.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxobjdict.h -->
# sources/distributed-fs/openafs/src/gtx/gtxobjdict.h

Purpose: declares an object dictionary API intended to map object names to `struct onode *` instances.

Important APIs: `gator_objdict_init`, `gator_objdict_add`, `gator_objdict_delete`, and `gator_objdict_lookup`.

Control flow and state: the header defines no storage. The intended lifecycle is initialize dictionary, add objects as they are created, delete them as they are destroyed, and look them up by name.

Dependencies and integration: includes `gtxobjects.h`. `objects.c` initializes the dictionary and delegates `gator_objects_lookup` to it. No effective add/delete calls are visible in the researched `objects.c` creation path.

Risks: the implementation is a stub: add/delete return success and lookup returns `NULL`. This means object-name lookup is currently nonfunctional, and successful add/delete statuses are misleading. Test signals should assert lookup behavior explicitly, especially if future code starts depending on `gator_objects_lookup` for navigation, help, or object discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxobjdict.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxobjects.h -->
# sources/distributed-fs/openafs/src/gtx/gtxobjects.h

Purpose: defines the generic GTX object abstraction, `struct onode`, used by text and light objects and displayed by frames.

Important APIs and types: `GATOR_OBJNAMELEN`, `struct onode` with type, name, geometry, changed/refcount state, window, operation table, graph/navigation pointers, and private data; `struct onodeops`; `OOP_DESTROY`, `OOP_DISPLAY`, `OOP_RELEASE`; initialization and creation parameter structs; `gator_objects_init`, `gator_objects_create`, and `gator_objects_lookup`.

Control flow and state: callers initialize object/window packages, then create typed objects via `onode_createparams`. The implementation attaches type-specific ops and private data and may link previous/parent objects.

Dependencies and integration: includes `gtxwindows.h`; used by light/text object headers, frame display lists, tests, and `objects.c`.

Risks: object type indexes are used directly into arrays in `objects.c`, so invalid `cr_type` can index outside initialized entries. Name copy uses fixed-size storage. Release/destroy semantics are incomplete in object implementations. Test signals should validate object creation bounds, parent/previous linking, display dispatch, and lookup expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxobjects.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxtest.c -->
# sources/distributed-fs/openafs/src/gtx/gtxtest.c

Purpose: interactive GTX integration test that creates text and light objects, two frames, key bindings, menus, and frame switching on a curses-backed window from `gtx_Init`.

Important functions: command callbacks `ChangeMenuCmd`, `ChangeListCmd`, `NoCallCmd`, `ChangeCmd`, `StupidCmd`, `SwitchToACmd`, and `SwitchToBCmd`, plus `main`. The callbacks mutate frame menus/lists, prompt for a new object string, or switch the active frame.

Control flow and state: `main` creates two text objects, one light object, `frameA` and `frameB`, binds keys and escape sequences, attaches menus and display lists, sets `frameA` on the base window, performs a temporary keymap create/delete test, then runs `gtx_InputServer`.

Dependencies and integration: exercises `gtxwindows`, `gtxobjects`, text/light objects, keymaps, frames, and input. It relies on `AFS_component_version_number.c` generated by the build.

Risks: no command-line selection or automated assertions; it is manual and terminal-dependent. Some callbacks mutate `frameA` even when invoked through current frame state, which is intentional for the demo but fragile. Test signals are visual: frame switch, menu updates, object-list clearing/restoration, prompt editing, and deletion of a normal binding before escape binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxtextcb.h -->
# sources/distributed-fs/openafs/src/gtx/gtxtextcb.h

Purpose: declares the circular text buffer used by GTX text objects.

Important APIs and types: `GATOR_TEXTCB_MAXINVERSIONS`, `struct gator_textcb_entry` with monotonically assigned ID, base highlight, inversion positions, used character count, and text pointer; `struct gator_textcb_hdr` with lock, capacity, current/oldest entry ids and indexes, entry array, and blank-line buffer. Public operations are init, create, write, blank-line insertion, and delete.

Control flow and state: the buffer stores fixed-length lines and rotates when entries fill or callers request skips. Highlight inversions capture changes within a line, though display code currently uses only base line highlight.

Dependencies and integration: includes `afs/afs_lock.h`. `textobject.c` creates and writes through this API; tests indirectly exercise it through text objects.

Risks: callers must pass valid positive dimensions; delete assumes a non-NULL header. Highlight inversion capacity is fixed at 10. Test signals should include wraparound, line filling, skip behavior, blank lines, highlight transitions, and concurrent writer locking if used outside single-threaded input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxtextcb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxtextobj.h -->
# sources/distributed-fs/openafs/src/gtx/gtxtextobj.h

Purpose: declares the GTX scrollable text object built on top of `gtxtextcb`.

Important APIs and types: `GATOR_OBJ_TEXT`, scroll direction constants, `struct gator_textobj` with lower-level rock, visible line count, circular buffer header, and first/last displayed entry IDs; `struct gator_textobj_params`; generic object operations; text-specific `gator_text_Scroll`, `gator_text_Write`, and `gator_text_BlankLine`; exported `gator_text_ops`.

Control flow and state: text object viewport state is represented by entry IDs rather than raw indexes, allowing it to follow circular buffer wraparound. Writes append to the circular buffer and can adjust displayed entry bounds.

Dependencies and integration: includes `gtxobjects.h` and `gtxtextcb.h`; instantiated by `objects.c`, displayed via generic `OOP_DISPLAY`, and exercised in object and frame tests.

Risks: destroy/release are no-ops in the implementation, so circular buffers are not reclaimed through object destruction. Display ignores per-line inversion arrays. Test signals should include creation, append, wrap, scroll up/down limits, blank lines, and memory cleanup expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxtextobj.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxwindows.h -->
# sources/distributed-fs/openafs/src/gtx/gtxwindows.h

Purpose: defines the generic GTX window abstraction and dispatch macros independent of curses, dumb-terminal, or X11 backends.

Important APIs and types: `struct gwin`, linked-list and parameter structs for initialization, creation, drawing lines/rectangles/chars/strings, inversion and size lookup, `struct gwinops`, `WOP_*` macros, `struct gwinbaseops`, global `gwinbops`, global `gator_basegwin`, `gw_init`, and `gtx_Init`.

Control flow and state: `gw_init` selects backend base ops. Created windows carry backend-private data in `w_data`, draw/input functions in `w_op`, parent pointers, and optional attached frame state. `WOP_CREATE` and `WOP_CLEANUP` dispatch through `gwinbops`; window-level operations dispatch through `w_op`.

Dependencies and integration: included by all backend headers, object headers, frames, input, and tests.

Risks: macros do no NULL checking and assume fully initialized operation tables. `w_data` is typed as `int *`, forcing casts. Test signals should cover backend initialization, base window invariants, subwindow creation, dimensions, display dispatch, and cleanup for each enabled backend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/gtxwindows.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/input.c -->
# sources/distributed-fs/openafs/src/gtx/input.c

Purpose: implements the GTX input loop and the high-level `gtx_Init` convenience initializer.

Important APIs: `gtx_InputServer` draws the active window, waits for backend input, reads one character, clears stale message state, dispatches through the current frame keymap, handles recursive-edit end flags, and redisplays. `gtx_Init` initializes objects/windows with a curses default and returns `&gator_basegwin`.

Control flow and state: `gtx_InputServer` repeatedly reads `awin->w_frame`; commands may change the frame, so it reloads after key processing. `GTXFRAME_NEWDISPLAY`, `GTXFRAME_RECURSIVEEND`, and `GTXFRAME_RECURSIVEERR` control message clearing and recursive prompt returns.

Dependencies and integration: uses pthreads, `gtxobjects`, `gtxwindows`, curses backend, keymaps, frames, `afs/stds.h`, and `opr_Verify`.

Risks: `gtx_Init` ignores its `atype` argument and hardcodes `GATOR_WIN_CURSES`. If `astartInput` is true, it starts `gtx_InputServer` with `NULL`, which would dereference a null window. Wait failures call `exit(1)`. Test signals should cover synchronous input with a valid frame, recursive prompt return, and either disable or repair threaded startup before testing it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/keymap.c -->
# sources/distributed-fs/openafs/src/gtx/keymap.c

Purpose: implements the GTX keymap trie and key-processing state machine.

Important functions: `keymap_Create`, `gtx_CopyString`, internal `BindIt`, `keymap_BindToString`, `keymap_Delete`, `keymap_InitState`, `keymap_ProcessKey`, and `keymap_ResetState`.

Control flow and state: binding walks each character in a command string, creating submaps for prefixes and installing a proc entry at the final character. Binding with a `NULL` proc deletes the final entry. Processing checks the current map slot: empty resets and returns `-1`; submap advances state; proc invokes the callback with runtime rock and entry rock, then resets.

Dependencies and integration: included by frames and tests. Callback signatures match frame/input usage: `(void *runtime, void *entry_rock)`.

Risks: no allocation failure check after `keymap_Create` inside submap creation before passing to `BindIt`; `BindIt` stores submap pointers through `void *aproc`; refcount is unused. `keymap_BindToString` silently succeeds for empty strings. Test signals should cover prefix maps, deletion, invalid key values, duplicate replacement freeing old names, and recursive map deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/keymap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/lightobject.c -->
# sources/distributed-fs/openafs/src/gtx/lightobject.c

Purpose: implements GTX light objects, which display a label with highlight reflecting on/off state.

Important functions: exported `gator_light_ops`; `gator_light_create` allocates `struct gator_lightobj` and a `gwin_strparams` lower-level rock, initializes label, appearance and flash metadata, and attaches private data; `gator_light_display` draws the label through `WOP_DRAWSTRING`; `gator_light_set` updates logical setting and string highlight. Destroy and release are no-ops.

Control flow and state: creation assumes base `onode` fields are already filled by `objects.c`. Display casts `onp->o_data` to light data and `llrock` to string parameters. Setting does not redisplay automatically; callers must display later.

Dependencies and integration: uses `gtxlightobj.h`, `gtxwindows` draw macros via included object definitions, and global `objects_debug`.

Risks: allocated private data and string params are never freed by destroy/release; `strcpy` into fixed label buffer assumes bounded input; flash and outline flags are stored but not implemented. Test signals should include set/display highlight transitions, oversized labels, object destruction leaks, and unsupported appearance flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/lightobject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/objdict.c -->
# sources/distributed-fs/openafs/src/gtx/objdict.c

Purpose: placeholder implementation for the GTX object dictionary.

Important functions: `gator_objdict_init` records debug state; `gator_objdict_add` and `gator_objdict_delete` log and return success; `gator_objdict_lookup` logs and returns `NULL`.

Control flow and state: the only persistent state is `objdict_debug`. No collection, hash table, or list is maintained, so add/delete have no effect and lookup cannot succeed.

Dependencies and integration: included by `objects.c`, which initializes it and delegates `gator_objects_lookup` to it. The researched creation path does not call `gator_objdict_add`, so the dictionary is doubly nonfunctional: no storage and no population.

Risks: callers can receive successful add/delete results while lookup remains impossible. Future code that depends on name lookup for object navigation or help will fail at runtime. Test signals should explicitly check `gator_objects_lookup` for created objects, and any repair should add population calls plus duplicate-name handling and lifecycle cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/objdict.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/object_test.c -->
# sources/distributed-fs/openafs/src/gtx/object_test.c

Purpose: manual test driver for GTX object operations across selectable window packages.

Important functions: `test_objects` initializes the requested backend, creates four light objects and one text object, toggles lights, writes strings to the text object, and scrolls it. `object_testInit` parses `-package` and `-debug`; `main` registers command syntax and dispatches.

Control flow and state: command-line parsing chooses backend, then `gator_objects_init` calls `gw_init`. The test creates objects using repeated parameter struct mutation, displays them via `OOP_DISPLAY`, writes text with sleeps between operations, scrolls up/down, and finally calls `WOP_CLEANUP`.

Dependencies and integration: includes object/window headers and `afs/cmd.h`; depends on backend globals such as `gator_basegwin`. It references `gtxscreenobj.h`, though the researched object code focuses on text/light.

Risks: old-style K&R declarations and `%x` pointer formatting are present. It lacks assertions and has an unconditional error print in the scroll-down loop even when no error occurs. The dumb backend path cannot create usable windows. Test signals are visual/manual: object creation, light toggling, text wrapping, highlighted lines, scroll bounds, and backend cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/object_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/objects.c -->
# sources/distributed-fs/openafs/src/gtx/objects.c

Purpose: implements the generic object factory and object subsystem initialization for GTX.

Important functions and state: `gator_objects_init` initializes debug state, installs type-specific ops for text and light, initializes the object dictionary, initializes the selected window backend through `gw_init`, and installs creation functions. `gator_objects_create` allocates/fills a generic `onode`, calls the type-specific creation routine, and links previous/parent object pointers. `gator_objects_lookup` delegates to the dictionary.

Control flow and state: module globals include `objects_debug`, `on_create[]`, and `objops[]`. Initialization is guarded by a static counter, but it never sets `initialized = 1` on first success, so the guard is ineffective.

Dependencies and integration: includes text/light object implementations by interface, the object dictionary, and windows. Tests and `gtx_Init` rely on it before creating objects.

Risks: no bounds check on `cr_type`; `strcpy` into fixed `o_name`; object dictionary is initialized but not populated; failed type-specific creation frees only the `onode`. Test signals should cover repeated initialization, invalid object type, duplicate/long names, parent/previous links, private-data failure cleanup, and lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/objects.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/screen_test.c -->
# sources/distributed-fs/openafs/src/gtx/screen_test.c

Purpose: manual test driver for generic GTX window operations and backend selection.

Important functions: `test_this_package` initializes a selected backend, writes screen-size strings, draws a diagonal of characters, boxes the base window, creates a subwindow, draws in it, displays, sleeps, and cleans up. `screen_testInit` parses `-package` and `-debug`; `main` registers the syntax and dispatches.

Control flow and state: the test starts with `gw_init`, uses global `gator_basegwin`, curses globals `LINES` and `COLS`, and a backend-specific creation parameter union by declaring all backend parameter types but filling the curses-shaped one for `WOP_CREATE`.

Dependencies and integration: includes generic, curses, dumb, and X11 window headers plus `afs/cmd.h`.

Risks: because it always fills `gator_cursesgwin_params` for subwindow creation, non-curses backends may receive mismatched parameters. It is visual and sleep-based, with no automated pass/fail. The dumb backend create path returns `NULL`. Test signals should include backend init failure paths, base draw operations, subwindow creation, display/cleanup, and portability around curses global dimensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/screen_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/textcb.c -->
# sources/distributed-fs/openafs/src/gtx/textcb.c

Purpose: implements the circular fixed-line text buffer backing GTX text objects.

Important functions: `gator_textcb_Init`, `gator_textcb_Create`, internal `bumpEntry`, `gator_textcb_Write`, `gator_textcb_BlankLine`, and `gator_textcb_Delete`.

Control flow and state: create allocates one contiguous text buffer, an entry array, a header, and a blank-line template. `bumpEntry` advances current entry ID/index, clears the target entry, and advances oldest entry after wraparound. `gator_textcb_Write` write-locks the buffer, copies chunks into the current entry, records highlight inversions when highlight changes mid-line, wraps full lines, and optionally skips to a new entry. Blank lines bump entries; delete write-locks, frees buffer/entries/blank line/header.

Dependencies and integration: uses AFS locks and `gtxtextcb.h`; consumed by `textobject.c`.

Risks: `gator_textcb_BlankLine` mutates without taking the buffer lock; delete has no NULL guard; allocation size uses `int`; newline-specific line breaks described in comments are not actually handled specially. Test signals should cover wraparound, skip, blank lines, highlight inversions, deletion, NULL writes, and concurrent blank/write behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/textcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/textobject.c -->
# sources/distributed-fs/openafs/src/gtx/textobject.c

Purpose: implements GTX scrollable text objects using `gator_textcb_hdr` circular buffers.

Important functions: exported `gator_text_ops`; `gator_text_create`, `gator_text_destroy`, `gator_text_display`, `gator_text_release`, `gator_text_Scroll`, `gator_text_Write`, and `gator_text_BlankLine`.

Control flow and state: creation allocates private `gator_textobj`, creates a circular buffer, stores visible line count from object height, and initializes first/last shown entry IDs. Display maps first shown entry ID to circular index, draws populated entries then blank lines through `WOP_DRAWSTRING`. Scroll clamps first/last shown IDs to buffer oldest/current. Write determines whether the current entry is visible before appending, then after buffer write adjusts viewport state when tracking the end. BlankLine delegates to the buffer and shifts viewport if it was at the end.

Dependencies and integration: includes text object, generic window, and backend headers; instantiated by `objects.c`; tested by `object_test` and `gtxtest`.

Risks: destroy/release are no-ops and leak circular buffers; write computes `writeDiff` before calling `gator_textcb_Write`, so viewport tracking may miss newly created lines; display ignores highlight inversions. Test signals should cover wrapping writes, visible-end tracking, scroll limits, blank-line follow behavior, and memory cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/textobject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/windows.c -->
# sources/distributed-fs/openafs/src/gtx/windows.c

Purpose: implements generic GTX window package initialization and backend selection.

Important functions and state: global `struct gwinbaseops gwinbops`, global `struct gwin gator_basegwin`, and `gw_init`. `gw_init` reads `gwin_initparams`, selects dumb, curses, or X11 backend, copies the backend base ops table, calls backend initialization, and returns errors for invalid package selection.

Control flow and state: initialization is a switch over `params->i_type`. It does not fill `gator_basegwin` directly in this file; backend initialization is responsible for base-window setup. `gwin_debug` is local and controls diagnostic logging.

Dependencies and integration: includes generic window header and all three backend headers. `gator_objects_init`, `screen_test`, and `gtx_Init` call `gw_init`; object and frame code depend on `gwinbops` and `gator_basegwin` after it succeeds.

Risks: no global initialized guard; reinitializing with another backend overwrites `gwinbops`. Invalid or partially initialized backends can leave globals inconsistent. Test signals should cover each backend type, invalid type errors, reinitialization behavior, and whether backend init correctly populates `gator_basegwin`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/windows.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/helper-splint.sh.in -->
# sources/distributed-fs/openafs/src/helper-splint.sh.in

Purpose: template shell helper for invoking `splint` with the OpenAFS common configuration and optional local overrides.

Important behavior: configure substitutes `@TOP_SRCDIR@` and `@HELPER_SPLINTCFG@`. The script initializes `cfargs` with the common helper config. If `splint-append.cfg` exists, it appends that config after the common one; otherwise if `splint.cfg` exists, it replaces the common config; otherwise it uses only the common config. It then execs `splint $cfargs -bad-flag "$@"`.

Control flow and state: no persistent state. It performs read checks in the current directory, so behavior depends on invocation working directory.

Dependencies and integration: used by developer/static-analysis workflows rather than runtime OpenAFS code. It depends on `splint` being installed and on configure-generated paths.

Risks: unquoted `$cfargs` intentionally expands into arguments but can be fragile if configured paths contain spaces. `TOP_SRCDIR` is assigned but unused. Test signals should run the helper in directories with no local config, with `splint.cfg`, and with `splint-append.cfg` to confirm intended precedence and argument construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/helper-splint.sh.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/Makefile.in -->
# sources/distributed-fs/openafs/src/kauth/Makefile.in

Purpose: Automake-style makefile template for building OpenAFS kauth libraries, generated RPC sources, server/client tools, tests, install targets, and cleanup rules.

Important targets and variables: object groups `BASE_objs`, `LT_objs`, `LWP_objs`, `KRB_objs`; dependency/library groups `LT_deps`, `LIBS`, `KLIBS`; `all`, `depinstall`, `generated`, `liboafs_kauth.la`, `libkauth_pic.la`, `libkauth.a`, `libkauth.krb.a`, `kaserver`, `kas`, `klog`, `klog.krb`, `knfs`, `kpasswd`, `kpwvalid`, `kdb`, `ka-forwarder`, `rebuild`, `install`, `dest`, and `clean`.

Control flow and state: generated files come from `kauth.rg` through `RXGEN` and from `kaerrors.et` through `COMPILE_ET`. Many object targets depend on generated `kautils.h`. Install/dest actions are gated by `INSTALL_KAUTH`.

Dependencies and integration: ties kauth to ubik, auth, prot, sys, rxkad, rx, lwp, cmd, com_err, audit, afsutil, opr, hcrypto/rfc3961, and roken. The researched `admin_tools.c`, `authclient.c`, and `client.c` build into libraries and commands here.

Risks: generated-header dependencies are critical for parallel builds; missed dependencies can race. The `clean` target removes generated RPC/error outputs and programs. Test signals are `make generated`, `make depinstall`, full `make`, `make test`, and install/dest dry runs with both `INSTALL_KAUTH` settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/admin_tools.c -->
# sources/distributed-fs/openafs/src/kauth/admin_tools.c

Purpose: implements the `kas` administrative command engine for Authentication Server database inspection, user management, password/key operations, server statistics/debugging, ticket cache helpers, and interactive mode.

Important APIs and functions: exported `ka_AdminInteractive`; command handlers `ListUsers`, `ExamineUser`, `CreateUser`, `DeleteUser`, `SetFields`, `Unlock`, `StringToKey`, `SetPassword`, `GetRandomKey`, `Statistics`, `DebugInfo`, `ForgetTicket`, and `ListTickets`; setup hooks `MyBeforeProc`/`MyAfterProc`; helpers `DefaultCell`, `DumpUser`, `handle_errors`, `parse_flags`, `ka_islocked`, `PrintName`, `PrintedName`, and `ListTicket`.

Control flow and state: global state includes current Ubik `conn`, selected `cell`, `whoami`, admin `passwd`, command name, interactive `finished`, cached startup argv, chosen admin principal, `noauth`, and explicit server list. `ka_AdminInteractive` registers command syntax and aliases, installs before/after hooks, dispatches initial argv, then optionally loops reading `ka> ` commands. `MyBeforeProc` derives identity/cell/server options, obtains or prompts for admin credentials, fetches admin/auth tokens, connects to the AuthServer maintenance service, and auto-prompts missing password parameters. `MyAfterProc` destroys `conn` after each command.

Dependencies and integration: uses Ubik/RX/RXKAD, token cache APIs, kauth protocol stubs, command parser, DES/hcrypto, password validation child helpers from `kkids`, and com_err.

Risks: security-sensitive legacy DES password handling; password strings live in global/static buffers and command items; hidden commands can print raw keys; retry/error handling varies by command; many fixed-size string copies rely on protocol maximums. Test signals should cover authenticated and `-noauth` connections, explicit server lists, all user lifecycle commands, lockout field packing, token listing/forgetting, password prompt flows, and cleanup of Ubik connections after failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/admin_tools.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/authclient.c -->
# sources/distributed-fs/openafs/src/kauth/authclient.c

Purpose: client-side convenience layer for locating Authentication Servers, creating RX/Ubik connections with the right security class, authenticating with a password-derived key, fetching service tickets, and changing passwords.

Important APIs and functions: `ka_ExplicitCell`, `ka_GetServers`, `ka_GetSecurity`, `ka_SingleServerConn`, `ka_AuthSpecificServersConn`, `ka_AuthServerConn`, `ka_Authenticate`, `ka_GetToken`, and `ka_ChangePassword`. Internal helpers include `myCellLookup`, `CheckTicketAnswer`, and `kawrap_ubik_Call`.

Control flow and state: module globals cache the client config dir, explicit/debug cell server lists, and flags. Server connection routines open CellServDB data, initialize RX, construct either null or rxkad security objects, create RX connections for one or many servers, then initialize a Ubik client. `ka_Authenticate` encrypts a request, tries v2/v1/old RPCs, decrypts the response, and validates challenge, ticket times, identities, lengths, and labels. `ka_GetToken` encrypts requested times with the auth token session key, calls current/old TGS RPCs, decrypts, validates, and fills a `ktc_token`.

Dependencies and integration: uses hcrypto DES, rx/rxkad, Ubik, cellconfig, token structs, kauth generated stubs, and global pthread lock macros. Admin tools and user utilities call these routines.

Risks: legacy DES/rxkad protocol handling is security-sensitive; response parsing uses packed buffers and length arithmetic; `oldkey` in `ka_ChangePassword` is unused; explicit/debug globals affect lookup process-wide. Test signals should include multi-server fallback, single-server ambiguity, old/new RPC compatibility, malformed ticket answers, password expiration extraction, and authenticated versus null security connections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/authclient.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/client.c -->
# sources/distributed-fs/openafs/src/kauth/client.c

Purpose: provides common kauth client utilities for password-to-key conversion, secure password reading, login-name parsing, and one-time client initialization.

Important APIs and functions: `ka_StringToKey`, `ka_ReadPassword`, `ka_ParseLoginName`, and `ka_Init`. Internal helpers are `Andrew_StringToKey`, Kerberos-style `StringToKey`, and `map_char`.

Control flow and state: `ka_StringToKey` maps a cell to a realm, lowercases for backward compatibility, and uses Andrew string-to-key for passwords of 8 characters or fewer, otherwise the DES CBC checksum-based string-to-key. `ka_ReadPassword` reads without echo and optionally verifies, rejects empty passwords, then derives a key. `ka_ParseLoginName` parses `name.instance@cell` with backslash quoting and three-digit octal escapes, uppercases the cell/realm, and bounds checks each component. `ka_Init` initializes error tables once and opens client cell configuration.

Dependencies and integration: uses hcrypto DES/UI helpers, `crypt`, pthread global lock macros, cellconfig/auth utilities, rxkad conversion helpers, and kauth error tables. Used by auth clients, admin tools, and command-line programs.

Risks: password handling is legacy DES-based and uses fixed buffers; `strncpy(password, str, sizeof(password))` may not NUL-terminate before `strlen` if input is oversized; backslash-octal parsing assumes enough following characters. Test signals should cover quoted login names, missing output parameters, component length limits, cell uppercasing, empty password rejection, short versus long password key derivation, and repeated `ka_Init`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/kauth/client.c -->
