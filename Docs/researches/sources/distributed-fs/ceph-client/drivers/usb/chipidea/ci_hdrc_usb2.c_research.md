# sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_usb2.c

Purpose: provides generic OF/platform glue for ChipIdea USB2 controllers, with optional clock management and match-specific platform data for Zynq and Zevio.

Important APIs/types/functions: defines `struct ci_hdrc_usb2_priv`, default/Zynq/Zevio `ci_hdrc_platform_data`, OF match table, `ci_hdrc_usb2_probe`, and `ci_hdrc_usb2_remove`.

Control flow: probe uses existing platform data or allocates default data, overrides it with match data when present, enables an optional clock, sets the platform name, creates the `ci_hdrc` child, stores private state, and enables no-callback runtime PM. Remove disables runtime PM, removes the child, and disables the clock.

State and persistence: private state stores child platform device and clock. Platform data persists in the child device copy created by `ci_hdrc_add_device`.

Dependencies and integration: integrates with OF match data, common clock, runtime PM, PHY/VBUS platform flags, and core ChipIdea child registration.

Risks: match data struct-copy overwrites any preexisting platform data fields, which is intended for compatible-specific defaults but could discard board-provided values if both are supplied. Clock enable failure blocks probe.

Test signals: generic, Zynq, and Zevio compatible probes; optional-clock absence; child probe deferral; and remove/unbind cleanup.
