# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_irq.c

## Purpose

`fbnic_irq.c` owns MSI-X vector allocation, firmware mailbox interrupt setup/teardown, MAC/PCS link interrupt setup/teardown, generic IRQ request/free wrappers, the MSI-X self-test, and NAPI vector IRQ sharing/refcounting. It connects PCI IRQ vectors and FBNIC interrupt CSRs to mailbox polling, phylink link-change reporting, and Tx/Rx NAPI cleanup.

## Important APIs, Types, And Functions

Firmware mailbox lifecycle is `fbnic_fw_request_mbx()` and `fbnic_fw_free_mbx()`, with handler `fbnic_fw_msix_intr()` and helper `__fbnic_fw_enable_mbx()`. MAC link IRQ lifecycle is `fbnic_mac_request_irq()` and `fbnic_mac_free_irq()`, with handler `fbnic_mac_msix_intr()`. Generic wrappers are `fbnic_synchronize_irq()`, `fbnic_request_irq()`, and `fbnic_free_irq()`.

MSI-X test support uses `struct fbnic_msix_test_data`, `fbnic_irq_test()`, and `fbnic_msix_test()`. NAPI IRQ functions are `fbnic_napi_name_irqs()`, `fbnic_napi_request_irq()`, and `fbnic_napi_free_irq()`. Global vector allocation is handled by `fbnic_alloc_irqs()` and `fbnic_free_irqs()`.

## Control Flow

`fbnic_alloc_irqs()` requests MSI-X vectors from PCI, with a minimum of non-NAPI vectors plus one data vector and a target of non-NAPI vectors plus up to online CPUs/Rx queue maximum. It records `fbd->num_irqs` and warns if fewer than desired were allocated.

Mailbox IRQ request obtains vector `FBNIC_FW_MSIX_ENTRY`, requests a threaded IRQ with `IRQF_ONESHOT | IRQF_NO_AUTOEN`, initializes/polls the mailbox ready state, enables the IRQ, and unmasks the firmware interrupt bit. The mailbox handler polls firmware messages and unmasks the vector through `FBNIC_INTR_MASK_CLEAR(0)`.

MAC IRQ request obtains vector `FBNIC_PCS_MSIX_ENTRY`, installs a hard IRQ handler, maps PCS cause to the vector through `FBNIC_INTR_MSIX_CTRL()`, and clears an RXB mapping. The MAC handler asks MAC ops for a link event; no-event paths unmask and exit, while link-down detection calls `phylink_pcs_change(fbn->pcs, false)`.

`fbnic_msix_test()` requests temporary IRQ handlers for NAPI vectors, then for each vector tests masked set, unmask delivery, no duplicate delivery on mask clear, unmasked delivery, status clear, and mask set behavior. It cleans up hardware status/mask bits and frees IRQs on all paths.

NAPI request/free uses `fbd->napi_irq[i].users` so multiple NAPI vector users can share an IRQ allocation and free it only when the last user releases it.

## State And Persistence

State is in `fbd->fw_msix_vector`, `fbd->mac_msix_vector`, `fbd->num_irqs`, and `fbd->napi_irq[]` names/user counts. Interrupt masks and MSI-X control mappings live in device CSRs. IRQ allocations persist until explicit free or PCI vector free.

## Dependencies And Integration Points

The file depends on Linux PCI IRQ vector APIs, request/free IRQ, FBNIC CSR interrupt registers, mailbox polling from `fbnic_fw.c`, MAC ops and phylink, netdev-private `struct fbnic_net`, and Tx/Rx NAPI handler `fbnic_msix_clean_rings()`. Ethtool offline self-test calls `fbnic_msix_test()`.

## Risks And Edge Cases

Mailbox request sets `fbd->fw_msix_vector` after attempting enable; if enable fails and the vector is freed, the stored vector is still assigned before return in the current code path, so callers must handle failure carefully or this may leave stale state. IRQ teardown must mask/synchronize before freeing to avoid handlers re-unmasking disabled vectors. MSI-X self-test temporarily requests all data-vector IRQs and manipulates global interrupt masks/status; it should only run offline. NAPI IRQ user refcounts must remain balanced or vectors leak or are freed while still in use.

## Test Signals

Useful tests include successful vector allocation with expected warning when fewer vectors are available, mailbox IRQ bringup and teardown across reset, MAC link-down interrupt propagation to phylink, NAPI IRQ request/free refcount balance, offline MSI-X self-test pass and each failure code under fault injection, and no interrupts after free. No executable tests were run for this research item.
