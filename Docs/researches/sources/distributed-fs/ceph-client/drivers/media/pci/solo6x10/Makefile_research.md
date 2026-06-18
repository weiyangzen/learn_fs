<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/Makefile

Purpose: kbuild object list for the SOLO6x10 driver.

Important APIs, types, and functions: composes `solo6x10.o` from core, I2C, P2M DMA, V4L2 display, TW28 decoder, GPIO, display register setup, encoder setup, V4L2 encoder, G.723 audio, and EEPROM objects.

Control flow: when `CONFIG_VIDEO_SOLO6X10` is enabled, kbuild links all listed objects into one module/built-in object.

State and persistence: no runtime state.

Dependencies and integration points: all SOLO6x10 submodules must match prototypes in `solo6x10.h`.

Risks: object order can matter for init/exit references only at link time; missing any source in the list breaks subsystem registration. The Makefile includes both low-level setup and user-facing V4L2/ALSA modules in one binary.

Test signals: `make M=drivers/media/pci/solo6x10`, link success, and module symbol coverage for each init/exit function called by core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/Makefile -->
