# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpic_timer.h

Purpose: declares MPIC global timer request, start/stop, remaining-time, and free APIs with stubs when timer support is disabled.

Important APIs/types/functions: `struct mpic_timer` stores client device pointer, cascade handle, timer number, and IRQ. Enabled builds declare `mpic_request_timer`, `mpic_start_timer`, `mpic_stop_timer`, `mpic_get_remain_time`, and `mpic_free_timer`; disabled builds return `NULL` or no-op.

Control flow: clients request a timer with an IRQ handler and period, start/stop it, query remaining time, and free it when done.

State and persistence: timer allocation and cascade state live in implementation and MPIC hardware registers. The handle persists while the timer is reserved.

Dependencies and integration points: depends on interrupt handlers and `time64_t`; integrates drivers with MPIC global timer hardware.

Risks: the disabled stubs are non-static function definitions in the header, so duplicate-definition risk depends on inclusion/build context. Clients must handle `NULL` request results.

Test signals: build with and without `CONFIG_MPIC_TIMER`, request timers, validate interrupt firing and remaining-time calculations, and confirm clients tolerate disabled support.
