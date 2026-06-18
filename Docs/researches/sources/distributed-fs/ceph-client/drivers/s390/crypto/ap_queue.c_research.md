## sources/distributed-fs/ceph-client/drivers/s390/crypto/ap_queue.c

Purpose: implements AP queue devices, their request/reply state machine, queue sysfs attributes, secure-execution bind/associate controls, and AP instruction send/receive/reset handling.

Important APIs/types/functions: exported functions include `ap_sm_event()`, `ap_sm_event_loop()`, `ap_queue_create()`, `ap_queue_init_reply()`, `ap_queue_message()`, `ap_queue_usable()`, `ap_cancel_message()`, `ap_flush_queue()`, `ap_queue_prepare_remove()`, `ap_queue_remove()`, and `ap_queue_init_state()`. Internal state handlers cover reset, reset wait, IRQ enable wait, read, write, queue full, and SE association wait.

Control flow: messages enter `requestq` through `ap_queue_message()`. The state machine sends with NQAP, moves successful sends to `pendingq`, receives replies with DQAP, matches by PSMID, invokes the message receive callback in tasklet context, and reschedules through `ap_wait()`. Timeouts reset queues. Queue creation initializes lists/timer and optional SE sysfs groups. Remove flushes pending/requested messages, zaps the queue, and returns state to uninitiated.

State and persistence: per queue state includes config/checkstop flags, device state, queue counters, request/pending lists, reply buffer, timeout timer, AP state-machine state, RAPQ F bit, last error response, SE bind state, and association index. Counters persist until reset through sysfs.

Dependencies and integration: uses s390 AP instructions (`nqap`, `dqap`, `rapq`, `zapq`, `aqic`, `bapq`, `aapq`, `tapq`), AP bus polling/interrupt helpers, AP tracepoints, and Linux device/sysfs/timer APIs.

Risks and test signals: risks include callback execution in tasklet context, lost replies after cancellation, queue_count recovery when hardware reports empty, reset races, and SE bind/association state errors. Test normal send/reply, queue full, timeout reset, cancellation, flush on config/checkstop, IRQ enablement, poll-only mode, driver override sysfs, and SE bind/associate transitions.
