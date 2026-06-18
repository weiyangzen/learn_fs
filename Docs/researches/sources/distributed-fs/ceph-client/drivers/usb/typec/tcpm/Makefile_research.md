# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/Makefile

## Purpose

`tcpm/Makefile` maps TCPM-related Kconfig symbols to object files and composite modules.

## Important APIs, Types, and Functions

`tcpm.o`, `fusb302.o`, `typec_wcove.o`, `tcpci.o`, `tcpci_rt1711h.o`, `tcpci_mt6360.o`, `tcpci_mt6370.o`, `tcpci_maxim.o`, and the `qcom/` subdirectory are selected by their matching config symbols. Composite definitions map `typec_wcove-y := wcove.o` and `tcpci_maxim-y += tcpci_maxim_core.o maxim_contaminant.o`.

## Control Flow

There is no runtime flow. Kbuild uses these object lists to decide module names and link composition.

## State and Persistence Behavior

The file controls build artifacts only. It has no runtime persistence.

## Dependencies and Integration Points

It integrates the generic TCPM core, TCPCI framework, vendor TCPCI helpers, FUSB302, WCOVE, Maxim contaminant helper, and Qualcomm PMIC subdirectory into the kernel build.

## Risks and Test Signals

Risks include stale object lists when files move or composite modules gain dependencies, especially Maxim contaminant coupling to `tcpci_maxim_core.o`. Test signals are module builds for each config and verifying expected module names.
