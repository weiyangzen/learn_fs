# sources/distributed-fs/ceph-client/drivers/power/sequencing/pwrseq-pcie-m2.c

## Purpose
`pwrseq-pcie-m2.c` is a power-sequencing provider for PCIe M.2 Key M and Key E connectors. It exposes `pcie` and, for Key E, `uart` targets backed by connector regulators and W_DISABLE GPIOs, and can dynamically create a Bluetooth serdev device for Qualcomm WCN7850 cards discovered over PCIe.

## Important APIs, Types, and Functions
Important state is `struct pwrseq_pcie_m2_ctx` with pwrseq device, connector OF node, regulator array, W_DISABLE GPIOs, PCI notifier, optional serdev, and OF changeset. Unit callbacks bulk-enable regulators and drive `w-disable1`/`w-disable2`; targets include `pcie` and `uart` with optional 50 ms post-enable delay. Matching walks OF graph endpoints to associate consumers with the connector.

## Control Flow
Probe reads match data for Key M or Key E, obtains all regulators from the connector node, gets optional W_DISABLE GPIOs initially high, registers the pwrseq provider, and conditionally registers a PCI bus notifier when the connector has both PCIe and serial graph links. The notifier filters PCI devices by the connector's PCIe endpoint and, for Qualcomm vendor device `0x1107`, creates or removes a serdev child plus a dynamic `bluetooth` OF node.

## State and Persistence Behavior
Persistent state includes regulator handles, GPIO output levels, pwrseq units' enable counts in the core, PCI notifier registration, optional serdev device, and an OF changeset that must be reverted on removal. Hardware rails and W_DISABLE lines persist while targets are powered.

## Dependencies and Integration Points
It depends on OF graph bindings for M.2 connectors, regulator bulk APIs including `of_regulator_bulk_get_all()`, GPIO descriptors, PCI bus notifiers, serdev, dynamic OF changesets, and the pwrseq provider core.

## Risks and Edge Cases
The WCN7850 serdev creation path is tightly coupled to PCI discovery order and graph port numbers. Regulator arrays are manually freed, so error/remove paths must stay balanced. A fixed 50 ms delay is a known FIXME because not all cards need it. Optional GPIO absence is allowed, so target semantics depend on connector wiring. Notifier unregister is called even if no notifier was registered, relying on core tolerance.

## Test Signals
Test Key M and Key E DT graph matching, regulator failure paths, W_DISABLE GPIO polarity, shared regulator refcounts through pwrseq core, PCI add/remove notifier filtering, WCN7850 serdev creation/removal and changeset rollback, and module removal with powered targets.
