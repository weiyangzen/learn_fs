<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/amd_xdma.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/amd_xdma.h

## Purpose
Declares AMD XDMA user interrupt helper APIs for platform devices.

## Important APIs, Types, And Functions
The API consists of `xdma_enable_user_irq()`, `xdma_disable_user_irq()`, and `xdma_get_user_irq()`, each operating on a `struct platform_device` and a user IRQ index or number.

## Control Flow
Platform consumers resolve a user IRQ with `xdma_get_user_irq()`, enable it when ready to receive interrupts, and disable it during teardown or masking.

## State And Persistence
State is controller-managed IRQ enablement and platform-device IRQ routing. There is no persistence.

## Dependencies And Integration Points
Depends on platform devices and interrupt infrastructure. It integrates AMD XDMA DMAengine/controller users with out-of-band user IRQ delivery.

## Risks And Edge Cases
Invalid IRQ indices or teardown races can enable the wrong line or leave interrupts active after resources are freed. Enable/disable must be balanced around handler lifetime.

## Test Signals
Tests should cover valid and invalid IRQ lookup, enable/disable balance, interrupt delivery after enable, no delivery after disable, and device removal with IRQs enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/amd_xdma.h -->
