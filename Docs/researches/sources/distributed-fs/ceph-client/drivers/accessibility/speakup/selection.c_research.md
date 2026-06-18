# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/selection.c

## Purpose
Asynchronous bridge from Speakup cut/paste review commands to kernel console selection and paste APIs.

## Important APIs, Types, And Functions
Globals `spk_xs`, `spk_ys`, `spk_xe`, `spk_ye`, and `spk_sel_cons` store mark/cut coordinates. Public APIs are `speakup_set_selection()`, `speakup_cancel_selection()`, `speakup_paste_selection()`, and `speakup_cancel_paste()`. `struct speakup_selection_work` carries work, tty, and `tiocl_selection`.

## Control Flow
Set-selection grabs a tty kref, claims the single work item with `cmpxchg`, fills 1-based coordinates, and schedules work. The worker verifies the foreground console, clears prior selection under `console_lock()`, calls `set_selection_kernel()`, then drops the tty reference. Paste schedules a similar worker calling `paste_selection()`.

## State And Persistence Behavior
Only one set or paste job can be pending per static work item. TTY refs are held until work or cancellation completes. The actual selected text belongs to console selection state.

## Dependencies, Integration Points, Risks, And Test Signals
Depends on tty refs, workqueues, memory barriers, foreground console state, and selection APIs. Risks are foreground-console races and kref leaks if cancellation/claiming is wrong. Test concurrent requests, changed consoles, cancellation, expected `-EBUSY`, and kref balance.
