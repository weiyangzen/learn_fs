# sources/distributed-fs/ceph-client/drivers/spi/spi-brcmstb-qspi.c

## Purpose
Provides the BRCMSTB-specific platform wrapper for the common Broadcom QSPI driver. It binds set-top SoC compatibles and delegates all substantive controller behavior to `spi-bcm-qspi.c`.

## Important APIs, Types, And Functions
The file defines an OF match table for `brcm,spi-brcmstb-qspi` and `brcm,spi-brcmstb-mspi`, a probe function that calls `bcm_qspi_probe(pdev, NULL)`, a remove function that calls `bcm_qspi_remove()`, and a `platform_driver` using the common `bcm_qspi_pm_ops`.

## Control Flow
When a matching platform device probes, the wrapper invokes the common QSPI probe with no SoC-specific interrupt controller, causing the common driver to use its direct/named IRQ handling paths. Remove and PM operations are similarly delegated to common code.

## State And Persistence
This wrapper maintains no private runtime state. Platform driver binding state is held by the driver core, and all controller state is allocated and stored by the common Broadcom QSPI driver.

## Dependencies And Integration Points
It depends on platform driver infrastructure, OF matching, module support, and `spi-bcm-qspi.h`. It integrates BRCMSTB device-tree compatibles with the common QSPI implementation.

## Risks And Edge Cases
Because it passes `NULL` for `soc_intc`, BRCMSTB devices that route interrupts through a SoC-specific mux would need a different wrapper or new integration. Any common-driver probe requirement for named resources, IRQs, or clocks applies here even though this file does not mention those resources.

## Test Signals
Probe a BRCMSTB QSPI/MSPI node and verify the common driver registers the SPI controller, resources map correctly, IRQs are requested, and suspend/resume uses `bcm_qspi_pm_ops`. Wrapper-specific testing is mostly compatible-string coverage.
