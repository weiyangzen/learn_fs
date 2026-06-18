# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/Makefile

## Purpose
Maps QE and CPM configuration symbols to built object files.

## Important build rules
`CONFIG_QUICC_ENGINE` builds `qe.o`, `qe_common.o`, `qe_ic.o`, and `qe_io.o`. `CONFIG_CPM` also builds `qe_common.o` for shared CPM MURAM support. Feature symbols add `tsa.o`, `qmc.o`, `ucc.o`, `ucc_slow.o`, `ucc_fast.o`, `qe_tdm.o`, `usb.o`, and the GPIO pair `gpio.o qe_ports_ic.o`.

## Control flow and state behavior
There is no runtime control flow. The Makefile determines which exported symbols are available and which platform drivers register at init time.

## Dependencies and integration points
The object grouping mirrors the Kconfig dependencies and shares `qe_common.o` between CPM and QE. `CONFIG_QE_GPIO` intentionally builds both gpiolib support and the port interrupt controller, so GPIO interrupt users require both objects to be present.

## Risks and test signals
Because `qe_common.o` appears under both `CONFIG_QUICC_ENGINE` and `CONFIG_CPM`, build combinations should confirm it is linked exactly as expected. Test signals are successful builds for QE-only, CPM-only, QE GPIO, TDM, TSA/QMC, USB, and UCC configurations.
