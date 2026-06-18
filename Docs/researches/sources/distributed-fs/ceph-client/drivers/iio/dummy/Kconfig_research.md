# sources/distributed-fs/ceph-client/drivers/iio/dummy/Kconfig

Purpose: Kconfig menu for IIO dummy/reference drivers. It declares the software dummy device, optional fake event generator, and optional triggered buffer support.

Important symbols: `IIO_DUMMY_EVGEN` is a hidden tristate that selects `IRQ_SIM`. `IIO_SIMPLE_DUMMY` is user-visible and depends on `IIO_SW_DEVICE`. `IIO_SIMPLE_DUMMY_EVENTS` is a bool under `IIO_SIMPLE_DUMMY` that selects `IIO_DUMMY_EVGEN`. `IIO_SIMPLE_DUMMY_BUFFER` is another bool under the dummy device that selects IIO buffer, trigger, kfifo, and triggered-buffer support.

Control flow: menu visibility depends on `IIO`. Enabling the simple dummy driver opens subordinate feature choices; event and buffer objects are compiled into the main dummy module through Makefile conditionals, while the event generator is its own module/object.

State/persistence: Kconfig state determines compile-time inclusion only. Runtime state is in the C files.

Dependencies/integration: integrates with the IIO software-device framework, IRQ simulator, and buffer/trigger subsystems. The event option couples the main dummy driver to the companion event generator.

Risks: `IIO_DUMMY_EVGEN` is selected rather than directly prompted, so it may be built solely because event support is enabled. Because `IIO_SIMPLE_DUMMY_EVENTS` and `IIO_SIMPLE_DUMMY_BUFFER` are bools, they become built-in pieces of `iio_dummy.o` rather than separately loadable add-ons. Test signals include Kconfig dependency resolution for modular and built-in combinations, ensuring event code sees exported evgen symbols, and verifying buffer dependencies are pulled in.
