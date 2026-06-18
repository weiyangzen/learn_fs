<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat.h

## Purpose

`kvm-stat.h` defines the shared types, callbacks, and arch hook declarations used by `perf kvm stat`.

## Important APIs, Types, and Functions

Key structures are `event_key`, `kvm_info`, `kvm_event_stats`, `kvm_event`, `child_event_ops`, `kvm_events_ops`, `exit_reasons_table`, `perf_kvm_stat`, and `kvm_reg_events_ops`. It declares common exit helpers, all per-architecture setup/ISA/table functions, tracepoint accessors, skip-event accessors, and default-event hooks under `HAVE_LIBTRACEEVENT`. It also provides refcounted `kvm_info` inline helpers and `STRDUP_FAIL_EXIT`.

## Control Flow

Generic KVM stat code uses `kvm_events_ops` callbacks to identify begin/end events, optional child events, and key decoding. Architecture code fills registered event ops and exit-reason tables. Refcount helpers increment/decrement/free `kvm_info` instances.

## State and Persistence Behavior

The header defines runtime aggregation state: per-event total and per-vCPU stats, histogram entry, total time/count/lost/duration counters, pid filters, display options, and live/report mode flags. State is in memory for one perf kvm stat run.

## Dependencies and Integration Points

It includes perf tool, sort, stat, symbol, record, errno, zalloc, and refcount support. It is shared by generic command code and all `kvm-stat-arch` modules.

## Risks and Edge Cases

Callback contracts must remain synchronized across all architectures. `STRDUP_FAIL_EXIT` assumes a local `ret` variable and `EXIT` label. Refcounting requires callers to use `kvm_info__zput()` to avoid leaks and dangling pointers.

## Test Signals

Compile tests should cover builds with and without `HAVE_LIBTRACEEVENT`. Runtime tests should cover event registration, child event decoding, refcount lifetime, per-vCPU resizing, pid-list filtering, and default-event argument mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat.h -->
