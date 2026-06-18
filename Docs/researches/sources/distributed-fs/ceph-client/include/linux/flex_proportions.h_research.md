# sources/distributed-fs/ceph-client/include/linux/flex_proportions.h

## Purpose
This header defines flexible aging-period proportion counters. It lets subsystems track a local event class as a fraction of a global event stream while periods advance and old counts decay.

## APIs, types, and control flow
`struct fprop_global` owns a per-cpu global event counter, current period, and sequence counter for period transitions. `struct fprop_local_percpu` owns a local per-cpu event counter, last-updated period, and raw spinlock protecting period/numerator updates. Initialization and teardown are split for global and local counters. `fprop_new_period()` advances aging periods. `__fprop_add_percpu()` and `_max()` add local/global events, with the max variant limiting by `FPROP_FRAC_SHIFT` precision. `fprop_fraction_percpu()` returns numerator/denominator. `fprop_inc_percpu()` wraps add-one with IRQ disable/restore.

## State and dependencies
State persists in percpu counters and period fields. Dependencies are percpu counters, spinlocks, seqcount, and GFP allocation.

## Integration, risks, and tests
Used by writeback and resource-balancing code that needs low-overhead approximate proportions. Risks include missing local destruction, period races if sequence handling is wrong in implementation, IRQ-context misuse outside the wrapper, and overflow/precision limits documented by `FPROP_FRAC_SHIFT`. Tests should cover init failure cleanup, period advancement, fraction monotonicity/decay, max-fraction limiting, concurrent increments, and teardown after active periods.
