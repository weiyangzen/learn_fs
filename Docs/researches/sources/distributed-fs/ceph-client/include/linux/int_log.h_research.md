<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/int_log.h -->
# sources/distributed-fs/ceph-client/include/linux/int_log.h

Purpose: Declares integer logarithm helpers for base-2 and base-10 style computations.

Important APIs/types/functions: Typically exposes `intlog2()`, `intlog10()`, or related fixed-point integer log helpers used by kernel subsystems needing approximate logarithms without floating point.

Control flow: Callers pass integer values and receive scaled integer logarithm results; no persistent control flow exists in the header.

State/persistence: Stateless math helpers.

Dependencies/integration: Used by drivers and core code that cannot use floating point in kernel context.

Risks: Scaling and zero-input behavior must be understood by callers; approximate integer math can overflow if inputs exceed expected range.

Test signals: Known-value log2/log10 vectors, zero/one boundaries, max integer inputs, and no-floating-point compile checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/int_log.h -->
