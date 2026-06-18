<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/console.c -->
## sources/distributed-fs/ceph-client/arch/alpha/kernel/console.c

**Purpose:** Finds and initializes VGA console resources on Alpha systems where VGA lives behind a nonzero PCI hose.

**Important APIs/types/functions:** `pci_vga_hose`, `alpha_vga`, `default_vga_hose_select`, `locate_and_init_vga`, and `find_console_vga_hose`.

**Control flow:** `locate_and_init_vga` scans VGA-class PCI devices, chooses a hose, requests VGA I/O resources relative to that hose, sets `pci_vga_hose`, and takes over the VGA console. Firmware CTB parsing can preselect the console graphics hose.

**State and persistence behavior:** Global `pci_vga_hose` records the active VGA hose; `alpha_vga` resource is rebased and requested once.

**Dependencies and integration points:** Depends on PCI enumeration, HWRPB CTB, VGA console, console locking, Alpha PCI hose list, and `asm/vga.h` fixups.

**Risks:** `alpha_vga.start/end` are mutated by adding hose offset; repeated calls can double-add if not guarded by hose/console state. Wrong hose selection breaks console I/O.

**Test signals:** Boot VGA console on multi-hose hardware, scan multiple VGA devices with custom selector, and verify resource requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/console.c -->
