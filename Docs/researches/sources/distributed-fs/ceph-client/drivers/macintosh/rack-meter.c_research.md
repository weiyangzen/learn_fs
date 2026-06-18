# sources/distributed-fs/ceph-client/drivers/macintosh/rack-meter.c

Purpose: drives the Xserve G5 front-panel CPU meter LEDs by streaming generated samples through I2S/DBDMA and updating LED bitmaps from CPU load measurements.

Important APIs and functions: `struct rackmeter` owns MacIO device, I2S/DBDMA mappings, coherent DMA buffers, sample buffer, IRQ, and per-CPU delayed work. `rackmeter_setup_i2s()` enables sound/I2S clocks; `rackmeter_setup_dbdma()` builds the four-command ring; `rackmeter_do_timer()` samples CPU idle time and updates 16 LED intensities; `rackmeter_irq()` refills the DMA buffer indicated by the DBDMA mark. Probe/remove/shutdown are MacIO callbacks.

Control flow: probe finds child `i2s-a` and a `lightshow` or virtual sound node, maps I2S and DBDMA resources, allocates sample and coherent DMA storage, initializes I2S, starts DMA, schedules per-CPU sampling, and requests the DMA IRQ. The IRQ alternates buffer refills. When both CPUs have zero load, delayed work pauses DMA; nonzero load restarts it.

State and persistence: runtime-only state includes DMA command ring, two sample buffers, LED byte buffer, delayed work per CPU, stale IRQ count, and pause flag. No userspace persistence.

Dependencies and integration: depends on MacIO, OF resources, KeyLargo feature bits, DBDMA, PCI DMA mapping via the MacIO parent PCI device, kernel CPU stats, and workqueues.

Risks: supports only CPU IDs 0 and 1 and does not handle CPU hotplug. It directly manipulates KeyLargo FCR/I2S state shared with sound drivers. IRQ is requested after DMA setup starts, so error unwind must stop DMA. Excess stale DMA marks reset the engine.

Test signals: Xserve G5 OF matching, visible LED activity under CPU load, DMA IRQs with marks 1/2, pause when idle, remove/shutdown stopping work and DMA, no interaction regression with sound/I2S, and SMP behavior with one or two online CPUs.
