# sources/distributed-fs/ceph-client/drivers/reset/reset-berlin.c

Purpose: Marvell/Synaptics Berlin reset provider using parent syscon registers and two-cell reset specifiers.

Important APIs/types/functions: `struct berlin_reset_priv`, `berlin_reset_reset()`, `berlin_reset_xlate()`, and `berlin2_reset_probe()`.

Control flow: xlate takes `(offset, bit)`, validates bit < 32, and encodes reset ID. Probe gets the parent node regmap, sets `of_reset_n_cells = 2`, and registers. Reset writes the bit mask to the encoded offset and waits 10 us.

State and persistence: command-style writes only; no cached reset state.

Dependencies and integration: platform bus, OF parent syscon, regmap, reset framework.

Risks and test signals: parent syscon lookup is required; no status/assert/deassert are provided. Test DT two-cell translation, invalid bit rejection, and reset timing for Berlin devices.
