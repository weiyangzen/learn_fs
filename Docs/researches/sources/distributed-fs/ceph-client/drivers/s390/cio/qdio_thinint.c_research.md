# sources/distributed-fs/ceph-client/drivers/s390/cio/qdio_thinint.c

Purpose: implements QDIO adapter thin interrupt registration, device-state-change indicators, and delivery to QDIO polling callbacks.

Important APIs/types/functions: `qdio_thinint_init()` allocates indicators and registers `tiqdio_airq`; `qdio_thinint_exit()` unregisters it. `qdio_establish_thinint()` assigns a DSCI, programs subchannel indicators, and adds the IRQ to `tiq_list`; `qdio_shutdown_thinint()` removes and resets it. `test_nonshared_ind()` helps the IRQ restart path avoid missed interrupts.

Control flow: up to 63 subchannels get non-shared indicators, while later users share one indicator. The adapter interrupt handler clears the shared indicator once, walks the RCU list, checks each DSCI, clears non-shared indicators with `xchg()`, calls `qdio_deliver_irq()`, records interrupt time, and updates stats. CHSC SADC programs or clears summary/subchannel indicator addresses.

State and persistence behavior: state is in `q_indicators` counts and indicator words, the RCU `tiq_list`, global `last_ai_time`, and per-IRQ `dsci` pointer/list entry. Hardware indicator registration is runtime-only and reset on shutdown.

Dependencies and integration points: depends on adapter interrupt infrastructure, ISC `QDIO_AIRQ_ISC`, CHSC SADC, RCU list semantics, QDIO IRQ structures, and CSS AI capability decisions.

Risks and test signals: shared indicator fan-out can cause extra scans, while non-shared indicators must be cleared atomically to avoid lost work. Tests should cover non-thin fallback, first 63 versus shared indicators, establish SADC failure cleanup, shutdown RCU synchronization, adapter interrupt delivery/discard when polling is disabled, and `qdio_start_irq()` rescan behavior with a set non-shared indicator.
