# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_irq.c

Purpose: implements MDP5 interrupt mask programming, install/uninstall hooks, top-level interrupt dispatch, vblank mask control, and underrun error reporting.

Important APIs and functions: `mdp5_set_irqmask()` writes interrupt clear and enable registers; `mdp5_irq_preinstall()` clears/disables interrupts under runtime PM; `mdp5_irq_postinstall()` registers underrun error handling; `mdp5_irq_uninstall()` disables interrupts; `mdp5_irq()` clears active enabled status, dispatches registered MDP IRQ callbacks, and notifies DRM vblank for matching CRTCs; `mdp5_enable_vblank()` and `mdp5_disable_vblank()` update the shared vblank mask under runtime PM.

Control flow: pre/post/uninstall wrap register access in `pm_runtime_get_sync()`/`put_sync()`. The IRQ handler reads enabled and status registers without explicit PM wrapping because it runs for active hardware, clears status, calls `mdp_dispatch_irqs()`, then calls `drm_crtc_handle_vblank()` for CRTCs whose current vblank mask matches.

State and persistence: hardware interrupt enable/status registers and shared MDP IRQ registration state. Static ratelimit state throttles optional dump output.

Dependencies and integration: used by MDP5 KMS ops, CRTC vblank/pp_done/error callbacks, DRM vblank core, runtime PM, and optional global `dumpstate`.

Risks: always returns `IRQ_HANDLED`; spurious IRQ accounting is not exposed. If runtime PM state is inconsistent, mask updates can fail or race. Ratelimited error logs may hide repeated underruns.

Test signals: vblank enable/disable, page flip completion, command-mode pp_done delivery through dispatch, underrun injection, suspend/resume mask restore, and dumpstate-triggered DRM state dump.
