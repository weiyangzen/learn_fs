# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp_kms.c

Purpose: Implements generic MDP IRQ registration, dispatch, mask aggregation, vblank mask updates, and short IRQ wait helper shared by MDP generations.

Important APIs/functions: `mdp_irq_register()` and `mdp_irq_unregister()` add/remove transient `struct mdp_irq` handlers. `mdp_dispatch_irqs()` walks registered handlers matching the IRQ status and invokes callbacks outside the list lock. `mdp_update_vblank_mask()` toggles userspace vblank IRQ bits. `mdp_irq_update()` recomputes the hardware IRQ mask. `mdp_irq_wait()` registers a temporary handler and waits up to 100 ms for a mask.

Control flow: The module keeps a global `list_lock` and wait queue. `update_irq()` ORs the vblank mask with all registered handler masks and calls the generation-specific `set_irqmask()` hook with old/new masks. Dispatch marks `in_irq` to defer immediate hardware mask updates while callbacks may register/unregister handlers, then recomputes the mask after the pass.

State and persistence: Per-KMS IRQ state lives in `struct mdp_kms`: handler list, current mask, vblank mask, and `in_irq`. The wait helper uses stack state and a global wait queue. No persistent storage exists.

Dependencies/integration: Used by MDP4/MDP5 IRQ code, CRTC vblank/commit wait paths, and CTL/encoder housekeeping. Requires `mdp_kms_funcs->set_irqmask`.

Risks and test signals: The lock is global, so multiple MDP devices would serialize and share the wait queue. Callback invocation outside the lock requires handler lifetime to be valid until unregister completes. `mdp_irq_wait()` has a fixed timeout and does not return status. Test vblank enable/disable, nested register/unregister from IRQ handlers, commit-done waits, and IRQ mask transitions under concurrent CRTCs.
