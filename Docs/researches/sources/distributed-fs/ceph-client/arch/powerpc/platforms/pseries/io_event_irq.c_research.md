# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/io_event_irq.c

Purpose: Implements pseries RTAS IO event interrupt handling and exposes an atomic notifier chain for device drivers that consume IO event sections.

Important APIs/types/functions: Exports `ATOMIC_NOTIFIER_HEAD(pseries_ioei_notifier_list)`, stores `ioei_check_exception_token`, uses RTAS buffer `ioei_rtas_buf`, and defines `ioei_find_event()`, `ioei_interrupt()`, and `ioei_init()`.

Control flow: Init resolves RTAS `check-exception`, finds `/event-sources/ibm,io-events`, and requests all event-source IRQs using `request_event_sources_irqs()`. On interrupt, the handler loops calling `check-exception` for the IRQ hardware number and RTAS IO events until RTAS returns nonzero. Each returned error log is validated as IO type, the IO event section is extracted, and the notifier chain is called so clients can claim or ignore the event.

State and persistence: Persistent state includes the notifier chain, RTAS token, cacheline-aligned shared RTAS buffer, and registered IRQ handlers. Event ownership is external to this file and determined by notifier clients.

Dependencies and integration points: Depends on RTAS error-log parsing, event-source IRQ helper, OF event-source node, IRQ hardware number translation, and `asm/io_event_irq.h` clients.

Risks: A single global RTAS buffer is used in interrupt context; concurrent IO event IRQs could contend if firmware routes more than one. Events must be processed sequentially and in returned order. Missing or malformed IO event sections are warned once and skipped. Notifier clients must be atomic-context safe.

Test signals: IO event interrupt initialization, RTAS check-exception loops with multiple events, notifier client registration/claiming, malformed event-log warning paths, interrupt storm handling, and absence of IO event node/token are useful.

Source read size: 161 lines, 5017 bytes.
