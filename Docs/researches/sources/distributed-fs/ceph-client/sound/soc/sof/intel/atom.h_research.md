# sources/distributed-fs/ceph-client/sound/soc/sof/intel/atom.h

Purpose: `atom.h` is the shared register-layout and API contract for Atom HiFi EP SOF support. It collects DSP memory/peripheral offsets, BAR indexes, panic decoding, mailbox sizing, and function declarations consumed by `atom.c`, `byt.c`, and any other Atom-family platform glue.

Important definitions: it defines IRAM, DRAM, SHIM, mailbox, exception, DMAC, SSP, stack dump, and PCI BAR sizes. BAR indexes are `DSP_BAR`, `PCI_BAR`, and `IMR_BAR`. `PANIC_OFFSET(x)` extracts the high panic offset bits from an IPC value. The public prototypes cover IRQ handling, IPC send, mailbox/window offsets, run/reset/dump, ACPI machine selection, machine parameter assignment, and the exported `atom_dai[]` table.

Control flow and integration: because this is a header, it does not execute, but it fixes the low-level addressing assumptions used by the Atom operations. `byt.c` uses memory and peripheral constants for debugfs maps and MMIO BAR setup, while `atom.c` uses SHIM/mailbox constants for IPC and panic dump flow.

State and persistence behavior: constants here define persistent ABI-like hardware assumptions. A wrong offset would make state reads and writes hit the wrong register or memory window across every Atom platform using these helpers.

Dependencies, risks, and test signals: the header assumes `struct snd_sof_dev`, `struct snd_sof_ipc_msg`, `struct snd_soc_acpi_mach`, and `struct snd_soc_dai_driver` are visible to including C files. Risks include shared-name collisions for generic BAR constants and accidental drift from hardware manuals. Test signals are successful Atom firmware load, readable debugfs memory windows, working IPC panic decoding, and no compiler warnings for exported function prototypes or namespace imports.
