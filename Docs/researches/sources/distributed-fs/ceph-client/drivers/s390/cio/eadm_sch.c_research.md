# sources/distributed-fs/ceph-client/drivers/s390/cio/eadm_sch.c

Purpose: registers and manages s390 Extended Asynchronous Data Mover subchannels and exposes `eadm_start_aob()` for SCM-style asynchronous operation blocks.

Important APIs/types/functions: exported `eadm_start_aob()` selects an idle ADM subchannel, programs an EADM ORB, and starts subchannel I/O. Core callbacks include `eadm_subchannel_probe()`, `eadm_subchannel_irq()`, `eadm_subchannel_timeout()`, `eadm_quiesce()`, and CSS driver methods for remove/shutdown/events. Global `eadm_list` and `list_lock` maintain a simple round-robin pool.

Control flow: probe allocates `struct eadm_private`, sets ISC, enables the subchannel, and adds it to the idle list. Starting an AOB marks a chosen private object busy, arms a timeout, fills EADM ORB fields, and calls `ssch()`. IRQ handling maps SCSW clear/error status to block status, stops the timeout, calls `scm_irq_handler()` with the AOB, returns the subchannel to idle, and completes quiesce waiters. Timeout clears the subchannel.

State and persistence behavior: per-subchannel state is `EADM_IDLE`, `EADM_BUSY`, or `EADM_NOT_OPER`, plus ORB, timer, optional completion, and list node. Hardware AOB execution state exists in the subchannel and is cleared during timeout/remove/shutdown. No persistent storage exists.

Dependencies and integration points: depends on CSS ADM subchannel matching, low-level `ssch()`/`csch()`, ISC registration, debug feature logging, EADM ORB format from `orb.h`, `asm/eadm.h`, and SCM completion callback `scm_irq_handler()`.

Risks and test signals: pool selection and state changes rely on lock ordering between `list_lock` and subchannel locks. Timeout and remove must not leave active AOBs orphaned. Tests should cover unavailable EADM facility, start with no idle subchannel, start failure marking not-operational, timeout clear, unsolicited IRQ, quiesce during busy I/O, and event recovery from `EADM_NOT_OPER`.
