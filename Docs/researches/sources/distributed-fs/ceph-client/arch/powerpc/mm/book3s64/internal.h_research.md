# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/internal.h

Purpose: Provides small internal declarations for Book3S64 MMU stress/static-key controls shared by hash and SLB code in this directory.

Important APIs and types: Declares `stress_slb_enabled`, `stress_hpt_enabled`, and `no_slb_preload`, plus static keys `stress_slb_key`, `stress_hpt_key`, and `no_slb_preload_key`. Inline helpers `stress_slb()`, `stress_hpt()`, and `slb_preload_disabled()` wrap `static_branch_unlikely()`. Declares `hpt_do_stress()`.

Control flow: Callers check the inline helpers in hot paths. Boot-time parsing in other files sets the booleans and early MMU initialization enables the static keys. When `stress_hpt()` is true, hash insertion paths call `hpt_do_stress()` after successful insertion to increase HPT churn.

State and persistence: State is global boot-lifetime boolean/static-key state. Static keys allow near-zero overhead in normal operation while enabling stress code dynamically during early boot.

Dependencies and integration: Depends on Linux jump labels. `hash_utils.c` defines `stress_hpt_enabled`, `stress_hpt_key`, and `hpt_do_stress()`. SLB code outside this file set likely defines the SLB symbols. `hash_64k.c` and related insertion paths include this header for `stress_hpt()`.

Risks: Header declarations must match exactly one definition elsewhere or link failures result. Static key enablement must occur after jump-label infrastructure is ready and before hot paths rely on it. Stress hooks are intentionally disruptive and should remain gated.

Test signals: Build coverage with and without hash/SLB stress options, boot with `stress_hpt` and SLB preload controls, and verify no overhead/regression in default boot.
