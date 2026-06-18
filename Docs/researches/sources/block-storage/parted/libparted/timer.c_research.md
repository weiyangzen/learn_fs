# File Research: sources/block-storage/parted/libparted/timer.c

## Purpose

`timer.c` implements libparted’s optional `PedTimer` progress reporting API, including nested timers for compound operations.

## Main Responsibilities

- Creates and destroys timers with caller-provided handlers.
- Creates nested timers that update a parent timer over a specified fraction of parent progress.
- Resets timers to the current time and zero progress.
- Updates progress fraction and predicts end time.
- Updates the current operation state name.
- Calls timer handlers whenever timer state changes.

## Important Functions

- `ped_timer_new()` allocates and initializes a timer.
- `ped_timer_new_nested()` creates a timer whose handler forwards progress to a parent.
- `ped_timer_destroy()` and `ped_timer_destroy_nested()` release timers and nested context.
- `ped_timer_touch()` refreshes `now`, clamps predicted end at least to `now`, and invokes the handler.
- `ped_timer_reset()` resets timing fields and progress.
- `ped_timer_update()` stores the new fraction and estimates `predicted_end`.
- `ped_timer_set_state_name()` updates the descriptive phase name.

## Behavior Details

Nested timers capture the parent’s current fraction as `start_frac` and multiply nested progress by `nest_frac`. Passing `NULL` timers is accepted by most operations and becomes a no-op, matching the optional nature of libparted progress reporting.

## Notable Edge Cases

`ped_timer_update()` computes predicted end only when `frac` is nonzero. There is no clamping of `frac` in the update path; only nested timer creation asserts that the nested fraction is between 0 and 1.
