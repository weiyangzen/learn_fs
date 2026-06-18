# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-spi.c

## Purpose
SPI4 Ethernet interface support for Octeon, including error interrupt handling and retraining.

## Important APIs, Types, And Functions
Exports `cvm_oct_spi_init()` and `cvm_oct_spi_uninit()`. Internal helpers include `cvm_oct_spi_rml_interrupt()`, `cvm_oct_spi_spx_int()`, `cvm_oct_spi_enable_error_reporting()`, `cvm_oct_spi_poll()`, `cvm_oct_spxx_int_pr()`, and `cvm_oct_stxx_int_pr()`.

## Control Flow
First SPI port initialization requests the shared RML IRQ. Interface-leading ports enable SPX/STX error masks and install `cvm_oct_spi_poll()`. RML interrupt checks SPX blocks, prints masked errors unless retraining is already pending, disables masks, and sets `need_retrain`. Polling restarts interfaces needing retrain, re-enables error reporting on success, and slowly checks SPI4000 speed for one port per second. Uninit decrements the active-port count; the last port disables masks and frees the IRQ.

## State And Persistence
Static `number_spi_ports` counts users, and `need_retrain[2]` tracks per-interface retraining. Per-port `priv->poll` is set for leading ports. State is runtime-only.

## Dependencies And Integration Points
Depends on common init/uninit, CVMX SPI/SPX/STX/NPI CSRs, RML IRQ, netdev private port/interface mapping, and SPI4000 helper code.

## Risks
Shared IRQ lifetime depends on correct active-port counting. Error masks are disabled on first error until polling retrains. Slow SPI4000 polling delays speed-change detection. Only two SPI interfaces are tracked.

## Test Signals
Single and multiple SPI ports, RML interrupt from SPX0/SPX1, each error bit log path, retrain success/failure, uninit of last port freeing IRQ, and SPI4000 speed polling rotation.
