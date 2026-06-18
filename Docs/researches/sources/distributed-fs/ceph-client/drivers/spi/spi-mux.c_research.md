<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mux.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-mux.c

## Purpose

`spi-mux.c` implements a generic SPI bus multiplexer. It binds as a child SPI device on a parent controller and registers a new downstream `spi_controller`; child devices on the downstream bus use mux states as logical chip selects, allowing boards to expand available SPI chip selects with a mux controller.

## Important APIs, Types, and Functions

`struct spi_mux_priv` stores the parent `spi_device`, current selected mux state, saved child message callback/context/device pointers, and the `mux_control`. `spi_mux_select()` selects the mux state, mirrors the child device's mode, speed, and bits-per-word into the parent SPI device, and calls `spi_setup()` on the parent. `spi_mux_setup()` defers meaningful setup to transfer time. `spi_mux_transfer_one_message()` rewrites the child message to target the parent device and submits it with `spi_async()`. `spi_mux_complete_cb()` restores message fields, finalizes the child controller message, and deselects the mux.

Probe allocates a controller, raises lockdep subclasses because parent bus locks nest under child bus locks, obtains the mux control, copies capability fields from the parent controller, sets `must_async` and `defer_optimize_message`, uses `mux_control_states()` as chip-select count, and registers the downstream controller.

## Control Flow

When a child message is submitted, the driver selects the mux state matching the child's chip select. If the selected child differs from the current state, parent SPI setup is updated to match the child's speed/mode/word size. The message callback, context, and `spi` pointer are saved, then replaced with mux-owned values and the parent device. The parent controller executes the message asynchronously. On completion, the mux callback restores the original child message metadata, finalizes the downstream controller's current message, and deselects the mux.

## State and Persistence Behavior

The only persistent state is `current_cs`, which caches the mux state last programmed, and the saved callback/context/device fields while one message is in flight. No data is persisted across boots or to disk. Mux hardware state persists only until deselected or reselected by later operations.

## Dependencies and Integration Points

The driver depends on the SPI core, mux consumer API, lockdep, device tree compatible `spi-mux`, and the parent SPI controller. It intentionally mirrors parent capabilities instead of implementing transfer logic itself.

## Risks and Edge Cases

Message field rewriting is delicate: callback, context, and `m->spi` must be restored exactly once on completion. If `spi_async()` fails after fields are replaced, the current code returns the error without restoring fields or deselecting the mux, which is a risk path to review. The comment states selection should not happen while the parent is already transferring; nested or shared parent use depends on SPI core locking and `must_async`.

The parent device is repeatedly reconfigured to child settings, so child configurations that the parent accepts in isolation but not across rapid switching need coverage.

## Test Signals

Tests should cover multiple downstream chip selects, repeated transfers to the same CS, switching between children with different modes/speeds/bits-per-word, parent `spi_async()` failure, mux select/deselect failure injection, lockdep under nested SPI controllers, unregister while transfers are inactive, and child device probing through device tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mux.c -->
