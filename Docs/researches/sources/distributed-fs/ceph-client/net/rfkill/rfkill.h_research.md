# sources/distributed-fs/ceph-client/net/rfkill/rfkill.h

## Purpose
Provides the private interface between rfkill core and optional input support.

## Important APIs, Types, and Functions
Declares global rfkill operations `rfkill_switch_all()`, `rfkill_epo()`, `rfkill_restore_states()`, `rfkill_remove_epo_lock()`, `rfkill_is_epo_lock_active()`, and `rfkill_get_global_sw_state()`, plus input lifecycle hooks `rfkill_handler_init()` and `rfkill_handler_exit()`.

## Control Flow
No executable code. The declarations let `core.c` initialize/exit input support and let `input.c` invoke global state changes without exposing these internals as public rfkill API.

## State and Persistence
No state is defined in this header.

## Dependencies and Integration
Depends on public rfkill types such as `enum rfkill_type` being available through included kernel headers in users. It is local to `net/rfkill`.

## Risks and Test Signals
Risks are compile-time only: mismatched prototypes or use when `CONFIG_RFKILL_INPUT` conditional compilation changes. Test signals are successful builds with input enabled and disabled.
