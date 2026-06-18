<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/recov_vollog.cc -->
# sources/distributed-fs/coda/coda-src/resolution/recov_vollog.cc

Purpose: manages per-volume recoverable resolution log storage, including RVM allocation, transient bitmap recovery, log growth, slot allocation, salvage, and wraparound reuse.

Important APIs/control flow: `operator new/delete` allocate in RVM. The constructor initializes admin limits, index blocks, recoverable bitmap, sequence counters, wraparound cursors, and transient stats. `ResetTransients` rebuilds VM bitmap and statistics after recovery. `Grow`, `FreeBlock`, `IndexToAddr`, and `Increase_Admin_Limit` manage block-indexed storage. `AllocRecord` reserves a VM slot and sequence number; `RecovPutRecord` marks it recoverable and grows backing storage if needed; `RecovFreeRecord` frees the recoverable bit while VM cleanup is deferred. `SalvageLog` compares recovered and shadow bitmaps. `AllocViaWrapAround` reclaims old vnode log entries when no free slot is available.

State/persistence: persistent state includes record blocks, `recov_inuse`, admin limit, sequence counter, and wraparound cursor. Transient state includes `vm_inuse`, `nused`, `max_seqno`, and `vmrstats`.

Dependencies/integration: called by `ops.cc` log spooling/truncation and volume recovery. Uses RVM transactions, vnode fetch/put, lockqueue, bitmap, and stats.

Risks/test signals: VM and recoverable bitmaps intentionally differ during transactions; misuse can leak or double-free slots. Wraparound avoids root vnode and skips modified vnodes but can fail under large active transactions. Test recovery rebuild, admin growth, empty block salvage, wraparound with child logs, and ENOSPC behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/recov_vollog.cc -->
