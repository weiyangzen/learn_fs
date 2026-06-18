# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe_io.c

## Purpose
Provides low-level QE parallel I/O configuration helpers for legacy users. It maps the PAR IO register array, configures pin direction/open-drain/assignment fields, writes pin data, and applies `pio-map` device-tree tables.

## Important APIs, types, and functions
Exports `par_io_init`, `__par_io_config_pin`, `par_io_config_pin`, `par_io_data_set`, and `par_io_of_config`. Global state is `par_io`, the mapped base pointer, and `num_par_io_ports`.

## Control flow and state behavior
`par_io_init` maps the register resource from a device node and reads optional `num-ports`. `__par_io_config_pin` computes one-bit and two-bit masks for a pin, updates open drain, direction, and assignment registers using big-endian MMIO, and ignores `has_irq`. `par_io_config_pin` validates initialization and port range before configuring a pin. `par_io_data_set` validates port and pin and sets or clears the data bit. `par_io_of_config` follows `pio-handle`, reads `pio-map`, validates six-cell entries, and applies each mapping.

## Dependencies and integration points
Used by `gpio.c` and older QE/UCC clients. Depends on QE PIO register layout from public headers, OF resource translation, and legacy device-tree properties `pio-handle` and `pio-map`.

## Risks and test signals
`par_io_data_set` does not check `par_io` for NULL, unlike `par_io_config_pin`. Read-modify-write sequences are not globally locked here, so concurrent users can race unless higher layers serialize. `has_irq` is accepted but unused. Test signals include correct pin mux register values after `pio-map`, invalid map length rejection, and GPIO driver direction changes through `__par_io_config_pin`.
