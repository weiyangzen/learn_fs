<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/rzv2h-ivc-dev.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/rzv2h-ivc-dev.c

Purpose: platform-device, runtime-PM, MMIO helper, resource acquisition, global configuration, and IRQ dispatch layer for the RZ/V2H(P) Input Video Control block. Video queue and subdevice details live in sibling composite objects.

Important APIs, types, and functions: exports internal helpers `rzv2h_ivc_write()` and `rzv2h_ivc_update_bits()` for register access. `rzv2h_ivc_get_hardware_resources()` maps MMIO and acquires three named clock/reset resources: `reg`, `axi`, and `isp`. `rzv2h_ivc_global_config()` programs single-exposure input, disables interrupts while changing context mode, selects single-context software/hardware configuration, and enables frame-end interrupt. `rzv2h_ivc_isr()` coordinates two interrupts per frame with `ivc->vvalid_ifp`, calling `rzv2h_ivc_buffer_done()` after transfer completion and `rzv2h_ivc_transfer_buffer()` after post-frame VBLANK. Runtime PM handlers enable/disable clocks, deassert/assert resets, configure hardware, request/free IRQ, and integrate with system sleep. Probe initializes locks, resources, autosuspend, IRQ number, and the subdevice.

Control flow: probe allocates `struct rzv2h_ivc`, initializes mutex/spinlock, maps resources, enables autosuspend runtime PM, gets the IRQ, and delegates media/subdevice initialization to `rzv2h_ivc_initialise_subdevice()`. Runtime resume powers hardware, configures global mode, and requests IRQ. Runtime suspend asserts resets, disables clocks, and frees IRQ. IRQ runs under spinlock and expects `vvalid_ifp` to be initialized to two events when a frame transfer is active.

State and persistence: device state is volatile in `struct rzv2h_ivc` from `rzv2h-ivc.h`, including MMIO base, clocks, resets, locks, IRQ number, and transfer counters. No persistent storage. Autosuspend delay is 2000 ms.

Dependencies and integration points: platform driver, OF compatible `renesas,r9a09g057-ivc`, runtime PM, system sleep PM, clk/reset bulk APIs, IRQ framework, and sibling IVC video/subdev modules through internal helper calls.

Risks: `pm_runtime_enable()` is not devm-managed and remove does not visibly disable runtime PM in this file, so sibling cleanup or core behavior must cover it. Requesting/freeing IRQ on every runtime resume/suspend is valid but sensitive to balanced PM usage. `rzv2h_ivc_isr()` warns if `vvalid_ifp` is zero; incorrect video-side initialization can make interrupts noisy or drop frames. Runtime suspend frees IRQ after clocks/resets are disabled, which should be verified against possible pending interrupts.

Test signals: build the composite module; probe with all three clock/reset names present and absent optional resets; runtime PM autosuspend/resume while streaming and idle; trigger frame transfers and verify the two-interrupt sequence; unbind/remove after active use; run media/v4l2 compliance through sibling video node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/rzv2h-ivc-dev.c -->
