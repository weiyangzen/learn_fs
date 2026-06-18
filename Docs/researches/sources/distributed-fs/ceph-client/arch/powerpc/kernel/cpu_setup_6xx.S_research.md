<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_6xx.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_6xx.S

Purpose: Provides low-level setup, cache/HID tuning, FPU initialization, and save/restore routines for 6xx/7xx/74xx Book3S 32-bit PowerPC CPUs.

Important APIs/types/functions: Setup entry points for 603, 604, 750 variants, 7400/7410/745x; helpers `setup_common_caches`, `setup_604_hid0`, `setup_g2_le_hid2`, workaround helpers, `setup_750_7400_hid0`, `setup_745x_specifics`, `__init_fpu_registers`, `__save_cpu_setup`, and `__restore_cpu_setup`.

Control flow: Setup routines preserve LR, initialize FPU when needed, enable/invalidate caches, set HID0/HID2/MSSCR/L2 prefetch and errata bits, adjust CPU feature flags such as NAP, and return. Save/restore stores selected SPRs into `cpu_state_storage` for sleep/resume and restores them with sync/isync ordering.

State and persistence: Mutates HID0/HID1/HID2, MSSCR0/MSSSR0, ICTC, L2CR2, L3/NAP-related feature flags, FPU register contents, and static `cpu_state_storage`.

Dependencies and integration points: Depends on CPU feature fixups, SPR definitions, cache constants, CPU spec layout offsets, and power-management callers.

Risks: SPR programming order and barriers are hardware-sensitive. Errata checks are revision-specific; wrong feature flag mutation can disable idle modes or leave caches misconfigured.

Test signals: PPC_BOOK3S_32 boot across 603/604/750/74xx, suspend/resume, cache/FPU smoke tests, NAP behavior tests, and assembly build coverage.

Source read size: 516 lines, 12010 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_6xx.S -->
