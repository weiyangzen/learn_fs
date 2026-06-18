# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khtracker.h

## Purpose

`khtracker.h` declares a pseudo-logarithmic duration editor used by NetIDMgr. It combines an edit control with a slider so users can choose lifetimes or renewal durations with coarser granularity for longer intervals.

## Important APIs, Types, and Functions

- `khui_tracker` stores original edit and tracker window procedures, slider and edit HWNDs, label layout positions, activation time, and current/min/max `time_t` values.
- `khui_tracker_install()` subclasses an edit control and attaches tracker behavior.
- `khui_tracker_reposition()` moves associated controls to match the edit control.
- `khui_tracker_initialize()` initializes structure fields before installation.
- `khui_tracker_refresh()` redraws or resynchronizes displayed state from current/min/max values.
- `khui_tracker_kill_controls()` tears down associated controls and subclassing.

## Control Flow

Callers initialize a `khui_tracker`, set valid `min`, `max`, and `current` durations, then install it on an edit control. The tracker subclasses the edit and creates/manages a slider. User typing or slider movement updates `current`, with tick mapping based on ranges documented in the header: minutes at short ranges, then 5/15/30-minute, hourly, 6-hour, and day increments for longer ranges. Reposition and refresh keep the edit/slider synchronized as the parent dialog moves or settings change.

## State and Persistence Behavior

The supplied `khui_tracker` structure must remain alive for the edit control lifetime. It owns runtime HWND/subclass state but does not persist duration settings; callers copy `current` into configuration or credential request fields when needed. `act_time` tracks interaction timing for UI behavior.

## Dependencies and Integration Points

The header depends on Win32 `WNDPROC`, `HWND`, `DWORD`, and standard `time_t`. It is included by `khuidefs.h` and is likely used by Kerberos lifetime/renewal controls in new-credential and configuration panels.

## Risks and Edge Cases

- Structure lifetime is caller-managed; stack allocation for a dialog that outlives the stack frame is unsafe.
- Subclass procedures must be restored by `khui_tracker_kill_controls()` to avoid calls into freed memory.
- Min/current/max must be valid before install; current outside range or min greater than max need rejection or clamping.
- Long durations above four days intentionally do not gain finer adjustment, which may surprise callers expecting exact seconds.

## Test Signals

- Install, move, refresh, and destroy trackers in a dialog while checking subclass restoration.
- Test tick/value mapping at every documented range boundary.
- Validate typed edits clamp or reject invalid durations.
- Persist a selected duration through a credential/config flow and verify expected seconds are stored.
