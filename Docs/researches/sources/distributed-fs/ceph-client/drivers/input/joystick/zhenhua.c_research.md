# sources/distributed-fs/ceph-client/drivers/input/joystick/zhenhua.c

Purpose: supports RC transmitters using the Zhen Hua five-byte serial protocol, such as Walkera Lama/EasyCopter transmitters, as four-axis joysticks.

Important APIs/types/functions: `struct zhenhua` contains input device, packet index, five-byte buffer, and phys path. `zhenhua_interrupt` frames and bit-reverses incoming bytes. `zhenhua_process_packet` reports ABS_Y, ABS_X, ABS_RZ, and ABS_Z. Connect/disconnect implement serio binding.

Control flow: the interrupt handler treats raw byte `0xef` as the synchronization marker, resets the index on it, ignores bytes until synchronized, stores `bitrev8(data)` for each packet byte, and processes once five bytes are collected. The decoder maps bytes 1-4 directly to four analog axes and syncs. Connect declares an ABS-only input device with 50..200 ranges for all four axes.

State and persistence: runtime state is only the packet buffer and index. No calibration or persistent settings exist.

Dependencies and integration: uses `SERIO_ZHENHUA`, `linux/bitrev.h`, serio registration, and Linux input. It reports `BUS_RS232` with fixed vendor/product placeholders.

Risks: comments mention sync `0xf7`, but code checks raw `0xef` before bit reversal; maintenance should preserve the raw-versus-reversed distinction. There is no validation that data bytes are in 50..200 after bit reversal. A missed sync byte drops reports until the next sync.

Test signals: verify sync on raw `0xef`, confirm bit reversal produces expected 0xf7/data values, test four axis reports through `evtest`, and feed out-of-range/misaligned bytes to confirm ignore/resync behavior.
