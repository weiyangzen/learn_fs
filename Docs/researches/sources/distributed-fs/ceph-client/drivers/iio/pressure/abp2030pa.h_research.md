<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa.h -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa.h

Purpose: shared private header for the Honeywell ABP2 core and bus adapters.

Important APIs, types, and functions: defines `ABP2_MEASUREMENT_RD_SIZE`, `enum abp2_func_id`, `struct abp2_data`, `struct abp2_ops`, and the exported `abp2_common_probe()` prototype. `struct abp2_data` carries device pointer, bus ops, pressure limits, output transfer limits, computed pressure conversion fields, IRQ/completion, scan buffer, and DMA-aligned RX/TX buffers.

Control flow: the header establishes the inversion point between transport and core. Bus adapters only implement `read` and `write`; the core owns all measurement sequencing and IIO registration.

State and persistence: defines the complete runtime state layout for ABP2 devices. It contains no persistent state by itself. Buffer alignment uses `IIO_DMA_MINALIGN` to protect DMA-capable bus controllers.

Dependencies and integration points: includes Linux completion, IIO, and types headers. It is consumed by `abp2030pa.c`, `abp2030pa_i2c.c`, and `abp2030pa_spi.c`. Namespace imports in bus modules must match the exported common probe.

Risks: public-to-submodule coupling is tight; changing buffer sizes or scan layout affects both transports. Only function A is enumerated, limiting future ABP2 transfer-function support. `p_scale_dec` and `p_offset` types constrain conversion precision and range.

Test signals: compile all bus variants after structure changes, verify namespace/modpost output, and run static checks for buffer-size assumptions in bus callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa.h -->
