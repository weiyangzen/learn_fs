# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/Kconfig

## Purpose
This Kconfig file exposes the Intel Infrastructure Data Path Function driver to kernel configuration. It controls whether the `idpf` module is built and whether optional legacy single queue datapath support is compiled.

## Important APIs, Types, And Functions
`config IDPF` is a tristate option named "Intel(R) Infrastructure Data Path Function Support". It depends on `PCI_MSI` and `PTP_1588_CLOCK_OPTIONAL`, and selects `DIMLIB` and `LIBETH_XDP`. `config IDPF_SINGLEQ` is a boolean nested under `if IDPF`; it enables legacy single Rx/Tx queues without completion/fill queues.

## Control Flow
Kconfig has declarative build-time control flow. If `IDPF` is disabled, the driver object is not built. If it is `m`, the driver builds as the `idpf` module. If `IDPF_SINGLEQ` is enabled, the Makefile includes `idpf_singleq_txrx.o`, and runtime helpers such as `idpf_is_queue_model_split()` allow either single or split queue models.

## State And Persistence
The file persists user or distribution build choices in the kernel `.config`. It does not create runtime state, but the selected options change the compiled code paths and hotpath checks available in the driver.

## Dependencies And Integration Points
`PCI_MSI` is required for interrupt support. `PTP_1588_CLOCK_OPTIONAL` permits optional PTP integration. `DIMLIB` supports dynamic interrupt moderation and `LIBETH_XDP` supports the XDP/libeth integration used by the driver. `IDPF_SINGLEQ` integrates with the Makefile and conditional code under `CONFIG_IDPF_SINGLEQ`.

## Risks
The help text for `IDPF_SINGLEQ` notes increased driver size and runtime hotpath checks. A misspelled help word "runtme" is cosmetic. Incorrect dependency selection would surface as build failures in objects that assume MSI, PTP optional APIs, DIM, or XDP helpers.

## Test Signals
Build matrix coverage should include `IDPF=n`, `IDPF=m`, `IDPF=y`, and `IDPF_SINGLEQ=y/n`. With single queue disabled, split queue paths should remain functional and no unresolved references to `idpf_singleq_txrx.o` should exist.
