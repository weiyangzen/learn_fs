# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-ext-caps.h

Purpose: defines generic xHCI capability, command/status, and extended capability constants plus the inline scanner used throughout xHCI to traverse extended capability lists.

Important APIs and types: macros decode capability length, HCC extended capability pointer, extended capability ID/NEXT/VALUE, protocol port fields, PSI fields, legacy ownership bits, L1/HLC/BLC flags, Intel vendor IDs, Intel SPR tunnel detection offsets, command/status bits, and IRQ masks. `struct xhci_protocol_caps` reflects the supported protocol capability header. `xhci_find_next_ext_cap()` is the key inline API.

Control flow: `xhci_find_next_ext_cap(base, start, id)` starts from HCCPARAMS when `start` is 0 or the HCCPARAMS offset, converts xECP dword offsets to byte offsets, follows each NEXT pointer, skips the start capability itself on subsequent searches, and returns the next matching offset or the next capability for `id == 0`. It stops on missing lists, NEXT zero, or all-ones MMIO reads.

State and persistence: no runtime state. The scanner reads MMIO and returns byte offsets into the controller capability space.

Dependencies and integration points: includes `linux/io.h` for `readl()`. Used by debugfs, DbC discovery, role-switch vendor capability handling, roothub port-array setup, and Intel USB4 tunnel detection.

Risks: malformed hardware capability chains can still cause repeated or out-of-range offsets; `XHCI_MAX_EXT_CAPS` is defined but this inline scanner does not enforce an iteration bound. Callers must treat offset 0 as not found and must add offsets to the correct MMIO base. All-ones reads are treated as device removal/dead hardware.

Test signals: controllers with no ext caps; multiple protocol caps; repeated calls with previous offset; `id == 0` enumeration; hot-removal/all-ones MMIO behavior; malformed NEXT pointer review in fuzzed/emulated hardware.
