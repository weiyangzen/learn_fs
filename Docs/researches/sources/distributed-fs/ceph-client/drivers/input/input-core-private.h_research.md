# sources/distributed-fs/ceph-client/drivers/input/input-core-private.h

`input-core-private.h` is a small internal header shared by input core support files. It forward-declares `struct input_dev` and declares `input_mt_release_slots()` plus `input_handle_event()`.

Its purpose is to avoid exposing internal core entry points through public input headers. `input.c` defines `input_handle_event()` as the lock-held event disposition/batching function, while `input-mt.c` defines `input_mt_release_slots()` to release active multitouch slots during inhibit/reset/disconnect paths. Both functions have locking assumptions that are meaningful only inside the input core: callers must hold `dev->event_lock` where required.

There is no state or persistence. Dependencies are minimal include guards and the internal build relationship between `input.c` and `input-mt.c`. Risks are accidental external use, stale prototypes after signature changes, and misuse without required locks. Test signals are normal input subsystem compilation and lockdep coverage during device inhibit/unregister paths that call `input_mt_release_slots()`.
