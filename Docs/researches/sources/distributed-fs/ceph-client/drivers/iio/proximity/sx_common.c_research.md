# sources/distributed-fs/ceph-client/drivers/iio/proximity/sx_common.c

Purpose: shared implementation for newer Semtech SAR/proximity IIO drivers. It centralizes IRQ handling, raw proximity reads, event configuration, channel enable management, triggered-buffer setup, reset/default programming, regulator enablement, and IIO registration.

Important APIs/types/functions: exports `sx_common_events`, `sx_common_read_proximity()`, `sx_common_read_event_config()`, `sx_common_write_event_config()`, and `sx_common_probe()` in namespace `SEMTECH_PROX`. The chip-specific interface is `struct sx_common_chip_info` plus `ops` callbacks for `read_prox_data`, `check_whoami`, `init_compensation`, `wait_for_sample`, and `get_default_reg`.

Control flow: `sx_common_probe()` allocates private data, creates regmap, enables `vdd`/`svdd`, validates identity, initializes the chip, registers an optional IRQ-backed trigger, sets up the triggered buffer, and registers the IIO device. Direct raw reads temporarily enable the channel and conversion-done IRQ, wait by completion or polling callback, read a big-endian sample via chip ops, sign extend, and disable temporary state. IRQ thread clears `IRQ_SRC`, emits threshold events from `reg_stat`, and completes conversions.

State and persistence: `chan_read` and `chan_event` bitmaps are the canonical channel enable state; `sx_common_update_chan_en()` writes the hardware enable register only when the union changes. `chan_prox_stat` suppresses duplicate proximity events. `trigger_enabled` gates top-half trigger polling. Register defaults are applied during init and may come from firmware properties through `get_default_reg`.

Dependencies/integration: depends on I2C regmap, regulator bulk enable, IIO events/triggers/buffers, and chip-specific wrappers that provide register layout and channel tables. It uses runtime-managed device resources and exports GPL namespace symbols for sibling modules.

Risks and test signals: direct reads drop the mutex while waiting and rely on bitmaps to reconcile concurrent buffer/event use. Test concurrent raw read plus event enable, no-IRQ polling callbacks, default register property handling, trigger enable/disable with active raw readers, event direction encoding, and failure unwind when disabling IRQ/channel after a read error.
