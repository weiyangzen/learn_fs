# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-proc.c

Purpose: creates DICE proc diagnostics for raw DICE register state and detected stream formation tables.

Important APIs/functions: `dice_proc_read_mem`, `dice_proc_fixup_string`, `dice_proc_read`, `dice_proc_read_formation`, `add_node`, and `snd_dice_create_proc`.

Control flow and state: proc reads fetch the section table and selected global/TX/RX/ext-sync registers, byte-swap quadlets, fix DICE string endianness, and print clock, enable, status, stream, AC3, and sync details. Formation reads print cached TX/RX PCM/MIDI counts for each stream and rate mode. No persistent state is changed, except extended status reads may clear device slip bits per interface semantics.

Dependencies/integration: depends on DICE register macros, FireWire transactions, ALSA info APIs, and detected format caches. Risks include reading variable-sized sections with minimum assumptions, string byte order handling, and side effects of reading slip status. Test signals are readable `firewire/dice` and `firewire/formation` proc nodes with sane section offsets and channel counts.
