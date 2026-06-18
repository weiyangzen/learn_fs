# File Research: sources/cow-pools/bcachefs-tools/include/linux/timer.h

Declares a minimal `timer_list` with expiration, callback, and pending state. Provides setup, stack setup/destroy stubs, pending check, `add_timer()`, and prototypes for delete/mod/flush functions.

The actual timer queue behavior is implemented outside this header.
