# sources/distributed-fs/ceph-client/drivers/usb/cdns3/drd.h

Purpose: describes Cadence DRD/OTG MMIO layouts for CDNS3 v0, CDNS3 v1, and CDNSP v2 and provides all command/status/interrupt/override bit definitions used by the DRD implementation.

Important APIs/types/functions: defines `struct cdns3_otg_regs`, `struct cdns3_otg_legacy_regs`, `struct cdnsp_otg_regs`, `struct cdns_otg_common_regs`, `struct cdns_otg_irq_regs`, DID detection macros, OTG command/status/interrupt masks, strap values, ready bits, override bits, and declarations for DRD helper functions.

Control flow: no executable flow; the header encodes register addressing and bit semantics consumed by `drd.c` and role code.

State and persistence: register structs mirror persistent hardware state such as command, status, OTG state, interrupt enable/vector, simulate, override, suspend control, and PHY reset configuration registers.

Dependencies and integration: includes Linux OTG definitions and `core.h`; it is the ABI-like internal contract between generic cdns3 core and generation-specific OTG register maps.

Risks: v0/v1/v2 register offsets differ; using the wrong struct for a detected version would corrupt unrelated registers. Some strap and ready bit meanings differ for CDNSP, requiring the version checks used in `drd.c`.

Test signals: compile-time consumers plus hardware probe on each controller generation, especially CDNSP ready-bit inversion and v0 ID-pullup override, are the primary validation signals.
