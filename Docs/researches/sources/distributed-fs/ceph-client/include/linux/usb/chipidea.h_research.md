<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/chipidea.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/chipidea.h

Purpose: defines platform data, flags, cable state, hooks, and device-management APIs for the ChipIdea dual-role USB controller driver.

Important APIs and types: `struct ci_hdrc_cable` tracks extcon cable connection/change/enabled state and notifier registration. `struct ci_hdrc_platform_data` carries register offsets, power budget, PHY pointers/mode, many quirk flags, dual-role mode, notifier callback, VBUS regulator, OTG caps, TPL support, interrupt/burst tuning, VBUS/ID extcon state, PHY clock gate delay, pinctrl states, hub-control hook, and low-power-mode hook. APIs add/remove a ChipIdea platform device and query available role.

Control flow: glue drivers fill platform data and call `ci_hdrc_add_device()`. The ChipIdea core uses flags and hooks to initialize host/device/OTG roles, manage PHY/regulator/pinctrl/extcon state, notify platform events, handle role switching, and apply hardware workarounds.

State and persistence: platform data is boot/probe-time configuration; cable structs hold runtime extcon state. Hardware controller state and role state live in the ChipIdea driver.

Dependencies and integration points: depends on extcon, USB OTG, regulators, PHY, pinctrl, platform devices, and hub-control integration. It bridges SoC glue layers to the generic ChipIdea controller.

Risks and test signals: risks include incompatible flag combinations, extcon notification races, VBUS/regulator ordering, dual-role-not-OTG confusion, DMA alignment constraints, and platform hook failures. Test host/device/dual-role modes, cable insertion/removal, suspend/resume, role switching, pinctrl transitions, and SoC-specific quirk coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/chipidea.h -->
