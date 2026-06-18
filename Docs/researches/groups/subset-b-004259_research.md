# subset-b-004259 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/core.c -->
# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/core.c

## Purpose
`core.c` is the LKDTM entry point. It exposes debugfs files under `provoke-crash`, accepts module parameters for crashpoint/crashtype/count selection, wires all LKDTM crash categories together, and optionally arms kprobes so a selected kernel execution point triggers a selected destructive test after a configurable hit count.

## Important APIs, Types, and Functions
Key local types are `struct crashpoint`, the `CRASHPOINT()` macro, and the global `crashpoints[]` table. Main routines are `find_crashtype()`, `lkdtm_do_action()`, `lkdtm_register_cpoint()`, `lkdtm_kprobe_handler()`, `lkdtm_debugfs_entry()`, `direct_entry()`, `lkdtm_debugfs_read()`, `lkdtm_check_bool_cmdline()`, `lkdtm_module_init()`, and `lkdtm_module_exit()`. It consumes the `struct crashtype_category` exports declared in `lkdtm.h`.

## Control Flow
Initialization validates module parameters, resolves requested crashpoint/type names, sets the kprobe hit counter, builds `lkdtm_kernel_info`, calls category init hooks, creates the debugfs directory, and creates one file per crashpoint. A write to `DIRECT` immediately resolves the requested crashtype and calls its function. A write to a kprobe-backed crashpoint registers a kprobe; its pre-handler decrements `crash_count`, resets it on zero, and calls the selected crashtype through `lkdtm_do_action()`.

## State and Persistence
State is in module globals: selected `lkdtm_kprobe`, `lkdtm_crashpoint`, `lkdtm_crashtype`, debugfs root, `crash_count`, module parameters, and allocated `lkdtm_kernel_info`. There is no persistence beyond module lifetime.

## Dependencies and Integration Points
Depends on debugfs, optional kprobes, module parameters, kernel command line parsing for built-in LKDTM, UTS release/machine strings, and category modules for bugs, heap, permissions, refcount, usercopy, stackleak, CFI, fortify, and optional powerpc tests.

## Risks
All paths intentionally provoke crashes or corruption. Incorrect parameter combinations are rejected, but selected tests can panic a system. Kprobe symbol names are configuration and architecture sensitive. Debugfs writable entries are powerful and should be restricted to test kernels.

## Test Signals
Useful signals are debugfs listing of all crash types, valid and invalid writes to `DIRECT`, kprobe registration failure handling, hit-count countdown behavior, module parameter validation, command-line bool parsing when built-in, and cleanup unregistering kprobes and removing debugfs files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/fortify.c -->
# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/fortify.c

## Purpose
`fortify.c` provides LKDTM tests for fortified string and memory helpers. It intentionally performs runtime-detected overflows against whole objects and struct members to validate `CONFIG_FORTIFY_SOURCE`.

## Important APIs, Types, and Functions
The exported category is `fortify_crashtypes`. Test functions are `lkdtm_FORTIFY_STR_MEMBER()`, `lkdtm_FORTIFY_MEM_OBJECT()`, `lkdtm_FORTIFY_MEM_MEMBER()`, and `lkdtm_FORTIFY_STRSCPY()`. It uses `strscpy()`, `memcpy()`, `strlen()`, `strncmp()`, `strcmp()`, `kmalloc()`, `kstrdup()`, and the LKDTM `pr_expected_config()` macro.

## Control Flow
Each crashtype prepares a destination object whose bounds should be known to fortified helpers, hides the copy length with a volatile variable where needed to avoid compile-time diagnostics, performs a copy that crosses a member or object boundary, and reports failure only if the fortify check did not stop execution. `FORTIFY_STRSCPY` also validates normal `strscpy()` return values before the final overflowing copy.

## State and Persistence
There is no durable state. `fortify_scratch_space` is a volatile global used to keep copied data observable so the compiler does not eliminate the tested operations.

## Dependencies and Integration Points
Integrates with LKDTM through the crashtype category table and relies on kernel fortified string/memory wrappers from `<linux/string.h>`. Expected behavior depends on compiler object-size analysis and `CONFIG_FORTIFY_SOURCE`.

## Risks
The tests are designed to trap or panic. Optimizer changes can accidentally convert runtime checks into build-time failures or remove code unless volatile guards remain. A passing bad copy means a hardening regression.

## Test Signals
Signals include expected fortify reports on member/object overflow, correct `strscpy()` `-E2BIG` and byte-count behavior, preservation of the union-source edge case, and `FAIL` messages only when fortify did not intercept the overflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/fortify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/heap.c -->
# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/heap.c

## Purpose
`heap.c` contains LKDTM heap and page allocator hardening tests. It provokes slab/vmalloc overflows, use-after-free reads and writes, init-on-alloc/free checks, buddy-page poisoning checks, double free, cross-cache free, and non-slab slab free handling.

## Important APIs, Types, and Functions
Important functions are `lkdtm_VMALLOC_LINEAR_OVERFLOW()`, `lkdtm_SLAB_LINEAR_OVERFLOW()`, `lkdtm_WRITE_AFTER_FREE()`, `lkdtm_READ_AFTER_FREE()`, `lkdtm_KFENCE_READ_AFTER_FREE()`, buddy allocator tests, init-on-alloc tests, `lkdtm_SLAB_FREE_DOUBLE()`, `lkdtm_SLAB_FREE_CROSS()`, `lkdtm_SLAB_FREE_PAGE()`, `lkdtm_heap_init()`, and `lkdtm_heap_exit()`. It owns three `struct kmem_cache *` globals used for free-integrity tests.

## Control Flow
The overflow tests allocate kernel memory and intentionally write just past valid bounds. Use-after-free tests allocate, initialize, free, and access memory again, then attempt to observe allocator poisoning. KFENCE loops until a KFENCE-backed allocation appears or a timeout expires. Init tests fill memory, free it, reallocate, and scan for stale bytes. Free-integrity tests allocate from dedicated caches and then free invalidly.

## State and Persistence
State is limited to `double_free_cache`, `a_cache`, and `b_cache`, created during LKDTM init and destroyed at module exit. Test allocations are transient.

## Dependencies and Integration Points
Uses slab, vmalloc, buddy allocator APIs, scheduler timing, KFENCE helpers, init-on-alloc/free boot parameters, and LKDTM configuration reporting. It exports `heap_crashtypes` for `core.c`.

## Risks
Many tests corrupt memory if hardening does not catch them. Some checks are probabilistic or allocator-layout dependent, such as getting the same object back after free or obtaining a KFENCE allocation before timeout.

## Test Signals
Expected signals are KASAN/KFENCE/SLUB/vmalloc guard faults, poisoning differences on read-after-free, stale-byte absence under init-on-alloc/free, detected double/cross/non-slab frees, and explanatory `FAIL` lines when the configured hardening is missing or ineffective.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/heap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/kstack_erase.c -->
# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/kstack_erase.c

## Purpose
`kstack_erase.c` verifies that stackleak/kstack erasure poisoned the unused portion of the current task stack with `KSTACK_ERASE_POISON`.

## Important APIs, Types, and Functions
The main implementation is `check_stackleak_irqoff()` under `CONFIG_KSTACK_ERASE`, wrapped by `lkdtm_KSTACK_ERASE()`. It uses `task_stack_page()`, `stackleak_task_low_bound()`, `stackleak_task_high_bound()`, `current_stack_pointer`, `current->lowest_stack`, `stackleak_find_top_of_poison()`, `instrumentation_begin/end()`, and IRQ save/restore.

## Control Flow
The test disables local IRQs to stabilize stack usage and calls a `noinstr` checker. The checker validates current and lowest stack pointers against task stack bounds, computes the untracked range, finds the top of poison, scans downward to the low bound for non-poison words, and prints either failure details or stack usage offsets. If stack erasure is not built, the crashtype reports an expected failure based on architecture support.

## State and Persistence
No persistent state is owned. It reads per-task stack metadata, especially `current->lowest_stack`, and stack memory contents.

## Dependencies and Integration Points
Depends on `CONFIG_KSTACK_ERASE`, `CONFIG_HAVE_ARCH_KSTACK_ERASE`, `<linux/kstack_erase.h>`, architecture stack bounds, and LKDTM crashtype registration through `stackleak_crashtypes`.

## Risks
Any function call, interrupt, or compiler-generated stack behavior can alter the measured area. The file avoids printing until after instrumentation is re-enabled to reduce false positives.

## Test Signals
Signals include bounds validation, reported poison coverage, `OK` when the rest of the stack is erased, `FAIL` on non-poison values below the poison boundary, and `XFAIL` when support is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/kstack_erase.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/lkdtm.h -->
# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/lkdtm.h

## Purpose
`lkdtm.h` is the shared LKDTM internal interface. It defines crash type descriptors, category descriptors, category exports, init/exit hooks, and helper macros for expected configuration reporting.

## Important APIs, Types, and Functions
Primary types are `struct crashtype` and `struct crashtype_category`. The `CRASHTYPE()` macro maps a symbolic test name to `lkdtm_<NAME>`. `pr_expected_config()` and `pr_expected_config_param()` format hardening expectation messages using `lkdtm_kernel_info`. Built-in kernels also expose `lkdtm_check_bool_cmdline()`.

## Control Flow
Category C files build static arrays with `CRASHTYPE()` and export one `struct crashtype_category`. `core.c` iterates those categories to list and dispatch tests. Expected-config helpers branch on `IS_ENABLED(kconfig)` and, for built-in kernels, parsed boot parameters.

## State and Persistence
The header declares the shared `lkdtm_kernel_info` string and all category symbols, but owns no storage except macro expansions in users.

## Dependencies and Integration Points
Depends on `<linux/kernel.h>`, LKDTM category object files, and module-vs-built-in compilation. The `lkdtm_rodata_do_nothing()` declaration is used by permissions tests to execute code placed in rodata through build tricks.

## Risks
The macro naming convention must match function definitions exactly. Missing category objects or mismatched init/exit declarations would fail link-time integration. Expected-config messages are diagnostic only and do not enforce hardening.

## Test Signals
Signals are successful linking of all category exports, debugfs listing containing all declared crashtypes, meaningful expected-config logs for positive and negative hardening cases, and built-in command-line parameter handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/lkdtm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/perms.c -->
# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/perms.c

## Purpose
`perms.c` validates kernel memory permission hardening: read-only data/text protections, non-executable data/stack/heap/vmalloc/user/null regions, user/kernel address separation, and function-descriptor write protection.

## Important APIs, Types, and Functions
Important routines include `execute_location()`, `execute_user_location()`, `setup_function_descriptor()`, `lkdtm_WRITE_RO()`, `lkdtm_WRITE_RO_AFTER_INIT()`, `lkdtm_WRITE_KERN()`, `lkdtm_WRITE_OPD()`, `lkdtm_EXEC_*()`, `lkdtm_ACCESS_USERSPACE()`, `lkdtm_ACCESS_NULL()`, and `lkdtm_perms_init()`. Static targets include `data_area`, `rodata`, `ro_after_init`, `do_nothing()`, and `do_overwritten()`.

## Control Flow
Write tests cast away protections and write into rodata, ro-after-init data, text, or function descriptors. Execution tests copy or reference a harmless return function into non-code regions and call through a function pointer. User/null tests map user memory or use NULL and then perform intentionally invalid kernel reads/writes. Initialization stores the real text address for `do_nothing()` and mutates `ro_after_init` while init-time writes are still allowed.

## State and Persistence
Static globals represent memory-section targets. `ro_after_init` transitions from writable during init to read-only after init. `do_nothing_ptr` preserves a runtime function pointer for later tests.

## Dependencies and Integration Points
Uses vmalloc, kmalloc, user mappings, `access_process_vm()`, cache flushing, architecture section/function-descriptor helpers, CFI annotations, and LKDTM crashtype registration.

## Risks
Architecture differences around function descriptors, instruction cache coherency, CFI/IBT, and MMU behavior can alter expected faults. Tests intentionally perform undefined or fatal operations.

## Test Signals
Expected signals are faults or panics on bad writes/executions/accesses, `XFAIL` for architectures without function descriptors, lack of `FAIL: survived` messages, and correct `ro_after_init` init-time mutation before final write test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/perms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/powerpc.c -->
# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/powerpc.c

## Purpose
`powerpc.c` provides a PowerPC hash-MMU-only LKDTM test that injects SLB multihit conditions and verifies the machine can recover.

## Important APIs, Types, and Functions
Key functions are `insert_slb_entry()`, `inject_vmalloc_slb_multihit()`, `inject_kmalloc_slb_multihit()`, `insert_dup_slb_entry_0()`, and `lkdtm_PPC_SLB_MULTIHIT()`. It uses PowerPC MMU helpers such as `mk_vsid_data()`, `mk_esid_data()`, `mmu_psize_defs`, `radix_enabled()`, and inline `slbmte/slbmfee/slbmfev` assembly.

## Control Flow
The crashtype checks that radix MMU is not enabled. It then allocates vmalloc and kmalloc memory, inserts duplicate SLB entries for those addresses, touches the memory to trigger the exception, and duplicates bolted SLB entry zero before reading from `PAGE_OFFSET`. Successful execution reaches a recovery log line.

## State and Persistence
It transiently modifies processor SLB entries while preemption is disabled. No persistent kernel data is retained after allocations are freed.

## Dependencies and Integration Points
Compiled only into LKDTM powerpc categories under the corresponding architecture configuration. It depends on ppc64 hash MMU semantics and low-level assembly instructions.

## Risks
If platform SLB multihit recovery is broken, the machine may not survive. Running on radix MMU is unsupported and reported as expected failure.

## Test Signals
Signals are successful recovery from vmalloc, kmalloc, and bolted-entry multihit injections, plus `XFAIL` on radix mode. Any hang, machine check, or panic indicates a recovery regression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/powerpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/refcount.c -->
# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/refcount.c

## Purpose
`refcount.c` exercises `refcount_t` hardening behavior across overflow, zero, underflow, saturated-value operations, and performance comparison with `atomic_t`.

## Important APIs, Types, and Functions
Helper checkers are `overflow_check()`, `check_zero()`, `check_negative()`, `check_from_zero()`, and `check_saturated()`. Crashtypes cover `refcount_inc/add/inc_not_zero/add_not_zero`, `dec`, `dec_and_test`, `sub_and_test`, saturated cases, and timing tests `lkdtm_ATOMIC_TIMING()` and `lkdtm_REFCOUNT_TIMING()`.

## Control Flow
Each test initializes a local `refcount_t` at a boundary value, performs a known-good operation when useful, then performs the bad operation and checks whether the counter saturated, stayed pinned, reset unsafely, or wrapped. Timing tests run large increment/decrement loops and verify the terminal count.

## State and Persistence
All tested counters are local stack variables. No persistent state is used.

## Dependencies and Integration Points
Uses `<linux/refcount.h>`, `REFCOUNT_MAX`, `REFCOUNT_SATURATED`, and LKDTM category registration. Timing examples can be driven through debugfs and `perf stat`.

## Risks
These tests assume kernel `refcount_t` semantics and warn/fail around alternatives. Timing tests intentionally run very long loops. Some behaviors allow more than one acceptable protected outcome, such as saturation or zero pinning.

## Test Signals
Signals include saturation on overflow/underflow, no increment from zero through protected APIs, no movement from saturated values, warnings rather than wraparound, and timing tests ending with synchronized up/down cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/refcount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/rodata.c -->
# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/rodata.c

## Purpose
`rodata.c` supplies a minimal function intended to be placed entirely in `.rodata` by LKDTM build handling so permissions tests can attempt execution from rodata.

## Important APIs, Types, and Functions
The only symbol is `void noinstr lkdtm_rodata_do_nothing(void)`, declared in `lkdtm.h` and consumed by `perms.c`.

## Control Flow
The function returns immediately. Its behavior is intentionally trivial so the relevant signal is whether the memory section is executable, not function logic.

## State and Persistence
No state is used.

## Dependencies and Integration Points
Depends on LKDTM build/linker or objcopy behavior that places this function in rodata. `perms.c` calls `execute_location(dereference_function_descriptor(lkdtm_rodata_do_nothing), CODE_AS_IS)`.

## Risks
If build placement changes, the `EXEC_RODATA` test may validate the wrong memory permission. The `noinstr` annotation reduces instrumentation side effects.

## Test Signals
The key signal is that `EXEC_RODATA` faults when attempting to execute this function from a non-executable rodata mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/rodata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/usercopy.c -->
# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/usercopy.c

## Purpose
`usercopy.c` provides LKDTM tests for hardened `copy_to_user()` and `copy_from_user()` checks over slab object bounds, slab usercopy whitelists, stack frame boundaries, kernel text, vmalloc memory, and folio page spans.

## Important APIs, Types, and Functions
Core helpers are `do_usercopy_stack()`, `do_usercopy_slab_size()`, `do_usercopy_slab_whitelist()`, and `do_usercopy_page_span()`. Crashtypes include slab size/whitelist to/from tests, stack frame/beyond tests, `USERCOPY_KERNEL`, `USERCOPY_VMALLOC`, and `USERCOPY_FOLIO`. Init/exit manage `whitelist_cache`.

## Control Flow
Tests allocate user memory with `vm_mmap()`, prepare valid kernel buffers, perform a good copy, then perform a copy that should violate hardened usercopy constraints. Stack tests distinguish current-frame buffers, caller-frame buffers, and addresses beyond the stack. Slab whitelist tests use `kmem_cache_create_usercopy()` with a narrow allowed window. Page-span tests copy from halfway through a page-sized allocation and then attempt an over-span copy.

## State and Persistence
`unconst` and `cache_size` force runtime-sized checks. `whitelist_cache` persists from LKDTM init to exit and defines the permitted usercopy subrange.

## Dependencies and Integration Points
Depends on hardened usercopy, slab, vmalloc, folio allocation, user mappings, task stack helpers, and LKDTM expected-config diagnostics.

## Risks
The bad copies intentionally test fatal hardening paths. Without hardening, stack or heap memory may be corrupted. Compiler optimization is deliberately obscured to keep copies on runtime validation paths.

## Test Signals
Signals include good copies succeeding, bad copies faulting or oopsing, no final `FAIL: bad usercopy not detected`, correct whitelist enforcement, stack-frame rejection, kernel-text copy rejection, and vmalloc/folio page-span detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/usercopy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/Kconfig

## Purpose
This Kconfig entry defines `CONFIG_GP_PCI1XXXX`, the Microchip PCI1xxxx PCIe GPIO expander plus OTP/EEPROM manager driver.

## Important APIs, Types, and Functions
The symbol is `GP_PCI1XXXX`, tristate. It depends on `PCI`, `GPIOLIB`, and `NVMEM_SYSFS`, and selects `GPIOLIB_IRQCHIP` and `AUXILIARY_BUS`.

## Control Flow
Selecting the symbol builds the PCI parent driver and both auxiliary child drivers for GPIO and OTP/EEPROM support. The help text describes PCI1xxxx as a PCIe Gen3 switch endpoint exposing GPIO and OTP/EEPROM registers.

## State and Persistence
No runtime state is defined here; it controls build-time inclusion.

## Dependencies and Integration Points
Integrates the subsystem with the kernel configuration system and guarantees required GPIO IRQ and auxiliary bus infrastructure.

## Risks
`NVMEM_SYSFS` exposes EEPROM/OTP access through sysfs once the runtime driver registers nvmem devices. Disabling any dependency prevents the subsystem from building.

## Test Signals
Signals are correct Kconfig dependency resolution, module or built-in build of all three objects, and availability of auxiliary bus and GPIO IRQ helpers when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/Makefile

## Purpose
The Makefile binds `CONFIG_GP_PCI1XXXX` to the three source objects that implement the Microchip PCI1xxxx GP subsystem.

## Important APIs, Types, and Functions
The sole rule is `obj-$(CONFIG_GP_PCI1XXXX) := mchp_pci1xxxx_gp.o mchp_pci1xxxx_gpio.o mchp_pci1xxxx_otpe2p.o`.

## Control Flow
When enabled, Kbuild compiles and links the PCI parent, GPIO auxiliary driver, and OTP/EEPROM auxiliary driver.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Integrates with Kbuild and matches the Kconfig symbol. The object order ensures all modules are part of the same enabled feature set.

## Risks
Any source file added to the subsystem must be listed here or it will not build. A mismatch with Kconfig would produce missing driver functionality.

## Test Signals
Signals are successful Kbuild compilation and presence of the PCI, GPIO auxiliary, and OTP/EEPROM auxiliary drivers in the resulting module or built-in image.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/mchp_pci1xxxx_gp.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/mchp_pci1xxxx_gp.c

## Purpose
`mchp_pci1xxxx_gp.c` is the PCI parent driver for Microchip PCI1xxxx GP devices. It enables the PCI function, allocates two auxiliary devices, passes BAR/IRQ metadata to them, and tears them down on remove.

## Important APIs, Types, and Functions
Key pieces are `struct aux_bus_device`, global `gp_client_ida`, `gp_auxiliary_device_release()`, `gp_aux_bus_probe()`, `gp_aux_bus_remove()`, `pci1xxxx_tbl`, and `pci1xxxx_gp_driver`. It creates auxiliary names `gp_otp_e2p` and `gp_gpio`.

## Control Flow
Probe enables the PCI device, allocates parent-private storage, creates the OTP/EEPROM auxiliary device with BAR0 start/end metadata, initializes and adds it, then creates the GPIO auxiliary device, allocates one PCI IRQ vector, records `pdev->irq`, initializes/adds the GPIO child, sets driver data, and enables bus mastering. Error paths uninit auxiliary devices, free IDs, and free wrappers in reverse order.

## State and Persistence
State is per-PCI-device `struct aux_bus_device` containing two wrapper pointers. Auxiliary wrapper lifetime is reference-counted through `auxiliary_device` release, which frees the IDA id and wrapper memory.

## Dependencies and Integration Points
Uses PCI core, auxiliary bus, IDA allocation, IRQ vector allocation, and the shared `mchp_pci1xxxx_gp.h` wrapper metadata. Child drivers bind by auxiliary device names.

## Risks
The code stores `pci_resource_end()` in `region_length`, which semantically looks like an end address rather than a length; children use fixed map lengths, reducing immediate effect. IRQ vector allocation is not explicitly freed in remove. Error labels must preserve auxiliary-device init/uninit pairing.

## Test Signals
Signals are successful binding for listed Microchip device IDs, creation of both auxiliary devices, valid IRQ delivery to GPIO, clean remove without leaks, and correct unwind when auxiliary add or IRQ allocation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/mchp_pci1xxxx_gp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/mchp_pci1xxxx_gp.h -->
# sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/mchp_pci1xxxx_gp.h

## Purpose
`mchp_pci1xxxx_gp.h` defines the shared auxiliary-device wrapper used by the PCI parent and Microchip PCI1xxxx child drivers.

## Important APIs, Types, and Functions
`struct gp_aux_data_type` carries `irq_num`, `region_start`, and `region_length`. `struct auxiliary_device_wrapper` embeds `struct auxiliary_device aux_dev` and the shared `gp_aux_data` payload.

## Control Flow
The PCI parent fills the wrapper before auxiliary device registration. Child probe functions recover the wrapper with `container_of()` and read `gp_aux_data`.

## State and Persistence
The wrapper persists for the auxiliary device lifetime. Its release is implemented in the parent C file.

## Dependencies and Integration Points
Includes Linux spinlock, mutex, kthread, types, and auxiliary bus headers. It is the contract between `mchp_pci1xxxx_gp.c`, `mchp_pci1xxxx_gpio.c`, and `mchp_pci1xxxx_otpe2p.c`.

## Risks
The name `region_length` implies a length but the parent fills it from `pci_resource_end()`. Child drivers currently ignore it in favor of fixed sizes, but future users could misinterpret it.

## Test Signals
Signals are correct child `container_of()` recovery, valid BAR and IRQ metadata, and no lifetime bugs when auxiliary devices are removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/mchp_pci1xxxx_gp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/mchp_pci1xxxx_gpio.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/mchp_pci1xxxx_gpio.c

## Purpose
`mchp_pci1xxxx_gpio.c` implements the PCI1xxxx GPIO auxiliary driver. It exposes 93 GPIOs, pin configuration, IRQ mapping, wake masks, and suspend/resume register programming over MMIO.

## Important APIs, Types, and Functions
Main state is `struct pci1xxxx_gpio`. GPIO callbacks are direction/get/set/set_config helpers. IRQ callbacks are `pci1xxxx_gpio_irq_ack()`, mask/unmask, `pci1xxxx_gpio_set_type()`, `pci1xxxx_gpio_set_wake()`, and `pci1xxxx_gpio_irq_handler()`. Probe/setup are `pci1xxxx_gpio_probe()` and `pci1xxxx_gpio_setup()`. PM callbacks are suspend/resume.

## Control Flow
Probe maps BAR0, initializes locks, writes a global GPIO config value, requests the parent IRQ as a threaded IRQ, configures `gpio_chip` and immutable `irq_chip`, reads PCI revision, stores driver data, and registers the gpiochip. GPIO operations do locked read-modify-write operations on banked registers. The IRQ handler enables global interrupt processing, scans three banks, acknowledges set bits, maps each GPIO hwirq, and calls `generic_handle_irq()`.

## State and Persistence
Persistent runtime state includes MMIO base, GPIO chip, two locks, device revision, IRQ base field, and `gpio_wake_mask[3]`. Register state persists in device hardware across callbacks and is altered during suspend/resume.

## Dependencies and Integration Points
Depends on gpiolib, gpiolib IRQ chip helpers, PCI config access through the parent device, auxiliary bus matching, IRQ core, and pinconf parameters.

## Risks
Register access must be serialized; most paths use `priv->lock`, but `set_type()` does not take it. `wa_lock` is used without visible initialization in probe. The IRQ handler assumes status width per bank and valid IRQ mappings. PM wake mask polarity must match hardware expectations.

## Test Signals
Signals are GPIO line direction/value tests, pinconf pull/open-drain tests, edge and level IRQ delivery across all banks, wake-from-D3 behavior, suspend/resume register restoration, and race testing under concurrent GPIO and IRQ operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/mchp_pci1xxxx_gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/mchp_pci1xxxx_otpe2p.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/mchp_pci1xxxx_otpe2p.c

## Purpose
`mchp_pci1xxxx_otpe2p.c` implements the PCI1xxxx OTP/EEPROM auxiliary driver and registers NVMEM providers for byte-wise EEPROM and OTP access.

## Important APIs, Types, and Functions
Main state is `struct pci1xxxx_otp_eeprom_device`. Key helpers are `set_sys_lock()`, `release_sys_lock()`, `is_eeprom_responsive()`, EEPROM read/write callbacks, `otp_device_set_address()`, OTP read/write callbacks, `pci1xxxx_otp_eeprom_probe()`, and remove.

## Control Flow
Probe maps the PF3 system register window, acquires the system lock, powers OTP on, conditionally registers an EEPROM nvmem device if the EEPROM controller responds, releases the lock, then registers an OTP nvmem device. EEPROM operations lock PF3, clamp out-of-range count, perform one byte per busy-polled command, and release the lock. OTP operations set high/low address registers, issue read or byte-program commands, poll busy status, check pass/fail, and release the lock.

## State and Persistence
Driver state stores MMIO base and two `nvmem_config`/device pairs. Hardware persistence is the actual EEPROM/OTP contents; OTP writes are one-time programmable by device nature.

## Dependencies and Integration Points
Uses auxiliary bus metadata from the PCI parent, `devm_ioremap()`, `read_poll_timeout()`, and nvmem provider registration. With `NVMEM_SYSFS`, users can access exposed cells/files through sysfs.

## Risks
Byte-wise loops can be slow. OTP writes are irreversible and exposed through nvmem write callbacks. `set_sys_lock()` reads a 32-bit register into `u8`, which only validates low bits. Probe returns before releasing the sys lock if EEPROM nvmem registration fails after lock acquisition.

## Test Signals
Signals are successful OTP power-up/down, EEPROM responsiveness detection, bounded reads/writes at size edges, timeout/error behavior, sys lock release on errors, nvmem registration visibility, and safe behavior when EEPROM is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/mchp_pci1xxxx_otpe2p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/Kconfig

## Purpose
This Kconfig file defines the Intel MEI driver family and feature modules for PCI ME, TXE, GSC, CSC, VSC, late binding, HDCP, PXP, and GSC proxy support.

## Important APIs, Types, and Functions
Symbols include `INTEL_MEI`, `INTEL_MEI_ME`, `INTEL_MEI_TXE`, `INTEL_MEI_GSC`, `INTEL_MEI_CSC`, `INTEL_MEI_VSC_HW`, `INTEL_MEI_VSC`, and `INTEL_MEI_LB`. It sources sub-Kconfigs for `hdcp`, `pxp`, and `gsc_proxy`.

## Control Flow
Selecting `INTEL_MEI` enables the core `/dev/mei` infrastructure. Subsymbols pull in hardware transports and MEI bus clients depending on PCI, ACPI/SPI, graphics driver availability, and platform type.

## State and Persistence
No runtime state is stored; the file controls build-time availability.

## Dependencies and Integration Points
Integrates MEI with PCI, X86 defaults, Intel graphics drivers (`i915`/`xe`), ACPI/SPI VSC transport, and downstream MEI client drivers.

## Risks
Dependency expressions gate which MEI services exist. Graphics-related MEI clients must avoid enabling when the needed DRM driver is unavailable except for compile testing.

## Test Signals
Signals are correct Kconfig dependency resolution across x86, compile-test, built-in, and module builds, plus inclusion of sourced HDCP/PXP/GSC proxy menus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/Makefile

## Purpose
The MEI Makefile maps Kconfig symbols to the core MEI module, hardware transport modules, optional trace/debug pieces, graphics service clients, and VSC/LB modules.

## Important APIs, Types, and Functions
`mei.o` is composed from `init.o`, `hbm.o`, `interrupt.o`, `client.o`, `main.o`, `dma-ring.o`, `bus.o`, and `bus-fixup.o`, with `debugfs.o` and `mei-trace.o` conditional. Hardware modules include `mei-me.o`, `mei-gsc.o`, `mei-csc.o`, `mei-txe.o`, and VSC modules.

## Control Flow
Kbuild includes objects according to selected `CONFIG_INTEL_MEI*` options and descends into `hdcp/`, `pxp/`, and `gsc_proxy/` directories when their client drivers are enabled.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Integrates core MEI, PCI/TXE/GSC hardware, event tracing include flags, and client subdirectories with the kernel build.

## Risks
Object composition is part of the MEI internal ABI; omitting `client.o`, `bus.o`, or `bus-fixup.o` breaks exported MEI client functionality. Trace CFLAGS must stay aligned with generated trace headers.

## Test Signals
Signals are successful modular and built-in builds for each selected transport/client combination and correct module names such as `mei`, `mei-me`, `mei-gsc`, and `mei_gsc_proxy`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/bus-fixup.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/bus-fixup.c

## Purpose
`bus-fixup.c` applies policy and firmware-specific setup before MEI firmware clients are exposed on the MEI bus. It blacklists, whitelists, renames, or initializes special clients.

## Important APIs, Types, and Functions
Important hooks are `number_of_connections()`, `blacklist()`, `whitelist()`, `mei_mkhi_fix()`, `mei_gsc_mkhi_ver()`, `mei_gsc_mkhi_fix_ver()`, `mei_wd()`, `mei_nfc()`, `vt_support()`, `pxp_is_ready()`, and `mei_cl_bus_dev_fixup()`. It defines UUIDs for NFC, watchdog, MKHI, IGSC MKHI, HDCP, PAVP, and wildcard matching.

## Control Flow
`mei_cl_bus_dev_fixup()` iterates the `mei_fixups[]` table and runs hooks whose UUID matches the client or wildcard. Generic hooks reject multi-connection clients and enable vtag clients. MKHI hooks enable a client temporarily to fetch firmware version, report OS version, or send GSC memory-ready. NFC connects to an info GUID, reads radio version, derives a radio name, and updates the client device name. PXP exposure depends on bus `pxp_mode`.

## State and Persistence
It mutates `cldev->do_match`, `cldev->name`, watchdog protocol version, `bus->fw_ver[]`, `bus->fw_ver_received`, and `bus->pxp_mode`. No filesystem persistence.

## Dependencies and Integration Points
Uses MEI client send/recv/connect helpers, MKHI message formats, NFC message protocol, PCI IDs for watchdog version quirks, and MEI bus enumeration in `bus.c`.

## Risks
Fixups run during bus enumeration, so blocking firmware requests can delay device exposure. Incorrect UUID policy can hide valid clients or expose unsafe ones. NFC lock/unlock sequencing intentionally drops `device_lock` around I/O.

## Test Signals
Signals include filtered multi-connection clients, hidden NFC info client, renamed NFC HCI device, watchdog protocol correction on selected PCI IDs, populated firmware version fields, successful OS-version and GSC memory-ready commands, vtag-client matching, and PXP client exposure only when ready/default.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/bus-fixup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/bus.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/bus.c

## Purpose
`bus.c` implements the MEI client bus. It exports MEI client send/receive APIs, callback registration, enable/disable, client DMA mapping, GSC scatter-gather command support, MEI bus device matching/probing/removal, sysfs attributes, uevents, and firmware-client rescanning.

## Important APIs, Types, and Functions
Exported APIs include `mei_cldev_send*()`, `mei_cldev_recv*()`, `mei_cldev_register_rx_cb()`, `mei_cldev_register_notif_cb()`, `mei_cldev_enable()`, `mei_cldev_disable()`, `mei_cldev_dma_map/unmap()`, `mei_cldev_send_gsc_command()`, driver registration helpers, and bus init/exit. Internal foundations include `__mei_cl_send_timeout()`, `__mei_cl_recv()`, `mei_cl_bus_rescan()`, and `mei_cl_bus_dev_alloc/setup/add/destroy()`.

## Control Flow
Send validates bus state, connection, vtag support, MTU, and TX queue limits, allocates a write callback, copies data or extended headers, and calls `mei_cl_write()`. Receive starts flow control if no completed read exists, optionally waits, copies normal or GSC extended data, and frees the read callback. Device rescans allocate `mei_cl_device` wrappers for active firmware clients, run fixups, and add matching devices to the Linux device model. Driver probe matches UUID/name/version and invokes the MEI client driver.

## State and Persistence
State spans `mei_cl_device`, its embedded `mei_cl`, bus/device refs, callback work items, `do_match`, `is_added`, sysfs-visible firmware client properties, and driver-private data. No persistence beyond runtime device model state.

## Dependencies and Integration Points
Depends on `client.c` state machine, MEI HBM support, Linux driver core bus APIs, sysfs/uevent modaliases, scatterlist DMA addresses, runtime PM through lower layers, and MEI client drivers such as GSC proxy, HDCP, and PXP.

## Risks
Locking is split between `device_lock`, `cl_bus_lock`, read-completion spinlocks, and workqueues. Send/receive error paths must free callbacks exactly once. GSC command validation relies on DMA-mapped scatterlists and matching fence/client IDs. Bus references must outlive client devices.

## Test Signals
Signals are successful MEI bus registration, sysfs attributes (`name`, `uuid`, `version`, `modalias`, `max_conn`, `fixed`, `vtag`, `max_len`), client driver autoload via modalias, blocking/nonblocking send/recv behavior, callback invocation, enable/disable connect lifecycle, DMA map/unmap lifecycle, GSC command round trips, and clean rescan/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/client.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/client.c

## Purpose
`client.c` is the core MEI host-client and firmware-client state machine. It manages firmware client references, host client IDs, callback queues, connect/disconnect handshakes, flow-control credits, virtual tags, read/write fragmentation, notifications, forced disconnects, and per-client DMA map/unmap.

## Important APIs, Types, and Functions
Important groups are `mei_me_cl_*()` firmware-client reference/list helpers; `mei_cl_allocate/link/unlink/connect/disconnect`; callback allocation/free/queue helpers; `mei_cl_read_start()`, `mei_cl_write()`, `mei_cl_irq_write()`, `mei_cl_complete()`, notification helpers, and `mei_cl_dma_alloc_and_map()/mei_cl_dma_unmap()`. It works with `struct mei_cl`, `struct mei_me_client`, `struct mei_cl_cb`, and `struct mei_cl_vtag`.

## Control Flow
Firmware clients are discovered elsewhere and stored under `me_clients_rwsem` with krefs. Host clients link by allocating a host ID bit and entering `file_list`. Connect queues or sends an HBM connect request, waits for state transition, and sets disconnected on failure. Reads enqueue flow-control requests and completed callbacks. Writes build MEI headers, optional vtag/GSC extended headers, choose host-buffer or DMA-ring transfer, fragment as needed, consume TX credits, and queue for completion. Completion wakes waiters or schedules bus callbacks.

## State and Persistence
State includes client file state, writing state, status, host/me IDs, firmware client krefs/connect counts, RX/TX flow-control credits, vtag maps and pending-read flags, DMA mapping metadata, waitqueues, and queued callbacks. No disk persistence.

## Dependencies and Integration Points
Depends on HBM helpers, interrupt processing, DMA ring helpers, runtime PM, waitqueues, fasync notification, and MEI bus APIs. It is used by both `/dev/mei` file operations and MEI bus client drivers.

## Risks
This file is concurrency critical. Risks include callback double-free/leaks, stale firmware client refs, host ID leaks, flow-control credit imbalance, timeout recovery, incorrect vtag-to-file routing, runtime PM imbalance, and DMA buffer ID conflicts. The message-fragment and DMA-ring paths must preserve header lengths and completion semantics.

## Test Signals
Signals include connect/disconnect success and timeout handling, forced disconnect on reset, host-client ID exhaustion handling, TX queue limit waiting, MTU enforcement, read flow-control behavior, vtag routing, notification start/stop/events, large writes via fragmentation and DMA ring, client DMA map/unmap, and clean queue flushing on close/reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/client.h -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/client.h

## Purpose
`client.h` declares the internal MEI client API shared by core, bus, interrupt, HBM, and debugfs code.

## Important APIs, Types, and Functions
It declares firmware-client list/ref helpers, host-client allocation/linking, callback allocation/enqueue/flush, vtag helpers, connect/disconnect/read/write IRQ paths, notification conversion/request/event helpers, DMA map/unmap helpers, and debug print macros. Inline helpers expose client UUID, version, MTU, fixed address, host address, and connection state.

## Control Flow
Callers use the declarations to move clients through allocation, link, connect, I/O, notification, DMA, disconnect, queue flush, and unlink phases. Inline helpers centralize state/property interpretation.

## State and Persistence
The header owns no storage. It defines access patterns for state in `struct mei_device`, `struct mei_cl`, and `struct mei_me_client`.

## Dependencies and Integration Points
Includes `<linux/mei.h>` and `mei_dev.h`, and is consumed by `client.c`, `bus.c`, `bus-fixup.c`, `debugfs.c`, interrupt/HBM code, and MEI hardware paths.

## Risks
Prototype changes affect many MEI core files. Inline assumptions, such as fixed clients using host address zero, are protocol-significant.

## Test Signals
Signals are successful compilation of all MEI core objects and behavior parity for all call paths that use these shared declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/debugfs.c

## Purpose
`debugfs.c` exposes diagnostic MEI state under debugfs: firmware clients, active host clients, device/HBM/power-gating/PXP state, and a writable fixed-address override.

## Important APIs, Types, and Functions
Show functions are `mei_dbgfs_meclients_show()`, `mei_dbgfs_active_show()`, and `mei_dbgfs_devstate_show()`. Lifecycle functions are `mei_dbgfs_register()` and `mei_dbgfs_deregister()`. `mei_dbgfs_write_allow_fa()` wraps bool writes and marks `override_fixed_address`.

## Control Flow
Registration creates a debugfs directory and files `meclients`, `active`, `devstate`, and `allow_fixed_address`. Show callbacks lock either `me_clients_rwsem` or `device_lock`, validate enabled state before dumping volatile lists, and print compact tabular state. Deregistration removes the tree recursively.

## State and Persistence
Debugfs files reflect runtime `mei_device` fields and do not persist. Writing `allow_fixed_address` changes `dev->allow_fixed_address` and sets `override_fixed_address` until device teardown/reset.

## Dependencies and Integration Points
Depends on debugfs, seq_file, MEI device/client structures, HBM state string helpers, power-gating helpers, and client reference helpers.

## Risks
Debugfs is diagnostic and not a stable ABI. Dumps can be inconsistent if state changes outside the protected enabled window. The fixed-address override is a privileged test/debug control.

## Test Signals
Signals include correct file creation/removal, readable tables with active firmware clients, active host-client queue state, devstate feature flags, PXP mode strings, and writable `allow_fixed_address` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/dma-ring.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/dma-ring.c

## Purpose
`dma-ring.c` manages coherent DMA ring buffers used by MEI for larger host-to-firmware and firmware-to-host transfers.

## Important APIs, Types, and Functions
Public functions include `mei_dmam_ring_alloc()`, `mei_dmam_ring_free()`, `mei_dma_ring_is_allocated()`, `mei_dma_ring_reset()`, `mei_dma_ring_read()`, `mei_dma_ring_empty_slots()`, and `mei_dma_ring_write()`. Internal helpers allocate/free descriptors and copy to/from ring slots.

## Control Flow
Allocation iterates all DMA descriptors, requires power-of-two sizes, and uses managed coherent DMA allocation. Reset clears the control block. Reads compute device-buffer read index, copy wrapped or contiguous slots into the caller buffer, or drop data when buffer is NULL, then advance `dbuf_rd_idx`. Writes compute host-buffer write index, copy wrapped or contiguous slots, and advance `hbuf_wr_idx`. Empty-slot calculation compares host read/write indices.

## State and Persistence
State is in `dev->dr_dscr[]` descriptor virtual/dma addresses and the firmware-shared `hbm_dma_ring_ctrl` indices. Buffers are coherent memory tied to the MEI device lifetime.

## Dependencies and Integration Points
Uses DMA mapping APIs, MEI slot conversion helpers, and is called from `client.c` write/read paths and hardware/HBM setup.

## Risks
Descriptor sizes must be powers of two because index masking assumes it. Incorrect index handling corrupts ring contents. Empty-slot calculation leaves no explicit one-slot guard in this file, so it relies on protocol-level sizing/semantics.

## Test Signals
Signals include successful descriptor allocation/free, reset to zero indices, wraparound read/write correctness, drop-read advancement, empty-slot accounting under firmware-consumed indices, and large-message transfer through client write paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/dma-ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/gsc-me.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/gsc-me.c

## Purpose
`gsc-me.c` is the auxiliary MEI hardware driver for Intel Graphics System Controller devices exposed by i915 or xe. It maps GSC MMIO, configures interrupts or polling, registers a MEI device, starts firmware handshaking, and implements system/runtime PM.

## Important APIs, Types, and Functions
Key functions are `mei_gsc_probe()`, `mei_gsc_remove()`, `mei_gsc_read_hfs()`, `mei_gsc_set_ext_op_mem()`, system sleep callbacks, runtime PM callbacks, and the auxiliary ID table for `i915.mei-gsc`, `i915.mei-gscfi`, and `xe.mei-gscfi`.

## Control Flow
Probe selects a MEI hardware config, initializes `mei_device`, maps the supplied BAR, stores IRQ/read-status hooks, programs external operation memory when present and sets `pxp_mode` to init, then either starts a polling thread or requests a threaded IRQ. It registers MEI, enables runtime PM, starts MEI firmware handshake, sets autosuspend, and returns even if startup handshake fails after registration. Remove stops MEI, stops polling if used, disables PM/interrupts, frees IRQ when used, and deregisters.

## State and Persistence
State is in `mei_device`, `mei_me_hw`, mapped MMIO, IRQ or polling thread state, runtime PM state, external operation memory registers, and `pxp_mode`.

## Dependencies and Integration Points
Depends on `mei_aux_device` supplied by graphics drivers, MEI ME hardware helpers, runtime PM, kthreads, IRQ handlers, and trace register logging.

## Risks
Startup intentionally tolerates firmware handshake failure for status visibility, so later clients must handle partially initialized firmware. Polling-thread lifecycle and runtime PM active flags must remain balanced. External operation memory must be reprogrammed on resume before restart.

## Test Signals
Signals are successful auxiliary binding from i915/xe, MMIO mapping, IRQ or polling operation, MEI registration, firmware status sysfs visibility after handshake failure, PXP memory-ready progression, suspend/resume restart, runtime autosuspend only when writes are idle, and clean remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/gsc-me.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/gsc_proxy/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/gsc_proxy/Kconfig

## Purpose
This Kconfig file defines `CONFIG_INTEL_MEI_GSC_PROXY`, the MEI client driver for Intel GSC proxy services.

## Important APIs, Types, and Functions
The symbol is tristate, depends on `INTEL_MEI_ME`, and requires `DRM_I915`, `DRM_XE`, or `COMPILE_TEST` availability.

## Control Flow
When selected, the build includes the GSC proxy MEI bus client that lets Intel graphics proxy messages between GSC service and CSE/ME firmware.

## State and Persistence
No runtime state is defined here.

## Dependencies and Integration Points
Integrates GSC proxy support with MEI ME hardware and Intel graphics drivers.

## Risks
The dependency must keep proxy code aligned with graphics component interfaces; enabling without a compatible graphics stack is limited to compile testing.

## Test Signals
Signals are correct menu visibility, module build when selected, and dependency behavior for i915, xe, and compile-test configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/gsc_proxy/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/gsc_proxy/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/gsc_proxy/Makefile

## Purpose
This Makefile builds the Intel MEI GSC proxy client driver when `CONFIG_INTEL_MEI_GSC_PROXY` is enabled.

## Important APIs, Types, and Functions
The sole build rule is `obj-$(CONFIG_INTEL_MEI_GSC_PROXY) += mei_gsc_proxy.o`.

## Control Flow
Kbuild compiles `mei_gsc_proxy.c` into a module or built-in object according to the Kconfig symbol.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Connects the `gsc_proxy` subdirectory to the MEI top-level Makefile and Kconfig.

## Risks
A symbol/object mismatch would silently omit the proxy driver.

## Test Signals
Signals are successful module build and presence of the `mei_gsc_proxy` MEI client driver when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/gsc_proxy/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/gsc_proxy/mei_gsc_proxy.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/gsc_proxy/mei_gsc_proxy.c

## Purpose
`mei_gsc_proxy.c` is a MEI bus client that bridges Intel graphics GSC proxy component users to ME firmware through MEI send/receive operations.

## Important APIs, Types, and Functions
Important routines are `mei_gsc_proxy_send()`, `mei_gsc_proxy_recv()`, component master bind/unbind callbacks, `mei_gsc_proxy_component_match()`, `mei_gsc_proxy_probe()`, and `mei_gsc_proxy_remove()`. The MEI UUID is `MEI_UUID_GSC_PROXY`.

## Control Flow
Probe enables the MEI client, allocates an `i915_gsc_proxy_component`, builds a typed component match for an Intel VGA PCI device on bus 0 with `I915_COMPONENT_GSC_PROXY`, stores driver data, and registers a component master. Bind publishes MEI-backed send/recv ops and the MEI device pointer to the graphics component, then binds subcomponents. Remove unregisters the component master, frees state, clears driver data, and disables the MEI client.

## State and Persistence
State is the allocated `i915_gsc_proxy_component` stored as MEI client driver data, plus the enabled MEI connection. There is no persistence.

## Dependencies and Integration Points
Depends on MEI client bus APIs, Linux component framework, PCI device matching, DRM Intel i915 component interfaces, and graphics GSC proxy headers.

## Risks
The component match intentionally rejects discrete graphics by requiring PCI bus 0. Send/recv are thin wrappers, so MEI connection loss propagates directly. Allocation or component registration failure must disable the MEI client to avoid leaked connections.

## Test Signals
Signals are MEI UUID driver match, successful `mei_cldev_enable()`, component binding to integrated Intel VGA, functioning proxy send/recv, clean unbind/remove, and rejection of non-Intel/non-VGA/discrete or wrong subcomponent devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/gsc_proxy/mei_gsc_proxy.c -->
