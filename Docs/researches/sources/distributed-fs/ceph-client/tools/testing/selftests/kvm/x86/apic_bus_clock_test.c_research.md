# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/apic_bus_clock_test.c

Purpose: Verifies KVM's APIC timer bus-frequency emulation when userspace configures `KVM_CAP_X86_APIC_BUS_CYCLES_NS`. It programs the APIC timer with a long initial count, waits for a configurable interval, and checks that the current count drops by the amount implied by the configured APIC bus rate and TDCR divide value.

Important APIs/types/functions: `tdcrs[]` enumerates legal APIC divide configurations; `apic_enable()`, `apic_read_reg()`, and `apic_write_reg()` abstract xAPIC versus x2APIC access; `apic_guest_code()` performs the in-guest timing check; `run_apic_bus_clock_test()` creates/configures the VM; `test_apic_bus_clock()` validates each TDCR case. It uses `KVM_CAP_X86_APIC_BUS_CYCLES_NS`, APIC `TMICT`, `TMCCT`, `TDCR`, and selftest delay helpers.

Control flow: Command-line options select APIC frequency, wait duration, and APIC mode. The host enables the VM capability before running the vCPU. Guest code enables the APIC, iterates over the TDCR table, arms a large-count periodic timer, delays, reads the current count, computes expected decrement, and allows a tolerance around the expected elapsed bus cycles.

State and persistence behavior: State is fully in-memory: configured bus cycles per nanosecond, APIC mode, APIC timer registers, and per-case timing observations. No VM state is saved across process runs.

Dependencies and integration points: Integrates with KVM local APIC emulation, xAPIC MMIO or x2APIC MSR access, the selftest APIC helpers, and host support for the APIC bus clock capability. Timing accuracy depends on guest delay calibration and host scheduling.

Risks and maintenance notes: The 1% tolerance is deliberate but still sensitive to noisy hosts, coarse delays, or unexpected APIC timer implementation details. Changes in APIC divide encoding, x2APIC enablement, or capability units would require corresponding updates.

Test signals: Passing means all supported APIC divide settings decrement `TMCCT` consistently with the configured bus frequency. Failures indicate incorrect APIC timer scaling, xAPIC/x2APIC register access issues, or capability setup regressions.
