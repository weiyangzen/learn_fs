# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mcs.h

## Purpose

`mcs.h` is the private interface and data-model header for the OcteonTX2 AF MCS MACsec driver. It defines hardware limits, interrupt bits, per-device state, resource ownership maps, variant operation callbacks, register access inlines, and the exported helper prototypes used by `mcs.c`, `mcs_cnf10kb.c`, and `mcs_rvu_if.c`.

## Important APIs, Types, And Constants

Hardware identity and limits include `PCI_DEVID_CN10K_MCS`, `MCS_ID_MASK`, `MCS_MAX_PFS`, port masks, custom tag limits, control packet rule counts and offsets, reserved resource count, interrupt vector IDs, BBE/PAB interrupt masks, and CPM RX/TX interrupt bits.

`struct mcs_pfvf` stores the enabled interrupt mask for one PF or VF. `struct mcs_intr_event` and `struct mcs_intrq_entry` define queued async notifications to PF/VF drivers. `struct secy_mem_map` is the normalized flow-to-SecY/SC/SCI mapping passed to family-specific map writers.

`struct mcs_rsrc_map` owns all per-direction software resource state: owner arrays for flow IDs, SecY entries, SC entries, SA entries, and control packet rules, plus the `rsrc_bmap` allocation bitmaps. `struct hwinfo` describes per-family capacities and topology. `struct mcs` is the main device state: BAR base, PCI/device pointers, hardware info, RX/TX maps, PF map, MCS ID, ops table, list node, stats mutex, PF/VF interrupt masks, RVU back pointer, TX active-SA cache, and bypass state.

`struct mcs_ops` abstracts the family-specific operations for capabilities, parser configuration, TX/RX SA map programming, flow-to-SecY mapping, and BBE/PAB interrupt handling. `mcs_reg_write()` and `mcs_reg_read()` are the MMIO accessors used throughout the driver.

## Control Flow

The header does not execute logic itself, but it establishes the control boundaries. PCI probe creates `struct mcs`, selects an `mcs_ops` table, calls capability and parser callbacks, and then common code calls the exported APIs. RVU mailbox handlers call the prototypes declared here after validating MCS IDs and holding resource/stat locks where needed.

The interrupt path also follows types from this header: hardware-specific handlers fill `struct mcs_intr_event`, `mcs_add_intr_wq_entry()` masks it against the target PF/VF `intr_mask`, and workqueue code sends an upward mailbox notification.

## State And Persistence Behavior

The header defines transient kernel state used to track persistent device programming. Resource bitmaps and owner maps are the authoritative software view of which PF/VF owns each hardware table entry. `hwinfo` determines how much hardware state exists and which register layout is active. `bypass` mirrors external bypass configuration. None of this state is persisted across driver reloads; the hardware state is rebuilt at probe/RVU init and cleaned on FLR/remove.

## Dependencies And Integration Points

`mcs.h` includes `<linux/bits.h>` and `rvu.h`, so it depends on RVU mailbox types, `struct rsrc_bmap`, `enum mcs_direction`, and all MCS mailbox request/response structures. It is included by the common driver, the CNF10KB variant file, and the RVU mailbox bridge. It also declares `extern struct pci_driver mcs_driver` for driver registration elsewhere in the AF module.

## Risks

Because `mcs.h` is shared across the common, variant, and RVU layers, layout or semantic changes have broad impact. Any change to resource limits or bit masks must match both hardware register layout and mailbox ABI expectations. `struct mcs_ops` additions require all variants to be updated together. The inline MMIO helpers assume `reg_base` is valid and offsets are already family-correct, putting correctness pressure on `mcs_reg.h`.

## Test Signals

Compile-time signals are missing prototypes, incomplete `mcs_ops` initializers, and mailbox type mismatches. Runtime signals include correct hardware-info responses, expected resource counts per family, interrupt masks honored per PF/VF, and no invalid BAR access during probe, RVU init, interrupt handling, or remove.
