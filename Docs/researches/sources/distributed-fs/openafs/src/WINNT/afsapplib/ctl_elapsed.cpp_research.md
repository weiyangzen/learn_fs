## sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_elapsed.cpp

Purpose: Implements a composite elapsed-time control with hours, minutes, seconds fields and a spinner that enforces min/max elapsed ranges.

Important APIs and functions: `RegisterElapsedClass` registers class `Elapsed`. `ElapsedProc` handles lifecycle, focus, enable, key forwarding, and `ELM_*` messages. `Elapsed_OnCreate` builds child edits/separators and initializes default range 0 to 24 hours. Range/time handlers get/set `SYSTEMTIME`. Edit helpers compute spinner ranges, update elapsed fields, enforce limits, and set formatted text.

Control flow: The placeholder control creates child edit/static controls in the parent, subclasses edits, and creates a spinner attached to the focused field. The hour spinner encodes days as `wDay * 24 + wHour`; minute/second spinners narrow their ranges when the current hour/minute is at the min or max boundary. Updates clamp values and notify the parent with `ELN_UPDATE`.

State and persistence: Global `aElapsed` table guarded by `csElapsed` stores HWNDs, range, current time, spinner handles, and callback suppression flags. No durable persistence.

Dependencies and integration points: Uses `ctl_spinner`, `dialog.h`, `resize.h`, `subclass.h`, locale time separator, and public macros in `ctl_elapsed.h`.

Risks: `fCanCallBack` is a `BOOL` but is incremented/decremented as a counter, which works only by convention. Parent color handler creates brushes without cleanup. Initial `timeNow` is zero and clamping depends on range setup. `ELN_CHANGE` is declared but implementation sends `ELN_UPDATE` on spinner/update flow.

Test signals: Default and custom min/max ranges, hour values over 24 via `wDay`, boundary minute/second clamping, focus/spinner migration, arrow/page key handling, disabled rendering, get/set time, and notification suppression during programmatic updates.
