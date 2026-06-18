# Research: subset-b-006843

Grouped research for the KVM selftest source files in `subset-b-006843`. Each section preserves the source path and is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/kvm_create_max_vcpus.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/kvm_create_max_vcpus.c

## Purpose
This selftest validates KVM's advertised vCPU capacity limits. It reads `KVM_CAP_MAX_VCPUS` and `KVM_CAP_MAX_VCPU_ID`, raises the process file descriptor limit, then attempts to create the maximum number of vCPUs with dense IDs and, when supported, with high sparse IDs.

## Important APIs, Types, and Functions
`main()` is the test driver. `test_vcpu_creation()` creates a barebones VM with `vm_create_barebones()`, calls `__vm_vcpu_add()` for each ID, and frees the VM. It depends on `kvm_check_cap()`, `kvm_set_files_rlimit()`, `TEST_ASSERT()`, and KVM capability constants from `linux/kvm.h`.

## Control Flow
The program prints both capabilities, falls back to `KVM_CAP_MAX_VCPUS` when old kernels report no `KVM_CAP_MAX_VCPU_ID`, asserts max ID is at least max count, then creates `kvm_max_vcpus` vCPUs starting at ID 0. If IDs allow sparse placement, it repeats with IDs ending at the maximum supported vCPU ID.

## State, Dependencies, and Integration
State is only transient VM/vCPU file descriptors and the process `RLIMIT_NOFILE`. It integrates tightly with the shared `kvm_util.c` VM lifecycle and intentionally uses low-level `__vm_vcpu_add()` because successful creation is the assertion.

## Risks and Test Signals
The main risk is environmental: low file descriptor limits or host/KVM capability inconsistencies. Passing output is successful process exit after both creation passes; failures are capability assertion failures or `KVM_CREATE_VCPU` ioctl errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/kvm_create_max_vcpus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/kvm_page_table_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/kvm_page_table_test.c

## Purpose
This test stresses KVM page-table creation, dirty-logging updates, huge-page splitting, and mapping coalescing across guest modes and backing sources. It is aimed at bugs such as stale TLB entries after block mappings are split and later coalesced.

## Important APIs, Types, and Functions
`enum test_stage` defines the guest access phases. `struct test_args` is shared with the guest and stores VM, page sizes, page counts, memory backing, and vCPU pointers. `guest_code()` performs read/write patterns. `vcpu_worker()` runs a vCPU per host thread. `pre_init_before_test()` creates the VM, adds the test memslot, maps GVA to GPA, initializes semaphores, and exports globals. `run_test()` sequences all stages and toggles `KVM_MEM_LOG_DIRTY_PAGES`.

## Control Flow
`main()` parses `-p`, `-m`, `-b`, `-v`, and `-s`, appends supported guest modes, and invokes `run_test()` for each enabled mode. `run_test()` starts vCPU threads at `KVM_BEFORE_MAPPINGS`, then drives `KVM_CREATE_MAPPINGS`, enables dirty logging and drives `KVM_UPDATE_MAPPINGS`, disables dirty logging and drives `KVM_ADJUST_MAPPINGS`, then tears down all threads and semaphores.

## State, Dependencies, and Integration
Host and guest coordinate through shared `guest_test_stage`, exported `test_args`, and two POSIX semaphores. It depends on `guest_modes`, `kvm_util`, `processor`, backing-source helpers, ucall syncs, pthreads, and KVM memslot flag updates.

## Risks and Test Signals
The test is sensitive to memory size alignment, guest physical placement, hugepage availability, vCPU count, and host backing type. Success is each vCPU reporting `UCALL_SYNC` for every stage without unexpected exits; timing logs are diagnostic rather than pass criteria.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/kvm_page_table_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/gic.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/gic.c

## Purpose
This is the architecture-neutral guest-facing ARM GIC wrapper used by arm64 selftests. It hides the concrete GIC implementation behind `struct gic_common_ops` and currently selects the GICv3 implementation.

## Important APIs, Types, and Functions
`gic_init()` initializes distributor state once and CPU interface state per vCPU. Public helpers include interrupt enable/disable, acknowledge/EOI/DIR, priority and priority mask operations, pending/active state manipulation, configuration, and group selection. `gic_dist_init()` serializes global initialization with `spin_lock()`.

## Control Flow
On first `gic_init()`, the calling vCPU acquires `gic_lock`, chooses `gicv3_ops` for `GIC_V3`, runs distributor initialization, publishes `gic_common_ops`, executes `dsb(sy)`, and releases the lock. Every caller then initializes its CPU interface.

## State, Dependencies, and Integration
Persistent guest state is the static `gic_common_ops` pointer and `gic_lock`. The code depends on `gic_private.h`, `gic_v3.c`, processor barriers, and the arm64 spinlock implementation. It integrates with guest interrupt tests that use generic `gic_*` APIs.

## Risks and Test Signals
Only GICv3 is implemented, so unsupported types assert. Correctness depends on one-time distributor initialization and memory ordering before other vCPUs call through the ops table. Tests signal issues through `GUEST_ASSERT()` or unexpected interrupt behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/gic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/gic_private.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/gic_private.h

## Purpose
This private header defines the internal operation table used by the arm64 GIC guest library. It is shared only by GIC wrapper and implementation files.

## Important APIs, Types, and Functions
`struct gic_common_ops` contains function pointers for distributor/CPU initialization, IRQ enable/disable, IAR/EOIR/DIR access, EOI split mode, priority controls, active and pending state, interrupt configuration, and group assignment. It declares `extern const struct gic_common_ops gicv3_ops`.

## Control Flow
There is no executable control flow. The table shape determines which callbacks `gic.c` can dispatch after `gic_init()` selects an implementation.

## State, Dependencies, and Integration
This header creates a contract between generic `gic.c` and `gic_v3.c`. It deliberately avoids public exposure of implementation-specific register details; public callers use `gic.h` while internal files exchange this vtable.

## Risks and Test Signals
Adding a public GIC operation requires updating this table and every implementation. Mismatched signatures or missing `gicv3_ops` entries fail at compile time, while semantically wrong entries show up as guest interrupt test failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/gic_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/gic_v3.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/gic_v3.c

## Purpose
This file implements guest-side GICv3 register programming for arm64 selftests, including distributor, redistributor, CPU interface, interrupt state controls, and LPIs for ITS-backed tests.

## Important APIs, Types, and Functions
Key internals include `struct gicv3_data`, `gicv3_gicd_wait_for_rwp()`, `gicv3_gicr_wait_for_rwp()`, `get_intid_range()`, `gicv3_access_reg()`, and register read/write helpers. Publicly consumed exports include `gicv3_ops`, `gicv3_reg_readl()`, `gicv3_reg_writel()`, and `gic_rdist_enable_lpis()`.

## Control Flow
`gicv3_init()` records CPU and SPI counts, caps SPIs at 1020, and initializes the distributor. `gicv3_dist_init()` disables the distributor, resets SPI group/active/enable/priority registers, then enables Group-1 with affinity routing. `gicv3_cpu_init()` validates redistributor CPU numbering, wakes the redistributor, resets SGI/PPI state, enables ICC system-register access, sets priority mask, and enables Group-1 interrupts.

## State, Dependencies, and Integration
The static `gicv3_data` records guest-visible GIC capacity. All MMIO accesses target fixed guest virtual bases from `gic_v3.h`, which host setup maps in `vgic.c`. The implementation uses arm64 sysreg accessors, memory barriers, `udelay()`, and KVM selftest asserts.

## Risks and Test Signals
Register write-pending waits can assert if emulation never clears RWP. The code assumes sequential redistributor layout and `GICR_TYPER.Processor_number == cpu`. Test failures surface as guest asserts, interrupt delivery errors, or timeouts in RWP loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/gic_v3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/gic_v3_its.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/gic_v3_its.c

## Purpose
This guest ITS helper programs GICv3 ITS tables and command queue entries for MSI/LPI-oriented KVM arm64 tests. It is derived from kernel ITS driver logic but scoped to selftest needs.

## Important APIs, Types, and Functions
`its_init()` installs collection, device, and command queue tables and enables the ITS. `struct its_cmd_block` represents a 32-byte command. Command helpers include `its_send_mapd_cmd()`, `its_send_mapc_cmd()`, `its_send_mapti_cmd()`, `its_send_invall_cmd()`, and `its_send_sync_cmd()`. Encoding helpers fill device IDs, event IDs, physical INTIDs, ITT addresses, target redistributors, collections, size, and valid bits.

## Control Flow
Initialization finds BASER registers by type, writes table attributes, writes CBASER, then sets `GITS_CTLR_ENABLE`. Command submission reads `GITS_CWRITER`, writes the command into the guest command queue, orders it with `dsb(ishst)`, advances CWRITER, and optionally polls CREADR.

## State, Dependencies, and Integration
The file operates on guest memory supplied by tests and fixed ITS MMIO base mappings from `vgic_its_setup()`. It depends on GICv3 register definitions, relaxed MMIO accessors, endian conversion, and KVM's synchronous ITS emulation assumption.

## Risks and Test Signals
The poll iteration count is zero because current KVM processes commands synchronously; asynchronous emulation would immediately assert. Wrong table sizing, alignment, or BASER type discovery causes guest failures or missing LPI delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/gic_v3_its.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/handlers.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/handlers.S

## Purpose
This assembly file builds the AArch64 guest exception vector table used by selftests. It preserves guest register state, calls the C exception router, and restores state before returning with `eret`.

## Important APIs, Types, and Functions
Macros `save_registers` and `restore_registers` save x0-x30, an observable SP value, ELR, and SPSR into an `ex_regs`-compatible stack frame. `HANDLER` emits a handler that calls `route_exception(regs, vector)`. `HANDLER_INVALID` emits direct unexpected-exception exits for invalid EL1t vectors. The global `vectors` symbol anchors the vector table.

## Control Flow
The `.entry.text` section is aligned to the architectural 0x800 vector-table boundary. Each 0x80-aligned vector branches to a generated handler. Valid EL1h and EL0 vectors save context, pass vector number to C, then restore context and return.

## State, Dependencies, and Integration
There is no persistent state beyond the stack frame. It integrates with `processor.c` through `route_exception()`, `kvm_exit_unexpected_exception()`, and `vcpu_init_descriptor_tables()`, which writes VBAR_EL1.

## Risks and Test Signals
Register layout must match `struct ex_regs`; any mismatch corrupts handler-visible state. Invalid vectors intentionally exit via ucall, giving tests a clear unexpected-exception failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/handlers.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/processor.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/processor.c

## Purpose
This is the arm64 processor backend for KVM selftests. It implements guest page-table management, vCPU setup, exception handling, guest-mode probing, SMCCC calls, and default VGIC integration.

## Important APIs, Types, and Functions
Page-table helpers include `virt_arch_pgd_alloc()`, `_virt_pg_map()`, `virt_get_pte_hva_at_level()`, `addr_arch_gva2gpa()`, and `virt_arch_dump()`. vCPU setup flows through `kvm_get_default_vcpu_target()`, `aarch64_vcpu_setup()`, `aarch64_vcpu_add()`, and `vm_arch_vcpu_add()`. Exception APIs include `vm_init_descriptor_tables()`, `vm_install_sync_handler()`, `vm_install_exception_handler()`, `route_exception()`, and `assert_on_unhandled_exception()`. Architecture hooks include `kvm_selftest_arch_init()`, `kvm_arch_vm_post_create()`, `kvm_arch_vm_finalize_vcpus()`, and `kvm_arch_vm_release()`.

## Control Flow
VM page mappings allocate page tables lazily according to the selected guest mode and LPA2 format. vCPU setup initializes target features, FP/ASIMD, SCTLR/TCR/MAIR/TTBR/TPIDR, stack pointer, and optional EL2 state. Exception vectors route synchronous exceptions by ESR EC and asynchronous vectors by vector number. VM post-create optionally enables MTE and creates a default VGICv3; finalize initializes the VGIC.

## State, Dependencies, and Integration
Static state tracks the guest exception handler table GVA and default feature requests (`request_mte`, `request_vgic`). It depends on KVM ARM ioctls, sysreg IDs, `guest_modes`, `vgic`, and generic `kvm_util` allocation.

## Risks and Test Signals
Risks include incorrect PTE address encoding for 52-bit/LPA2 modes, unsupported guest modes, and implicit default VGIC behavior affecting tests. Signals are assertion failures, unexpected exception ucalls, or failed KVM register/device ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/processor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/spinlock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/spinlock.c

## Purpose
This file provides the guest-side arm64 spinlock primitive used by selftest guest libraries, notably the GIC initialization path.

## Important APIs, Types, and Functions
`spin_lock()` uses `ldaxr`/`stxr` to acquire `lock->v` with acquire semantics. `spin_unlock()` uses `stlr wzr` to release by storing zero with release ordering.

## Control Flow
The lock loops while the value is nonzero, then attempts an exclusive store of one. A failed exclusive store retries from the beginning. Unlock is a single ordered store.

## State, Dependencies, and Integration
The only state is the integer field in `struct spinlock`. It depends on `spinlock.h` and arm64 exclusive load/store instructions. It integrates with guest code that needs synchronization before shared guest globals are visible to other vCPUs.

## Risks and Test Signals
This is a simple busy-wait lock with no fairness or backoff. Bugs usually manifest as guest hangs or failed one-time initialization assertions, especially under multi-vCPU GIC tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/spinlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/ucall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/ucall.c

## Purpose
This arm64 ucall backend maps the generic selftest "hypercall to userspace" mechanism onto an MMIO write exit.

## Important APIs, Types, and Functions
`ucall_arch_init()` allocates an unused guest virtual page, maps it to the selected MMIO GPA, records `vm->ucall_mmio_addr`, and writes the guest global `ucall_exit_mmio_addr`. `ucall_arch_get_ucall()` recognizes matching `KVM_EXIT_MMIO` writes and returns the ucall payload pointer from `run->mmio.data`.

## Control Flow
During VM creation, generic ucall setup calls `ucall_arch_init()`. At runtime, guest ucall code writes a pointer-sized value to the mapped MMIO page, causing KVM to exit; host code calls `get_ucall()`, which delegates to this backend.

## State, Dependencies, and Integration
The file stores per-VM MMIO GPA in `struct kvm_vm` and guest-visible GVA in a guest global. It depends on `virt_map()`, `vm_unused_gva_gap()`, and `write_guest_global()`.

## Risks and Test Signals
Unexpected access width or read accesses assert. If the MMIO address collides with real memory or is not mapped, guest/host synchronization through `GUEST_SYNC()` and `GUEST_ASSERT()` fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/ucall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/vgic.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/vgic.c

## Purpose
This host-side arm64 helper creates and manages VGICv3 and ITS KVM devices for selftest VMs, maps their MMIO regions into the guest, and offers interrupt injection/state helpers.

## Important APIs, Types, and Functions
`kvm_supports_vgic_v3()` probes device creation. `__vgic_v3_setup()` creates a VGICv3 device, sets IRQ count, distributor address, redistributor region, and guest mappings. `__vgic_v3_init()` initializes the device. `vgic_v3_setup()` validates vCPU count before setup. IRQ helpers include `_kvm_irq_set_level_info()`, `kvm_arm_irq_line()`, `kvm_irq_write_ispendr()`, `kvm_irq_write_isactiver()`, and `vgic_its_setup()`.

## Control Flow
The default VM hook in arm64 `processor.c` calls setup after VM creation and initialization after all vCPUs are created. Explicit callers can use `vgic_v3_setup()` to create and initialize in one path. ITS setup creates a separate device, assigns its GPA, initializes it, and maps the ITS window.

## State, Dependencies, and Integration
State lives in KVM device file descriptors and guest MMIO mappings. The helpers depend on KVM device attributes, ARM VGIC constants, `virt_map()`, and the GIC register layout expected by guest-side `gic_v3.c`.

## Risks and Test Signals
Private interrupt poking is limited to vCPU 0. Incorrect setup order, mismatched vCPU counts, or unsupported VGIC/ITS devices lead to assertions, negative setup returns, or failed interrupt delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/vgic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/assert.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/assert.c

## Purpose
This file implements the KVM selftest assertion failure path. It prints contextual failure information, emits a stack trace when possible, and exits with the selftest-expected status.

## Important APIs, Types, and Functions
`test_assert()` is the exported noinline assertion handler behind `TEST_ASSERT`. `test_dump_stack()` gathers up to 20 frames with `backtrace()` and runs `addr2line` on the current executable. `_gettid()` wraps `SYS_gettid` for thread-specific diagnostics.

## Control Flow
If an expression is false, `test_assert()` prints file, line, expression, PID, TID, errno, and strerror, dumps the resolved stack, prints optional formatted details, and exits. `EACCES` maps to `KSFT_SKIP`; other assertion failures exit with 254.

## State, Dependencies, and Integration
There is no persistent state. It depends on libc backtrace support, `addr2line`, `kselftest.h`, and `test_util.h`. All KVM selftest libraries and programs rely on this behavior for hard failure reporting.

## Risks and Test Signals
The stack trace uses `system()` and `/proc/$PPID/exe`, so symbolization is best-effort and environment-dependent. The important signal is deterministic process termination with either skip or failure status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/assert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/elf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/elf.c

## Purpose
This utility loads the current selftest ELF image into a guest VM's virtual address space, allowing guest code and data from the test binary to run inside KVM.

## Important APIs, Types, and Functions
`elfhdr_get()` opens and validates a 64-bit ELF header, including magic, class, host-matching endianness, version, and program/section header sizes. `kvm_vm_elf_load()` walks program headers, allocates guest virtual memory for each `PT_LOAD` segment, zeroes BSS, and copies file-backed bytes.

## Control Flow
The loader opens the file, validates the header, iterates all program headers, skips non-loadable entries, aligns segment virtual ranges to guest pages, allocates exactly at the segment's requested GVA, clears memory, seeks to segment data, and reads bytes into the guest mapping.

## State, Dependencies, and Integration
State is transient file descriptor and allocated guest pages. It depends on `test_read()`, `__vm_alloc()`, `addr_gva2hva()`, ELF UAPI definitions, and `kvm_util.c` VM creation. `__vm_create()` loads `program_invocation_name` through this path.

## Risks and Test Signals
The loader supports only ELF64 with same-endian host and guest file representation and does not enforce segment permissions. Failures are assertion messages for malformed ELF, allocation mismatch, short reads, or seek errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/elf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/guest_modes.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/guest_modes.c

## Purpose
This file manages the list of guest address/page-size modes that a selftest should run. It provides architecture-aware default mode discovery, command-line mode selection, help text, and iteration.

## Important APIs, Types, and Functions
Global `guest_modes[NUM_VM_MODES]` stores support/enabled state. `guest_modes_append_default()` appends supported modes based on architecture capability probing. `for_each_guest_mode()` invokes a callback for enabled modes. `guest_modes_help()` prints supported IDs. `guest_modes_cmdline()` enables explicit mode IDs.

## Control Flow
Non-arm64/riscv architectures append `VM_MODE_DEFAULT`. arm64 probes IPA and page-size support; s390 probes CPU model to add 47-bit mode; RISC-V checks GPA bits and SATP modes. Explicit `-m` selection first disables all modes, then enables requested IDs.

## State, Dependencies, and Integration
State is process-global mode enablement plus `vm_mode_default` on arm64/RISC-V. It depends on architecture probing helpers from `processor.c`, KVM capabilities, and parsing/assert helpers. Test programs like `kvm_page_table_test.c` use it to sweep modes.

## Risks and Test Signals
Incorrect support detection can skip coverage or select unsupported modes. `for_each_guest_mode()` asserts if an enabled mode is unsupported, providing an immediate signal for bad command-line selection or probing errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/guest_modes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/guest_sprintf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/guest_sprintf.c

## Purpose
This file implements a small guest-safe `snprintf`/`vsnprintf` for KVM selftest guest code, avoiding reliance on full libc formatting inside the guest.

## Important APIs, Types, and Functions
`guest_vsnprintf()` parses format strings and writes bounded output. `guest_snprintf()` is the variadic wrapper. Helpers include `skip_atoi()`, `number()`, and `APPEND_BUFFER_SAFE`, which asserts before every write. Supported conversions include `%c`, `%s`, `%p`, `%n`, `%o`, `%x`, `%X`, `%d`, `%i`, `%u`, and `%%`, with common flags, width, precision, and `h`/`l`/`ll` handling.

## Control Flow
The formatter scans literals and `%` sequences, parses flags, width, precision, and qualifier, then either emits character/string/pointer/special cases or formats numeric output through `number()`. It terminates with NUL and returns the number of bytes written.

## State, Dependencies, and Integration
There is no persistent state. It depends on guest assertion macros and limited string helpers. It integrates with guest-side diagnostics such as `GUEST_ASSERT` formatting.

## Risks and Test Signals
The implementation is intentionally limited and asserts on buffer overflow instead of truncating like standard `snprintf`. Unsupported formats are emitted literally after `%`, which can hide formatting mistakes but preserves guest progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/guest_sprintf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/io.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/io.c

## Purpose
This file provides robust selftest wrappers around `read(2)` and `write(2)` that complete full-count I/O or fail the test with diagnostics.

## Important APIs, Types, and Functions
`test_write()` writes the entire buffer, retrying on `EAGAIN` and `EINTR`, treating short writes as progress, and failing on EOF or unexpected errors. `test_read()` mirrors that behavior for reading exactly the requested byte count.

## Control Flow
Both wrappers loop until `num_written` or `num_read` reaches `count`. `-1` with retryable errno repeats, zero is unexpected EOF, and positive values advance the buffer pointer and remaining length.

## State, Dependencies, and Integration
No state persists beyond loop counters. The wrappers depend on `TEST_ASSERT()` and `TEST_FAIL()` and are used by ELF loading and other file-backed helpers to avoid duplicating short-I/O handling.

## Risks and Test Signals
They assume the caller expects exactly `count` bytes; using them on streams where EOF is valid will fail hard. Successful return always equals requested count, making failures explicit and easy to diagnose.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/kvm_util.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/kvm_util.c

## Purpose
This is the central KVM selftest utility implementation. It handles `/dev/kvm` access, capability probing, VM and vCPU lifecycle, guest memory registration, virtual/physical allocation, address translation, device attributes, IRQ routing, dirty-ring mapping, stats, signal handling, and architecture hook dispatch.

## Important APIs, Types, and Functions
Creation flows through `____vm_create()`, `__vm_create()`, `__vm_create_with_vcpus()`, and `__vm_vcpu_add()`. Memory APIs include `vm_mem_add()`, `vm_userspace_mem_region_add()`, `memslot2region()`, `vm_mem_region_set_flags()`, `vm_mem_region_delete()`, `__vm_phy_pages_alloc()`, `virt_map()`, `addr_gpa2hva()`, `addr_hva2gpa()`, and `addr_gva2hva()`. Other major APIs include `kvm_check_cap()`, `kvm_set_files_rlimit()`, `_vcpu_run()`, `vcpu_run()`, device attribute wrappers, IRQ routing helpers, `vm_dump()`, and binary stats readers.

## Control Flow
VM creation initializes mode-derived address properties, opens KVM, sets up valid GVA bitmaps, creates slot 0 with `KVM_SET_USER_MEMORY_REGION2`, loads the ELF image, initializes ucall MMIO, seeds guest RNG state, and invokes architecture post-create hooks. VCPU creation creates the KVM vCPU fd, maps `struct kvm_run`, attaches stats, and links into the VM list. Memory creation allocates host backing, optional memfd/guest_memfd, registers a memslot, and indexes it by GPA, HVA, and slot.

## State, Dependencies, and Integration
`struct kvm_vm` owns file descriptors, memslot hash/tree indexes, sparsebit allocators, vCPU list, stats cache, and architecture fields. `struct userspace_mem_region` persists backing mappings, aliases, guest_memfd state, and allocation bitmaps. The file depends on Linux KVM ioctls, sparsebit/rbtree/list/hash helpers, architecture weak hooks, ucall, ELF loading, and kselftest utilities.

## Risks and Test Signals
The biggest risks are stale region indexes, overlapping memslots, incorrect page-count adjustment across host/guest page sizes, guest_memfd ownership mistakes, and architecture hook assumptions. Assertions and VM dumps provide strong failure signals; constructor signal handlers turn unexpected SIGBUS/SIGSEGV/SIGILL/SIGFPE into test failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/kvm_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/loongarch/exception.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/loongarch/exception.S

## Purpose
This LoongArch guest assembly implements TLB refill and general exception entry code for KVM selftests.

## Important APIs, Types, and Functions
`handle_tlb_refill` loads page-table entries through `lddir`/`ldpte` and executes `tlbfill`. `handle_exception` saves general-purpose registers and key CSRs into an `ex_regs` stack frame, calls `route_exception`, restores state, and returns with `ertn`. Macros `save_gprs` and `restore_gprs` handle GPR preservation.

## Control Flow
Both entry points are 4K aligned. TLB refill temporarily saves `t0`, walks PGD state from CSR, fills TLB, restores, and returns. General exception switches to the exception stack from `KS1`, saves registers/ERA/ESTAT/BADV/PRMD, calls C, restores ERA/PRMD and GPRs, then resumes.

## State, Dependencies, and Integration
State is per-exception stack contents and LoongArch CSRs. It integrates with `loongarch_vcpu_setup()`, which programs `TLBRENTRY`, `EENTRY`, page-walk CSRs, and exception stack CSR.

## Risks and Test Signals
The saved frame layout must match C structs and CSR setup. Bad page-walk configuration or stack CSR state causes guest traps, unexpected ucalls, or hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/loongarch/exception.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/loongarch/processor.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/loongarch/processor.c

## Purpose
This is the LoongArch processor backend for KVM selftests. It implements page-table setup, address translation, vCPU register/CSR initialization, exception routing, and argument passing.

## Important APIs, Types, and Functions
Page-table functions include `virt_arch_pgd_alloc()`, `virt_populate_pte()`, `virt_arch_pg_map()`, `addr_arch_gva2gpa()`, and `virt_arch_dump()`. vCPU functions include `loongarch_vcpu_setup()`, `vm_arch_vcpu_add()`, `vcpu_arch_set_entry_point()`, and `vcpu_args_set()`. Exception APIs include `route_exception()`, `vm_init_descriptor_tables()`, `vm_install_exception_handler()`, and `assert_on_unhandled_exception()`.

## Control Flow
PGD allocation prebuilds invalid page-table pages for each level. Mapping lazily allocates child tables and writes present/read/write/cache/user PTEs. vCPU setup validates guest mode, mirrors CPUCFG6, programs CRMD/PRMD/EUEN/ASID/page-walk CSRs, installs refill and general exception entries, allocates exception and runtime stacks, and assigns CPUID/TMID.

## State, Dependencies, and Integration
Static state includes `invalid_pgtable[]` and guest `exception_handlers`. It depends on LoongArch KVM register IDs, CSR helpers, `exception.S` symbols, generic VM allocation, and ucall handling.

## Risks and Test Signals
Risks include invalid table sentinel misuse, recursive dump level decrement behavior, mode assumptions limited to 16K LoongArch modes, and CSR misprogramming. Failures surface through `UCALL_UNHANDLED`, TEST_ASSERTs, or inability to translate/map guest addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/loongarch/processor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/loongarch/ucall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/loongarch/ucall.c

## Purpose
This LoongArch ucall backend uses an MMIO write exit to pass guest ucall payload pointers back to userspace.

## Important APIs, Types, and Functions
`ucall_arch_init()` maps a free guest virtual page to the selected MMIO GPA, records `vm->ucall_mmio_addr`, and writes guest global `ucall_exit_mmio_addr`. `ucall_arch_get_ucall()` recognizes `KVM_EXIT_MMIO` writes to that GPA and returns the pointer stored in MMIO data.

## Control Flow
Generic ucall setup calls init during VM construction. Guest code writes a u64 to the mapped MMIO page; host exit handling recognizes the physical address and extracts the payload.

## State, Dependencies, and Integration
State is per-VM MMIO GPA plus a guest global GVA. The code depends on generic virtual mapping and global writing helpers, matching the arm64 MMIO ucall pattern.

## Risks and Test Signals
Unexpected access direction or length asserts. Misconfigured mapping breaks `GUEST_SYNC()` and `GUEST_ASSERT()` delivery and typically appears as an unexpected KVM exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/loongarch/ucall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/lru_gen_util.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/lru_gen_util.c

## Purpose
This helper parses and drives Linux multi-generational LRU debugfs state for KVM selftests that need page-aging behavior tied to a memory cgroup.

## Important APIs, Types, and Functions
`lru_gen_read_memcg_stats()` parses `LRU_GEN_DEBUGFS` into `struct memcg_stats`. `lru_gen_sum_memcg_stats_for_gen()` and `lru_gen_sum_memcg_stats()` aggregate pages. `lru_gen_do_aging()` issues aging commands. `lru_gen_find_generation()` finds a generation containing enough pages. `lru_gen_usable()` validates kernel feature and debugfs availability.

## Control Flow
Parsing is state-machine based through `memcg_stats_handle_searching()`, `memcg_stats_handle_in_memcg()`, and `memcg_stats_handle_in_node()`. It scans for a named memcg, records node IDs, records generation age/anon/file counts, and stops at the next memcg. Aging rereads stats, computes each node's max generation, writes `+ memcg node max_gen 1 force_scan` commands, and rereads updated stats.

## State, Dependencies, and Integration
The file persists no global mutable state except static `force_scan`. It depends on debugfs files, cgroup naming, parser limits (`MAX_NR_NODES`, `MAX_NR_GENS`), and kselftest skip/assert behavior.

## Risks and Test Signals
Input format changes, removed memcgs, missing debugfs, or missing MGLRU features cause clear assertions or skips. The parser mutates line buffers with `strtok_r`, so it duplicates lines when it may need to hand them to another state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/lru_gen_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/memstress.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/memstress.c

## Purpose
This file implements reusable memory-stress VM setup and vCPU-thread orchestration for KVM selftests that dirty, read, and fault large guest memory regions.

## Important APIs, Types, and Functions
`memstress_guest_code()` performs guest memory accesses. `memstress_create_vm()` creates the VM, extra memslots, mappings, vCPU args, optional nested setup, and guest globals. `memstress_setup_vcpus()` partitions or shares test memory. Thread helpers include `memstress_start_vcpu_threads()` and `memstress_join_vcpu_threads()`. Dirty-log helpers enable/disable logging, get/clear bitmaps, and allocate/free bitmap arrays.

## Control Flow
VM creation computes guest pages from vCPU memory size and guest mode, reserves nested overhead if needed, creates vCPUs, places test memory near the top of GPA space, adds one or more test memslots, maps them at `DEFAULT_GUEST_TEST_MEM`, sets per-vCPU GVA/GPA/page ranges, and syncs `memstress_args`. Guest code repeatedly touches args pages, then iterates assigned pages randomly or sequentially with read/write probability, ending each pass with `GUEST_SYNC(1)`.

## State, Dependencies, and Integration
Global `memstress_args`, static vCPU thread records, a test vCPU array, and callback pointer store runtime state. It depends on `kvm_util`, `processor`, guest RNG, backing-source helpers, pthreads, bitmap helpers, and weak nested-virtualization hooks.

## Risks and Test Signals
Risks include invalid alignment, uneven slot division, excessive requested GPA space, busy-wait thread synchronization, and architecture gaps for nested support. Test signals are ucall syncs, dirty bitmap contents, and assertions during VM setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/memstress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/rbtree.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/rbtree.c

## Purpose
This file imports the shared rbtree implementation into the KVM selftest library build by including `../../../../lib/rbtree.c`.

## Important APIs, Types, and Functions
It does not define local functions. The included implementation supplies Linux-style red-black tree primitives such as insertion rebalancing and erase support used by KVM selftest memory-region indexes.

## Control Flow
Compilation effectively inlines the common library source into this object. Runtime control flow is that of the included rbtree implementation, not this wrapper.

## State, Dependencies, and Integration
The wrapper depends on the relative source-tree layout. `kvm_util.c` uses rbtree roots and nodes to index memory regions by GPA and HVA, relying on this compiled implementation.

## Risks and Test Signals
The main risk is path drift: moving the file or shared library breaks compilation. Functional failures would appear as broken memory-region lookup, duplicate insertion assertions, or crashes in VM memory management.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/rbtree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/riscv/handlers.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/riscv/handlers.S

## Purpose
This RISC-V assembly file implements the guest exception vector entry used by selftests with custom exception/interrupt handlers.

## Important APIs, Types, and Functions
`save_context` stores integer registers plus `sepc`, `sstatus`, `stval`, and `scause` into a stack frame. `restore_context` restores those CSRs and registers. The global `exception_vectors` entry calls C `route_exception()` and returns with `sret`.

## Control Flow
On trap entry, the vector subtracts stack space, saves context, passes the stack frame pointer in `a0`, calls the C router, restores context, and resumes guest execution with `sret`.

## State, Dependencies, and Integration
State is per-trap stack data. It depends on RISC-V CSR names and must match the C `pt_regs` layout expected by `processor.c`. `vcpu_init_vector_tables()` programs `stvec` to this symbol.

## Risks and Test Signals
Incorrect frame offsets or CSR restore order can corrupt guest state or loop traps. Unexpected exceptions are routed to ucall failure paths in `processor.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/riscv/handlers.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/riscv/processor.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/riscv/processor.c

## Purpose
This is the RISC-V processor backend for KVM selftests. It implements page-table construction, SATP setup, vCPU initialization, register dumps, exception routing, SBI calls, guest-mode probing, and default IRQ-chip detection.

## Important APIs, Types, and Functions
Important helpers include `__vcpu_has_ext()`, `virt_arch_pgd_alloc()`, `virt_arch_pg_map()`, `addr_arch_gva2gpa()`, `riscv_vcpu_mmu_setup()`, `vm_arch_vcpu_add()`, `vcpu_args_set()`, `route_exception()`, `vm_init_vector_tables()`, `vm_install_exception_handler()`, `vm_install_interrupt_handler()`, `sbi_ecall()`, `guest_sbi_probe_extension()`, `get_host_sbi_spec_version()`, and `riscv64_get_satp_mode()`.

## Control Flow
Mapping starts at the top-level page table and lazily allocates child tables until the leaf, where it writes a valid permission PTE. VCPU setup allocates stack, creates the vCPU, programs SATP based on selected mode and KVM-supported max SATP mode, sets MP state runnable, copies host `gp`, sets stack and `sscratch`, and installs a default unexpected-trap vector. Custom vector tables can later route through `handlers.S`.

## State, Dependencies, and Integration
Static `exception_handlers` stores the guest handler table GVA. The file depends on RISC-V KVM register namespaces, SBI extension IDs, generic `guest_modes`, ucall, and KVM capability probing.

## Risks and Test Signals
Risks include unsupported SATP modes, assumptions about 4K page tables, default unexpected trap behavior via SBI, and register ID mismatches. Signals are register dumps, `UCALL_UNHANDLED`, SBI exits, and KVM ioctl assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/riscv/processor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/riscv/ucall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/riscv/ucall.c

## Purpose
This RISC-V ucall backend uses KVM's RISC-V SBI exit path for guest-to-userspace selftest communication.

## Important APIs, Types, and Functions
`ucall_arch_get_ucall()` inspects `KVM_EXIT_RISCV_SBI` exits with extension `KVM_RISCV_SELFTESTS_SBI_EXT`. Function `KVM_RISCV_SELFTESTS_SBI_UCALL` returns the ucall pointer from SBI arg0. Function `KVM_RISCV_SELFTESTS_SBI_UNEXP` dumps vCPU state and fails the test.

## Control Flow
Guest code performs an SBI ecall through the selftest extension. Host exit handling checks extension and function IDs, extracts payloads for ordinary ucalls, or treats unexpected-trap notifications as hard failures.

## State, Dependencies, and Integration
There is no per-VM MMIO mapping state in this backend. It depends on RISC-V KVM SBI exit fields, `processor.h`, and generic `get_ucall()` integration.

## Risks and Test Signals
Wrong extension/function IDs return NULL and may look like an unexpected exit to callers. Unexpected traps produce immediate vCPU dump output and assertion failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/riscv/ucall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/s390/diag318_test_handler.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/s390/diag318_test_handler.c

## Purpose
This s390x helper obtains DIAGNOSE 0x0318 information through an ad-hoc KVM VM so tests can verify or use the userspace-handled instruction payload.

## Important APIs, Types, and Functions
`guest_code()` executes `diag 0,0,0x318` with a known info value. `diag318_handler()` creates a one-vCPU VM, runs it, validates `KVM_EXIT_S390_SIEIC`, extracts the register encoded in IPA, reads the GPR value, and frees the VM. `get_diag318_info()` caches and returns the value, or returns zero if `KVM_CAP_S390_DIAG318` is unsupported.

## Control Flow
The first successful caller probes KVM capability, runs the temporary VM until the diagnose intercept, validates intercept code and IPA, reads the info register, asserts nonzero, caches it, and returns it. Later calls reuse the cached value.

## State, Dependencies, and Integration
Persistent state is static cached `diag318_info` and `printed_skip`. It depends on s390 KVM exit layout, generic VM creation, and kselftest skip-style messaging.

## Risks and Test Signals
If KVM lacks the capability, tests receive zero and a single skip message. Incorrect intercept decoding or zero payload causes assertions, which protects callers from silently using invalid diagnostic data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/s390/diag318_test_handler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/s390/facility.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/s390/facility.c

## Purpose
This file defines global storage for s390 facility-test state shared by the facility helpers and tests.

## Important APIs, Types, and Functions
It defines `u64 stfl_doublewords[NB_STFL_DOUBLEWORDS]` and `bool stfle_flag`. There are no functions.

## Control Flow
There is no executable control flow. Other compilation units read or populate these globals to represent Store Facility List data and whether extended facility-list behavior is active.

## State, Dependencies, and Integration
The globals are persistent process state and depend on declarations/constants from `facility.h`. This file exists to provide exactly one definition for link-time storage.

## Risks and Test Signals
Risks are ordinary global-state hazards: tests must initialize or refresh these fields before relying on them. Link failures catch missing or duplicate definitions; semantic issues show up in facility-dependent tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/s390/facility.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/s390/processor.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/s390/processor.c

## Purpose
This is the s390x processor backend for KVM selftests. It implements s390 page tables, address translation, vCPU setup, argument passing, dumps, and default IRQ-chip reporting.

## Important APIs, Types, and Functions
`virt_arch_pgd_alloc()` allocates and invalidates the top region table. `virt_alloc_region()` allocates region/segment/page-table levels. `virt_arch_pg_map()` walks and populates region tables and leaf PTEs. `addr_arch_gva2gpa()` translates GVAs. `virt_arch_dump()` prints region/PTE state. `vm_arch_vcpu_add()`, `vcpu_arch_set_entry_point()`, `vcpu_args_set()`, and `vcpu_arch_dump()` implement vCPU integration.

## Control Flow
PGD allocation reserves four pages and fills them with invalid entries. Mapping walks four region/segment levels using 11-bit indexes, allocating invalidated child tables when needed, then writes the page table entry. VCPU setup allocates a stack, creates the vCPU, sets GPR15 stack pointer, enables floating point in CR0, points CR1 to the primary region table, and sets PSW mask for DAT and 64-bit mode.

## State, Dependencies, and Integration
State lives in the generic VM MMU fields, guest page tables, KVM regs/sregs, and `kvm_run` PSW fields. It depends on s390 page-table constants, generic allocation, and KVM register ioctls.

## Risks and Test Signals
Only 4K pages are supported. `virt_alloc_region()` clears `PAGES_PER_REGION * page_size` even for page tables, so table allocation assumptions must remain aligned with available memory. Failures assert on unsupported page size, missing mappings, or KVM register errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/s390/processor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/s390/ucall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/s390/ucall.c

## Purpose
This s390x ucall backend decodes selftest ucalls from DIAGNOSE instruction intercepts delivered as `KVM_EXIT_S390_SIEIC`.

## Important APIs, Types, and Functions
`ucall_arch_get_ucall()` checks for intercept code 4, DIAGNOSE IPA class `0x83`, and IPB function `0x501`. It extracts the register number from IPA and returns the guest pointer stored in that GPR.

## Control Flow
On each KVM exit, generic ucall handling delegates here. Matching DIAGNOSE exits produce a payload pointer; all other exits return NULL for higher-level handling.

## State, Dependencies, and Integration
There is no persistent state. The backend depends on s390 KVM run-structure fields and the guest-side ucall convention of placing the pointer in the IPA-selected GPR.

## Risks and Test Signals
The decoder is tightly coupled to the DIAGNOSE encoding. Encoding drift or wrong register selection causes missing ucalls, usually observed as unexpected exit reasons or failed guest synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/s390/ucall.c -->
