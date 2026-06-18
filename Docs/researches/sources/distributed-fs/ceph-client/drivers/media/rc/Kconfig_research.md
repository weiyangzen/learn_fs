<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/rc/Kconfig

Purpose: top-level Kconfig menu for Linux remote-controller core support, LIRC/raw IR interfaces, protocol decoders, and standalone IR/RF receiver/transmitter drivers.

Important APIs and symbols: `RC_CORE` gates the subsystem and depends on input. `BPF_LIRC_MODE2` enables eBPF attachment to LIRC raw devices when `RC_CORE=y`, `LIRC`, and `BPF_SYSCALL` are present. `LIRC` enables `/dev/lirc*`. `RC_DECODERS` gates protocol decoder tristates such as NEC, RC5, RC6, JVC, Sony, Sanyo, Sharp, XMP, MCE keyboard, iMON, and RC-MM. `RC_DEVICES` gates hardware drivers including ENE, Fintek, GPIO RX/TX, USB receivers/transceivers, Super I/O CIR devices, serial/SPI/PWM transmitters, ATI/X10 RF remotes, loopback, ST, and Xbox DVD receiver. It sources keymaps and ImgTec IR Kconfig files.

Control flow: the selected symbols drive the rc Makefile, which builds the rc core, raw decoders, keymaps, and hardware drivers. Dependencies constrain drivers to required buses, architecture features, PNP, GPIO, PWM, USB, LIRC, timers, or compile-test paths.

State and persistence: no runtime state. Config selections persist in the kernel config and determine available modules and built-in decoders/devices.

Dependencies and integration points: integrates media rc-core with Linux input, BPF, LIRC, USB, PNP, OF/GPIO, PWM, SPI, architecture-specific SoC drivers, LEDs, and the `img-ir` subdirectory.

Risks: dependency accuracy is critical because many drivers perform direct I/O port or timing-sensitive operations. `BPF_LIRC_MODE2` requires built-in rc-core (`RC_CORE=y`), so it is not available for modular rc-core. Some help text exposes hardware limitations, such as IgorPlugUSB's very small pulse buffer.

Test signals: Kconfig dependency tests, `allmodconfig`/`randconfig`, module build matrix, and runtime checks that selected decoders/devices register expected rc-core capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/Kconfig -->
