# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arch_timer.c

Purpose: this host-side KVM arch-timer runner creates a multi-vCPU VM and validates timer interrupt delivery, timing margins, and optional vCPU migration stress. Architecture-specific guest logic is provided by the paired timer implementation files and common `timer_test.h`.

Important APIs and functions: global `test_args`, `vcpus`, and `vcpu_shared_data` are shared with guest/timer helpers. Host functions include `test_vcpu_run()`, `test_get_pcpu()`, `test_migrate_vcpu()`, `test_vcpu_migration()`, `test_run()`, `test_print_help()`, `parse_args()`, and `main()`.

Control flow: `main()` parses timer period, vCPU count, iteration count, migration frequency, counter offset, and error margin. It requires at least two CPUs when migration is requested, calls `test_vm_create()`, runs all vCPU threads, and cleans up. Each vCPU thread performs a single `vcpu_run()` and treats any guest exit as completion, then decodes ucalls. A migration thread periodically pins active vCPU threads to random online pCPUs until all are done.

State and persistence: state is process-local: pthread IDs, a bitmap of completed vCPUs protected by a mutex, global test arguments, and per-vCPU shared data synchronized from the guest on failure. No durable state is stored.

Dependencies and integration points: depends on pthreads, CPU affinity helpers, bitmap helpers, KVM lib helpers, timer common code, and architecture-specific `test_vm_create()` / `test_vm_cleanup()`. On arm64, this integrates with VGIC and timer IRQ setup in `arm64/arch_timer.c`.

Risks: timer tests are timing-sensitive and can fail on slow or overloaded systems unless error margins are tuned. Migration relies on CPU affinity and can race with vCPU thread completion, so `ESRCH` is tolerated. Any unexpected guest exit is a failure.

Test signals: per-vCPU `PASS(vCPU-n)` messages, guest assertion reports containing stage/iteration, timeout/margin failures, and successful process exit are the main signals.
