# sources/distributed-fs/ceph-client/mm/kmsan/report.c

## Purpose
`report.c` formats and emits KMSAN bug reports. It converts origins and bug reasons into human-readable stacks, local-variable descriptions, copy-to-user/USB leak types, tainting, and optional panic behavior.

## Important APIs, Types, And Functions
`panic_on_kmsan` is an exported module parameter under `kmsan.panic`. `kmsan_report_lock` serializes reports and protects `report_local_descr`. `get_stack_skipnr()` removes internal `__msan_*` and `kmsan_*` frames from displayed stacks. `pretty_descr()` extracts readable local variable names from Clang-provided descriptions. `kmsan_print_origin()` prints alloca origins, chained store origins, and generic creation stacks. `kmsan_report()` emits the full report.

## Control Flow
`kmsan_report()` exits if KMSAN is disabled, already in runtime, suppressed for the current task, or given a zero origin. Otherwise it enters runtime, saves user-access state, locks report output, chooses a bug type from reason plus the origin UAF bit, prints the current access stack, prints origin details, prints byte-range and user-address context when available, taints the kernel, optionally panics, then restores state and leaves runtime. `kmsan_print_origin()` follows origin-chain records until it reaches an alloca or generic origin.

## State And Persistence
The file persists the panic setting and report serialization buffer. It also taints the kernel with `TAINT_BAD_PAGE` for each report. Origin data itself remains in stack depot and is only read here.

## Dependencies And Integration Points
It depends on stack depot, stacktrace, printk, module parameters, console output, user access helpers, KMSAN origin encodings from `kmsan.h`, and report callers in `core.c`, `hooks.c`, and `instrumentation.c`. KUnit tests observe its output through the printk console tracepoint.

## Risks
Report code runs in sensitive contexts and must avoid recursion. Holding a raw spinlock while printing serializes output but increases latency. Local description parsing depends on Clang's current string shape. `panic_on_kmsan` is intentionally dangerous and must be controlled for tests.

## Test Signals
KUnit report matching validates bug-type strings such as `uninit-value`, `use-after-free`, `kernel-infoleak`, and USB leak variants indirectly through expected headers. Long origin-chain and stackdepot tests validate origin printing does not create new KMSAN reports.
