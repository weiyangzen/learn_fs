<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/atom/punit_atom_debug.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/atom/punit_atom_debug.c

## Purpose
`punit_atom_debug.c` is a debug driver for Intel Atom SoC Punit power-state visibility. It exposes North Complex device D-state information through debugfs and, when ACPI suspend support is present, checks selected devices before s2idle.

## Important APIs, types, and functions
`struct punit_device` maps device names to IOSF PMC register/bit positions. Tables cover Bay Trail, Tangier/Merrifield, and Cherry Trail. `punit_dev_state_show()` reads IOSF MBI registers and prints D0/D0i1/D0i2/D0i3. `punit_dbgfs_register()` creates `debugfs/punit_atom/dev_power_state`. `punit_s2idle_check()` reports devices still in D0 before low-power idle. `punit_atom_debug_init()` matches CPUs with `x86_match_cpu()`.

## Control flow
Module init matches an Atom CPU with MWAIT support, selects the right Punit table, registers debugfs, and registers ACPI LPS0 check ops if enabled. Debugfs reads iterate the table and issue `iosf_mbi_read()` calls. Exit unregisters LPS0 ops and removes debugfs recursively.

## State and persistence behavior
Persistent state is minimal: `punit_dbg_file` for debugfs removal and `punit_dev` for s2idle checks. Hardware state is read-only; the driver does not alter Punit registers.

## Dependencies and integration points
It depends on CPU model matching, IOSF MBI PMC access, debugfs, seq_file, ACPI LPS0 hooks, suspend support, and Intel family IDs.

## Risks and edge cases
IOSF reads can fail and are reported per device. The s2idle check skips MIO because it remains on until late suspend. CPU matching must select correct register layouts or D-state names will be misleading.

## Test signals
On supported Atom platforms, read `debugfs/punit_atom/dev_power_state`, trigger s2idle and inspect pre-suspend logs, verify unsupported CPUs return `-ENODEV`, and confirm module removal cleans debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/atom/punit_atom_debug.c -->
