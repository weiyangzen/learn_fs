# sources/distributed-fs/ceph-client/arch/parisc/kernel/head.S

## Purpose

`head.S` is the PA-RISC kernel entry path. It handles the transition from firmware/loader state into the virtual-memory kernel, builds initial mappings, validates CPU capabilities, configures PDC and interrupt vectors, and provides the SMP slave entry path.

## Important APIs, Types, And Labels

`boot_args` stores four 32-bit bootloader arguments. `parisc_kernel_start` is the primary entry point. `common_stext` contains setup shared by the monarch CPU and SMP slave CPUs. `aligned_rfi` performs the final return-from-interruption transition into virtual mode. `smp_slave_stext` is the firmware rendezvous entry for secondary CPUs. `stext_pdc_ret`, `stext_pdc_btlb_ret`, and `smp_callin_rtn` are local return labels for firmware calls and failure traps.

The code imports `init_task`, `init_stack`, `fault_vector_20`, `fault_vector_11`, `start_parisc`, `smp_callin`, and `smp_init_current_idle_task`. It writes page-zero rendezvous fields such as `MEM_RENDEZ` and uses page table symbols including `swapper_pg_dir`, `pmd0`, `pg0`, and `_end`.

## Control Flow

Entry clears kernel space registers, zeros BSS, saves boot arguments, and on PA2.0-configured kernels verifies that the CPU supports the required wide control-register behavior. If the CPU check fails, it prints an IODC panic message and loops.

The boot CPU initializes early page tables covering the initial kernel physical range, sets kernel and user root pointers, initializes `cr30` with `init_task`, sets the physical stack, and on 64-bit function-tracing builds initializes the `_mcount` function descriptor GP field. SMP builds install `smp_slave_stext` in page-zero rendezvous fields; non-SMP clears them.

`common_stext` optionally switches to wide mode, calls PDC to set default wide PSW on 64-bit, clears block TLBs on 32-bit PA1.1, clears user space registers and protection registers, loads the global pointer, selects the correct fault vector, installs the IVA in `cr14`, prepares the IIA queues and IPSW, converts the stack to virtual, and executes `rfi` into `start_parisc` or `smp_callin`.

`smp_slave_stext` initializes secondary CPU space registers, enables wide mode early on 64-bit, installs the idle task and stack provided by the monarch, points at `swapper_pg_dir`, loads `smp_callin`, and branches through `common_stext`.

## State And Persistence Behavior

The file initializes persistent machine-wide boot state: zeroed BSS, saved `boot_args`, early page tables, root pointers, IVA, page-zero SMP rendezvous addresses, task pointer in `cr30`, and initial PSW defaults. It does not use filesystem persistence.

## Dependencies And Integration Points

It is tightly coupled to linker symbols, assembly offsets, PDC page-zero layout, PSW/control-register definitions, fault-vector assembly, SMP CPU bring-up, and the C entry points `start_parisc()` and `smp_callin()`.

## Risks

Ordering is critical. Installing IVA too early can break HPMC behavior, switching to virtual addresses before page tables are valid can trap, and incorrect stack or `cr30` setup breaks exception handling. 64-bit wide-mode setup depends on firmware quirks such as the PCX-W2 bug workaround. SMP rendezvous uses physical addresses and assumes the slave entry is below 4 GB in the stored high word case.

## Test Signals

Signals include reaching `start_parisc()` on boot, correct saved boot arguments, successful PA1.1 and PA2.0 fault vector installation, secondary CPU bring-up through `smp_callin`, no early RFI traps, and successful boot with `CONFIG_64BIT`, `CONFIG_SMP`, `CONFIG_HOTPLUG_CPU`, and `CONFIG_FUNCTION_TRACER` combinations.
