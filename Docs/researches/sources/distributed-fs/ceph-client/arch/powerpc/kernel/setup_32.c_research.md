# sources/distributed-fs/ceph-client/arch/powerpc/kernel/setup_32.c

Purpose: 32-bit PowerPC early boot and setup helpers for relocated MMU-enabled startup, cache command-line overrides, interrupt/emergency stack allocation, BookE exception stacks, power-save callback selection, and default cache-info initialization.

Important APIs/types/functions: globals `boot_cpuid_phys`, `smp_hw_index`, `DMA_MODE_READ`, `DMA_MODE_WRITE`; `machine_init()`, boot params `l2cr=` and `l3cr=`, `ppc_init()`, `irqstack_early_init()`, VMAP `emergency_stack_init()`, BookE `exc_lvl_early_init()`, `setup_power_save()`, and `initialize_cache_info()`.

Control flow: `machine_init()` runs before `start_kernel()` after relocation, enables feature keys, early ioremap/debug, patches nocache copy/memset behavior, parses the flat device tree, initializes MMU, and sets up the kdump trampoline. Later arch init clears progress display and calls platform `ppc_md.init()`. Stack helpers allocate per-CPU hardirq/softirq and BookE critical/debug/machine-check stacks from memblock. Cache command-line options directly program L2CR/L3CR on CPUs that support them. `setup_power_save()` chooses 6xx or e500 idle callbacks based on CPU features.

State and persistence: establishes exported 32-bit boot CPU/hardware indexes, DMA mode globals, early stacks, optional emergency contexts, platform init side effects, and cache controller register settings.

Dependencies and integration points: depends on flat device-tree early parsing, feature fixups/text patching, kdump, early ioremap, platform machine callbacks, BookE exception arrays, CPU feature tables, and common setup hooks.

Risks: early boot code runs with limited services; wrong patching or device-tree pointer handling prevents boot. `l2cr=`/`l3cr=` are raw privileged hardware overrides. Stack allocation must stay in reachable low memory for early exception paths. BookE hardware CPU indexing must match SMP mappings.

Test signals: PPC32 boot matrix including Book3S and BookE, kdump boot, command-line cache override smoke tests on supported hardware, interrupt stack sanity under IRQ load, and idle/power-save behavior.
