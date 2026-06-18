# sources/distributed-fs/orangefs/src/apps/karma/karma.c

## Purpose
`karma.c` is the GTK application entry point for the Karma OrangeFS monitoring GUI. It creates the main window, menu, notebook pages, message frame, initializes communication with OrangeFS, schedules periodic status and traffic refreshes, and starts the GTK event loop.

## Important APIs, Types, and Functions
The file defines global `GtkWidget *main_window` and `gui_set_title()`. `get_notebook_pages()` creates Status, Details, and Traffic pages through `gui_status_setup()`, `gui_details_setup()`, and `gui_traffic_setup()`. `main()` performs GTK initialization, rejects command-line arguments, creates the window, wires delete/destroy callbacks, initializes menus and communication, builds layout, shows widgets, primes the two timer callbacks, and registers `gtk_timeout_add()` timers.

`status_timer_callback()` retrieves server stats with `gui_comm_stats_retrieve()`, prepares graph data with `gui_status_data_prepare()`, updates six status graphs, and updates the details table. `traffic_timer_callback()` retrieves raw traffic data, lazily allocates/reallocates `gui_traffic_graph_data`, prepares graph units/rates, and updates the traffic graph.

## Control Flow
Startup order matters: menus are created, `gui_comm_setup()` initializes PVFS and filesystem state, notebook pages are constructed, the message frame is created, widgets are shown, then timers are run once manually. A timer that fails on its initial run is not scheduled. Later timer failures return `FALSE`, disabling that timer and appending a message.

## State and Persistence
The app is single-process GTK state. Persistent state is not written by this file. Static traffic graph allocation persists for the process lifetime and is resized when server count changes. Server stats and active filesystem state live in `comm.c`.

## Dependencies and Integration Points
`karma.c` is the coordinator for the Karma modules declared in `karma.h`. It depends on GTK2 and OrangeFS management data indirectly through `comm.c` and `prep.c`. It also relies on `gui_message_new()` for user-visible error reporting.

## Risks and Edge Cases
Because `gui_comm_setup()` is called before `gui_message_setup()`, early messages from communication setup can be dropped by `messages.c`. Timer callbacks do not free stat or graph data because those buffers are owned/cached by other modules, but allocation failures in traffic graph setup are unchecked. If server count changes, traffic graph storage is reallocated but `traffic_graph->svr_ct` is not updated in the resize branch, leaving stale count metadata. `gtk_timeout_add()` is deprecated GTK2 API. The app exits on any command-line argument, so there is no runtime configurability.

## Test Signals
Launch with no args and with an unexpected arg. Validate startup against a working PVFS config and against failing `gui_comm_setup()`. Simulate status/traffic retrieval failures and verify timers disable independently. Switch filesystems with different server counts and watch traffic graph reallocation. UI smoke tests should verify all three notebook pages render before timer data arrives.
