# sources/storage-engines/wiredtiger tools subset-b-009094 research

This grouped report covers the WiredTiger tool files assigned to `subset-b-009094`. Each file section preserves the original source path and is delimited for reconciliation into the required source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/hexfiend/Templates/hexparse -->
## sources/storage-engines/wiredtiger/tools/hexfiend/Templates/hexparse

### Purpose
`hexparse` is a Tcl command-line compatibility runner for Hex Fiend binary templates. It lets WiredTiger's Hex Fiend templates be executed outside the GUI against one or more binary files, producing textual section/entry output and optional hexdumps. It implements a practical subset of the Hex Fiend template API: endian declarations, integer readers, byte/string readers, sections, entry emission, navigation, includes, and template discovery.

### Important APIs, Types, and Functions
The runtime state is stored in globals: `__f` for the open binary file, `__fs` for file size, `__flag_hexdump` for output mode, indentation buffers, and section accumulator variables. `__args` wraps `cmdline::getoptions`; `__unpack` and `__unpack_entry` read fixed-size binary values with Tcl `binary scan`; integer template functions such as `uint64`, `int32`, `uint16`, and `uint8` delegate to `__unpack_entry`. `bytes`, `ascii`, `str`, and `cstr` provide byte/string readers. `section`, `entry`, `sectionname`, and `sectionvalue` build the displayed parse tree. `goto`, `move`, `pos`, `len`, and `end` expose stream navigation.

### Control Flow
Startup parses hexdump options, computes indentation behavior, resolves the requested template with `__find_template_path`, then loops over each input filename. For each file it prints a header, stores file size, opens the file in binary mode, sources the resolved template, and closes the handle. Template code executes in the interpreter where the compatibility functions are already defined. `section` captures nested output into `__output`, runs its body at caller scope, calculates consumed length by comparing current position with entry position, then flushes at top level.

### State and Persistence
The script does not persist state beyond stdout output. During a file parse, all state is global and reused across template execution; the per-file loop resets `__fs` and `__f` but does not broadly reset every output/control global beyond top-level `section` flushing. `include` reads template support files from `$HOME/Library/Application Support/com.ridiculousfish.HexFiend/Templates`.

### Dependencies and Integration Points
It depends on Tcl, the `cmdline` package, and Hex Fiend template files installed under the macOS application-support path. `install.sh` copies this runner and templates into that location. WiredTiger-specific templates can call this subset of Hex Fiend's Tcl-like API to decode `.wt` files or other binary artifacts.

### Risks and Test Signals
Many Hex Fiend APIs are stubs (`big_endian`, floating-point readers, uuid/date readers, bit readers, hex/utf16, `endsection`) and will fail if templates use them. `cstr` compares against `"\x000"` and may include the terminator in returned data. Template lookup has an apparent bug in ambiguous-name reporting where `file rootname` is called without the candidate path. All file and section state is global, so parser reuse is fragile. Useful tests are small binary fixtures that exercise fixed-width integer parsing, nested sections, `include`, all hexdump modes, EOF handling, and ambiguous/missing template lookup.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/hexfiend/Templates/hexparse -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/hexfiend/install.sh -->
## sources/storage-engines/wiredtiger/tools/hexfiend/install.sh

### Purpose
`install.sh` installs the Hex Fiend application if missing and copies the local `Templates` directory, including `hexparse`, into Hex Fiend's macOS application-support template directory.

### Important APIs, Types, and Functions
The script derives `SRCDIR` from `BASH_SOURCE` and sets `DSTDIR` to `$HOME/Library/Application Support/com.ridiculousfish.HexFiend`. It conditionally invokes `brew install --cask hex-fiend`, creates the destination directory, and copies templates with `cp -a`.

### Control Flow
It checks for `/Applications/Hex Fiend.app`; if absent, it uses Homebrew to install the cask. It then unconditionally copies the source `Templates` directory into the destination and prints guidance for adding `hexparse` to the user's path through copy, symlink, or shell alias.

### State and Persistence
Persistent effects are external to the repository: installation of a macOS app through Homebrew and replacement/copying of template files under the user's home directory. It does not track versions or remove stale templates.

### Dependencies and Integration Points
The script assumes macOS, Homebrew, Bash, and the Hex Fiend bundle/path naming. It integrates directly with `hexparse` because the runner's template search path is hard-coded to the same application-support directory.

### Risks and Test Signals
Unquoted variables in some commands are limited but mostly safe because the main destination is quoted. `cp -a "$SRCDIR/Templates" "$DSTDIR/"` can overwrite existing template files without a diff or backup. CI coverage is unlikely because it requires macOS/Homebrew; a dry-run style test can validate `SRCDIR`/`DSTDIR` derivation and that the copied tree contains `Templates/hexparse`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/hexfiend/install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/CMakeLists.txt -->
## sources/storage-engines/wiredtiger/tools/io-trace-explorer/CMakeLists.txt

### Purpose
This CMake file builds the GTKmm-based `IOTraceExplorer` GUI for visualizing block-device and WiredTiger I/O traces.

### Important APIs, Types, and Functions
The project requires CMake 3.0, defaults to `RelWithDebInfo`, sets C++17, and creates an executable from `io_trace.cpp`, `main.cpp`, `main_window.cpp`, and `plot.cpp`. GTKmm dependencies are resolved either through `pkg-config` for `gtkmm-4.0` or through individual `find_library`/`find_path` calls when `VCPKG_TOOLCHAIN` is set.

### Control Flow
Configuration first chooses build type, then dependency strategy, then platform GUI options: `WIN32` with `mainCRTStartup` on MSVC and `MACOSX_BUNDLE` on Apple. Link libraries are registered globally before the executable target is declared.

### State and Persistence
Build artifacts are emitted into the CMake build tree only. No runtime state is created by this file.

### Dependencies and Integration Points
The build expects GTKmm 4 and its transitive C++ bindings for ATK, Cairo, GDK, GIO, GLib, Pango, and libsigc++. The target integrates the local parser, application, window, and plotting modules into one executable.

### Risks and Test Signals
The `VCPKG_TOOLCHAIN` branch uses broad `find_library` names and global `link_libraries`, so library names may not match all package managers. `add_cmake_flag` appears in the MSVC branch but is not a standard CMake command unless provided elsewhere, making that branch suspect. Build tests should configure both pkg-config and vcpkg paths where supported and compile with GTKmm 4 headers.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/io_trace.cpp -->
## sources/storage-engines/wiredtiger/tools/io-trace-explorer/io_trace.cpp

### Purpose
`io_trace.cpp` loads trace files into sorted in-memory trace series. It supports blkparse device-level output and WiredTiger verbose read/write logs, normalizing records into `io_trace_operation` values grouped by device or logical WiredTiger file category.

### Important APIs, Types, and Functions
`io_trace_collection::load_from_file` opens a file and dispatches based on its first character. `load_from_file_blkparse` parses blkparse `C` completion records, recognizes RWBS flags, converts 512-byte block offsets/lengths to bytes, extracts optional duration/process fields, and stores only reads/writes. `load_from_file_wt_logs` parses WT verbose lines with `[WT_VERB_READ][DEBUG_2]` or `[WT_VERB_WRITE][DEBUG_2]`, accepts `read`, `read-mmap`, `write`, and `write-mmap`, converts absolute timestamps to seconds relative to the first WT record, and stores file-path operations. `add_data_point` creates named `io_trace` buckets and keeps each operation vector timestamp-sorted.

### Control Flow
The parser reads files line by line into fixed 256-byte buffers, tokenizes with `strsep`, validates expected fields, constructs `io_trace_operation`, and calls `add_data_point`. `add_data_point` rewrites names for WT logs into combined logs, main files, table files, or other, and rewrites device traces as `Raw Device: ...`. If appended timestamps are monotonic it pushes back; otherwise it inserts by `std::upper_bound`.

### State and Persistence
All parsed data lives in `io_trace_collection::_traces`, a map from display name to heap-owned `io_trace`. The collection destructor deletes traces. There is no persistence beyond memory; the GUI consumes the collection after all input files load.

### Dependencies and Integration Points
The file depends on C stdio/string parsing, `io_trace.h`, and `util.h::ends_with`. It is called from `main.cpp`, and its `operations()` vectors are read by `plot_widget`.

### Risks and Test Signals
The parser uses fixed 256-byte lines, so long WT paths or verbose prefixes can truncate and cause parse failures or bad grouping. `strncpy(item.process, p, sizeof(item.process))` may leave a non-null-terminated process name if exactly full. `load_from_file_wt_logs` assumes offset and length token positions and simple comma/colon stripping, which is brittle for path names or changed log formatting. Unit tests should cover monotonic and out-of-order insertion, blkparse lines with and without duration/process, WT read/write-mmap lines, log-file grouping, malformed line errors, empty files, and unsupported first-line formats.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/io_trace.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/io_trace.h -->
## sources/storage-engines/wiredtiger/tools/io-trace-explorer/io_trace.h

### Purpose
`io_trace.h` declares the data model for I/O trace loading and display: trace kinds, individual operations, named trace series, and collections of related traces.

### Important APIs, Types, and Functions
`io_trace_kind` distinguishes raw device, generic file, and WiredTiger log traces. `io_trace_operation` stores timestamp, action, read/write/sync/barrier/discard flags, byte offset, byte length, duration, and issuing process. It defines `wrap_timestamp` plus timestamp-only comparison operators for sorted lookup. `io_trace` owns a name and vector of operations. `io_trace_collection` exposes `load_from_file`, `traces()`, and protected `add_data_point`, with private loaders for blkparse and WT logs.

### Control Flow
The header itself has no runtime flow, but it defines the insertion and query contract used by `io_trace.cpp` and the GUI. Consumers treat `operations()` as immutable sorted data after loading.

### State and Persistence
Trace state is in-memory only. `io_trace_collection` owns raw pointers in `_traces`, which makes destructor cleanup important and copy semantics dangerous because no copy/move operations are disabled.

### Dependencies and Integration Points
It depends on STL `map`, `string`, and `vector`. `main.cpp` owns one collection per application run, `main_window.cpp` iterates the map to build plot widgets, and `plot.cpp` relies on sorted operation vectors for binary searches.

### Risks and Test Signals
The raw pointer map invites accidental shallow copies and double-free if copied. `operations()` exposes references whose lifetime depends on collection lifetime. `process[32]` is small relative to modern command names. Test signals are compile-time checks for model use, parser tests that assert sorted operations, and UI tests that avoid empty-operation traces because plotting assumes `ops[0]` exists.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/io_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/main.cpp -->
## sources/storage-engines/wiredtiger/tools/io-trace-explorer/main.cpp

### Purpose
`main.cpp` defines the GTK application class and command-line entry point for `IOTraceExplorer`.

### Important APIs, Types, and Functions
`io_trace_explorer` subclasses `Gtk::Application` with `Gio::Application::Flags::HANDLES_COMMAND_LINE`. `on_command_line` registers `--quiet`, parses input filenames, loads each into `_traces`, logs timing through GLib messages, and activates the UI. `on_activate` creates a `main_window`, adds it to the application, shows it, and focuses it. `main` simply runs an instance.

### Control Flow
GTK invokes `on_command_line`; the code parses arguments from `Gio::ApplicationCommandLine`, rejects missing inputs, loads all trace files synchronously on the command-line path, then calls `activate()`. Exceptions are caught and reported through `g_error`, returning failure.

### State and Persistence
The application owns one `io_trace_collection` for the process lifetime and a raw `_main` window pointer. It does not persist state or remember open files.

### Dependencies and Integration Points
It depends on GTKmm/Glibmm, `io_trace_collection`, `main_window`, plotting declarations, and `current_time`. It bridges trace loading and display construction.

### Risks and Test Signals
`optind` is used after Glib option parsing; this assumes global getopt state lines up with GTK parsing. Loading is synchronous before the window appears, so large traces can delay startup. `_main` is raw and never deleted explicitly. Tests should cover argument parsing, no-input failure, multi-file loading, `--quiet`, and startup with malformed files.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/main.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/main_window.cpp -->
## sources/storage-engines/wiredtiger/tools/io-trace-explorer/main_window.cpp

### Purpose
`main_window.cpp` builds the GTK application window: toolbar controls, vertically split plot widgets, status bar, keyboard shortcuts, and plot-tool coordination.

### Important APIs, Types, and Functions
The constructor creates one `plot_widget` per trace, resets shared X extents, wires toolbar buttons/toggles, nests plots in vertical `Gtk::Paned` containers, installs an `EventControllerKey`, and sets window defaults. `set_plot_tool` updates every plot and blocks toggle signal recursion while syncing button states. Event handlers route back/forward/reset and zoom to `plot_group` or the active plot.

### Control Flow
Construction iterates the trace map to create plots, then uses `last_plot`/`last_paned` state to assemble either a single plot or a chain of split panes. Toolbar and key events later call handlers that update plot state and queue redraws through the plot layer.

### State and Persistence
The window stores raw pointers to heap-allocated `plot_widget` and `Gtk::Paned` instances in vectors. The destructor contains a TODO and does not delete them, relying on GTK object ownership or process teardown. View history lives inside each plot and the group.

### Dependencies and Integration Points
It depends on GTKmm widgets/signals, `io_trace_collection`, `plot_group`, and `plot_widget`. It is constructed by `main.cpp` after trace parsing and owns the visible user interaction surface.

### Risks and Test Signals
If there are zero traces, the window will show only toolbar/status with no plot; if a trace has zero operations, `plot_widget` construction can fail. Raw allocation and uncertain GTK ownership are memory-risk areas. Shortcut tests should verify undo/redo, zoom in/out, tool selection, and reset. UI tests should verify one trace, multiple traces, and no trace layouts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/main_window.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/main_window.h -->
## sources/storage-engines/wiredtiger/tools/io-trace-explorer/main_window.h

### Purpose
`main_window.h` declares the `main_window` GTK application window class and its UI state.

### Important APIs, Types, and Functions
The class extends `Gtk::ApplicationWindow` and exposes a constructor taking `io_trace_collection&`. Protected members include toolbar buttons/toggles, signal connections, plot group, vectors of plots/panes, status bar, `set_plot_tool`, and handlers for toggles, navigation, zoom, reset, and key presses.

### Control Flow
The header defines callback boundaries used by GTK signals. The implementation dispatches all user events through these handlers to plot state.

### State and Persistence
State is transient UI state: active tool toggles, plot/pane object pointers, and shared plot group. Nothing is saved to disk.

### Dependencies and Integration Points
It depends on `gtkmm.h`, `io_trace.h`, and `plot.h`; `main.cpp` includes it to create the top-level window.

### Risks and Test Signals
The header exposes raw pointer vectors without ownership semantics. Any future refactor should clarify whether GTK owns these children or whether `main_window` must delete them. Compile tests and static analysis around object lifetime are the main signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/main_window.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/plot.cpp -->
## sources/storage-engines/wiredtiger/tools/io-trace-explorer/plot.cpp

### Purpose
`plot.cpp` implements the interactive trace plot widgets and synchronized plot groups. It renders operation intervals into a pixbuf, draws axes and titles with Cairo, and supports inspect, move, zoom, undo, redo, reset, and synchronized X-axis navigation across plots.

### Important APIs, Types, and Functions
`plot_widget` construction registers draw and drag handlers, calculates top-level x/y ranges from operations, and initializes view state. Drag handlers clamp coordinates into the plot area, update move/zoom state, and draw inspect crosshairs or zoom rectangles. `set_view`, `view_sync`, `view_back`, `view_forward`, `view_reset`, `zoom_in`, and `zoom_out` manage view state and history. `render_worker` paints a subset of operations into the shared pixbuf. `on_draw` handles background, title, cached pixbuf rendering, threaded data drawing, overlays, and axes. `plot_group` owns plot registration and shared X-axis sync.

### Control Flow
Rendering starts in GTK's draw callback. If the pixbuf is absent, resized, or view-changed, `on_draw` allocates a new RGB pixbuf, binary-searches the timestamp-sorted operations for the visible window, splits work across one or eight threads, joins them, and then paints the pixbuf. User gestures call drag callbacks; move gestures set a shifted view in place, while zoom end converts selected viewport coordinates back to data coordinates and commits the view. Group-level navigation iterates plots and invokes individual history functions.

### State and Persistence
Each plot stores current/toplevel views, undo/redo stacks, drag coordinates and mode flags, cached pixbuf and view, margins, active tool, and a reference to immutable trace data. No state is persisted. Plot group stores a vector of plot pointers and the active plot pointer.

### Dependencies and Integration Points
The module depends on GTKmm, Cairo, Gdk Pixbuf, STL algorithms/threads, `io_trace_operation` ordering, and `current_time`. It is used by `main_window` and depends on `io_trace_collection` having already loaded sorted operations.

### Risks and Test Signals
The constructor indexes `ops[0]` and `ops[ops.size()-1]`, so empty traces are unsafe. `render_worker` has a likely bounds bug: it checks `y2 >= pixbuf_width` instead of `pixbuf_height`. Multiple worker threads write to the same pixbuf without synchronization, so overlapping operations can race; the visual result may be acceptable but is not data-race safe in C++. The pixbuf cache invalidation compares `_pixbuf->get_height()` to full widget `height` instead of `pixbuf_height`, causing extra rerenders. Division by zero can occur in move math if the drawable area is zero. Tests should cover coordinate transforms, view history, empty/single-operation traces, zoom/move gestures, rendering under ThreadSanitizer, and screenshot checks for axes/data after resizing.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/plot.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/plot.h -->
## sources/storage-engines/wiredtiger/tools/io-trace-explorer/plot.h

### Purpose
`plot.h` declares plotting primitives for the I/O Trace Explorer: coordinate transforms, interaction modes, individual plot widgets, and synchronized plot groups.

### Important APIs, Types, and Functions
`plot_view` stores data extents and provides `data_to_view_x`, `data_to_view_y`, `view_to_data_x`, `view_to_data_y`, equality, and inequality. `plot_tool` enumerates `NONE`, `INSPECT`, `MOVE`, and `ZOOM`. `plot_widget` extends `Gtk::DrawingArea` with public navigation/zoom methods and active-tool accessors, protected draw/drag/view methods, and render internals. `plot_group` exposes group-level back/forward/reset/reset-X/sync and active-plot lookup.

### Control Flow
The header defines the methods implemented in `plot.cpp`. Coordinate conversions are inline and called during rendering and gestures.

### State and Persistence
The declared state is transient UI state: current/toplevel/cached views, history stacks, drag flags, margins, pixbuf, and references to trace/group. There is no disk persistence.

### Dependencies and Integration Points
It depends on GTKmm, Glibmm, and `io_trace.h`. `main_window` uses the public API to switch tools and navigate. `plot.cpp` relies on the inline conversion semantics for all drawing.

### Risks and Test Signals
`plot_view` equality compares doubles exactly, acceptable for cached view assignment but risky if future code performs incremental floating-point operations. `plot_widget` stores references, so the trace collection and group must outlive widgets. Tests should exercise transform round-trips and group sync invariants.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/plot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/scripts/trace-wtperf.sh -->
## sources/storage-engines/wiredtiger/tools/io-trace-explorer/scripts/trace-wtperf.sh

### Purpose
`trace-wtperf.sh` runs a WiredTiger `wtperf` workload while capturing block-device traces and WiredTiger verbose read/write logs. It can optionally format a target block device, run `blktrace`, parse with `blkparse`, and generate an `iowatcher` SVG summary.

### Important APIs, Types, and Functions
The script parses `-D DEVICE`, `-d DIR`, `-F FS`, `-O DIR`, `-T TAG`, and `-h`. It resolves `WT_DIR` through `git rev-parse`, expects `build/bench/wtperf/wtperf`, and checks required tools with `exists`. Safety checks validate workload file resolution, mountpoints, block device identity, output tag collisions, and that output directory is on a different device from the workload.

### Control Flow
After argument parsing and dependency checks, predefined workload names are expanded to `bench/wtperf/runners/*.wtperf`. Formatting mode requires explicit directory or device, unmounts/wipes/mkfs/mounts/chowns, and uses a `wt` subdirectory under the mount. Non-format mode removes and recreates the workload directory. The script starts `blktrace` in the output directory, runs `wtperf` with `WIREDTIGER_CONFIG=verbose=[read:2,write:2]`, sleeps, interrupts `blktrace`, then runs `blkparse -t` and `iowatcher`.

### State and Persistence
It mutates the workload directory, may format and mount a block device, writes stdout capture, raw blktrace files, parsed device trace, and summary SVG into the output directory. It also writes WT verbose output to the captured stdout file for later parsing by `io_trace.cpp`.

### Dependencies and Integration Points
Requires Linux tracing tools (`blktrace`, `blkparse`, `iowatcher`), `findmnt`, `stat`, `realpath`, `sudo`, optional `mkfs.*`/`wipefs`, and a compiled WiredTiger `wtperf`. Output feeds `IOTraceExplorer`.

### Risks and Test Signals
Formatting mode is intentionally destructive and relies on explicit device/directory checks; shell quoting is incomplete in several test expressions and commands. `sudo killall -INT blktrace` can affect unrelated blktrace processes. Removing `$WORKLOAD_DIR` in non-format mode is dangerous if misconfigured. Tests should mock `findmnt`, `stat`, and tool availability; integration tests should use disposable loop devices and verify output tag collision protection and device separation checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/scripts/trace-wtperf.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/util.h -->
## sources/storage-engines/wiredtiger/tools/io-trace-explorer/util.h

### Purpose
`util.h` provides small inline helpers shared by the I/O Trace Explorer.

### Important APIs, Types, and Functions
`current_time()` returns wall-clock seconds using `gettimeofday`. `ends_with(std::string_view, std::string_view)` performs suffix checking.

### Control Flow
Both functions are straight-line inline helpers. `current_time` fills a `timeval`, converts seconds plus microseconds to `double`, and returns it. `ends_with` checks size and then compares the suffix.

### State and Persistence
No state is stored or persisted.

### Dependencies and Integration Points
It depends on `<sys/time.h>` and `<string_view>`. `current_time` is used for load/render timing; `ends_with` is used by trace name classification.

### Risks and Test Signals
`gettimeofday` is wall-clock and can move backward; monotonic timing would be better for performance measurements. Suffix tests should cover empty suffix, suffix longer than string, exact match, and mismatch.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/memory-model-test/CMakeLists.txt -->
## sources/storage-engines/wiredtiger/tools/memory-model-test/CMakeLists.txt

### Purpose
This CMake file builds the standalone `memory_model_test` executable used to demonstrate and stress memory-ordering behavior on x86 and ARM64.

### Important APIs, Types, and Functions
It requires CMake 3.21, sets C++20, prefers pthreads, finds `Threads`, builds `memory_model_test` from `memory_model_test.cpp` and `basic_semaphore.h`, links `Threads::Threads`, and compiles with `-O2 -Wall -Werror`.

### Control Flow
Configuration is linear: project declaration, language standard, thread package discovery, executable creation, link, and compile options.

### State and Persistence
No runtime state is managed by CMake. Build artifacts are local to the build tree.

### Dependencies and Integration Points
Requires a C++20-capable compiler unless `AVOID_CPP20_SEMAPHORE` is passed to the source build. The target links platform thread support.

### Risks and Test Signals
`-Werror` can break builds on compiler-version warning changes. The source has architecture-specific barrier definitions only for x86_64 and aarch64, so other architectures may fail. Test signals are successful configure/build and smoke runs with small `-n` iteration counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/memory-model-test/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/memory-model-test/basic_semaphore.h -->
## sources/storage-engines/wiredtiger/tools/memory-model-test/basic_semaphore.h

### Purpose
`basic_semaphore.h` implements a minimal counting semaphore used as a fallback for compilers lacking C++20 `std::binary_semaphore`.

### Important APIs, Types, and Functions
`basic_semaphore` has a constructor with initial count, `acquire()` that waits on a condition variable while count is zero and decrements it, and `release()` that increments count and notifies one waiter. Private state is `_mutex`, `_condition_variable`, and `_count`.

### Control Flow
`acquire` locks, waits in a loop to handle spurious wakeups, and consumes one count. `release` locks, increments, and signals.

### State and Persistence
State is purely in-memory synchronization state. It is process-local and not persistent.

### Dependencies and Integration Points
It depends on `<mutex>` and `<condition_variable>`. `memory_model_test.cpp` aliases it to `binary_semaphore` when `AVOID_CPP20_SEMAPHORE` is defined.

### Risks and Test Signals
It is a counting semaphore despite being used as a binary semaphore; repeated releases can accumulate permits. It does not enforce nonnegative construction. Concurrency tests should cover acquire blocking, release waking one waiter, spurious wake tolerance, and repeated release behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/memory-model-test/basic_semaphore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/memory-model-test/memory_model_test.cpp -->
## sources/storage-engines/wiredtiger/tools/memory-model-test/memory_model_test.cpp

### Purpose
`memory_model_test.cpp` is a standalone memory-ordering litmus-test driver. It repeatedly runs pairs of operations in two threads to observe whether out-of-order effects occur with plain writes/reads, compiler barriers, CPU memory barriers, and GCC/Clang atomic builtins.

### Important APIs, Types, and Functions
`thread_function` waits on a start semaphore, adds a random delay, runs a supplied lambda, and releases an end semaphore for each iteration. `test_config` packages a test name, description, two thread lambdas, an out-of-order predicate, and whether out-of-order results are allowed. `perform_test` runs a configured pair, resets shared variables per iteration, coordinates workers, counts predicate hits, reports totals, and flags forbidden reorderings. `thread_pair` declares padded shared variables, builds lambdas for write/read and two-write/two-read cases, defines test configurations, and runs them. `main` parses `-n` loop count and `-p` number of thread pairs.

### Control Flow
At startup the program chooses `std::binary_semaphore` or `basic_semaphore`, chooses an architecture barrier instruction (`mfence` on x86_64, `dmb ish` on aarch64), prints environment details, and starts the requested number of thread-pair drivers. Each test spawns two worker threads once and drives them through `loop_count` iterations via semaphores.

### State and Persistence
State is volatile runtime state only: padded integers `x`, `y`, `r1`, `r2`, semaphores, random generators, and counters. Output is printed to stdout; no files are written.

### Dependencies and Integration Points
Depends on C++ threads, semaphores or the fallback semaphore, inline assembly barriers, `unistd.h` getopt, and compiler atomic builtins. It is built by the local CMake file and used as a diagnostic/development tool rather than WiredTiger runtime code.

### Risks and Test Signals
The shared variables are plain `int` and intentionally data-racy for litmus purposes; sanitizers will report races. The `"one barrier and one atomic"` test description does not match the code, which uses atomics in both lambdas. No barrier definition exists for non-x86_64/non-aarch64 architectures. `atoi` permits zero/negative loop or pair counts without validation, and percentage calculations divide by `iterations` after the loop. Test signals include small smoke runs, architecture-specific expected forbidden-count behavior, and build with/without `AVOID_CPP20_SEMAPHORE`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/memory-model-test/memory_model_test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/modularity_check/build_dependency_graph.py -->
## sources/storage-engines/wiredtiger/tools/modularity_check/build_dependency_graph.py

### Purpose
`build_dependency_graph.py` converts parsed WiredTiger C-file metadata into a module dependency graph. Edges record why one module depends on another through function calls, type use, or struct field access.

### Important APIs, Types, and Functions
`Link` stores counters for `func_calls`, `types_used`, and nested `struct_accesses`, with printing helpers. `incr_edge_struct_access`, `incr_edge_func_call`, and `incr_edge_type_use` create/update graph edges unless the source and destination modules are identical. `build_graph(parsed_files)` builds reverse maps from functions, structs, fields, and types to modules, then walks every parsed function to add dependency edges. `AMBIG_NODE` captures unresolved or ambiguous relationships.

### Control Flow
The function first collects reverse indexes across all files. It then creates a `networkx.DiGraph`, adds each file module, and processes field accesses, function calls, and type uses. Single-owner references resolve to the owning module; multi-owner or missing references point to the ambiguous node. Ambiguous fields are also accumulated for privacy reporting.

### State and Persistence
Graph state is in-memory. Nothing is written here; consumers such as `query_dependency_graph.generate_dependency_file` may persist graph-derived output.

### Dependencies and Integration Points
Depends on dataclasses, collections counters/defaultdicts, NetworkX, and `parse_wt_ast.File`. It is called by `modularity_check.py`.

### Risks and Test Signals
Field-to-struct inference by field name is approximate and can over-report ambiguity. Empty reverse-map lookups are treated as ambiguous edges, which can obscure parser misses. Tests should use synthetic parsed files with unique, duplicate, and missing symbols, verifying edge metadata and self-edge suppression.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/modularity_check/build_dependency_graph.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/modularity_check/header_mappings.py -->
## sources/storage-engines/wiredtiger/tools/modularity_check/header_mappings.py

### Purpose
`header_mappings.py` provides manual mapping from `src/include/*.h` headers to WiredTiger modules for the modularity checker, plus a skip list for forward-declaration/extern headers.

### Important APIs, Types, and Functions
`header_mappings` maps header filenames such as `btmem.h`, `cache_inline.h`, `transaction.h`-adjacent headers, and OS-layer headers to module names. `skip_files` lists headers that should not participate in dependency graph construction, including generated extern and public extension headers.

### Control Flow
There is no runtime control flow beyond module import. `parse_wt_ast.file_path_to_module_and_file` consults these collections when resolving include headers.

### State and Persistence
The mappings are static source data. No state is persisted.

### Dependencies and Integration Points
Imported by `parse_wt_ast.py`. The correctness of dependency graph nodes for include headers depends on this file staying in sync with WiredTiger's source tree.

### Risks and Test Signals
Missing mappings cause warnings and default to `include`, which can pollute the graph. Stale mappings can misattribute dependencies. Tests should compare current `src/include` headers against mapped/skipped lists and fail on unmapped headers that are not intentionally skipped.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/modularity_check/header_mappings.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/modularity_check/modularity_check.py -->
## sources/storage-engines/wiredtiger/tools/modularity_check/modularity_check.py

### Purpose
`modularity_check.py` is the command-line entry point for querying WiredTiger module dependencies and privacy characteristics.

### Important APIs, Types, and Functions
`parse_args` defines subcommands: `who_uses`, `who_is_used_by`, `list_cycles`, `explain_cycle`, `privacy_report`, and `generate_dependency_file`. `main` parses all WiredTiger files through `parse_wiredtiger_files`, builds the dependency graph, and dispatches to query functions.

### Control Flow
On execution, the script changes the current working directory to its own directory because parser paths are hard-coded relative to it. It always reparses the source tree and rebuilds the graph before executing a command. Cycle listing uses `nx.simple_cycles` with `length_bound=3` and prints cycles containing the requested module.

### State and Persistence
Most commands only print. `generate_dependency_file` writes `dep_file.new` via the query module. No cache is maintained, so every invocation recomputes.

### Dependencies and Integration Points
Depends on argparse, ast literal parsing for cycle arguments, os, NetworkX, `parse_wt_ast`, `build_dependency_graph`, and `query_dependency_graph`. It integrates the parser/build/query pipeline.

### Risks and Test Signals
Full-tree parsing can be expensive and sensitive to tree-sitter dependency availability. `explain_cycle` trusts `ast.literal_eval` input shape. Tests should cover every subcommand with a small mocked graph/parser or a known fixture source tree, including working-directory behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/modularity_check/modularity_check.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/modularity_check/parse_wt_ast.py -->
## sources/storage-engines/wiredtiger/tools/modularity_check/parse_wt_ast.py

### Purpose
`parse_wt_ast.py` parses WiredTiger C and header files with tree-sitter to extract module-level functions, macro functions, structs, typedefs, field accesses, function calls, and type uses for dependency analysis.

### Important APIs, Types, and Functions
Dataclasses `Struct`, `Function`, and `File` carry parsed metadata. `descendants_with_name` recursively collects AST nodes. `parse_struct`, `parse_typedef_struct`, `parse_function`, `parse_macro_funcs`, `parse_funcs`, and `parse_types` extract symbols and uses. `preprocess_file` rewrites problematic WT macros/attributes before parsing. `file_path_to_module_and_file` maps `../../src/...` paths to module names with special handling for checksum, OS folders, and include headers. `source_files` reads `dist/filelist` and `dist/extlist`; `parse_wiredtiger_files` filters source files and uses multiprocessing by default.

### Control Flow
The module initializes a C tree-sitter parser at import. Parsing reads and preprocesses each file, parses to an AST, and builds a `File` object by combining parsed functions/macros and type definitions. In non-debug mode, `parse_wiredtiger_files` maps `process_file` across a multiprocessing pool.

### State and Persistence
No persistent output is written. Runtime state includes parser objects and parsed-file lists. Multiprocessing workers return dataclass objects to the parent process.

### Dependencies and Integration Points
Depends on `tree_sitter`, `tree_sitter_c`, multiprocessing, regex/glob/os, and `header_mappings`. Output feeds `build_dependency_graph`.

### Risks and Test Signals
Parsing is approximate: macro bodies are not fully analyzed, field access is inferred by identifier only, common call filtering is heuristic, and preprocessing may miss new macros. Assertions enforce assumptions about source shape, e.g. checksum subfolders and unique struct definitions. Tests should parse small C fixtures covering typedef structs, function pointers, macros, include-header mapping, skipped externs, WT packed/cache-line macros, and duplicate functions under conditional branches.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/modularity_check/parse_wt_ast.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/modularity_check/query_dependency_graph.py -->
## sources/storage-engines/wiredtiger/tools/modularity_check/query_dependency_graph.py

### Purpose
`query_dependency_graph.py` provides reporting functions over the NetworkX module dependency graph, including edge explanations, cycle explanations, privacy reports, and dependency-file generation.

### Important APIs, Types, and Functions
`print_edge` prints a graph edge's `Link` metadata. `who_uses` prints incoming dependencies for a module; `who_is_used_by` prints outgoing dependencies. `explain_cycle` validates and prints each edge in a requested cycle. `privacy_report_functions` determines which module functions are called from outside; `privacy_report_structs` determines which struct fields are externally accessed, marking ambiguous fields. `privacy_report` aggregates structs/functions for a module. `generate_dependency_file` writes non-ambiguous `caller -> callee` edges.

### Control Flow
Reports iterate sorted graph edges and parsed-file lists, pull edge metadata through `nx.get_edge_attributes`, and print human-readable details. Dependency-file generation writes a header and all non-ambiguous outgoing edges.

### State and Persistence
Most functions print only. `generate_dependency_file` persists `dep_file.new` in the current working directory.

### Dependencies and Integration Points
Depends on NetworkX, collections, typing, `parse_wt_ast` dataclasses, and `build_dependency_graph.AMBIG_NODE`. It is called by `modularity_check.py`.

### Risks and Test Signals
The `who_is_used_by` local variable is named `incoming_edges` despite using `out_edges`, a readability issue not a behavior bug. Privacy counts can divide by zero if a module has no non-ambiguous fields or functions in certain branches; current code only prints percentages when private counts are nonzero, but a module with zero totals and nonzero private count should be impossible. Tests should verify reports for graphs with no edges, ambiguous edges, cycles, and mixed private/public symbols.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/modularity_check/query_dependency_graph.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/optrack/find-latency-spikes.py -->
## sources/storage-engines/wiredtiger/tools/optrack/find-latency-spikes.py

### Purpose
`find-latency-spikes.py` visualizes WiredTiger operation tracking text logs, finding function-duration outliers and generating Bokeh HTML dashboards. It creates per-function outlier histograms and bucketed cross-file timeline views.

### Important APIs, Types, and Functions
Global state tracks colors, first/last timestamps, user thresholds, per-file DataFrames, per-function DataFrames, and output dimensions. `initColorList` and `getColorForFunction` assign stable colors. `getIntervalData`, `createCallstackSeries`, and `assignStackDepths` pair begin/end records into intervals with stack depth and duration. Plot functions include `plotOutlierHistogram`, `generateBucketChartForFile`, `createLegendFigure`, `generateNavigatorFigure`, and `generateCrossFilePlotsForBucket`. `generateTSSlicesForBuckets` parallelizes bucket page generation. `parseConfigFile` reads time unit and threshold configuration. `processFile` reads logs and populates DataFrames. `main` wires CLI parsing, processing, plotting, and final output.

### Control Flow
The script validates input and open-file limits, sets job parallelism, initializes colors, optionally parses a config, creates `BUCKET-FILES`, processes each input log into interval DataFrames, normalizes timestamps, generates cross-file bucket HTML files in parallel, then creates `WT-outliers.html` containing outlier histograms that link into bucket pages.

### State and Persistence
Persistent output includes `WT-outliers.html`, `BUCKET-FILES/bucket-*.html`, optional `*-clean.txt` logs, and per-input hidden error logs such as `.filename.log`. In-memory state is heavily global and accumulates across all inputs.

### Dependencies and Integration Points
Depends on pandas, NumPy, Bokeh, multiprocessing, subprocess, and text logs produced by `wt_optrack_decode.py`. It assumes each input row has event type, function, and timestamp, with an optional first line containing seconds since epoch.

### Risks and Test Signals
The script uses older Bokeh APIs (`plot_width`, `TapTool.callback`, `LabelSet render_mode`) that may break on newer Bokeh versions. Several bugs are visible: a malformed string concatenation in timestamp parse error handling, `numOutliers = bucketDF.size` counts cells rather than rows, `threshold = -units` for `stdev` assigns a string-negation error path, and `timeUnitsPerBucket` can be zero when the trace duration is shorter than the bucket count. Global state makes repeated in-process invocation unsafe. Tests should cover malformed begin/end stacks, config parsing, short traces, empty function DataFrames, Bokeh output generation with the pinned dependency version, and multiprocessing bucket generation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/optrack/find-latency-spikes.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/optrack/optrack_to_t2.py -->
## sources/storage-engines/wiredtiger/tools/optrack/optrack_to_t2.py

### Purpose
`optrack_to_t2.py` converts operation tracking text logs into CSV time-series data suitable for T2-style visualization. It aggregates per-function execution time percentages over fixed one-second intervals.

### Important APIs, Types, and Functions
It reuses interval pairing helpers similar to `find-latency-spikes.py`: `assignStackDepths`, `getIntervalData`, `createCallstackSeries`, and `checkForTimestampAndGetRowSkip`. `getSessionFromFileName` extracts a session id from `optrack.<PID>.<session-id>-<type>.txt`. `parseIntervals` creates columns named with T2 metadata (`#units=%;section=Session ...;name=...`) and computes each function's percentage of interval time. `processFile` reads a log and writes CSV. `main` parallelizes one process per input file with optional `-j`.

### Control Flow
For each file, the script reads optional epoch timestamp, parses event/function/timestamp rows into intervals, then iterates from first to last interval. For each interval it accounts for functions that start/end inside, start inside and end later, end inside after starting earlier, or span the full interval. The resulting DataFrame is written next to the source with `.csv` extension.

### State and Persistence
Persistent output is one CSV per input plus hidden per-file error logs. Runtime state is per process, with globals for units and interval length. No combined output is produced.

### Dependencies and Integration Points
Depends on pandas, NumPy, multiprocessing, and text logs from the binary optack decoder. CSV output is intended for a separate T2 visualizer.

### Risks and Test Signals
`percentDuration` uses floor division (`//`) on floats, losing fractional percentages and under-reporting short functions. Interval boundary choices use inclusive comparisons and then advance `currentIntBeginUnits = currentIntEndUnits + 1`, which may skip or double-count boundary timestamps depending on input semantics. Log parsing assumes space-delimited function names. Tests should cover spanning intervals, exact-boundary begin/end times, empty logs, malformed stacks, session id parsing, and percentage sums.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/optrack/optrack_to_t2.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/optrack/wt_optrack_decode.py -->
## sources/storage-engines/wiredtiger/tools/optrack/wt_optrack_decode.py

### Purpose
`wt_optrack_decode.py` decodes binary WiredTiger operation tracking logs into text rows consumed by the other optack tools.

### Important APIs, Types, and Functions
`buildTranslationMap` reads `optrack-map` lines mapping numeric function IDs to names. `funcIDtoName` resolves IDs. `parseOneRecord` reads a 16-byte record with `struct.unpack('Qhhxxxx')`: timestamp, function id, and operation type. `validateHeader` reads version/thread type/tsc ratio and, for version 3+, epoch seconds. `getStringFromThreadType` maps thread type 0/1 to external/internal. `parseFile` validates the header, calculates nanosecond timestamps from the TSC ratio, writes an output text file, and counts records. `main` parses CLI options and runs files in parallel.

### Control Flow
The script loads the translation map before spawning workers. Each worker opens a binary log, validates its header, creates `<input>-<threadType>.txt`, writes the epoch timestamp line, then streams records until EOF and writes `opType functionName time` rows.

### State and Persistence
Persistent output is one decoded text file per binary input. The process-global `functionMap` is populated before forking. No checkpointing or partial-file cleanup exists.

### Dependencies and Integration Points
Depends on Python `struct`, multiprocessing, and the binary layout defined in WiredTiger `src/include/optrack.h`. Output feeds `find-latency-spikes.py` and `optrack_to_t2.py`.

### Risks and Test Signals
The unpack format uses native endian/alignment for record parsing (`Qhhxxxx`) while the header uses standard `=III`; portability depends on writer layout and host endianness. `getStringFromThreadType` returns undefined `unknown` for unexpected thread types. `validateHeader` has inconsistent return tuple lengths on failure branches, which can break unpacking. `currentLogVersion` is declared but not used for validation. Tests should cover v2/v3 headers, unknown function IDs, missing map file, truncated records, bad thread type, and multiple parallel inputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/optrack/wt_optrack_decode.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/__init__.py -->
## sources/storage-engines/wiredtiger/tools/py_common/__init__.py

### Purpose
`__init__.py` marks `py_common` as a Python package for shared WiredTiger tool helpers.

### Important APIs, Types, and Functions
The file exposes no package-level imports or functions; it only contains licensing text.

### Control Flow
There is no runtime control flow on import beyond executing the module body.

### State and Persistence
No state is stored or persisted.

### Dependencies and Integration Points
It enables imports such as `from py_common import binary_data` in decode tools including `btree_format.py`.

### Risks and Test Signals
Because it does not re-export modules, callers must import submodules explicitly. A simple import test from the tools root verifies package discoverability.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/binary_data.py -->
## sources/storage-engines/wiredtiger/tools/py_common/binary_data.py

### Purpose
`binary_data.py` provides primitive binary decoding helpers used by WiredTiger file-format tools: packed integer decoding, 4-bit array decoding, escaped-hex decoding, file-as-array access, little-endian reads, and display formatting.

### Important APIs, Types, and Functions
`get_bits`, `get_int`, and `unpack_int` implement WiredTiger variable-length integer decoding. `unpack_4b_array` decodes compact small-integer arrays used by disaggregated address cookies. `decode_esc_hex` reverses WiredTiger escaped hex output. `FileAsArray` adapts a file-like stream to indexed/sliced byte access for `unpack_int`. `BinaryFile` wraps a file object with saved-byte tracking and typed reads (`read_uint8/16/32/64`, `read_packed_uint64`, `read_long_length`, `seek`, `tell`, `saved_bytes`). `ts`, `txn`, and `d_and_h` format values.

### Control Flow
Packed integer decoding branches on marker byte ranges matching WiredTiger's signed/unsigned encoding. `BinaryFile.read_packed_uint64` constructs a `FileAsArray` over itself; byte indexing causes sequential reads and updates stream position. `saved_bytes` returns bytes accumulated since the previous call and clears the accumulator.

### State and Persistence
`BinaryFile` maintains in-memory stream position through the wrapped file and a `saved` bytearray for split/raw output. `FileAsArray` tracks logical position and slice offset. No disk state is written.

### Dependencies and Integration Points
Used by `btree_format.py` and likely other decode tools. It depends only on Python typing and file-like objects.

### Risks and Test Signals
`FileAsArray.__getitem__` rejects slices only when both `stop` and `step` are non-None; stricter slice validation may be intended. It assumes reads return at least one byte before indexing `[0]`, so truncated data can raise `IndexError`. `unpack_int` needs bounds checks for short buffers. Tests should cover every marker range, truncated packed integers, `read_long_length`, `saved_bytes` after seek, escaped hex errors, and 4-bit array incomplete/excess cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/binary_data.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/btree_format.py -->
## sources/storage-engines/wiredtiger/tools/py_common/btree_format.py

### Purpose
`btree_format.py` models and decodes WiredTiger on-disk B-tree/block formats for diagnostic tooling. It parses file headers, page headers, block headers, disaggregated-storage headers and address cookies, block-manager extent lists, row-page cells, timestamps, transaction ids, optional Snappy-compressed pages, CRC32C checksums, and BSON cell values.

### Important APIs, Types, and Functions
`BlockFileHeader`, `PageHeader`, `BlockHeader`, and `BlockDisaggHeader` parse fixed-format headers. `PageType`, `PageFlags`, `BlockFlags`, `BlockDisaggFlags`, `CellType`, and `DisaggAddrFlags` mirror WiredTiger enum/flag constants. `ExtentItem` parses block-manager extent records. `Cell.parse` decodes descriptor bytes, optional second descriptor/timestamps, run length/address values, key/value/overflow payload lengths, short cells, prefix cells, and disaggregated delta value flags. `DisaggAddr.parse` decodes packed page address cookies. `verify_block_checksum` validates CRC32C when the optional module is installed. `WTPage.parse` is the top-level page parser, while `print_page`, `print_cells`, `decode_rows`, and `decode_extlist` provide interpretation and display.

### Control Flow
`WTPage.parse` records disk position, reads the appropriate normal or disagg header bytes, validates unused fields/page type/size/checksum, optionally skips payload, reads or decompresses payload, then dispatches by page type. Block-manager pages decode extent lists until end marker or validation failure. Row internal/leaf pages decode `entries` cells and feed timestamp/key statistics. Printing later walks parsed structures and chooses raw bytes, BSON decode, or disaggregated address JSON according to options.

### State and Persistence
Decoded page state is held in a `WTPage` dataclass with headers, cells/extents, stats, success flag, and raw byte stream. `BinaryFile.saved` supports split raw-byte output. The module itself writes no files, but `Printer` and callers can emit decoded text/CSV stats.

### Dependencies and Integration Points
Depends on `py_common.binary_data`, `py_common.stats.PageStats`, `py_common.printer`, `py_common.snappy_util`, optional `crc32c`, and optional `bson`. It is designed for higher-level page/file decoders that provide a `BinaryFile` and `DecodeOptions`.

### Risks and Test Signals
Checksum zeroing assumes checksum bytes at offsets 32-35, which must match both normal and disagg layouts. `WTPage.print_page` uses `len(self.raw_bytes)` for overflow pages even though `BinaryFile` has no `__len__`, so that branch is suspect. Several cell types and overflow address details are marked TODO or treated unsupported; `ignore_unsupported=True` prevents hard failures in row decoding but may hide format drift. `Cell` size fields are annotated but not initialized in `__init__` unless corresponding timestamps exist, requiring `PageStats` to tolerate missing attributes. Tests should use binary fixtures for normal row leaf pages, compressed pages, checksum success/failure with and without `cont`, block-manager extent lists, disagg base/delta pages, timestamp windows, unsupported cell types, BSON decode, and truncated payloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/btree_format.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/decode_opts.py -->
## sources/storage-engines/wiredtiger/tools/py_common/decode_opts.py

### Purpose
`decode_opts.py` defines a shared dataclass for options used by WiredTiger binary/page decode tools.

### Important APIs, Types, and Functions
`DecodeOptions` groups input-routing flags (`dumpin`, `disagg_table`, `fragment`), decode behavior (`disagg`, `skip_data`, `cont`), output formatting (`split`, `bson`, `output`), seek/page limits (`offset`, `pages`), and disaggregated-storage filters/secrets (`keyfile`, `lsn`, `page_id`).

### Control Flow
There is no behavior beyond dataclass construction with defaults.

### State and Persistence
Instances are in-memory option carriers. `output` can hold a writable file-like object owned by the caller, but this module does not write to it directly.

### Dependencies and Integration Points
Depends on `dataclasses`, `typing.Any`, and `typing.Optional`. It is intended for command-line decode tools that need a consistent option object passed into page/file decoding code.

### Risks and Test Signals
The loose `Any` type for `output` keeps the dataclass flexible but defers validation to users. Tests should instantiate defaults, override every field, and verify downstream decoders interpret `pages=0` as unlimited and optional filters as `None`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/decode_opts.py -->
