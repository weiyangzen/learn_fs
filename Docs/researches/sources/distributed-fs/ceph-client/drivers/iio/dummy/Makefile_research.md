# sources/distributed-fs/ceph-client/drivers/iio/dummy/Makefile

Purpose: build rules for the IIO dummy driver family.

Important targets: `obj-$(CONFIG_IIO_SIMPLE_DUMMY) += iio_dummy.o` builds the main software dummy module. `iio_dummy-y := iio_simple_dummy.o` makes the core file mandatory. Conditional object additions include `iio_simple_dummy_events.o` and `iio_simple_dummy_buffer.o` when their Kconfig booleans are enabled. `obj-$(CONFIG_IIO_DUMMY_EVGEN) += iio_dummy_evgen.o` builds the companion fake IRQ event generator separately.

Control flow: Kbuild links optional event and buffer code into `iio_dummy.o`; this matches the header stubs in `iio_simple_dummy.h`, where disabled features become no-op inline functions. The event generator is not linked into `iio_dummy.o`, but is selected by Kconfig when events are enabled.

State/persistence: no runtime state. This file controls compile/link composition.

Dependencies/integration: depends on Kconfig symbols from the same directory. It also makes the symbol boundary between dummy core and event generator visible: `iio_dummy_evgen.c` exports IRQ helper symbols used by `iio_simple_dummy_events.c`.

Risks: misconfigured symbol combinations could produce unresolved references if Kconfig selection is changed without updating Makefile linkage. Since event and buffer options are bools, they cannot be loaded independently from the main dummy driver. Test signals include `allyesconfig`/`allmodconfig` style builds and combinations with events disabled and buffer enabled.
