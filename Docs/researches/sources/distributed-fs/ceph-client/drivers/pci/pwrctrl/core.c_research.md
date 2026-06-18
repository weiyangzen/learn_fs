# sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/core.c

## Purpose
This file is the shared PCI power-control core. It creates platform devices for devicetree PCI children that require pre-enumeration power control, invokes provider power-on/power-off callbacks in a depth-first order, and marks duplicated OF nodes as reused when the actual PCI device appears.

## Important APIs, types, and functions
The public provider API is `pci_pwrctrl_init()`, `pci_pwrctrl_device_set_ready()`, `pci_pwrctrl_device_unset_ready()`, and `devm_pci_pwrctrl_device_set_ready()`. Host-controller-facing APIs are `pci_pwrctrl_create_devices()`, `pci_pwrctrl_destroy_devices()`, `pci_pwrctrl_power_on_devices()`, and `pci_pwrctrl_power_off_devices()`. Internal helpers walk the OF tree, create/destroy platform devices, detect whether a node requires pwrctrl, and invoke `struct pci_pwrctrl::power_on` or `power_off`.

## Control flow
Host controllers call `pci_pwrctrl_create_devices()` before PCI scan. The core recursively traverses available children under the host OF node, skips nodes that already have platform devices, and creates pwrctrl platform devices only for compatible strings beginning with `pci` that have PCI supplies locally or in a remote endpoint parent. Providers bind to those platform devices, initialize `struct pci_pwrctrl`, and register a PCI bus notifier via `devm_pci_pwrctrl_device_set_ready()`. Host controllers then call `pci_pwrctrl_power_on_devices()` before enumeration; the core descends into children first, requires each pwrctrl platform driver to be bound, and rolls back earlier powered devices on error. Power-off and destroy paths mirror the tree traversal.

## State and persistence
State lives in platform devices, their driver data (`struct pci_pwrctrl`), the registered notifier block, and OF node population flags. There is no durable state. The notifier sets `dev->of_node_reused` for the PCI device that shares the same fwnode as the pwrctrl platform device, avoiding duplicate pin binding.

## Dependencies and integration points
The core depends on OF graph helpers, OF platform device creation, fwnode matching, PCI bus notifiers, platform devices, and the public `<linux/pci-pwrctrl.h>` contract. It integrates with host controllers such as Qualcomm DWC and MediaTek Gen3 controllers that create, power, and destroy pwrctrl devices around PCI link bring-up and enumeration. Provider drivers in this directory implement the actual power sequencing.

## Risks
The power-on path currently uses `-EPROBE_DEFER` when a platform device exists but its driver is not bound; the comment notes a blocking wait would be better. Depth-first order must match hardware dependencies, and rollback only powers off earlier siblings before the failed child. `pci_pwrctrl_is_required()` is intentionally selective; incorrect DT compatible strings or missing supply properties silently skip platform-device creation. Destroying devices clears `OF_POPULATED`, so ordering with other OF platform users must remain correct.

## Test signals
Boot tests should show pwrctrl platform devices created only for eligible PCI DT nodes and no duplicate pinctrl binding when PCI devices enumerate. Controller tests should cover deferred provider binding, power-on rollback, recursive child ordering, remote endpoint supply detection, destroy cleanup, and module unload of providers with the devm notifier cleanup path.
