# sources/distributed-fs/ceph-client/drivers/gpib/eastwood/Makefile

Purpose: builds the Fluke/Eastwood GPIB adapter module when `CONFIG_GPIB_FLUKE` is enabled. The single kbuild line maps the configuration symbol to `fluke_gpib.o`.

Important build API: uses standard `obj-$(CONFIG_GPIB_FLUKE) += fluke_gpib.o` syntax. The resulting module contains the platform driver for compatible `flk,fgpib-4.0` devices and the three registered GPIB board interfaces (`fluke_unaccel`, `fluke_hybrid`, and `fluke`).

Control flow and integration: this module depends on `gpib_common` exports and NEC7210 helper symbols. It must be selected only in configurations that provide platform-device and DMAengine support needed by `fluke_gpib.c`.

State and persistence: no runtime state is encoded in the Makefile. The build choice determines whether user space can select Fluke board types through `CFCBOARDTYPE`.

Dependencies: Kconfig should enforce dependencies on the GPIB common core, NEC7210 support, platform bus, MMIO, and DMAengine facilities.

Risks: if `CONFIG_GPIB_FLUKE` can be enabled without the common GPIB module or DMAengine symbols, link or load failures will occur. Since all three Fluke board interfaces live in the same object, there is no build-time way to include only unaccelerated support.

Test signals: build with `CONFIG_GPIB_FLUKE=m`, verify `modpost` dependencies, load the module on a kernel with and without matching platform devices, and confirm `gpib_register_driver` exposes all three interface names.
