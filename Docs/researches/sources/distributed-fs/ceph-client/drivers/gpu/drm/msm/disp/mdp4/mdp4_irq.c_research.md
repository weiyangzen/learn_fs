# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_irq.c

Purpose: provides MDP4 interrupt mask programming, install/uninstall hooks, top-level IRQ dispatch, vblank mask control, and underrun error reporting.

Important APIs and functions: `mdp4_set_irqmask()` writes clear and enable registers; `mdp4_irq_preinstall()` clears/disables interrupts; `mdp4_irq_postinstall()` registers the underrun error handler; `mdp4_irq_uninstall()` disables interrupts; `mdp4_irq()` reads enabled status, clears handled bits, dispatches MDP callbacks, and notifies DRM vblank; `mdp4_enable_vblank()` and `mdp4_disable_vblank()` update the MDP vblank mask.

Control flow: the IRQ handler masks raw status with enabled bits, clears those bits, lets the shared MDP dispatcher invoke registered `mdp_irq` callbacks, then loops CRTCs to call `drm_crtc_handle_vblank()` for matching CRTC vblank masks.

State and persistence: hardware interrupt enable/clear registers and shared MDP IRQ registration state. The file itself keeps no persistent state except static ratelimit state in the error handler.

Dependencies and integration: integrates with `mdp_kms` IRQ registration, DRM vblank core, `mdp4_crtc_vblank()`, and optional global `dumpstate` for ratelimited state dumps.

Risks: top-level handler always returns `IRQ_HANDLED`, even if no enabled status bits were active. Vblank mask updates temporarily enable clocks around register access. Error reporting is ratelimited, which can hide frequent underrun details.

Test signals: interrupt install/uninstall, vblank enable/disable, page flip completion, underrun injection, and dumpstate-triggered DRM state dumps.
