# Research: sources/distributed-fs/ceph-client/drivers/media/radio/Makefile

Purpose: maps radio driver Kconfig symbols to object files and subdirectories. It keeps entries alphabetically sorted by Kconfig name.

Important mappings in this subset: `CONFIG_RADIO_ISA` builds `radio-isa.o`; `CONFIG_RADIO_AZTECH`, `RADIO_CADET`, `RADIO_GEMTEK`, `RADIO_RTRACK`, and `RADIO_MAXIRADIO` build their respective drivers; `CONFIG_USB_DSBR`, `USB_KEENE`, and `USB_MA901` build USB drivers. `shark2-objs` composes a multi-object driver outside this subset.

Control flow/state: no runtime state; it controls compilation/linking. Risks are stale Kconfig symbol names or missing helper object linkage. Test signals are build success for each symbol and `make W=1`/modpost coverage.
