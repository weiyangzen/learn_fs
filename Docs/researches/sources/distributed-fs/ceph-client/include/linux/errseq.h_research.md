# sources/distributed-fs/ceph-client/include/linux/errseq.h

Purpose: compact sequence/error tracking type used to report writeback and other delayed errors once per observer.

Important APIs/types/functions: `typedef u32 errseq_t`, `errseq_set()`, `errseq_check()`, and `errseq_check_and_advance()`.

Control flow: producers update an `errseq_t` when an error occurs; consumers snapshot a prior value and later check or advance their cursor to detect new errors without repeatedly reporting old ones.

State/persistence: the sequence word is stored in owning kernel objects such as superblocks/files and persists for their lifetime, not across reboot.

Dependencies/integration: writeback error reporting, file `fsync`/`close`, superblock error state.

Risks/test signals: risks are lost errors due to wrap/incorrect cursor updates, reporting stale errors to new observers, and data races if used outside intended atomic implementation. Test delayed writeback errors, multiple file descriptors with different cursors, repeated fsync, and error overwrite ordering.
