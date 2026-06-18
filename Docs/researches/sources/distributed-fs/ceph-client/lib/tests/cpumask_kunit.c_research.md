
# sources/distributed-fs/ceph-client/lib/tests/cpumask_kunit.c

## Purpose
`cpumask_kunit.c` validates basic CPU mask counting, first/last/next lookup helpers, iterator macros, binary mask-iterator variants, wrap iteration, and built-in possible/online/present CPU iterators.

## Important APIs, types, and functions
The file uses `cpumask_t`, `cpu_possible_mask`, `cpu_online_mask`, `cpu_present_mask`, `cpumask_weight()`, `cpumask_empty()`, `cpumask_full()`, `cpumask_first()`, `cpumask_first_zero()`, `cpumask_last()`, `cpumask_next()`, `cpumask_next_zero()`, `for_each_cpu*()` macros, `num_*_cpus()`, and `cpu_hotplug_disable()/enable()`.

## Control flow
Suite init clears `mask_empty` and fills `mask_all`. The tests compare helper results against `nr_cpu_ids` and `nr_cpumask_bits`, then use iterator-count macros to ensure iteration count equals `cpumask_weight()` or the result of a corresponding mask operation. Built-in online and present iterator tests run while CPU hotplug is disabled so the masks do not change mid-test.

## State and persistence
The file has three static masks: `mask_empty`, `mask_all`, and `mask_tmp`. They are initialized per KUnit test through the suite `.init` hook. CPU hotplug is temporarily disabled in one test and re-enabled before return.

## Dependencies and integration points
It depends on `<linux/cpu.h>`, `<linux/cpumask.h>`, and KUnit. It is built via `CONFIG_CPUMASK_KUNIT_TEST`.

## Risks and edge cases
The suite assumes CPU 0 is possible and that `nr_cpu_ids` aligns with possible CPU mask weight in the active test configuration. Any failure path inside the hotplug-disabled region must still re-enable hotplug; the current code has no early assert/return there.

## Test signals
KUnit messages print mask contents with `%*pbl`, making failures diagnosable by actual mask membership and iterator count.
