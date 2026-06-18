<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/Kconfig -->
# sources/distributed-fs/ceph-client/arch/um/drivers/Kconfig

Purpose: declares UML driver configuration options for character channels, consoles, sound, vector networking, virtio/vhost-user, RTC wakeup, and PCI emulation/passthrough. It determines which channel backends and device families are compiled into the UML architecture driver directory.

Important APIs/types/functions: key symbols are `STDERR_CONSOLE`, `SSL`, `NULL_CHAN`, `PORT_CHAN`, `PTY_CHAN`, `TTY_CHAN`, `XTERM_CHAN`, `XTERM_CHAN_DEFAULT_EMULATOR`, `NOCONFIG_CHAN`, `CON_ZERO_CHAN`, `CON_CHAN`, `SSL_CHAN`, `UML_SOUND`, `UML_NET_VECTOR`, `VIRTIO_UML`, `UML_RTC`, `UML_PCI`, `UML_PCI_OVER_VIRTIO`, `UML_PCI_OVER_VIRTIO_DEVICE_ID`, and `UML_PCI_OVER_VFIO`.

Control flow: Kconfig presents character-device options first, derives `NOCONFIG_CHAN` when any channel backend is absent, sets default command-line channel strings, then exposes network and virtio/PCI/RTC options with dependencies and selects.

State and persistence: selections persist in `.config` and control object inclusion in `drivers/Makefile`. Default strings become compiled-in defaults used by `stdio_console.c` and `ssl.c`.

Dependencies and integration points: integrates with generic `NET`, `SOUND`, `SOUND_OSS_CORE`, `VIRTIO`, `RTC_CLASS`, `PM_SLEEP`, PCI/MSI helpers, UML I/O memory and DMA emulation, and runtime dependency handling through `MAY_HAVE_RUNTIME_DEPS`.

Risks: channel defaults can reference a backend configured out of the build, causing runtime `not_configged_ops` failures. `UML_NET_VECTOR` depends on host kernel/libc capabilities and runtime components. `UML_RTC` is intentionally tied to suspend/time-travel usefulness.

Test signals: build matrix with each channel enabled/disabled, boot with `con=` and `ssl=` defaults, verify missing backends report clear errors, exercise vector network config parsing, and validate virtio/PCI options select required lower-level support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/Kconfig -->
