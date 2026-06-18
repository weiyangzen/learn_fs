# Research Group: subset-b-003880

This grouped report covers the requested source-tree-aligned IIO amplifier, buffer, CDC, and chemical sensor files. Each section is wrapped for deterministic reconciliation into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/amplifiers/ada4250.c -->
# sources/distributed-fs/ceph-client/drivers/iio/amplifiers/ada4250.c

## Purpose
`ada4250.c` is a SPI IIO output voltage amplifier driver for the Analog Devices ADA4250 programmable gain instrumentation amplifier. It exposes a single indexed output voltage channel with hardware gain, offset calibration, calibration bias, and scale controls.

## Important APIs, Types, And Functions
The main private state is `struct ada4250_state`, holding the SPI device, regmap, mutex, AVDD voltage, cached offset/gain/bias, reference-buffer setting, and an aligned 16-bit transfer scratch field. `ada4250_read_raw()`, `ada4250_write_raw()`, and `ada4250_read_avail()` implement the IIO ABI. `ada4250_set_offset_uv()` computes sensor-offset calibration range and raw polarity/code from the requested microvolt offset. `ada4250_init()` enables the `avdd` regulator, resets the chip, reads the chip ID, and writes the optional `adi,refbuf-enable` property. `ada4250_probe()` builds a SPI regmap and registers the IIO device.

## Control Flow
Probe allocates `iio_dev`, initializes regmap and lock, calls `ada4250_init()`, then registers the device. Runtime reads either fetch register-backed gain/bias or return cached offset and fixed scale. Writes update the gain mux, calibration bias bits, or run the offset computation before programming calibration range/value registers.

## State And Persistence
State is volatile kernel/device state only. The driver caches `gain`, `bias`, `offset_uv`, and `refbuf_en`; hardware registers hold the active device configuration until reset or power loss. Offset calculation depends on the cached AVDD voltage and current gain/bias. A mutex protects offset register programming and state updates, but simple gain/bias writes are not locked.

## Dependencies And Integration Points
The driver integrates with SPI, regmap, regulator, device properties, and IIO direct sysfs attributes. It uses `devm_regulator_get_enable_read_voltage()` for supply voltage and `devm_regmap_init_spi()` with an 8-bit register/8-bit value map.

## Risks
`ada4250_init()` logs an invalid chip ID but does not fail, so wrong hardware may still register. `write_raw()` accepts arbitrary gain values and uses `ilog2(val)` without explicit membership validation beyond the advertised availability list, making malformed direct kernel callers risky. Offset programming rejects disabled or invalid bias and gain zero, so user order matters. The lock is not applied uniformly to all cached fields.

## Test Signals
Useful tests include SPI regmap read/write fault injection, invalid chip ID behavior, gain availability and `ilog2()` edge cases, offset limits across gains/bias sources, reference-buffer property handling, and regulator voltage failure paths. Hardware tests should verify output gain and signed offset polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/amplifiers/ada4250.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/amplifiers/adl8113.c -->
# sources/distributed-fs/ceph-client/drivers/iio/amplifiers/adl8113.c

## Purpose
`adl8113.c` is a platform IIO driver for the ADL8113 low-noise amplifier with integrated bypass switches. It models the active RF signal path as a hardware-gain setting on a voltage channel.

## Important APIs, Types, And Functions
`enum adl8113_signal_path` names internal amplifier, internal bypass, and two optional external bypass paths. `struct adl8113_gain_config` maps a path to a gain in dB, and `struct adl8113_state` stores the GPIO array and current path. `adl8113_set_path()` converts a selected path into the two control GPIO values. `adl8113_init_gain_configs()` builds the available gain/path table from fixed internal values and optional `adi,external-bypass-*-gain-db` properties. `adl8113_read_raw()` reports current gain as `IIO_VAL_INT_PLUS_MICRO_DB`, while `adl8113_write_raw()` selects a gain by exact integer dB match.

## Control Flow
Probe allocates the IIO device, acquires exactly two `ctrl` GPIOs, enables `vdd1`, `vss2`, and `vdd2` supplies, initializes gain configurations, sets internal amplifier mode by default, and registers the IIO device. Reads scan the configured table for the current path; writes find the requested gain and call `adl8113_set_path()`.

## State And Persistence
The driver keeps only volatile state: `current_path` and the device-managed gain table. Hardware state is the two GPIO output levels. There is no explicit mutex, so concurrent sysfs writes rely on GPIO array calls and simple state assignment without serialization.

## Dependencies And Integration Points
It uses platform device matching through `adi,adl8113`, GPIO descriptor arrays, regulator bulk enable, firmware properties, and IIO direct hardwaregain ABI. The implementation assumes board firmware supplies the control GPIOs in Va/Vb order.

## Risks
External bypass gains can collide with fixed gains, making the first matching table entry win. The driver does not expose an availability list, so users discover valid gains indirectly. Lack of locking can race read/write of `current_path`, though consequences are limited to transient reporting. Incorrect GPIO ordering changes RF path selection.

## Test Signals
Tests should cover GPIO count validation, regulator failure, fixed and optional gain mappings, duplicate gain handling, exact rejection of fractional dB (`val2 != 0`), and Va/Vb output patterns for all four paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/amplifiers/adl8113.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/amplifiers/hmc425a.c -->
# sources/distributed-fs/ceph-client/drivers/iio/amplifiers/hmc425a.c

## Purpose
`hmc425a.c` supports GPIO-controlled gain attenuators/amplifiers in the HMC425A family plus HMC540S, ADRF5740, and LTC6373. It exposes one voltage output channel with writable hardware gain; LTC6373 also exposes a `powerdown` extended attribute.

## Important APIs, Types, And Functions
`struct hmc425a_chip_info` describes per-part channel metadata, GPIO count, gain range, default code, powerdown support, and conversion callbacks. `struct hmc425a_state` stores the chip info, GPIO descriptors, cached gain code, powerdown flag, and mutex. Conversion helpers map dB values to GPIO codes and back for each supported part. `hmc425a_write()` pushes the bit pattern to all GPIOs. `hmc425a_read_raw()` and `hmc425a_write_raw()` implement hardwaregain as `IIO_VAL_INT_PLUS_MICRO_DB`. `ltc6373_read_powerdown()` and `ltc6373_write_powerdown()` control shutdown.

## Control Flow
Probe obtains chip data from OF match data, validates the number of `ctrl` GPIOs, enables `vcc-supply`, initializes the mutex, sets IIO direct mode, then writes either a powerdown value for LTC6373 or the default gain for the other parts. Runtime writes validate dB range and powerdown state, convert to a code, cache it, and write GPIOs.

## State And Persistence
Gain and powerdown state are cached in memory and mirrored to GPIO lines. There is no nonvolatile persistence. The mutex serializes gain and powerdown changes. On probe, hardware is initialized to a fixed default rather than reading any previous pin state.

## Dependencies And Integration Points
The driver integrates with platform/OF matching, GPIO descriptor arrays, regulators, IIO sysfs, and IIO extended channel attributes. Supported compatible strings select static conversion tables.

## Risks
The GPIO bit ordering must match board wiring. Code conversion uses bitwise inversion and integer rounding; boundary and fractional dB behavior is part-specific and easy to regress. `ltc6373_write_powerdown()` sets `powerdown` before writing GPIO and ignores `hmc425a_write()` return, though GPIO helper currently returns void-equivalent success. Reads/writes return `-EPERM` while powered down.

## Test Signals
Validate each compatible's GPIO count, default code, min/max gain boundaries, fractional dB conversion, read-after-write, LTC6373 powerdown gating, and regulator/GPIO probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/amplifiers/hmc425a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/buffer/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/buffer/Kconfig

## Purpose
This Kconfig file defines selectable Industrial I/O buffer implementation modules: callback buffers, generic DMA buffers, DMAengine integration, hardware consumer buffers, kfifo buffers, and triggered-buffer helpers.

## Important APIs, Types, And Functions
The file defines `IIO_BUFFER_CB`, `IIO_BUFFER_DMA`, `IIO_BUFFER_DMAENGINE`, `IIO_BUFFER_HW_CONSUMER`, `IIO_KFIFO_BUF`, and `IIO_TRIGGERED_BUFFER`. `IIO_BUFFER_DMAENGINE` selects `IIO_BUFFER_DMA`; `IIO_TRIGGERED_BUFFER` selects `IIO_TRIGGER` and `IIO_KFIFO_BUF`.

## Control Flow
There is no runtime control flow. Build-time dependency resolution determines which C objects from the sibling Makefile are compiled and which helper APIs are available to drivers.

## State And Persistence
Kconfig state is persisted in kernel configuration artifacts such as `.config`, not in this source file. It controls module/built-in availability.

## Dependencies And Integration Points
This file is consumed by the kernel Kconfig system and matches object rules in `drivers/iio/buffer/Makefile`. Other IIO drivers select these symbols to gain buffer helper functionality.

## Risks
Missing `select` relationships can lead to link failures or unavailable helper APIs. The help text notes that kfifo buffers do not provide buffer events, so userspace polling semantics differ from event-driven buffers. Dependency descriptions should stay aligned with exported APIs and Makefile entries.

## Test Signals
Build tests should cover configurations for each symbol as built-in and module, especially DMAengine selecting generic DMA and triggered buffers selecting trigger plus kfifo support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/buffer/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/buffer/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/buffer/Makefile

## Purpose
The Makefile maps IIO buffer Kconfig symbols to their implementation objects.

## Important APIs, Types, And Functions
It builds `industrialio-buffer-cb.o`, `industrialio-buffer-dma.o`, `industrialio-buffer-dmaengine.o`, `industrialio-hw-consumer.o`, `industrialio-triggered-buffer.o`, and `kfifo_buf.o` according to their `CONFIG_*` symbols.

## Control Flow
There is no runtime behavior. Kbuild evaluates `obj-$(CONFIG_...)` assignments and includes matching objects in the kernel image or modules.

## State And Persistence
The file has no runtime state. It persists the build contract between Kconfig symbols and object names.

## Dependencies And Integration Points
It integrates with the kernel build system and must remain consistent with `drivers/iio/buffer/Kconfig` and source file names. The comment asks maintainers to preserve alphabetical ordering.

## Risks
Renaming a source file or Kconfig symbol without updating this Makefile breaks builds. Ordering is mostly maintainability, but missing `obj-*` entries silently omit enabled functionality.

## Test Signals
Use configuration matrix builds for all buffer symbols, plus module install checks to verify expected object/module names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/buffer/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/buffer/industrialio-buffer-cb.c -->
# sources/distributed-fs/ceph-client/drivers/iio/buffer/industrialio-buffer-cb.c

## Purpose
This file implements the IIO callback buffer, an in-kernel consumer path where samples pushed by an IIO provider are delivered to a caller-supplied callback instead of userspace file I/O.

## Important APIs, Types, And Functions
`struct iio_cb_buffer` embeds `struct iio_buffer`, callback pointer, private data, acquired channels, and provider IIO device. `iio_channel_get_all_cb()` allocates the buffer, acquires all channels for a consumer, validates that all channels belong to the same `iio_dev`, and builds the scan mask. `iio_buffer_cb_store_to()` invokes the callback from the buffer store path. Exported helpers set watermark, start/stop buffering with `iio_update_buffers()`, release resources, and expose channels/provider device.

## Control Flow
A consumer allocates a callback buffer, optionally sets a watermark, starts it, receives callbacks from provider buffer pushes, stops it, and releases it. Release drops channels and puts the buffer; the access `release` frees the scan mask and object.

## State And Persistence
State is in-memory and reference-counted through the embedded IIO buffer. The scan mask persists only for the lifetime of the callback buffer. The callback must be safe in any context and must not sleep.

## Dependencies And Integration Points
The implementation uses the IIO consumer API, IIO buffer core, bitmap allocation, and exported GPL symbols. Access modes are software and triggered buffering.

## Risks
Callbacks that sleep or assume process context can break provider paths. Multi-provider channel lists are rejected after allocation and must unwind cleanly. Watermark zero is invalid. Consumers must call stop before release if active to avoid provider-side lifecycle issues.

## Test Signals
Test single-provider and mixed-provider channel acquisition, callback invocation under trigger/software modes, watermark validation, start/stop ordering, and release/unwind paths with allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/buffer/industrialio-buffer-cb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/buffer/industrialio-buffer-dma.c -->
# sources/distributed-fs/ceph-client/drivers/iio/buffer/industrialio-buffer-dma.c

## Purpose
`industrialio-buffer-dma.c` is the generic DMA-backed IIO buffer queue implementation. It manages DMA blocks, file I/O double-buffering, imported dma-bufs, buffer enable/disable, polling wakeups, and block lifetime.

## Important APIs, Types, And Functions
The file operates on `struct iio_dma_buffer_queue` and `struct iio_dma_buffer_block` from public IIO DMA headers. Exported APIs include `iio_dma_buffer_block_done()`, `iio_dma_buffer_block_list_abort()`, `iio_dma_buffer_request_update()`, `iio_dma_buffer_enable()`, `iio_dma_buffer_disable()`, file read/write callbacks, dma-buf attach/detach/enqueue, queue lock/unlock helpers, datum/length setters, `iio_dma_buffer_init()`, `iio_dma_buffer_exit()`, and `iio_dma_buffer_release()`.

## Control Flow
File I/O mode allocates two page-aligned coherent blocks sized to half the configured buffer length. Input blocks start on the incoming queue and are submitted on enable; completed blocks become readable and then are re-enqueued. Output blocks are filled from userspace before submission. Imported dma-bufs disable file I/O mode, attach an external buffer, and enqueue it under the queue mutex with an optional fence and scatterlist. Hardware-specific drivers provide `submit()` and optional `abort()` callbacks.

## State And Persistence
Block state transitions through queued, active, done, and dead. Blocks are kref-counted; file I/O blocks own coherent DMA memory, while dma-buf blocks increment `num_dmabufs`. Completion from atomic context uses a global dead-block list and workqueue because coherent free can sleep. Queue state includes active flag, incoming list, fileio block array, active fileio block, position, mutex, and spinlock.

## Dependencies And Integration Points
The code integrates with IIO buffer core, DMA mapping, dma-buf, dma-fence, poll wait queues, workqueues, mutexes, spinlocks, and hardware-specific DMA buffer drivers such as DMAengine.

## Risks
Drivers must call `iio_dma_buffer_block_done()` for every submitted block, including aborted/no-transfer blocks, or blocks leak and userspace stalls. Missing `abort()` can leave active blocks unavailable across disable. Correct lock ordering between queue mutex and list spinlock is critical. File I/O and dma-buf modes are mutually exclusive, and incorrect state checks can expose use-after-free or stuck queues. `submit()` failure is only recoverable by disable/re-enable.

## Test Signals
Tests should cover input/output file I/O, short reads/writes rounded to datum size, length clamping to at least two, enable/disable abort, submit failure, dma-buf attach while fileio is enabled, fence signaling success/error, dead block cleanup from atomic completion, and poll wakeups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/buffer/industrialio-buffer-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/buffer/industrialio-buffer-dmaengine.c -->
# sources/distributed-fs/ceph-client/drivers/iio/buffer/industrialio-buffer-dmaengine.c

## Purpose
This file adapts the generic IIO DMA buffer queue to Linux DMAengine channels, providing a reusable hardware IIO buffer for devices with DMAengine-connected converter ports.

## Important APIs, Types, And Functions
`struct dmaengine_buffer` wraps an `iio_dma_buffer_queue`, DMA channel, active block list, transfer alignment, and max segment size. `iio_dmaengine_buffer_submit_block()` prepares either a `dma_vec` transfer for scatter-gather dma-bufs or a slave single transfer for coherent file I/O blocks. `iio_dmaengine_buffer_block_done()` removes active blocks, subtracts residue, and completes the generic block. Exported setup APIs include `iio_dmaengine_buffer_setup_ext()`, `devm_iio_dmaengine_buffer_setup_ext()`, `devm_iio_dmaengine_buffer_setup_with_handle()`, and `iio_dmaengine_buffer_teardown()`.

## Control Flow
Setup requests or accepts a DMA channel, allocates a DMAengine buffer, marks the IIO device as hardware-buffer capable, sets the buffer direction, and attaches it. On queue submission, the code chooses device-to-memory or memory-to-device direction, prepares a descriptor, installs a completion callback, submits the descriptor, records the block on the active list, and issues pending DMA. Disable calls `dmaengine_terminate_sync()` and aborts active blocks.

## State And Persistence
State is volatile: active DMA blocks, channel pointer, alignment, max size, and generic queue state. The `length_align_bytes` sysfs attribute exposes minimum transfer alignment inferred from DMA slave capabilities.

## Dependencies And Integration Points
It depends on DMAengine, scatterlist DMA addresses, IIO DMA buffer namespace, IIO buffer core, and optional devm cleanup. It imports the `IIO_DMA_BUFFER` namespace and exports `IIO_DMAENGINE_BUFFER` symbols.

## Risks
Alignment and max segment handling are central: zero or overlarge `bytes_used` is rejected for fileio. SG paths allocate `dma_vec` with `GFP_ATOMIC`; memory pressure can fail submissions. The code assumes SG entries are already DMA-mapped by the dma-buf attachment path. Active-list manipulation must pair with completion and abort to avoid list corruption.

## Test Signals
Exercise DMA slave capability variations, both input and output directions, residue accounting, abort paths, devm setup teardown, external channel handles, SG dma-buf enqueue, and `length_align_bytes` ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/buffer/industrialio-buffer-dmaengine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/buffer/industrialio-hw-consumer.c -->
# sources/distributed-fs/ceph-client/drivers/iio/buffer/industrialio-hw-consumer.c

## Purpose
This file implements the IIO hardware consumer helper, used when an IIO provider is directly connected in hardware to another device and buffers represent hardware data paths rather than CPU-readable storage.

## Important APIs, Types, And Functions
`struct iio_hw_consumer` stores all acquired channels and a list of per-provider hardware buffers. `struct hw_consumer_buffer` embeds an IIO buffer and scan mask for one provider `iio_dev`. `iio_hw_consumer_alloc()` acquires all channels for a device and groups them by provider, setting scan-mask bits. `iio_hw_consumer_enable()` and `iio_hw_consumer_disable()` attach/detach all provider buffers through `iio_update_buffers()`. Devm and manual free helpers are exported.

## Control Flow
A consumer allocates the hardware consumer, enables it when the downstream hardware path should run, disables it when done, then frees it. Enable rolls back already-enabled buffers if a later provider fails.

## State And Persistence
All state is memory-only. Each hardware buffer is reference-counted through the IIO buffer core and contains only access methods, provider pointer, and scan mask. No data is stored by the helper.

## Dependencies And Integration Points
It uses IIO consumer channel acquisition, IIO buffer core, bitmap scan masks, and hardware buffer mode. Exported GPL symbols support both devm and explicit lifetime management.

## Risks
`iio_hw_consumer_get_buffer()` sets `buffer.access` before `iio_buffer_init()`, and `iio_buffer_init()` behavior must preserve or be compatible with subsequent access assignment assumptions. Allocation unwind uses `iio_buffer_put()` for listed buffers but must not miss scan-mask release through buffer release. Provider grouping depends on `chan->indio_dev` termination semantics from `iio_channel_get_all()`.

## Test Signals
Test multiple channels on one provider, channels spanning multiple providers, enable rollback on second provider failure, devm cleanup, missing channel acquisition, and scan mask correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/buffer/industrialio-hw-consumer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/buffer/industrialio-triggered-buffer.c -->
# sources/distributed-fs/ceph-client/drivers/iio/buffer/industrialio-triggered-buffer.c

## Purpose
This helper combines common IIO triggered-buffer setup: allocate a kfifo buffer, allocate a pollfunc, attach the buffer, and mark the device as triggered-buffer capable.

## Important APIs, Types, And Functions
`iio_triggered_buffer_setup_ext()` is the central exported setup helper. It accepts top-half and threaded pollfunc handlers, buffer direction, optional setup ops, and optional buffer attributes. `iio_triggered_buffer_cleanup()` deallocates the pollfunc and frees the kfifo. `devm_iio_triggered_buffer_setup_ext()` wraps setup with managed cleanup.

## Control Flow
Drivers call setup before registering the IIO device. The helper refuses to proceed if `indio_dev->buffer` already exists because cleanup assumes it owns that buffer. On success, it sets `indio_dev->setup_ops`, ORs `INDIO_BUFFER_TRIGGERED` into modes, attaches a kfifo buffer, and stores pollfunc metadata.

## State And Persistence
State consists of the allocated kfifo buffer and pollfunc pointers attached to `indio_dev`. It is released explicitly or through devm cleanup. No persistent configuration is stored.

## Dependencies And Integration Points
It depends on the kfifo buffer implementation, IIO trigger consumer/pollfunc APIs, IIO buffer core, and optional buffer setup ops from sensor drivers.

## Risks
Ownership assumptions are strict: using this helper after attaching another buffer returns `-EADDRINUSE`. Cleanup assumes setup succeeded and the buffer is the kfifo allocated here. Drivers that call non-devm setup must pair cleanup on all later registration errors and remove paths.

## Test Signals
Validate success path, pollfunc allocation failure unwind, pre-existing buffer rejection, attach failure unwind, devm action behavior, and driver remove/error paths using this helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/buffer/industrialio-triggered-buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/buffer/kfifo_buf.c -->
# sources/distributed-fs/ceph-client/drivers/iio/buffer/kfifo_buf.c

## Purpose
`kfifo_buf.c` provides the standard software/triggered IIO buffer backed by Linux `kfifo`, supporting sample push, userspace read/write, data/space reporting, and dynamic reallocation when datum size or length changes.

## Important APIs, Types, And Functions
`struct iio_kfifo` embeds `struct iio_buffer`, the kfifo, a `user_lock`, and an update flag. Access callbacks include `iio_store_to_kfifo()`, `iio_read_kfifo()`, `iio_kfifo_write()`, `iio_kfifo_remove_from()`, availability callbacks, length/datum setters, and `iio_request_update_kfifo()`. Exported helpers are `iio_kfifo_allocate()`, `iio_kfifo_free()`, and `devm_iio_kfifo_buffer_setup_ext()`.

## Control Flow
Allocation initializes the buffer with length 2 and marks an update needed. When the IIO core requests an update, the kfifo is allocated or reset. Producers push one datum at a time; userspace reads bytes through `kfifo_to_user()`, and output consumers can remove samples or accept writes from userspace.

## State And Persistence
The kfifo storage is volatile and protected by `user_lock` for userspace-facing operations. `update_needed` defers reallocation until request-update time. Buffer length is clamped to at least two to avoid invalid states.

## Dependencies And Integration Points
It integrates with IIO buffer access functions, kfifo, poll wakeups, mutexes, and devm buffer setup for drivers that need a software buffer without full triggered-buffer helper setup.

## Risks
`iio_store_to_kfifo()` is not protected by `user_lock`, matching kfifo producer assumptions but requiring correct IIO core serialization. Overflow returns `-EBUSY`. Length overflow is checked before kfifo power-of-two rounding. Data availability returns sample count from `kfifo_len()`, so consumers must understand kfifo element sizing.

## Test Signals
Test allocation/reallocation on length and datum-size changes, invalid zero sizes, overflow protection, push/read ordering, write/remove output paths, poll wake on remove, and devm attach behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/buffer/kfifo_buf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/cdc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/cdc/Kconfig

## Purpose
This Kconfig menu defines capacitance-to-digital converter drivers for Analog Devices AD7150-family and AD7745/AD7746/AD7747 sensors.

## Important APIs, Types, And Functions
It defines `AD7150` and `AD7746`, both tristate and dependent on I2C. Help text identifies supported chips and module names.

## Control Flow
No runtime control flow exists; Kconfig controls whether corresponding I2C IIO drivers are built.

## State And Persistence
State is the kernel build configuration. The selected symbols persist in `.config` and determine compiled objects.

## Dependencies And Integration Points
The menu integrates with `drivers/iio/cdc/Makefile`, where `CONFIG_AD7150` maps to `ad7150.o` and `CONFIG_AD7746` maps to `ad7746.o`.

## Risks
Dependencies are minimal; if future code adds regulators, events, or buffers with extra config dependencies, this file must be updated. Help text says direct sysfs access, matching the direct-mode drivers.

## Test Signals
Build each driver as built-in and module, and verify I2C dependency hides options when I2C is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/cdc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/cdc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/cdc/Makefile

## Purpose
This Makefile connects CDC Kconfig symbols to object files.

## Important APIs, Types, And Functions
`obj-$(CONFIG_AD7150) += ad7150.o` and `obj-$(CONFIG_AD7746) += ad7746.o` are the only build rules.

## Control Flow
There is no runtime behavior; Kbuild selects objects according to configuration.

## State And Persistence
The file persists the build mapping and has no runtime state.

## Dependencies And Integration Points
It integrates with `drivers/iio/cdc/Kconfig`, the I2C driver source files, and kernel module naming.

## Risks
Wrong object mapping causes missing modules or link failures. New CDC drivers must update both Kconfig and this Makefile.

## Test Signals
Run kernel builds with `CONFIG_AD7150` and `CONFIG_AD7746` as `m` and `y`, verifying expected modules are generated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/cdc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/cdc/ad7150.c -->
# sources/distributed-fs/ceph-client/drivers/iio/cdc/ad7150.c

## Purpose
`ad7150.c` is an I2C IIO driver for AD7150, AD7151, and AD7156 capacitive sensors. It exposes raw and averaged capacitance channels, scale/offset/sample frequency, and optional threshold events when IRQs are available.

## Important APIs, Types, And Functions
`struct ad7150_chip_info` holds the I2C client, cached threshold/adaptive sensitivity/timeout parameters, state mutex, IRQ numbers/enables, and currently programmed event type/direction. `ad7150_read_raw()` reads raw/average capacitance and returns fixed scale/offset/sample frequency. Event methods implement config and value reads/writes. `ad7150_write_event_params()` writes cached active event parameters to device registers. IRQ handlers read status bits and push IIO events.

## Control Flow
Probe enables `vdd`, attempts to obtain one or two firmware IRQs depending on chip type, and registers either event-capable channels or no-IRQ channels. Enabling an event may disable both IRQs, rewrite the shared threshold mode in `CFG`, update parameters, and re-enable IRQs. IRQ handlers validate status bits before pushing the configured event code.

## State And Persistence
Threshold values, adaptive sensitivity, timeout nibbles, current event mode, and IRQ enable state are cached in memory. Hardware has one shared threshold-type/fixed/adaptive configuration and per-channel threshold/sensitivity/timeout registers. The mutex serializes event state updates.

## Dependencies And Integration Points
It uses I2C SMBus word/byte operations, regulators, fwnode IRQ lookup, threaded IRQs, IIO events, and direct-mode IIO channels.

## Risks
The chip has a single shared event mode, so enabling a new type/direction changes semantics for both channels. The code notes an unavoidable race because chip-side interrupts cannot be disabled while changing configuration. Disable paths outside the mutex can race with mode changes. Default cached thresholds are zero until userspace writes them.

## Test Signals
Test no-IRQ and IRQ probe variants, AD7150 two-channel versus AD7151 one-channel layouts, event enable/disable mode switching, timeout encoding validation, status-bit filtering, regulator failures, and IRQ request failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/cdc/ad7150.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/cdc/ad7746.c -->
# sources/distributed-fs/ceph-client/drivers/iio/cdc/ad7746.c

## Purpose
`ad7746.c` is an I2C direct-mode IIO driver for AD7745, AD7746, and AD7747 capacitance-to-digital converters. It exposes voltage, temperature, and capacitance channels, calibration controls, CAPDAC offset/zeropoint, and sample frequency selection.

## Important APIs, Types, And Functions
`struct ad7746_chip_info` caches the I2C client, mutex, config byte, cap/vt setup bytes, per-channel CAPDAC values, and active CAPDAC channel. `ad7746_select_channel()` programs CAP setup or VT setup and returns conversion delay. `ad7746_read_channel()` selects a channel, starts a single conversion, sleeps, and reads 24-bit data. `ad7746_read_raw()`, `ad7746_write_raw()`, and `ad7746_read_avail()` implement ABI access. Calibration sysfs attributes call `ad7746_start_calib()` with offset/gain calibration modes.

## Control Flow
Probe allocates state, chooses full AD7746 channel set or a reduced set for AD7745/AD7747, configures excitation outputs from firmware properties, and registers the IIO device. Runtime reads and writes lock around stateful I2C register sequences. Sample frequency writes update the cached config byte; later conversions use the selected filter index and delay.

## State And Persistence
The driver caches config/setup/CAPDAC state because channel selection and conversion setup are shared hardware resources. Calibration gain/offset writes persist in device registers until reset. CAPDAC offset values are cached per channel/differential mode and re-applied on channel selection.

## Dependencies And Integration Points
It uses I2C SMBus byte/word/block operations, firmware properties for excitation pins and level, IIO direct sysfs attributes, unaligned big-endian 24-bit parsing, and mutex serialization.

## Risks
For voltage/temperature selection, delay uses the capacitance filter table with the VT index; this may be intentional or a latent bug because a VT-specific table exists. Channel selection before calibration sysfs is done without the main mutex in the wrapper, then `ad7746_start_calib()` locks, so external concurrent reads could intervene. Invalid excitation permille values are silently ignored.

## Test Signals
Test each chip variant's channel count, excitation property combinations, sample frequency rounding, CAPDAC offset limits and scaling, single conversion timing, calibration timeout, endian conversion, and concurrent direct reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/cdc/ad7746.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/Kconfig

## Purpose
This Kconfig menu declares chemical and air-quality IIO sensor drivers, including the subset's AGS02MA, Atlas, BME680, CCS811, ENS160, iAQ-Core, MH-Z19B, PMS7003, and SCD30 symbols.

## Important APIs, Types, And Functions
Relevant symbols include `AOSONG_AGS02MA`, `ATLAS_PH_SENSOR`, `ATLAS_EZO_SENSOR`, `BME680`, `BME680_I2C`, `BME680_SPI`, `CCS811`, `ENS160`, `ENS160_I2C`, `ENS160_SPI`, `IAQCORE`, `MHZ19B`, `PMS7003`, `SCD30_CORE`, `SCD30_I2C`, and `SCD30_SERIAL`. It also includes other chemical drivers outside this work item.

## Control Flow
There is no runtime control flow. Kconfig dependency and `select` statements determine bus support, regmap support, CRC helpers, serial bus support, IIO buffering, and triggered-buffer helper availability.

## State And Persistence
Kernel configuration persists symbol selections and controls which modules or built-ins are produced.

## Dependencies And Integration Points
The file integrates with the sibling Makefile, bus frameworks (`I2C`, `SPI`, `SERIAL_DEV_BUS`), `REGMAP`, `CRC8`/`CRC16`, `IIO_BUFFER`, and `IIO_TRIGGERED_BUFFER`.

## Risks
Core/transport split symbols must select the right transport support. `ENS160_I2C` and `ENS160_SPI` select regmap transports but do not explicitly depend on `ENS160`; they are selected by `ENS160` when buses are present. Missing buffer selects would break drivers using `devm_iio_triggered_buffer_setup()`.

## Test Signals
Run randconfig and targeted builds for each bus combination, especially `BME680` with only I2C or only SPI and `ENS160` with transport modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/Makefile

## Purpose
This Makefile maps chemical sensor Kconfig symbols to driver objects.

## Important APIs, Types, And Functions
It builds the subset objects `ags02ma.o`, `atlas-sensor.o`, `atlas-ezo-sensor.o`, `bme680_core.o`, `bme680_i2c.o`, `bme680_spi.o`, `ccs811.o`, `ens160_core.o`, `ens160_i2c.o`, `ens160_spi.o`, `ams-iaq-core.o`, `mhz19b.o`, `pms7003.o`, and SCD30 transport/core objects, plus additional chemical drivers.

## Control Flow
No runtime behavior exists. Kbuild includes objects based on `CONFIG_*` selections from `Kconfig`.

## State And Persistence
The file stores build mappings only. It has no runtime state.

## Dependencies And Integration Points
It must stay aligned with `drivers/iio/chemical/Kconfig`, module names in help text, and source file names. The comment requests alphabetical insertion for new entries.

## Risks
Core/transport split drivers can build incorrectly if core and bus objects are mapped to the wrong symbols. Missing object rules are caught by build tests only when the corresponding symbol is enabled.

## Test Signals
Targeted module builds for every chemical sensor symbol and all bus combinations are the main validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/ags02ma.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/ags02ma.c

## Purpose
`ags02ma.c` is an I2C IIO driver for the Aosong AGS02MA TVOC sensor. It exposes one VOC concentration channel with raw value and ppb scale.

## Important APIs, Types, And Functions
`struct ags02ma_data` stores the I2C client. `struct ags02ma_reading` is a packed 32-bit big-endian data word plus CRC byte. `ags02ma_register_read()` sends a register command, waits the datasheet processing delay, receives data, validates CRC8 with polynomial `0x31` and init `0xff`, and returns the 32-bit value. `ags02ma_read_raw()` reads TVOC raw data or returns scale. Probe initializes the CRC table and verifies the version register.

## Control Flow
Probe allocates the IIO device, populates CRC lookup data, reads the version register with a shorter delay, initializes state, and registers the single-channel IIO device. Runtime raw reads send register `0x00`, wait 1500 ms, receive and validate a reading.

## State And Persistence
The driver keeps only the client pointer. There is no explicit mutex; concurrent reads can overlap I2C command/delay/read sequences. Sensor configuration is not modified.

## Dependencies And Integration Points
It depends on I2C master send/receive, CRC8 table helpers, delays, and IIO direct channel ABI.

## Risks
`i2c_master_send()` and `i2c_master_recv()` only check negative errors, not short positive transfers. The long interruptible sleep return value is ignored. Lack of serialization can interleave reads from multiple callers.

## Test Signals
Test CRC mismatch, short transfer behavior, version read failure, raw read delay, scale ABI, and concurrent read stress on a mocked I2C adapter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/ags02ma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/ams-iaq-core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/ams-iaq-core.c

## Purpose
`ams-iaq-core.c` is an I2C IIO driver for AMS iAQ-Core VOC sensors. It exposes processed equivalent CO2 concentration, sensor resistance, and TVOC concentration.

## Important APIs, Types, And Functions
`struct ams_iaqcore_reading` maps the 9-byte sensor frame. `struct ams_iaqcore_data` stores the I2C client, lock, `last_update` jiffies cache timestamp, and frame buffer. `ams_iaqcore_read_measurement()` performs a raw I2C read transfer. `ams_iaqcore_get_measurement()` enforces the one-second maximum polling rate. `ams_iaqcore_read_raw()` returns channel-specific processed values and units.

## Control Flow
Probe initializes state, sets `last_update` to force the first read, configures direct IIO channels, and registers. Runtime reads lock, refresh the measurement if at least one second elapsed, and decode the cached frame.

## State And Persistence
The latest frame is cached in memory for up to one second. There is no persistent configuration and no power-management state. The mutex serializes cache updates and reads.

## Dependencies And Integration Points
It uses I2C transfer, IIO direct processed channels, jiffies timing, and module/I2C/OF matching.

## Risks
`i2c_transfer()` returns number of messages, normally `1`, but the code compares it to `AMS_IAQCORE_DATA_SIZE` and therefore treats a successful transfer as an error on standard I2C semantics. This is a high-value test/review point. Sensor status byte is read but not interpreted. Cached stale data is returned within the one-second window.

## Test Signals
Validate I2C return handling, one-second cache behavior, endian decoding, status-byte error cases, and channel scale/processed unit expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/ams-iaq-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/atlas-ezo-sensor.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/atlas-ezo-sensor.c

## Purpose
`atlas-ezo-sensor.c` supports Atlas Scientific EZO CO2, O2, and humidity sensors over I2C, exposing one raw channel per device with appropriate scale.

## Important APIs, Types, And Functions
`struct atlas_ezo_device` describes the channel table and conversion delay. `struct atlas_ezo_data` stores the client, device descriptor, lock, and receive buffer. `atlas_ezo_sanitize()` removes a decimal point for fixed integer representation. `atlas_ezo_read_raw()` sends the ASCII `R` read command, waits the device-specific delay, receives up to eight bytes, checks response code `1`, parses the ASCII result, and returns raw or scale. Probe selects chip data through I2C/OF match data.

## Control Flow
Probe builds a direct-mode IIO device for the matched sensor type. Runtime raw reads lock the I2C command/response transaction, issue `R`, wait 950 ms for gas or 350 ms for humidity, receive the response, sanitize decimal formatting, and parse.

## State And Persistence
State is volatile. The driver keeps no calibration or persistent configuration. The mutex serializes command/response traffic.

## Dependencies And Integration Points
It uses I2C SMBus write byte, I2C master receive, firmware match data, and IIO concentration/humidity channel ABIs.

## Risks
`atlas_ezo_read_raw()` rejects any channel whose type is not `IIO_CONCENTRATION` before the switch, which prevents humidity raw and scale reads despite defining a humidity channel. Receive data may not be NUL-terminated before string operations. Short positive receive lengths are not explicitly validated. Decimal removal is simplistic for negative or longer values.

## Test Signals
Test CO2/O2 parsing and scale, humidity channel access, busy response code handling, short/unterminated I2C responses, and concurrent reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/atlas-ezo-sensor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/atlas-sensor.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/atlas-sensor.c

## Purpose
`atlas-sensor.c` supports Atlas Scientific OEM SM pH, EC, ORP, dissolved oxygen, and RTD sensors. It provides direct reads, writable temperature compensation channels where relevant, optional interrupt-triggered buffering, calibration status warnings, and runtime power management.

## Important APIs, Types, And Functions
`struct atlas_data` stores client, trigger, chip descriptor, regmap, irq_work, interrupt flag, and aligned scan buffer. `struct atlas_device` defines channel arrays, data register, calibration callback, and measurement delay. Calibration helpers inspect device-specific status registers. `atlas_read_measurement()` resumes the device, waits after suspend, reads a 32-bit big-endian value, and autosuspends. `atlas_trigger_handler()` bulk-reads scan channels and pushes timestamped buffers. `atlas_buffer_postenable()` and `atlas_buffer_predisable()` manage runtime PM and device interrupt enable.

## Control Flow
Probe allocates IIO device and trigger, initializes regmap, marks runtime PM active, checks calibration, registers the trigger, sets up a triggered kfifo buffer, optionally requests a data-ready IRQ that schedules irq_work, powers the device, enables autosuspend, and registers the IIO device. Direct reads claim direct mode for measurement channels; buffer mode reads data in the trigger handler.

## State And Persistence
The driver persists no configuration beyond hardware power/interrupt state and optional temperature compensation writes. Runtime PM powers the device down after autosuspend. `interrupt_enabled` gates register writes when no IRQ was requested.

## Dependencies And Integration Points
It integrates with I2C regmap, IIO triggers/buffers, irq_work, threaded IRQs, runtime PM, and multiple IIO channel types.

## Risks
`chip->calibration` is NULL for RTD, but probe calls it unconditionally, which is a likely NULL function pointer bug for `atlas-rtd-sm`. Buffer push passes `sizeof(data->buffer)` rather than the active channel byte count, relying on scan layout tolerance. Direct temperature reads do not use runtime PM while measurement reads do. Error unwinds must balance trigger/buffer/PM setup.

## Test Signals
Test every compatible, especially RTD probe; direct and buffered reads; IRQ and no-IRQ operation; runtime suspend/resume delays; calibration warning paths; temperature compensation writes; and cleanup on trigger/buffer registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/atlas-sensor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/bme680.h -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/bme680.h

## Purpose
`bme680.h` is the shared header for Bosch BME680 core, I2C, and SPI drivers. It defines register addresses, bit masks, calibration block sizes, public regmap/PM objects, and the core probe entry point.

## Important APIs, Types, And Functions
Important definitions include chip ID/reset registers, measurement data registers, oversampling masks, gas heater registers, status bits, measurement skipped sentinel, trim mask, startup time, channel/bulk-read counts, and calibration range addresses/lengths. It declares `bme680_regmap_config`, `bme680_dev_pm_ops`, and `bme680_core_probe()`.

## Control Flow
The header has no runtime control flow. It shapes the core/transport contract: transports create a regmap and call the core probe; both transport drivers reference the same runtime PM ops.

## State And Persistence
No state is stored here. Constants define how runtime state in `bme680_core.c` maps to hardware registers.

## Dependencies And Integration Points
It depends on Linux PM and regmap headers and is included by BME680 core, I2C, and SPI source files.

## Risks
Incorrect masks or register addresses corrupt sensor configuration and compensation. Because transport drivers import the core namespace, this header must remain stable across built-in/module combinations.

## Test Signals
Validate compile coverage for I2C-only, SPI-only, and dual-bus builds; compare register constants against datasheet; and test reset/chip-ID paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/bme680.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/bme680_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/bme680_core.c

## Purpose
`bme680_core.c` implements the Bosch BME680 IIO core for temperature, pressure, humidity, and gas resistance. Bus-specific drivers supply regmap access; the core handles calibration, compensation, forced conversions, triggered buffering, heater setup, regulators, and runtime PM.

## Important APIs, Types, And Functions
`struct bme680_calib` stores factory calibration coefficients. `struct bme680_data` stores regmap, calibration cache, mutex, oversampling settings, heater settings, scan buffer, and transfer scratch union. `bme680_read_calib()` reads and decodes three calibration ranges. Compensation helpers compute temperature, pressure, humidity, gas resistance, heater resistance, heater duration, and preheat current. `bme680_chip_config()`, `bme680_gas_config()`, `bme680_set_mode()`, and `bme680_wait_for_eoc()` control conversions. IIO access is via `bme680_read_raw()`, `bme680_write_raw()`, and `bme680_trigger_handler()`. `bme680_core_probe()` is exported.

## Control Flow
Probe enables `vdd`/`vddio`, resets the chip, checks chip ID, reads calibration, programs default oversampling and gas heater settings, sets up a triggered buffer, enables runtime PM, and registers the IIO device. Direct reads resume PM, force one conversion, wait for end-of-conversion, then read and compensate the requested channel. Buffered reads force one conversion and bulk-read all measurement registers before pushing a timestamped scan.

## State And Persistence
Calibration, oversampling ratios, heater temperature/duration/current, and scan scratch are in-memory state protected by a mutex. Hardware registers mirror oversampling and heater settings and are reprogrammed on runtime resume. Sensor measurements are not cached; reads trigger fresh forced conversions.

## Dependencies And Integration Points
The core uses regmap with Maple cache, regulator bulk enable, runtime PM, IIO direct and triggered-buffer APIs, unaligned endian helpers, and namespaces for transport modules.

## Risks
Compensation math is integer-heavy and sensitive to calibration endian/bitfield extraction. `bme680_read_gas()` reads status but does not check the regmap read return before testing `data->check`. Raw read paths for pressure/humidity return compensated values under `RAW`, preserving legacy behavior but potentially confusing. Wait time depends on oversampling and heater duration; wrong formulas cause stale or busy data. `preheat_curr_mA` state is not updated when writing current, only the hardware register is written.

## Test Signals
Test chip ID/reset failures, calibration decoding with known vectors, compensation vectors from Bosch API, runtime suspend/resume reconfiguration, direct versus buffered scan values, oversampling validation, gas heater stabilization failures, and regmap read error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/bme680_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/bme680_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/bme680_i2c.c

## Purpose
`bme680_i2c.c` is the I2C transport driver for the BME680 core.

## Important APIs, Types, And Functions
`bme680_i2c_probe()` initializes an I2C regmap with `bme680_regmap_config`, chooses the I2C ID name when available, and calls `bme680_core_probe()`. The driver declares I2C and OF match tables for `"bme680"` and `"bosch,bme680"`.

## Control Flow
The I2C bus matches a device, probe builds regmap, and all sensor setup is delegated to the core. Runtime PM operations are the shared `bme680_dev_pm_ops`.

## State And Persistence
No transport-specific runtime state is kept. The regmap is device-managed and owned by the core after probe delegation.

## Dependencies And Integration Points
It depends on I2C, regmap-I2C, the shared BME680 header, and imports the `IIO_BME680` namespace.

## Risks
If `i2c_client_get_device_id()` returns NULL for an OF-only device, the core receives a NULL name and the IIO device name may be absent or less useful. Regmap errors are logged and propagated.

## Test Signals
Test I2C and OF matching, regmap init failure, namespace/module builds, and runtime PM callback linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/bme680_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/bme680_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/bme680_spi.c

## Purpose
`bme680_spi.c` is the SPI transport driver for BME680, adapting the chip's paged 7-bit SPI register address space to regmap and delegating sensor logic to the BME680 core.

## Important APIs, Types, And Functions
`struct bme680_spi_bus_context` stores the SPI device and current memory page. `bme680_regmap_spi_select_page()` changes the page bit in the status register with read-modify-write. `bme680_regmap_spi_write()` and `bme680_regmap_spi_read()` implement regmap bus operations, masking or setting bit 7 for write/read. `bme680_spi_probe()` allocates context, initializes regmap, and calls `bme680_core_probe()`.

## Control Flow
Probe sets `current_page` unknown, builds a custom regmap bus, and enters the shared core. Each regmap transfer selects the correct page for the target register before issuing SPI IO.

## State And Persistence
The only transport state is the cached current page. It is volatile and initialized to invalid on probe to force the first page write.

## Dependencies And Integration Points
It uses SPI, custom regmap bus callbacks, shared BME680 core definitions, runtime PM ops, OF/SPI ID matching, and the `IIO_BME680` namespace.

## Risks
Every page switch requires a status register read-modify-write; failures block subsequent register access. Cached page state can become stale if another agent changes the page bit outside this regmap. The write helper copies exactly two bytes, matching 8-bit register/value regmap assumptions.

## Test Signals
Test register accesses on both page ranges, warm-boot first access, page switch error propagation, SPI ID/OF matching, and regmap multi-byte reads used by the core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/bme680_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/ccs811.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/ccs811.c

## Purpose
`ccs811.c` supports AMS CCS811 VOC sensors over I2C. It exposes raw current, voltage, equivalent CO2, and TVOC readings, plus optional IRQ-backed triggered buffering for CO2/VOC samples.

## Important APIs, Types, And Functions
`struct ccs811_reading` maps the 8-byte algorithm result frame. `struct ccs811_data` stores the I2C client, lock, reading buffer, optional trigger, wakeup GPIO, trigger state, and scan buffer. `ccs811_start_sensor_application()` transitions boot firmware to application mode. `ccs811_setup()` selects 1-second IAQ mode. `ccs811_get_measurement()` wakes the sensor, polls data-ready up to one second, and reads results. Trigger callbacks enable interrupt mode, poll the trigger, read scan data, and push buffers.

## Control Flow
Probe validates I2C functionality, acquires optional wakeup/reset GPIOs, resets the chip, verifies hardware ID/version, starts application mode, initializes direct IIO channels, optionally registers a data-ready trigger, sets up a triggered buffer, and registers the device. Remove unregisters and puts the chip in idle mode.

## State And Persistence
The device is configured into 1-second IAQ mode and later idle on remove. `drdy_trig_on` tracks trigger enable state, and the latest direct-read frame is stored in memory. Wakeup GPIO state is toggled around direct reads and probe operations.

## Dependencies And Integration Points
It uses I2C SMBus, GPIO descriptors, IIO triggers, triggered buffers, direct-mode claiming, and optional IRQ data-ready integration.

## Risks
`ccs811_get_measurement()` returns early on status-read errors without deasserting wakeup GPIO. It does not read/log detailed error register contents despite TODOs. Direct reads claim direct mode, but trigger-mode I2C operations are not guarded by the same mutex. Trigger handler reads only the first four bytes into big-endian scan channels.

## Test Signals
Test boot-to-app transition, reset GPIO and software reset paths, wakeup GPIO cleanup on errors, data-ready timeout, direct read units, IRQ trigger enable/disable bits, buffer scans, and remove idle write failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/ccs811.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/ens160.h -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/ens160.h

## Purpose
`ens160.h` defines the shared interface between the ENS160 core and I2C/SPI transport drivers.

## Important APIs, Types, And Functions
It declares `devm_ens160_core_probe(struct device *dev, struct regmap *regmap, int irq, const char *name)` and exports `ens160_pm_ops` for transport drivers.

## Control Flow
No runtime control flow exists in the header. Transports create a regmap and call the core probe, passing IRQ and name.

## State And Persistence
No state is stored here. It only describes the cross-file API.

## Dependencies And Integration Points
The header relies on visible `struct device`, `struct regmap`, and `struct dev_pm_ops` declarations through included contexts. It is included by `ens160_core.c`, `ens160_i2c.c`, and `ens160_spi.c`.

## Risks
The header itself does not include `<linux/device.h>`, `<linux/regmap.h>`, or `<linux/pm.h>`, so include order in transport files matters. API changes must be synchronized across all three files and namespace exports.

## Test Signals
Compile transports independently as modules, include-order checks, and namespace import/export validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/ens160.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/ens160_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/ens160_core.c

## Purpose
`ens160_core.c` implements the ScioSense ENS160 multi-gas IIO core. It exposes TVOC and equivalent CO2 concentration channels, optional IRQ-triggered buffering, chip initialization, and sleep PM.

## Important APIs, Types, And Functions
`struct ens160_data` stores regmap, mutex, aligned scan buffer, firmware version bytes, and a 16-bit scratch buffer. `ens160_chip_init()` resets the device, verifies part ID, moves to idle, clears GPR, requests firmware version, enters standard mode, registers an idle cleanup action, and checks device status validity. `ens160_read_raw()` handles direct raw reads and scales. `ens160_trigger_handler()` bulk-reads TVOC/ECO2 into the scan. `ens160_setup_trigger()` registers an own-device data-ready trigger. `devm_ens160_core_probe()` wires everything together and is exported.

## Control Flow
Transport probe calls the core with regmap and IRQ. The core optionally registers a trigger if IRQ is positive, initializes the chip, initializes the mutex, sets up a triggered buffer, and registers the IIO device. Direct reads claim direct mode, lock, bulk-read one channel, and release. IRQ-triggered buffer reads both channels from consecutive registers.

## State And Persistence
Firmware version and mode state are cached/logged during init. The cleanup action returns the chip to idle. Suspend enters deep sleep; resume transitions idle then standard. The mutex serializes direct and buffered reads.

## Dependencies And Integration Points
It depends on regmap, IIO direct/triggered-buffer APIs, IIO triggers, sleep PM ops, and `IIO_ENS160` namespace export for transports.

## Risks
The mutex is initialized after `ens160_chip_init()`, but direct/buffer callbacks are not registered until later, so this is acceptable but fragile if init starts using the mutex. Status validity is checked only once. Environmental compensation input registers are defined but not exposed. IRQ setup occurs before chip init; trigger won't be active yet, but error ordering should be tested.

## Test Signals
Test part ID mismatch, firmware version command sequence, status validity failure, direct read scales, IRQ and no-IRQ probe paths, trigger enable bits, suspend/resume modes, and cleanup action on probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/ens160_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/ens160_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/ens160_i2c.c

## Purpose
`ens160_i2c.c` is the I2C transport for the ENS160 core.

## Important APIs, Types, And Functions
It defines an 8-bit register/8-bit value regmap config and `ens160_i2c_probe()`, which initializes I2C regmap and calls `devm_ens160_core_probe()` with `client->irq` and name `"ens160"`.

## Control Flow
I2C or OF matching invokes probe, which creates regmap and delegates all device initialization to the core. Sleep PM uses shared `ens160_pm_ops`.

## State And Persistence
No transport-specific state is kept beyond devm regmap lifetime.

## Dependencies And Integration Points
It depends on I2C, regmap-I2C, OF/I2C ID tables, shared ENS160 core API, and imports namespace `IIO_ENS160`.

## Risks
The transport passes a fixed name rather than ID-derived name. Regmap init failure is propagated with `dev_err_probe()`. Build correctness depends on Kconfig selecting `REGMAP_I2C`.

## Test Signals
Test I2C/OF match, regmap failure, IRQ forwarding, sleep PM linkage, and module namespace import.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/ens160_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/ens160_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/ens160_spi.c

## Purpose
`ens160_spi.c` is the SPI transport for the ENS160 core.

## Important APIs, Types, And Functions
It defines `ENS160_SPI_READ`, a regmap config with 8-bit register/value fields, `reg_shift = -1`, and read flag bit 0. `ens160_spi_probe()` creates SPI regmap and calls `devm_ens160_core_probe()` with `spi->irq`.

## Control Flow
SPI or OF matching invokes probe, regmap handles the protocol-specific shifted/read-flag format, and the shared core performs chip setup and IIO registration.

## State And Persistence
No transport-private runtime state is kept.

## Dependencies And Integration Points
It depends on SPI, regmap-SPI, OF/SPI ID tables, shared ENS160 core API, shared sleep PM ops, and namespace `IIO_ENS160`.

## Risks
The `reg_shift = -1`/read-flag protocol is easy to break if the core assumes ordinary register numbering. Build correctness depends on Kconfig selecting `REGMAP_SPI`. Fixed name `"ens160"` is used for all SPI instances.

## Test Signals
Test SPI read/write framing, OF/SPI matching, IRQ forwarding, PM callback linkage, and regmap init failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/ens160_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/mhz19b.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/mhz19b.c

## Purpose
`mhz19b.c` is a serdev IIO driver for Winsen MH-Z19B CO2 sensors. It exposes raw CO2 concentration and calibration sysfs controls for automatic baseline correction, zero point, and span point.

## Important APIs, Types, And Functions
`struct mhz19b_state` stores the serdev device, completion, receive index, and 9-byte command/response buffer. `mhz19b_get_checksum()` computes the protocol checksum. `mhz19b_serdev_cmd()` builds commands, writes them synchronously, and for read commands waits for a full response and validates checksum. `mhz19b_receive_buf()` appends received bytes and completes when nine bytes are collected. Attribute stores call calibration commands.

## Control Flow
Probe configures serdev at 9600 baud, no flow control, no parity; allocates IIO state; enables `vin`; and registers one CO2 channel. Runtime reads send command `0x86` and wait up to 100 ms. Calibration writes send no-response commands.

## State And Persistence
The receive buffer and completion are volatile. Sensor calibration commands alter device-side calibration state, but the driver does not cache it. No mutex serializes command/response access.

## Dependencies And Integration Points
It uses serdev, completions, regulator enable, unaligned big-endian helpers, IIO sysfs attrs, and OF matching.

## Risks
`mhz19b_receive_buf()` copies `len` bytes without bounding against remaining buffer space, so fragmented or oversized receive chunks can overflow `buf`. Concurrent reads/calibration commands can interleave because there is no lock and completion is not reinitialized before commands. The checksum formula returns two's complement of sum without the common `+1`, which should be verified against the protocol.

## Test Signals
Test fragmented and oversized RX frames, read timeout, checksum validation, concurrent reads, calibration argument bounds, regulator failure, and serial settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/mhz19b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/pms7003.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/pms7003.c

## Purpose
`pms7003.c` is a serdev IIO driver for Plantower particulate matter sensors. It exposes processed PM1, PM2.5, and PM10 mass concentration channels and supports triggered buffering.

## Important APIs, Types, And Functions
`struct pms7003_frame` tracks data bytes, expected length, and current length. `struct pms7003_state` stores serdev, frame, completion, mutex, and scan buffer. `pms7003_do_cmd()` sends a 7-byte command and waits for a valid frame. `pms7003_receive_buf()` parses start-of-frame magic, length, payload, and checksum. `pms7003_read_raw()` and `pms7003_trigger_handler()` request passive readings and decode PM offsets. `pms7003_stop()` sends sleep as a devm cleanup action.

## Control Flow
Probe configures serdev, wakes the sensor, enters passive mode, registers sleep cleanup, sets up a triggered buffer, and registers the IIO device. Direct reads and trigger handler both lock, send `CMD_READ_PASSIVE`, wait for the receive callback to complete a frame, decode clamped PM values, and return or push data.

## State And Persistence
The sensor is put in passive mode and later sleep. Frame parser state persists across receive callbacks and is protected indirectly by command lock for consumers, though receive callback itself does not take the mutex. Scan data is volatile.

## Dependencies And Integration Points
It integrates with serdev, completions, IIO direct channels, triggered buffers, scan masks, and OF matching for several Plantower models.

## Risks
`pms7003_do_cmd()` does not reinitialize `frame_ready` before each command, so stale completions may satisfy later reads. The receive callback mutates frame state without locking against command users. If invalid checksums arrive, callers wait until timeout. Initial receive parsing returns consumed byte counts that may drop partial headers.

## Test Signals
Test wake/passive/sleep command flow, frame parsing with fragmented input, bad checksum timeout, stale completion behavior, direct and buffered reads, PM value clamping, and serdev configuration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/pms7003.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/scd30.h -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/scd30.h

## Purpose
`scd30.h` is the shared header for Sensirion SCD30 CO2 sensor core and transports. It defines command IDs, common state, command callback type, PM ops, and core probe signature.

## Important APIs, Types, And Functions
`enum scd30_cmd` lists transport-neutral operations: start/stop measurement, interval, readiness, read measurement, automatic self calibration, forced recalibration, temperature offset, firmware version, and reset. `scd30_command_t` abstracts transport command execution. `struct scd30_state` stores serialization lock, device/regulator, measurement completion, transport private pointer, IRQ, cached pressure compensation, interval, latest measurements, and command callback. `scd30_probe()` is the shared core entry.

## Control Flow
The header has no executable control flow. Transport drivers provide a `scd30_command_t` implementation and call `scd30_probe()`, after which the core uses the callback for all device operations.

## State And Persistence
The shared state caches pressure compensation because the sensor cannot report it, measurement interval, and latest measurements. The mutex serializes device access and completion reports data readiness.

## Dependencies And Integration Points
It depends on completion, mutex, device, PM, regulator, and fixed-width types. It bridges I2C/serial transport implementations with the SCD30 core.

## Risks
Transport-private storage is embedded as `void *priv` because device driver data is already used for IIO; misuse can create lifetime issues. Cached pressure compensation can drift from hardware if commands fail. Command enum and transport implementations must remain synchronized.

## Test Signals
Compile all SCD30 transports, verify command callback coverage for every enum value, test cached pressure/interval behavior, IRQ and polling readiness paths, and suspend/resume PM ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/scd30.h -->
