# sources/distributed-fs/ceph-client/net/netfilter/xt_LED.c

Purpose: `LED` target triggers named LED subsystem triggers when packets match.

Important APIs/types/functions: `struct xt_led_info_internal`, `led_tg()`, `led_timeout_callback()`, `led_trigger_lookup()`, `led_tg_check()`, and `led_tg_destroy()`.

Control flow: check validates trigger id, reuses an existing trigger by incrementing refcount or allocates/registers a new LED trigger and timer. Runtime turns LED on, optionally blink-one-shots if always-blink and timer pending, updates timer for positive delay, or turns off immediately for zero delay. Destroy decrements refcount and unregisters/frees on last user.

State and persistence: global trigger list, LED trigger registrations, timers, and refcounts. Dependencies include x_tables, LED trigger core, timers, mutexes, and hidden kernel pointers. Risks: duplicate trigger names, timer callback after unregister, shared refcount correctness, and delay semantics. Test signals: shared ids, always-blink, zero/positive/negative delay, invalid id, timer shutdown, and IPv4/IPv6 registration.
