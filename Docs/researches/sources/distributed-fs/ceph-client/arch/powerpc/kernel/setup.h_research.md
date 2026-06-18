# sources/distributed-fs/ceph-client/arch/powerpc/kernel/setup.h

Purpose: private header sharing setup prototypes and config-dependent stubs among `setup-common.c`, `setup_32.c`, `setup_64.c`, and closely related architecture code.

Important APIs/types/functions: declarations for `initialize_cache_info()`, `irqstack_early_init()`, `setup_power_save()`, `check_smt_enabled()`, `setup_tlb_core_data()`, `exc_lvl_early_init()`, `emergency_stack_init()`, `ppc64_bolted_size()`, `spr_default_dscr`, `kvm_cma_reserve()`, and TAU temperature helpers.

Control flow: no runtime logic except inline no-op stubs selected when configs do not provide a feature. This lets the common setup path call architecture-specific hooks unconditionally.

State and persistence: declares exported setup-time state but owns none. `spr_default_dscr` preserves firmware/kexec DSCR default on PPC64.

Dependencies and integration points: ties common setup code to PPC32 power-save, PPC64 SMT/TLB/bolted-memory helpers, BookE exception stacks, VMAP/emergency stacks, KVM CMA reservation, and TAU thermal support.

Risks: incorrect config guards here cause link failures or silently skip required setup. Because common setup calls these names early, a wrong stub can become a boot-time functional bug rather than a local compile issue.

Test signals: compile matrix across PPC32, PPC64, SMP, BookE, VMAP_STACK, KVM HV, and TAU configurations; check that `setup_arch()` links and that expected hooks are non-stubbed under the right configs.
