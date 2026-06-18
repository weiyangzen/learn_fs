# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rcar-ep.c

## Purpose

`pcie-rcar-ep.c` is the Renesas R-Car PCIe endpoint-controller driver. It configures an R-Car PCIe block in endpoint mode, exposes PCI EPC operations to endpoint-function drivers, manages inbound BAR windows and outbound host-memory windows, programs endpoint headers/MSI capability, raises INTx/MSI interrupts, and initializes endpoint memory windows from platform resources.

## Important APIs, Types, And Functions

- `struct rcar_pcie_endpoint` wraps shared `struct rcar_pcie` with outbound memory window metadata, mapped outbound addresses, max functions, BAR-to-ATU mapping, inbound window bitmap, and window counts.
- `rcar_pcie_ep_hw_init()` places hardware in endpoint mode, initializes PCIe capabilities, header type, MPSS/MRRS, target speed, completion timeout, and capability termination.
- `rcar_pcie_ep_get_pdata()` maps controller registers, allocates outbound window descriptors, parses outbound memory resources, and reads `max-functions`.
- `rcar_pcie_parse_outbound_ranges()` collects `memoryN` platform resources into `pci_epc_mem_window` entries and requests those regions.
- `rcar_pcie_ep_write_header()` writes vendor/device/class/subsystem IDs and INTx pin into endpoint config registers.
- `rcar_pcie_ep_set_bar()` allocates inbound windows, rounds/alignment-limits BAR size, programs inbound translation, and waits for PHY readiness.
- `rcar_pcie_ep_map_addr()` finds the outbound window matching an EPC memory allocation, checks data link, and programs outbound translation to host PCI address.
- `rcar_pcie_ep_raise_irq()`, `rcar_pcie_ep_assert_intx()`, and `rcar_pcie_ep_assert_msi()` implement EPC interrupt requests.
- `rcar_pcie_ep_probe()` enables runtime PM, maps resources, allocates bitmaps, creates the EPC, initializes hardware and EPC memory windows, and calls `pci_epc_init_notify()`.

## Control Flow

Probe allocates endpoint state, resumes the device with runtime PM, gathers MMIO and outbound memory resources, allocates the inbound bitmap and outbound mapped-address table, creates a devm EPC using `rcar_pcie_epc_ops`, stores driver data, initializes endpoint hardware registers, initializes EPC memory windows with `pci_epc_multi_mem_init()`, and notifies endpoint-function drivers that the controller is ready.

Endpoint-function operations then call into this file. Header writes update config identity registers. BAR setup finds free inbound windows, marks a pair because BARs are treated as 64-bit, calculates the largest supported aligned size, and calls shared R-Car inbound programming. Outbound mapping requires the link to be up and uses the memory window whose physical base matches the EPC allocation. Start writes MAC and controller init bits; stop clears the controller enable register.

## State And Persistence

Inbound window allocation persists in `ib_window_map`; `bar_to_atu` remembers which inbound ATU index backs each BAR; `ob_mapped_addr` records outbound windows currently mapped to endpoint physical addresses. Hardware config registers persist until stop/reset/power loss. Runtime PM keeps the controller powered after probe. No disk persistence exists.

## Dependencies And Integration Points

The file depends on the shared R-Car PCIe helpers in `pcie-rcar.h`, the PCI endpoint controller framework (`pci_epc`, `pci_epc_mem_window`, endpoint-function callbacks), platform named memory resources (`memory0` and onward), OF address mapping, runtime PM, and Renesas compatible strings `renesas,r8a774c0-pcie-ep` and `renesas,rcar-gen3-pcie-ep`.

## Risks And Edge Cases

- `rcar_pcie_ep_get_pdata()` calls `rcar_pcie_parse_outbound_ranges()` but does not check its return value, so missing outbound resources may not abort as intended.
- `rcar_pcie_ep_clear_bar()` computes `atu_index` but calls `rcar_pcie_set_inbound()` with `bar` rather than the mapped ATU index, which looks suspicious when BAR numbers and inbound indices diverge.
- BAR setup marks `idx` and `idx + 1` without explicitly checking that `idx + 1` is within the bitmap.
- Outbound mapping matches only exact physical window bases; suballocations are intentionally not supported because page size equals window size.
- INTx is rejected when MSI is enabled or INTx disable is set; endpoint-function drivers need to select the right interrupt mode.

## Test Signals

Test probe with complete and missing `memoryN` resources, EPC creation, endpoint function binding, config header writes, BAR0/2/4 setup and clear, inbound bitmap exhaustion, outbound map/unmap before and after link-up, INTx and MSI interrupt generation, runtime PM failures, max-functions clamping, and host-side enumeration of the endpoint capabilities and BAR sizes.
