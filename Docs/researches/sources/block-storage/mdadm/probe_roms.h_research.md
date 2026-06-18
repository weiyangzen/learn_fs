# File Research: sources/block-storage/mdadm/probe_roms.h

Purpose: public interface for the option ROM probing helper.

Exports:
- `probe_roms_init(unsigned long align)`
- `probe_roms_exit(void)`
- `probe_roms(void)`
- `scan_adapter_roms(scan_fn fn)`
- `scan_fn`, a callback receiving `start`, `end`, and `data` pointers for a discovered ROM.

Notes:
- The header has no include guard.
- It deliberately exposes only lifecycle, scan, and callback traversal APIs; ROM resource internals remain private to `probe_roms.c`.
