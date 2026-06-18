# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khalerts.h

## Purpose

`khalerts.h` defines NetIDMgr's alert object and the public API for displaying user-visible notifications, modal alerts, queued alerts, and alerts backed by the error-reporting subsystem. Alerts bridge plugin/core errors to UI windows or notification balloons and carry action command IDs for user responses.

## Important APIs, Types, and Functions

- `khui_alert` stores alert magic, severity, up to `KHUI_MAX_ALERT_COMMANDS` action IDs, title/message/suggestion strings, optional target point on Windows, flags, associated `kherr_context` and `kherr_event`, response command, refcount, and list links.
- Size limits are `KHUI_MAXCCH_TITLE` 256, `KHUI_MAXCCH_MESSAGE` 1024, and `KHUI_MAXCCH_SUGGESTION` 1024 wide characters.
- `khui_alert_create_empty()` and `khui_alert_create_simple()` allocate held alert objects.
- Setter APIs manage owned strings and validation: `khui_alert_set_title`, `khui_alert_set_message`, `khui_alert_set_suggestion`, `khui_alert_set_severity`, and `khui_alert_set_flags`.
- Command APIs are `khui_alert_clear_commands()` and `khui_alert_add_command()`.
- Display APIs are `khui_alert_show()`, `khui_alert_show_modal()`, `khui_alert_queue()`, and `khui_alert_show_simple()`.
- Lifetime and synchronization APIs are `khui_alert_hold()`, `khui_alert_release()`, `khui_alert_lock()`, and `khui_alert_unlock()`.
- Flag groups distinguish internal ownership (`FREE_STRUCT`, `FREE_TITLE`, `FREE_MESSAGE`, `FREE_SUGGEST`), caller-settable behavior (`DEFACTION`, `REQUEST_WINDOW`, `REQUEST_BALLOON`), targeting/error validity, display state, and modal state.

## Control Flow

Callers construct an alert, set severity and localized text, optionally add action IDs, optionally associate `kherr` context or event data, then choose immediate show, modal show, or queue. `khui_alert_show()` chooses a balloon when NetIDMgr is minimized/backgrounded or when a balloon is requested; otherwise it shows an alert window. Long text, suggestions, or custom commands force a placeholder balloon that opens the full alert window unless `KHUI_ALERT_FLAG_DEFACTION` is set. Modal alerts always use a window and must run on the UI thread. Queued alerts are stored until the user activates pending-alert UI.

## State and Persistence Behavior

Alert objects are reference-counted and also linked into a global alert list managed by the UI library. Text ownership is controlled by internal flags, not by direct field mutation. The `response` field is set after a user chooses a command. The alert lock is documented as global, so locking one alert serializes access to all alerts. Alert state is transient UI state; persistence is limited to any externally retained `kherr_context` or application logs that describe the same event.

## Dependencies and Integration Points

The header depends on `kherr.h` for severity, contexts, and events; `khlist.h` for list fields; `khactiondef.h` for command IDs used as buttons; Windows `POINT` for alert targeting; and KMQ alert message types in `khmsgtypes.h` (`KMSG_ALERT_SHOW`, `QUEUE`, `SHOW_QUEUED`, `CHECK_QUEUE`, `SHOW_MODAL`). `khuidefs.h` includes this header for plugins and UI consumers.

## Risks and Edge Cases

- Direct field mutation can bypass allocation flags and global synchronization, leading to leaks, double frees, or UI races.
- Only four custom command buttons are supported; extra commands should be rejected or ignored by implementation.
- Balloon title/message truncation is part of the contract; callers should avoid assuming all text appears in the balloon path.
- `KHUI_ALERT_FLAG_DEFACTION` is invalid without commands or with `REQUEST_WINDOW`; callers need to validate these combinations.
- Error context/event pointers are not self-owned by the header. Implementations must hold/release them correctly to avoid dangling references.

## Test Signals

- Create simple and empty alerts, set each string at boundary sizes, and confirm setters enforce wide-character limits.
- Show window, balloon, modal, and queued paths with and without suggestions and commands.
- Verify command ordering and default response assignment.
- Exercise error-context and error-event display integration with `kherr_evaluate_event()`.
- Run concurrent hold/release and lock/unlock tests to catch refcount and global-lock regressions.
