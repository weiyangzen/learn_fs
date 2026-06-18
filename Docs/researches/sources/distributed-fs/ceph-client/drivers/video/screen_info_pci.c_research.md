# sources/distributed-fs/ceph-client/drivers/video/screen_info_pci.c

Purpose: PCI-specific helpers for firmware framebuffer relocation and parent-device discovery. It tracks which display PCI BAR contains the firmware linear framebuffer and updates `screen_info` if firmware framebuffer memory is relocated by PCI resource assignment.

Important APIs, types, and functions: exported `screen_info_apply_fixups` and `screen_info_pci_dev`. Internal state includes `screen_info_lfb_pdev`, BAR index, original resource start, and framebuffer offset. Internal helpers include `__screen_info_relocation_is_valid`, `__screen_info_lfb_pci_bus_region`, `screen_info_fixup_lfb`, and `__screen_info_pci_dev`.

Control flow: a PCI header fixup runs for display-class devices, converts the screen_info LFB bus range into a resource, finds the containing PCI resource, and records pdev/BAR/offset/original base once. Later `screen_info_apply_fixups` compares current BAR start with the original; if relocated and still valid, it updates the primary display LFB base, otherwise warns and disables usability by not applying the invalid relocation. `screen_info_pci_dev` derives screen resources and scans display-class PCI devices for a containing memory resource.

State and persistence: static boot/runtime state tracks one firmware framebuffer PCI owner. It mutates `sysfb_primary_display.screen` when applying fixups. No disk persistence.

Dependencies and integration points: depends on PCI fixup infrastructure, `sysfb_primary_display`, `screen_info_resources`, PCI bus-to-resource translation, and display-class resource matching. Integrates with firmware framebuffer/simple framebuffer setup.

Risks: only one LFB owner is tracked. Invalid relocation warns but leaves consumers dependent on later handling. Resource math must avoid overflow and relies on firmware screen_info accuracy. PCI device references from scanning must be managed by callers according to PCI API expectations.

Test signals: boot systems where EFI/VESA framebuffer is inside a display BAR; test PCI BAR relocation before sysfb registration; validate offset calculation through host bridge translation; run unsupported/non-LFB types; verify `screen_info_pci_dev` returns matching pdev or NULL/ERR_PTR correctly.
