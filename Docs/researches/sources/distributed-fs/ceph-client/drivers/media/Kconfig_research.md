# sources/distributed-fs/ceph-client/drivers/media/Kconfig

Purpose: This top-level media Kconfig file defines the user-visible multimedia subsystem menu and sources the subordinate Kconfig trees for remote controllers, CEC, V4L2, DVB, media controller, platform drivers, test drivers, and ancillary drivers. It explicitly keeps CEC and remote-controller support outside the `MEDIA_SUPPORT` dependency so those subsystems can be enabled independently.

Important APIs, types, and functions: Kconfig symbols include `MEDIA_SUPPORT`, `MEDIA_SUPPORT_FILTER`, `MEDIA_SUBDRV_AUTOSELECT`, media device-type selectors (`MEDIA_CAMERA_SUPPORT`, `MEDIA_ANALOG_TV_SUPPORT`, `MEDIA_DIGITAL_TV_SUPPORT`, `MEDIA_RADIO_SUPPORT`, `MEDIA_SDR_SUPPORT`, `MEDIA_PLATFORM_SUPPORT`, `MEDIA_TEST_SUPPORT`), core API selectors (`VIDEO_DEV`, `MEDIA_CONTROLLER`, `DVB_CORE`), `MEDIA_HIDE_ANCILLARY_SUBDRV`, and `MEDIA_ATTACH`.

Control flow and state: Kconfig flow starts by sourcing RC and CEC support unconditionally, then presents `menuconfig MEDIA_SUPPORT`. When enabled, filter and device-type choices set defaults for V4L2/DVB/media-controller core symbols, which then source their option submenus. Driver menus conditionally source USB/PCI/radio/platform/mmc/test/firewire/common and ancillary I2C/SPI/tuner/frontend trees. `MEDIA_SUPPORT_FILTER` controls whether users see a focused set of driver classes or all core functionality.

State and persistence behavior: Build selections are persisted in kernel `.config`; there is no runtime state. Defaults depend on whether the user selected filtering, expert mode, module support, and digital-TV/media-platform/test support.

Dependencies and integration points: The file integrates the media subsystem with `HAS_IOMEM`, `I2C`, `I2C_MUX`, `MODULES`, `CRC32`, V4L2, DVB, media controller, RC, and CEC Kconfig namespaces. Its sourcing order is important because it exposes CEC/RC even without `MEDIA_SUPPORT` and allows ancillary drivers to be hidden unless selected automatically.

Risks and edge cases: Mis-gating can hide required drivers or silently disable hardware functionality on embedded systems. `MEDIA_SUBDRV_AUTOSELECT` is convenient but can pull in broad ancillary dependencies; disabling it can create kernels that build but lack required tuners/sensors/frontends. CEC/RC independence means users may see those options even when the rest of media is off.

Test signals: Kernel config tests should verify expected visibility/defaults for expert and non-expert configs, allnoconfig/allyesconfig/modular builds, `MEDIA_SUPPORT=n` with CEC or RC enabled, and platform-only embedded configurations with autoselect disabled.
