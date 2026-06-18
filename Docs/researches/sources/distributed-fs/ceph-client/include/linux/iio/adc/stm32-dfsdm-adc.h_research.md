# `sources/distributed-fs/ceph-client/include/linux/iio/adc/stm32-dfsdm-adc.h`

Purpose: callback registration API for STM32 DFSDM ADC audio-buffer integration.

Important APIs/types/functions: `stm32_dfsdm_get_buff_cb` registers a buffer callback with private data; `stm32_dfsdm_release_buff_cb` releases it.

Control flow and state: callback state is managed by the STM32 DFSDM driver outside this header and persists against an `iio_dev` until released.

Dependencies/integration: depends on IIO core. Used by STM32 audio/ADC glue that consumes DFSDM samples through callback buffers.

Risks: callback lifetime and private data ownership must outlive streaming; callback context may be constrained by IIO buffer/IRQ rules; release must be balanced.

Test signals: register/release callback, streaming sample delivery, double register/release error paths, probe/remove ordering, and callback under buffer stop.
