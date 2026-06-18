# sources/distributed-fs/ceph-client/tools/thermal/tmon/tui.c

## Purpose
`tui.c` implements TMON's ncurses interface. It creates and refreshes windows for the title/status bars, thermal zones, cooling devices, sampled thermal data, controller state, and a tunables dialog. It also runs the keyboard event loop that lets users toggle the dialog, set cooling-device states, adjust target temperature, or quit.

## Important APIs, Types, and Functions
Global/static UI objects include `WINDOW *` windows, `PANEL *` panels, terminal dimensions, `status_bar_slots`, and `tui_disabled`. Public functions are `initialize_curses()`, `setup_windows()`, `resize_handler()`, `close_windows()`, `disable_tui()`, drawing functions (`show_title_bar()`, `show_sensors_w()`, `show_cooling_device()`, `show_data_w()`, `show_control_w()`, `show_dialogue()`), `write_status_bar()`, and `handle_tui_events()`. Internal helpers draw bars, convert trip types to display characters, handle dialog choices/values, and calculate dialog rows.

## Control Flow
`setup_windows()` sizes subwindows based on current terminal dimensions and `ptdata` counts, then wraps cooling/dialog windows in panels. The main loop in `tmon.c` periodically calls drawing functions after sampling. The input thread reads from `cooling_device_window`, locks `input_lock`, handles dialog interactions when active, toggles panels on TAB, and sets `tmon_exit` on `q`/`Q`. Dialog value entry writes a cooling device `cur_state` through `sysfs_set_ulong()` or updates `p_param.t_target` after range validation.

## State and Persistence
UI state is process-local. External effects occur when dialog writes to sysfs cooling-device state. `dialogue_on` and `top` control whether periodic redraws update data windows or leave the dialog visible. The resize handler destroys and recreates all windows.

## Dependencies and Integration Points
The file depends on ncurses, panel library, pthreads, signals, and the globals in `tmon.h`. It reads `ptdata`, `trec`, `p_param`, `target_thermal_zone`, and `ctrl_cdev`; it calls sysfs write/read helpers and controller display state.

## Risks and Edge Cases
Many coordinates are derived from thermal instance IDs rather than compact indices, so large or sparse instance IDs can push columns off-screen. The file has defensive checks for disabled TUI and missing windows, but some functions assume windows exist after initialization. The input mutex protects event handling, yet the sampling/display loop reads the same globals without broad locking, so visual races are possible. Dialog choice labels are limited to alphabetic offsets and become awkward if cooling devices exceed `A-Z` practical bounds. `close_panel()` and `close_window()` set only local pointer copies to NULL, leaving stale static pointers until overwritten.

## Test Signals
Run TMON in terminals of varying sizes, with zero/many cooling devices, long names, sparse IDs, and repeated resize events. Verify TAB dialog navigation, target-temperature validation, cooling-state writes, quit handling, and daemon mode where TUI functions should return early.
